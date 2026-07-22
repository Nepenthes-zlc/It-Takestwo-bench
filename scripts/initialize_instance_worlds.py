#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_ROOT = ROOT / "env"
DEFAULT_TEMPLATE = ROOT / "bench/world_templates/superflat"
DEFAULT_PACK = ROOT / "bench/data/0714_2_class/datapacks/time_lock_difficulty_scene_pack"
WORLD_PATH = Path("run/saves/New World")
PACK_NAME = "multiagent_scene_pack"


def select_instances(env_root: Path, patterns: list[str]) -> list[Path]:
    matches = {path.resolve() for pattern in patterns for path in env_root.glob(pattern) if path.is_dir()}
    return sorted(matches, key=lambda path: path.name)


def running_pids(instance_root: Path) -> list[int]:
    run_root = (instance_root / "run").resolve()
    matches: list[int] = []
    for process in Path("/proc").iterdir():
        if not process.name.isdigit() or int(process.name) == os.getpid():
            continue
        try:
            cwd = (process / "cwd").resolve(strict=True)
            cwd.relative_to(run_root)
        except (FileNotFoundError, PermissionError, OSError, ValueError):
            continue
        matches.append(int(process.name))
    return sorted(matches)


def initialize_world(instance_root: Path, template: Path, pack_src: Path) -> Path:
    world = instance_root / WORLD_PATH
    if world.exists():
        shutil.rmtree(world)
    shutil.copytree(template, world)
    pack_dst = world / "datapacks" / PACK_NAME
    pack_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(pack_src, pack_dst)
    return world


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recreate superflat worlds and copy the datapack for test and training instances."
    )
    parser.add_argument("--env-root", type=Path, default=DEFAULT_ENV_ROOT)
    parser.add_argument("--patterns", nargs="+", default=["instance-test-*", "instance-train-*"])
    parser.add_argument("--world-template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--pack-src", type=Path, default=DEFAULT_PACK)
    parser.add_argument("--yes", action="store_true", help="Perform deletion; otherwise only print the plan.")
    parser.add_argument("--force-running", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env_root = args.env_root.expanduser().resolve()
    template = args.world_template.expanduser().resolve()
    pack_src = args.pack_src.expanduser().resolve()
    if not (template / "level.dat").is_file():
        raise SystemExit(f"missing superflat level.dat: {template}")
    if not (pack_src / "pack.mcmeta").is_file():
        raise SystemExit(f"missing datapack pack.mcmeta: {pack_src}")

    instances = select_instances(env_root, args.patterns)
    if not instances:
        raise SystemExit(f"no instances matched under {env_root}")
    print(f"instances={len(instances)} template={template} datapack={pack_src}")

    running: dict[Path, list[int]] = {}
    for instance in instances:
        pids = running_pids(instance)
        if pids:
            running[instance] = pids
        state = "RUNNING" if pids else "stopped"
        print(f"{state:7} {instance.name}: {instance / WORLD_PATH}")

    if not args.yes:
        print("dry-run only; pass --yes to delete and recreate these worlds")
        return
    if running and not args.force_running:
        details = ", ".join(f"{path.name}={pids}" for path, pids in running.items())
        raise SystemExit(f"refusing to modify running instances: {details}")

    for instance in instances:
        print(f"initialized {instance.name}: {initialize_world(instance, template, pack_src)}")


if __name__ == "__main__":
    main()
