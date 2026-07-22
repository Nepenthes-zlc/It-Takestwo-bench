#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / 'mc_rollout') not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / 'mc_rollout'))
if str(PROJECT_ROOT / 'verl_adapter') not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / 'verl_adapter'))

from game_functions import load_task_list
from launch import DEFAULT_TASKS
from build_dataset import build_prompt, load_scene_colors, ATOMIC_ROLE_BY_AGENT


def angle_delta(current: float, target: float) -> float:
    return (float(current) - float(target) + 180.0) % 360.0 - 180.0


def door_target(task: dict[str, Any]) -> list[float]:
    goal = task['players']['player_b'].get('goal', {})
    target = goal.get('target_pos')
    if isinstance(target, list) and len(target) >= 3:
        return [float(target[0]), float(target[1]) + 1.0, float(target[2])]
    reg = goal['target_region']
    return [(float(reg[0]) + float(reg[3])) / 2.0 + 0.5, float(reg[1]) + 1.0, (float(reg[2]) + float(reg[5])) / 2.0 + 0.5]


def geometry(task: dict[str, Any]) -> dict[str, float]:
    player = task['players']['player_b']
    pos = [float(v) for v in player['start_pos']]
    rot = [float(v) for v in player.get('start_rotation', [0.0, 0.0])]
    yaw = rot[0] if rot else 0.0
    pitch = rot[1] if len(rot) > 1 else 0.0
    target = door_target(task)
    eye = [pos[0], pos[1] + 1.35, pos[2]]
    dx, dy, dz = target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]
    horiz = max(math.hypot(dx, dz), 1e-6)
    desired_yaw = math.degrees(math.atan2(-dx, dz))
    desired_pitch = math.degrees(math.atan2(-dy, horiz))
    yaw_err = abs(angle_delta(yaw, desired_yaw))
    pitch_err = abs(pitch - desired_pitch)
    dist = math.hypot(target[0] - pos[0], target[2] - pos[2])
    geom_score = 0.55 * min(yaw_err / 180.0, 1.0) + 0.25 * min(pitch_err / 45.0, 1.0) + 0.20 * min(dist / 12.0, 1.0)
    return {'yaw_error': round(yaw_err, 3), 'pitch_error': round(pitch_err, 3), 'distance': round(dist, 3), 'geometry_score': round(geom_score, 4)}


