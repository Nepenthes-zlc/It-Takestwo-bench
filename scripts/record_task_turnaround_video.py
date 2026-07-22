#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mc_rollout"))

from game_functions import capture_rollout_agent_pov, datapack_dst, ensure_datapack, game_cmd, load_task_list, parse_index_list, sanitize_superflat_above_ground, tp
from launch import DEFAULT_LOG_DIR, DEFAULT_PACK_SRC, InstanceRunner, JsonLineClient, load_instance_config, wait_for_tcp


def patch_tickgate_start_timeout() -> None:
    def connect_tickgate(self: InstanceRunner) -> None:
        wait_for_tcp(self.config.tickgate_host, self.config.tickgate_port, self.config.ready_timeout)
        self.tickgate = JsonLineClient(self.config.tickgate_host, self.config.tickgate_port, timeout=10.0)
        self.tickgate.cmd("ping", timeout=5.0)
        self.tickgate.cmd("wait_ready", timeout=self.config.ready_timeout)
        self.tickgate.cmd("pause", timeout=5.0)
        status = self.tickgate.cmd(f"observe_ready {self.config.render_frames}", timeout=self.config.ready_timeout)
        print(
            f"[{self.config.name}] TickGate ready: "
            f"server={status.get('completedServerTicks')} render={status.get('completedRenderFrames')}"
        )

    InstanceRunner._connect_tickgate = connect_tickgate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record 4-way AgentB POV frames for ordered tasks and stitch a video.")
    parser.add_argument("--tasks", type=Path, default=ROOT / "assert" / "ConstructScene" / "generated" / "generated_tasks.json")
    parser.add_argument("--config", type=Path, default=ROOT / "yaml" / "instance_train_single.yaml")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--task-start", type=int, default=0)
    parser.add_argument("--task-count", type=int, default=100)
    parser.add_argument("--task-indices", default=None, help="Comma/range list of task indices, e.g. 40,55. Overrides --task-start/--task-count.")
    parser.add_argument("--fps", type=float, default=4.0)
    parser.add_argument("--hide-hud", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--refresh-pack", action="store_true")
    parser.add_argument("--capture-ticks", type=int, default=2)
    parser.add_argument("--capture-render-frames", type=int, default=2)
    parser.add_argument("--capture-timeout", type=float, default=90.0)
    parser.add_argument("--pov-camera-settle-ticks", type=int, default=12)
    parser.add_argument("--pov-extra-settle-ticks", type=int, default=4)
    parser.add_argument("--pov-settle-render-frames", type=int, default=4)
    parser.add_argument("--turn-settle-ticks", type=int, default=4)
    parser.add_argument("--turn-settle-render-frames", type=int, default=1)
    parser.add_argument("--training-capture", action="store_true", help="Use the slower training-style AgentB POV capture path.")
    return parser.parse_args()


def spawn_agents(runner: InstanceRunner, commands: list[str]) -> None:
    for agent in ("AgentA", "AgentB"):
        game_cmd(runner, f"kill @e[type=player,name={agent}]", 5, commands=commands)
    for agent in ("AgentA", "AgentB"):
        game_cmd(runner, f"player {agent} spawn", 40, commands=commands)
        game_cmd(runner, f"gamemode creative {agent}", 5, commands=commands)
        game_cmd(runner, f"effect give {agent} minecraft:glowing 999 0 true", 5, commands=commands)


def task_pose(task: dict[str, Any], agent_key: str) -> tuple[list[float], float, float]:
    player = task["players"][agent_key]
    pos = [float(v) for v in player["start_pos"]]
    rot = [float(v) for v in player.get("start_rotation", [0.0, 0.0])]
    yaw = rot[0] if len(rot) > 0 else 0.0
    pitch = rot[1] if len(rot) > 1 else 0.0
    return pos, yaw, pitch


def write_video(frames: list[Path], output: Path, fps: float) -> tuple[int, int, int]:
    if not frames:
        raise RuntimeError("no frames to encode")
    first = cv2.imread(str(frames[0]))
    if first is None:
        raise RuntimeError(f"failed to read first frame: {frames[0]}")
    height, width = first.shape[:2]
    output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), float(fps), (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"failed to open video writer: {output}")
    try:
        for frame_path in frames:
            frame = cv2.imread(str(frame_path))
            if frame is None:
                raise RuntimeError(f"failed to read frame: {frame_path}")
            if frame.shape[:2] != (height, width):
                frame = cv2.resize(frame, (width, height))
            writer.write(frame)
    finally:
        writer.release()
    return len(frames), width, height


