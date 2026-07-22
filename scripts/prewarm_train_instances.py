#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import math
import os
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MC_ROLLOUT_DIR = PROJECT_ROOT / "mc_rollout"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(MC_ROLLOUT_DIR) not in sys.path:
    sys.path.insert(0, str(MC_ROLLOUT_DIR))

from game_functions import datapack_dst, ensure_datapack, game_cmd, query_agent_pose, sanitize_superflat_above_ground, tp  # noqa: E402
from rollout import spawn_agents  # noqa: E402
from launch import DEFAULT_LOG_DIR, DEFAULT_PACK_SRC, InstanceRunner, load_instance_config, tcp_ready  # noqa: E402
from verl_adapter.mc_env import training_instance_config  # noqa: E402


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def pose_distance(pose: dict[str, Any], target: list[float]) -> float:
    pos = pose.get("pos")
    if not (isinstance(pos, list) and len(pos) >= 3):
        return math.inf
    return math.sqrt(sum((float(pos[idx]) - float(target[idx])) ** 2 for idx in range(3)))


def normalize_prewarm_agent(raw: str) -> str:
    value = raw.strip().lower().replace("_", "")
    if value in {"agenta", "a", "playera"}:
        return "AgentA"
    if value in {"agentb", "b", "playerb"}:
        return "AgentB"
    raise ValueError(f"unsupported prewarm agent: {raw!r}")


def prewarm_agents() -> tuple[str, ...]:
    raw_agents = os.environ.get("IT_TAKETWO_PREWARM_AGENTS")
    if raw_agents:
        agents = tuple(dict.fromkeys(normalize_prewarm_agent(part) for part in raw_agents.split(",") if part.strip()))
        if agents:
            return agents
    task_mode = os.environ.get("IT_TAKETWO_TASK_MODE", os.environ.get("TASK_MODE", "multiagent"))
    task_mode = task_mode.strip().lower().replace("-", "_")
    if task_mode in {"single", "single_agent", "singleagent", "atomic"}:
        return (normalize_prewarm_agent(os.environ.get("IT_TAKETWO_SINGLE_AGENT_DEFAULT", os.environ.get("SINGLE_AGENT_DEFAULT", "AgentA"))),)
    return ("AgentA", "AgentB")


def wait_for_agent_pose(
    runner: InstanceRunner,
    agent: str,
    target: list[float],
    *,
    attempts: int,
    delay: float,
    tolerance: float,
    required_consecutive: int,
) -> dict[str, Any]:
    last_pose: Any = None
    consecutive = 0
    for attempt in range(1, max(1, attempts) + 1):
        last_pose = query_agent_pose(runner, agent)
        if isinstance(last_pose, dict) and isinstance(last_pose.get("pos"), list):
            distance = pose_distance(last_pose, target)
            if distance <= tolerance:
                consecutive += 1
                if consecutive >= max(1, required_consecutive):
                    return last_pose
            else:
                consecutive = 0
        else:
            consecutive = 0
        if attempt < attempts:
            time.sleep(max(0.0, delay))
    raise RuntimeError(
        f"prewarm pose validation failed for {agent}: target={target} "
        f"tolerance={tolerance} last_pose={last_pose}"
    )