def collect_rollout_stats(run_dir: Path) -> dict[int, dict[str, float]]:
    stats: dict[int, dict[str, float]] = defaultdict(lambda: {'attempts': 0, 'successes': 0, 'reward_sum': 0.0, 'steps_sum': 0.0})
    if not run_dir or not run_dir.exists():
        return {}
    task_re = re.compile(r'_task(\d+)_')
    for steps_path in run_dir.glob('*/steps.jsonl'):
        m = task_re.search(steps_path.parent.name)
        if not m:
            continue
        task_index = int(m.group(1))
        try:
            rows = [json.loads(line) for line in steps_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        except Exception:
            continue
        if not rows:
            continue
        success = any(bool(row.get('done')) or float(row.get('binary_reward') or 0.0) > 0.0 for row in rows)
        reward = max(float(row.get('reward') or 0.0) for row in rows)
        stats[task_index]['attempts'] += 1
        stats[task_index]['successes'] += 1 if success else 0
        stats[task_index]['reward_sum'] += reward
        stats[task_index]['steps_sum'] += len(rows)
    out: dict[int, dict[str, float]] = {}
    for idx, row in stats.items():
        attempts = max(1, int(row['attempts']))
        out[idx] = {
            'attempts': attempts,
            'success_rate': round(float(row['successes']) / attempts, 4),
            'avg_reward': round(float(row['reward_sum']) / attempts, 4),
            'avg_steps': round(float(row['steps_sum']) / attempts, 2),
        }
    return out


def combined_rank(tasks: list[dict[str, Any]], rollout_stats: dict[int, dict[str, float]]) -> list[dict[str, Any]]:
    rows = []
    for idx, task in enumerate(tasks):
        geo = geometry(task)
        emp = rollout_stats.get(idx)
        if emp and emp.get('attempts', 0) > 0:
            failure = 1.0 - float(emp['success_rate'])
            low_reward = 1.0 - float(emp['avg_reward'])
            # Empirical success is the strongest signal; geometry breaks ties and covers sparse runs.
            difficulty = 0.55 * failure + 0.25 * low_reward + 0.20 * float(geo['geometry_score'])
            source = 'rollout+geometry'
        else:
            difficulty = float(geo['geometry_score'])
            source = 'geometry_only'
            emp = {'attempts': 0, 'success_rate': None, 'avg_reward': None, 'avg_steps': None}
        rows.append({'task_index': idx, 'task_id': task.get('id', idx), 'scene_id': task.get('scene_id'), 'difficulty': round(difficulty, 4), 'difficulty_source': source, **geo, **emp})
    return sorted(rows, key=lambda r: (r['difficulty'], r['task_index']))


def pick_evenly(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    if len(rows) <= limit:
        return rows
    chosen = []
    used = set()
    # 8 easy, 8 medium, 8 hard for limit=24; generalizes by thirds.
    thirds = [rows[: len(rows)//3], rows[len(rows)//3 : 2*len(rows)//3], rows[2*len(rows)//3 :]]
    per = [limit // 3, limit // 3, limit - 2 * (limit // 3)]
    for group, n in zip(thirds, per):
        if not group:
            continue
        if n == 1:
            picks = [group[len(group)//2]]
        else:
            picks = [group[round(i * (len(group)-1) / (n-1))] for i in range(n)]
        for row in picks:
            if row['task_index'] not in used:
                chosen.append(row)
                used.add(row['task_index'])
    # Fill any duplicate gaps by globally spaced rows.
    for row in rows:
        if len(chosen) >= limit:
            break
        if row['task_index'] not in used:
            chosen.append(row)
            used.add(row['task_index'])
    return sorted(chosen, key=lambda r: (r['difficulty'], r['task_index']))


def make_row(task: dict[str, Any], original_task_index: int, row_index: int, split: str, seed: int, train_instance_count: int) -> dict[str, Any]:
    controlled_agent = 'AgentB'
    atomic_role = ATOMIC_ROLE_BY_AGENT[controlled_agent]
    return {
        'data_source': 'it_taketwo_minecraft',
        'agent_name': 'minecraft_agent',
        'prompt': build_prompt(task, 'single_agent', controlled_agent, atomic_role),
        'ability': 'minecraft_rollout',
        'reward_model': {'style': 'rule', 'ground_truth': 'success'},
        'extra_info': {
            'split': split,
            'index': row_index,
            'task_index': original_task_index,
            'task_id': task.get('id'),
            'scene_id': task.get('scene_id'),
            'random_seed': seed + row_index,
            'instance_index': row_index % max(1, train_instance_count) + 1,
            'task_mode': 'single_agent',
            'controlled_agent': controlled_agent,
            'atomic_role': atomic_role,
            'difficulty_subset': 'difficulty24',
        },
    }


def write_parquet(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), str(path))
    print(f'wrote {len(rows)} rows -> {path}')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tasks', type=Path, default=DEFAULT_TASKS)
    ap.add_argument('--run-dir', type=Path, default=None)
    ap.add_argument('--output-dir', type=Path, required=True)
    ap.add_argument('--limit', type=int, default=24)
    ap.add_argument('--seed', type=int, default=20260630)
    ap.add_argument('--train-instance-count', type=int, default=24)
    args = ap.parse_args()

    tasks_path = args.tasks.resolve()
    tasks = load_task_list(tasks_path)
    load_scene_colors(tasks_path.parent / 'scene_manifest.json')
    stats = collect_rollout_stats(args.run_dir) if args.run_dir else {}
    ranked = combined_rank(tasks, stats)
    selected = pick_evenly(ranked, args.limit)
    selected_indices = [int(row['task_index']) for row in selected]

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        'tasks_path': str(tasks_path),
        'run_dir': str(args.run_dir.resolve()) if args.run_dir else None,
        'selection': '8 easy + 8 medium + 8 hard from difficulty-ranked tasks',
        'selected_task_indices': selected_indices,
        'selected': selected,
        'ranked_all': ranked,
    }
    (out / 'difficulty_selection.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    train_rows = [make_row(tasks[idx], idx, i, 'train', args.seed, args.train_instance_count) for i, idx in enumerate(selected_indices)]
    val_rows = [make_row(tasks[idx], idx, i, 'val', args.seed + 100000, args.train_instance_count) for i, idx in enumerate(selected_indices)]
    write_parquet(train_rows, out / 'train.parquet')
    write_parquet(val_rows, out / 'val.parquet')
    print('selected_task_indices:', ','.join(str(i) for i in selected_indices))


if __name__ == '__main__':
    main()
