#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "mc_rollout"))

from game_functions import game_cmd, load_task_list, query_agent_pose, send_agent_action, sync_datapack, tp  # noqa: E402
from launch import DEFAULT_LOG_DIR, DEFAULT_PACK_SRC, DEFAULT_TASKS, InstanceRunner, load_instance_config  # noqa: E402
from rollout import setup_rollout_world, spawn_agents  # noqa: E402


def yaw_delta(after: float, before: float) -> float:
    return (after - before + 180.0) % 360.0 - 180.0


def pose_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, float]:
    bpos = before["pos"]
    apos = after["pos"]
    dx = float(apos[0]) - float(bpos[0])
    dy = float(apos[1]) - float(bpos[1])
    dz = float(apos[2]) - float(bpos[2])
    return {
        "dx": dx,
        "dy": dy,
        "dz": dz,
        "horizontal": math.hypot(dx, dz),
        "yaw": yaw_delta(float(after["yaw"]), float(before["yaw"])),
        "pitch": float(after["pitch"]) - float(before["pitch"]),
    }


def wait_ticks(runner: InstanceRunner, ticks: int) -> None:
    if runner.tickgate is not None:
        runner.tickgate.cmd(f"advance_wait {ticks} 1", timeout=90.0)


def reset_agent(runner: InstanceRunner, start: dict[str, Any], settle_ticks: int) -> dict[str, Any]:
    tp(runner, "AgentB", start["pos"], start["yaw"], start["pitch"], max(5, settle_ticks))
    send_agent_action(runner, "AgentB", "wait")
    wait_ticks(runner, settle_ticks)
    return query_agent_pose(runner, "AgentB")


def run_action(
    runner: InstanceRunner,
    action: str,
    action_ticks: int,
    settle_ticks: int,
) -> dict[str, Any]:
    before = query_agent_pose(runner, "AgentB")
    send_agent_action(runner, "AgentB", action, action_ticks)
    wait_ticks(runner, action_ticks)
    send_agent_action(runner, "AgentB", "wait")
    wait_ticks(runner, settle_ticks)
    after = query_agent_pose(runner, "AgentB")
    return {"action": action, "before": before, "after": after, "delta": pose_delta(before, after)}


def summarize_action(action: str, deltas: list[dict[str, float]]) -> dict[str, Any]:
    def avg(key: str) -> float:
        return sum(float(delta[key]) for delta in deltas) / max(1, len(deltas))

    return {
        "action": action,
        "trials": len(deltas),
        "avg_horizontal": avg("horizontal"),
        "max_horizontal": max(float(delta["horizontal"]) for delta in deltas),
        "avg_yaw_delta": avg("yaw"),
        "avg_pitch_delta": avg("pitch"),
        "max_abs_yaw_delta": max(abs(float(delta["yaw"])) for delta in deltas),
        "max_abs_pitch_delta": max(abs(float(delta["pitch"])) for delta in deltas),
    }


def classify(summary: dict[str, Any]) -> str:
    action = summary["action"]
    move = float(summary["avg_horizontal"])
    yaw = abs(float(summary["avg_yaw_delta"]))
    pitch = abs(float(summary["avg_pitch_delta"]))
    if action in {"forward", "backward"}:
        if move > 0.05 and yaw < 2.0 and pitch < 2.0:
            return "clean"
        return "suspicious"
    if action in {"turn_left", "turn_right"}:
        if move < 0.04 and yaw > 5.0 and pitch < 2.0:
            return "clean"
        return "suspicious"
    if action in {"look_up", "look_down"}:
        if move < 0.04 and yaw < 2.0 and pitch > 5.0:
            return "clean"
        return "suspicious"
    if action == "wait":
        if move < 0.03 and yaw < 1.0 and pitch < 1.0:
            return "clean"
        return "suspicious"
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", type=Path, default=REPO / "yaml" / "instance_single.yaml")
    parser.add_argument("--task-index", type=int, default=0)
    parser.add_argument("--action-ticks", type=int, default=4)
    parser.add_argument("--settle-ticks", type=int, default=4)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    tasks = load_task_list(DEFAULT_TASKS)
    task = tasks[args.task_index]
    config = load_instance_config(args.instance)
    sync_datapack(config.root, DEFAULT_PACK_SRC, refresh=False)

    rollout_args = SimpleNamespace(
        hide_hud=False,
        randomize_starts=False,
        random_seed=None,
        start_position_jitter=0.0,
        start_yaw_jitter=0.0,
        start_pitch_min=-25.0,
        start_pitch_max=25.0,
    )

    player_b = task["players"]["player_b"]
    rotation = [float(value) for value in player_b.get("start_rotation", [0.0, 0.0])]
    start = {
        "pos": [float(value) for value in player_b["start_pos"]],
        "yaw": rotation[0] if len(rotation) > 0 else 0.0,
        "pitch": rotation[1] if len(rotation) > 1 else 0.0,
    }
    commands: list[str] = []
    actions = ["forward", "backward", "turn_left", "turn_right", "look_up", "look_down", "wait"]
    chain_actions = ["forward", "turn_left", "wait", "look_up", "wait", "turn_right", "wait", "backward", "look_down", "wait"]

    result: dict[str, Any] = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "task_index": args.task_index,
        "task_id": task.get("id"),
        "scene_id": task.get("scene_id"),
        "action_ticks": args.action_ticks,
        "settle_ticks": args.settle_ticks,
        "start": start,
        "isolated": [],
        "chain": [],
        "commands": commands,
    }

    runner = InstanceRunner(config, DEFAULT_LOG_DIR)
    try:
        runner.start()
        setup_rollout_world(runner, commands, task, rollout_args)
        spawn_agents(runner, commands, active_agents=("AgentB",))
        game_cmd(runner, "effect clear AgentB", 5, commands=commands)
        reset_agent(runner, start, args.settle_ticks)

        for action in actions:
            trials: list[dict[str, Any]] = []
            for _ in range(args.trials):
                reset_agent(runner, start, args.settle_ticks)
                trials.append(run_action(runner, action, args.action_ticks, args.settle_ticks))
            summary = summarize_action(action, [trial["delta"] for trial in trials])
            summary["status"] = classify(summary)
            result["isolated"].append({"summary": summary, "trials": trials})
            print(json.dumps(summary, ensure_ascii=False), flush=True)

        reset_agent(runner, start, args.settle_ticks)
        for action in chain_actions:
            step = run_action(runner, action, args.action_ticks, args.settle_ticks)
            result["chain"].append(step)
            print(json.dumps({"chain_action": action, **step["delta"]}, ensure_ascii=False), flush=True)
    finally:
        runner.close(force=True)

    output = args.output
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output = REPO / "runs" / f"action_cleanliness_tick_controlled_{stamp}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"WROTE {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