def apply_post_prewarm_setup(instance_config: Any, log_root: Path) -> bool:
    """Apply one-time world cleanup after an instance is warm and ready.

    This disables drops/spawning, removes non-player entities, and clears stale
    generated blocks above the superflat floor once per persistent instance."""
    if not env_flag("IT_TAKETWO_POST_PREWARM", True):
        return True
    runner = InstanceRunner(instance_config, log_root)
    try:
        runner.start()  # keep_running=True + tcp_ready => attaches without relaunch
        game_cmd(runner, "gamerule commandBlockOutput false", 2)
        game_cmd(runner, "gamerule sendCommandFeedback false", 2)
        game_cmd(runner, "gamerule logAdminCommands false", 2)
        game_cmd(runner, "gamerule doDaylightCycle false", 2)
        game_cmd(runner, "time set noon", 2)
        game_cmd(runner, "weather clear", 2)
        if env_flag("IT_TAKETWO_PREWARM_SANITIZE", False):
            sanitize_superflat_above_ground(runner)
        active_agents = prewarm_agents()
        all_targets = {
            "AgentA": [-8.0, -58.0, -8.0],
            "AgentB": [-6.0, -58.0, -8.0],
        }
        targets = {agent: all_targets[agent] for agent in active_agents}
        spawn_agents(runner, [], active_agents=active_agents)
        for agent, target in targets.items():
            tp(runner, agent, target, 0.0, 0.0, 10)
        if runner.tickgate is not None:
            runner.tickgate.cmd("advance_wait 10 1", timeout=30.0)
        pose_attempts = env_int("IT_TAKETWO_PREWARM_POSE_ATTEMPTS", 8)
        pose_delay = env_float("IT_TAKETWO_PREWARM_POSE_DELAY", 0.5)
        pose_tolerance = env_float("IT_TAKETWO_PREWARM_POSE_TOLERANCE", 3.0)
        pose_consecutive = env_int("IT_TAKETWO_PREWARM_POSE_CONSECUTIVE", 2)
        for agent, target in targets.items():
            wait_for_agent_pose(
                runner,
                agent,
                target,
                attempts=pose_attempts,
                delay=pose_delay,
                tolerance=pose_tolerance,
                required_consecutive=pose_consecutive,
            )
        return True
    except BaseException as exc:  # noqa: BLE001
        print(
            f"post-prewarm setup failed instance={instance_config.name}: {type(exc).__name__}: {exc}",
            flush=True,
        )
        return False
    finally:
        try:
            runner.close()  # keep_running=True => leaves the Minecraft process alive
        except BaseException:  # noqa: BLE001
            pass


def strict_post_prewarm(args: argparse.Namespace) -> bool:
    return bool(args.strict_post_prewarm) and env_flag("IT_TAKETWO_POST_PREWARM", True)


def require_post_prewarm_setup(args: argparse.Namespace, instance_config: Any, log_root: Path) -> bool:
    ok = apply_post_prewarm_setup(instance_config, log_root)
    if not ok and strict_post_prewarm(args):
        raise RuntimeError("post-prewarm setup/validation failed")
    return ok


def force_close_instance(instance_config: Any, log_root: Path) -> None:
    runner = InstanceRunner(instance_config, log_root)
    try:
        runner.close(force=True)
    except BaseException:  # noqa: BLE001
        pass


