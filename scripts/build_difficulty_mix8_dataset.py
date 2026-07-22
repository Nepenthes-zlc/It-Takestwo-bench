#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "mc_rollout") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "mc_rollout"))
if str(PROJECT_ROOT / "verl_adapter") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "verl_adapter"))

from build_dataset import ATOMIC_ROLE_BY_AGENT, build_prompt, load_scene_colors  # noqa: E402
from build_difficulty24_dataset import collect_rollout_stats, combined_rank  # noqa: E402
from game_functions import load_task_list  # noqa: E402
from launch import DEFAULT_TASKS  # noqa: E402


def pick_spread(rows: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    if count <= 0:
        return []
    if len(rows) <= count:
        return list(rows)
    if count == 1:
        return [rows[len(rows) // 2]]
    return [rows[round(i * (len(rows) - 1) / (count - 1))] for i in range(count)]


def select_mix(ranked: list[dict[str, Any]], easy_count: int, medium_count: int, hard_count: int) -> list[dict[str, Any]]:
    if not ranked:
        return []
    n = len(ranked)
    one_third = n // 3
    two_third = (2 * n) // 3
    easy_pool = ranked[:one_third]
    medium_pool = ranked[one_third:two_third]
    hard_pool = ranked[two_third:]

    chosen: list[dict[str, Any]] = []
    for row in easy_pool[:easy_count]:
        chosen.append({**row, "difficulty_bucket": "easy"})
    for row in pick_spread(medium_pool, medium_count):
        chosen.append({**row, "difficulty_bucket": "medium"})
    for row in (hard_pool[-hard_count:] if hard_count > 0 else []):
        chosen.append({**row, "difficulty_bucket": "hard"})

    seen: set[int] = set()
    unique: list[dict[str, Any]] = []
    for row in chosen:
        idx = int(row["task_index"])
        if idx not in seen:
            unique.append(row)
            seen.add(idx)

    target = easy_count + medium_count + hard_count
    for row in ranked:
        if len(unique) >= target:
            break
        idx = int(row["task_index"])
        if idx not in seen:
            unique.append({**row, "difficulty_bucket": "fill"})
            seen.add(idx)
    return sorted(unique, key=lambda r: (float(r["difficulty"]), int(r["task_index"])))


def make_row(task: dict[str, Any], task_index: int, row_index: int, split: str, seed: int, train_instance_count: int) -> dict[str, Any]:
    controlled_agent = "AgentB"
    atomic_role = ATOMIC_ROLE_BY_AGENT[controlled_agent]
    return {
        "data_source": "it_taketwo_minecraft",
        "agent_name": "minecraft_agent",
        "prompt": build_prompt(task, "single_agent", controlled_agent, atomic_role),
        "ability": "minecraft_rollout",
        "reward_model": {"style": "rule", "ground_truth": "success"},
        "extra_info": {
            "split": split,
            "index": row_index,
            "task_index": task_index,
            "task_id": task.get("id"),
            "scene_id": task.get("scene_id"),
            "random_seed": seed + row_index,
            "instance_index": row_index % max(1, train_instance_count) + 1,
            "task_mode": "single_agent",
            "controlled_agent": controlled_agent,
            "atomic_role": atomic_role,
            "difficulty_subset": "mix8_2easy4medium2hard",
        },
    }


def write_parquet(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), str(path))
    print(f"wrote {len(rows)} rows -> {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--easy-count", type=int, default=2)
    parser.add_argument("--medium-count", type=int, default=4)
    parser.add_argument("--hard-count", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260702)
    parser.add_argument("--train-instance-count", type=int, default=24)
    args = parser.parse_args()

    tasks_path = args.tasks.resolve()
    tasks = load_task_list(tasks_path)
    load_scene_colors(tasks_path.parent / "scene_manifest.json")
    stats = collect_rollout_stats(args.run_dir) if args.run_dir else {}
    ranked = combined_rank(tasks, stats)
    selected = select_mix(ranked, args.easy_count, args.medium_count, args.hard_count)
    selected_indices = [int(row["task_index"]) for row in selected]

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "tasks_path": str(tasks_path),
        "run_dir": str(args.run_dir.resolve()) if args.run_dir else None,
        "selection": f"{args.easy_count} easy + {args.medium_count} medium + {args.hard_count} hard from difficulty-ranked tasks",
        "selected_task_indices": selected_indices,
        "selected": selected,
        "ranked_all": ranked,
    }
    (out / "difficulty_selection.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    train_rows = [make_row(tasks[idx], idx, i, "train", args.seed, args.train_instance_count) for i, idx in enumerate(selected_indices)]
    val_rows = [make_row(tasks[idx], idx, i, "val", args.seed + 100000, args.train_instance_count) for i, idx in enumerate(selected_indices)]
    write_parquet(train_rows, out / "train.parquet")
    write_parquet(val_rows, out / "val.parquet")
    print("selected_task_indices:", ",".join(str(i) for i in selected_indices))


if __name__ == "__main__":
    main()