def main() -> int:
    args = parse_args()
    out_dir = args.output_dir.resolve()
    frames_dir = out_dir / "agent_b_pov_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("frame_*.png"):
        old.unlink()

    tasks = load_task_list(args.tasks)
    if args.task_indices:
        indices = parse_index_list(args.task_indices)
        for index in indices:
            if index < 0 or index >= len(tasks):
                raise IndexError(f"task index {index} out of range for {len(tasks)} tasks")
        selected = [(index, tasks[index]) for index in indices]
    else:
        end = min(len(tasks), args.task_start + args.task_count)
        selected = list(enumerate(tasks))[args.task_start:end]
        if len(selected) != args.task_count:
            raise ValueError(f"requested {args.task_count} tasks from {args.task_start}, but only {len(selected)} are available")

    patch_tickgate_start_timeout()
    instance_config = load_instance_config(args.config)
    instance_config.ready_timeout = max(instance_config.ready_timeout, 300.0)
    ensure_datapack(DEFAULT_PACK_SRC, datapack_dst(instance_config.root), refresh=args.refresh_pack)

    capture_args = SimpleNamespace(
        capture_ticks=args.capture_ticks,
        capture_render_frames=args.capture_render_frames,
        capture_timeout=args.capture_timeout,
        pov_camera_settle_ticks=args.pov_camera_settle_ticks,
        pov_extra_settle_ticks=args.pov_extra_settle_ticks,
        pov_settle_render_frames=args.pov_settle_render_frames,
        agent_pov_mode="camera_entity",
        hide_hud=args.hide_hud,
    )

    commands: list[str] = []
    records: list[dict[str, Any]] = []
    frame_paths: list[Path] = []
    previous_clear: str | None = None
    runner = InstanceRunner(instance_config, DEFAULT_LOG_DIR)
    os.environ.setdefault("IT_TAKETWO_QUIET_MC_LOGS", "1")
    try:
        runner.start()
        game_cmd(runner, "reload", 40, commands=commands)
        game_cmd(runner, "gamerule commandBlockOutput false", 5, commands=commands)
        game_cmd(runner, "gamerule sendCommandFeedback false", 5, commands=commands)
        game_cmd(runner, "gamerule logAdminCommands false", 5, commands=commands)
        sanitize_superflat_above_ground(runner, commands)
        game_cmd(runner, "gamemode spectator Dev", 5, commands=commands)
        game_cmd(runner, "effect give Dev minecraft:night_vision 999 0 true", 5, commands=commands)
        if args.hide_hud and runner.puppet is not None:
            runner.puppet.send("f1", wait=False)
            if runner.tickgate is not None:
                runner.tickgate.cmd("advance_wait 5 1", timeout=30.0)
        spawn_agents(runner, commands)
        if runner.puppet is not None and not args.training_capture:
            runner.puppet.send("pov AgentB", wait=False)
            runner.puppet.send("camera first_person", wait=False)
            if runner.tickgate is not None:
                runner.tickgate.cmd("advance_wait 4 1", timeout=30.0)

        for ordinal, (task_index, task) in enumerate(selected):
            clear_fn = task["scene_clear_function"]
            if previous_clear and previous_clear != clear_fn:
                game_cmd(runner, f"function {previous_clear}", 20, commands=commands)
            game_cmd(runner, f"function {clear_fn}", 20, commands=commands)
            game_cmd(runner, f"function {task['scene_setup_function']}", 40, commands=commands)
            previous_clear = clear_fn

            a_pos, a_yaw, a_pitch = task_pose(task, "player_a")
            b_pos, b_yaw, b_pitch = task_pose(task, "player_b")
            tp(runner, "AgentA", a_pos, a_yaw, a_pitch, 5, commands=commands)

            for view_i, offset in enumerate((0.0, 90.0, 180.0, 270.0)):
                yaw = b_yaw + offset
                tp(runner, "AgentB", b_pos, yaw, b_pitch, 5, commands=commands)
                pose = {"agent": "AgentB", "type": "minecraft:player", "pos": b_pos, "yaw": yaw, "pitch": b_pitch}
                if args.training_capture:
                    image = capture_rollout_agent_pov(runner, commands, "AgentB", pose, capture_args)
                else:
                    if runner.tickgate is not None:
                        runner.tickgate.cmd(f"advance_wait {args.turn_settle_ticks} {args.turn_settle_render_frames}", timeout=30.0)
                    image = runner.capture_image(
                        ticks=args.capture_ticks,
                        render_frames=args.capture_render_frames,
                        timeout=args.capture_timeout,
                    )
                    image["camera_entity"] = "AgentB"
                    image["camera_pose"] = pose
                frame_index = ordinal * 4 + view_i
                frame_path = frames_dir / f"frame_{frame_index:04d}_task{task_index:03d}_view{view_i}.png"
                frame_path.write_bytes(image["image_bytes"])
                frame_paths.append(frame_path)
                records.append(
                    {
                        "frame_index": frame_index,
                        "task_index": task_index,
                        "task_id": task.get("id"),
                        "scene_id": task.get("scene_id"),
                        "view_index": view_i,
                        "yaw_offset": offset,
                        "agent_b_pos": b_pos,
                        "agent_b_yaw": yaw,
                        "agent_b_pitch": b_pitch,
                        "frame": str(frame_path),
                        "serverTick": image.get("serverTick"),
                        "renderFrame": image.get("renderFrame"),
                    }
                )
                print(f"captured task={task_index:03d} view={view_i} frame={frame_index:04d}", flush=True)
    finally:
        runner.close()

    video_path = out_dir / "task000-099_agentB_4way_turnaround.mp4"
    frame_count, width, height = write_video(frame_paths, video_path, args.fps)
    manifest = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "tasks": str(args.tasks),
        "config": str(args.config),
        "task_start": args.task_start,
        "task_count": len(selected),
        "task_indices": [index for index, _ in selected],
        "frames_per_task": 4,
        "yaw_offsets": [0, 90, 180, 270],
        "fps": args.fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "video": str(video_path),
        "frames_dir": str(frames_dir),
        "records": records,
        "commands": commands,
        "log": str(runner.log_path) if runner.log_path else None,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("video", "frame_count", "width", "height", "fps", "log")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