def resolve_project_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def read_puppet_port(root: Path) -> int | None:
    port_file = root / "run" / "socketpuppet_data" / "port.txt"
    if not port_file.exists():
        return None
    try:
        port = int(port_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None
    if 1 <= port <= 65535:
        return port
    return None


def latest_launch_log(log_root: Path, name: str) -> Path | None:
    log_dir = log_root / name
    if not log_dir.exists():
        return None
    logs = sorted(log_dir.glob("launch-*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def persistent_instance_ready(instance_config: Any) -> bool:
    if not tcp_ready(instance_config.tickgate_host, instance_config.tickgate_port, timeout=1.0):
        return False
    if not instance_config.use_puppet:
        return True
    puppet_port = instance_config.puppet_port or read_puppet_port(instance_config.root)
    if puppet_port is None:
        return False
    return tcp_ready(instance_config.puppet_host, puppet_port, timeout=1.0)


def prewarm_one(args: argparse.Namespace, index: int) -> dict[str, Any]:
    base_config = load_instance_config(resolve_project_path(args.config))
    base_config = replace(
        base_config,
        device=args.device or base_config.device,
        ready_timeout=args.ready_timeout or base_config.ready_timeout,
        puppet_timeout=args.puppet_timeout or base_config.puppet_timeout,
        keep_running=True,
    )
    instance_config = training_instance_config(base_config, args.prefix, index, args.base_port)
    pack_src = resolve_project_path(args.pack_src)
    log_root = resolve_project_path(args.log_dir) or DEFAULT_LOG_DIR
    pack_dst = datapack_dst(instance_config.root)
    ensure_datapack(pack_src, pack_dst, refresh=args.refresh_pack)

    last_exc: BaseException | None = None
    attempts = max(1, int(args.retries) + 1)
    for attempt in range(1, attempts + 1):
        if persistent_instance_ready(instance_config):
            log_path = latest_launch_log(log_root, instance_config.name)
            try:
                require_post_prewarm_setup(args, instance_config, log_root)
                return {
                    "index": index,
                    "name": instance_config.name,
                    "tickgate_port": instance_config.tickgate_port,
                    "log": str(log_path) if log_path else None,
                    "attempt": attempt,
                    "attached": True,
                }
            except BaseException as exc:  # noqa: BLE001
                last_exc = exc
                force_close_instance(instance_config, log_root)
                if attempt >= attempts:
                    break
                print(
                    f"prewarm retry instance={index:02d} attempt={attempt}/{attempts}: "
                    f"{type(exc).__name__}: {exc}",
                    flush=True,
                )
                time.sleep(max(0.0, float(args.retry_delay)))
                continue

        runner = InstanceRunner(instance_config, log_root)
        try:
            runner._start_launcher()
            deadline = time.time() + float(args.ready_timeout)
            while time.time() < deadline:
                if runner.proc is not None and runner.proc.poll() is not None:
                    raise RuntimeError(f"Minecraft exited early with code {runner.proc.returncode}; log={runner.log_path}")
                if persistent_instance_ready(instance_config):
                    log_path = runner.log_path or latest_launch_log(log_root, instance_config.name)
                    require_post_prewarm_setup(args, instance_config, log_root)
                    return {
                        "index": index,
                        "name": instance_config.name,
                        "tickgate_port": instance_config.tickgate_port,
                        "log": str(log_path) if log_path else None,
                        "attempt": attempt,
                    }
                time.sleep(1.0)
            raise TimeoutError(
                f"timed out waiting for persistent instance {instance_config.name} "
                f"tickgate={instance_config.tickgate_host}:{instance_config.tickgate_port}"
            )
        except BaseException as exc:
            last_exc = exc
            if runner.proc is not None and runner.proc.poll() is None:
                try:
                    runner._terminate_process()
                except BaseException:
                    pass
            if attempt >= attempts:
                break
            print(
                f"prewarm retry instance={index:02d} attempt={attempt}/{attempts}: {type(exc).__name__}: {exc}",
                flush=True,
            )
            time.sleep(max(0.0, float(args.retry_delay)))
    assert last_exc is not None
    raise last_exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prewarm persistent Minecraft train instances.")
    parser.add_argument("--config", default="yaml/instance_train_single.yaml")
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--prefix", default="instance-train")
    parser.add_argument("--base-port", type=int, default=25690)
    parser.add_argument("--parallel", type=int, default=8)
    parser.add_argument("--device", default=None)
    parser.add_argument("--ready-timeout", type=float, default=600.0)
    parser.add_argument("--puppet-timeout", type=float, default=180.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-delay", type=float, default=5.0)
    parser.add_argument("--pack-src", default=str(DEFAULT_PACK_SRC))
    parser.add_argument("--log-dir", default=str(DEFAULT_LOG_DIR))
    parser.add_argument(
        "--strict-post-prewarm",
        action=argparse.BooleanOptionalAction,
        default=env_flag("IT_TAKETWO_STRICT_POST_PREWARM", True),
        help="Fail and retry an instance when post-prewarm agent validation fails.",
    )
    parser.add_argument(
        "--refresh-pack",
        action="store_true",
        default=os.environ.get("IT_TAKETWO_REFRESH_PACK", "0").lower() in {"1", "true", "yes", "on"},
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count = max(1, int(args.count))
    parallel = max(1, min(int(args.parallel), count))
    print(f"prewarm persistent Minecraft instances: count={count} parallel={parallel}", flush=True)
    failures: list[tuple[int, BaseException]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = {pool.submit(prewarm_one, args, index): index for index in range(1, count + 1)}
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                result = future.result()
            except BaseException as exc:
                failures.append((index, exc))
                print(f"prewarm failed instance={index:02d}: {type(exc).__name__}: {exc}", flush=True)
            else:
                print(
                    f"prewarm ready {result["name"]}: tickgate_port={result["tickgate_port"]} "
                    f"attempt={result.get("attempt", 1)} log={result["log"]}",
                    flush=True,
                )
    if failures:
        lines = ", ".join(f"{idx:02d}:{type(exc).__name__}" for idx, exc in failures)
        raise SystemExit(f"prewarm failed for {len(failures)} instance(s): {lines}")


if __name__ == "__main__":
    main()
