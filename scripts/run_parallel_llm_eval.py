#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_CONFIG = ROOT / "yaml" / "lowlevel_qwen25vl7b_elevator_door_hard4.yaml"
DEFAULT_INSTANCE_TEMPLATE = ROOT / "yaml" / "instances_train24_keep_running.yaml"
DEFAULT_TASKS = ROOT / "assert" / "ConstructScene" / "generated" / "generated_tasks.json"
DEFAULT_PYTHON = "/home/azvm/miniconda3/envs/verl/bin/python"


def resolve_path(value: str | Path, *, base: Path = ROOT) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def safe_name(value: str) -> str:
    value = value.strip().replace("/", "-")
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value)
    return value.strip("-") or "model"


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML must be a mapping: {path}")
    return data


def build_runtime_config(template_path: Path, instance_count: int, output_dir: Path) -> Path:
    data = load_yaml(template_path)
    raw_instances = data.get("instances")
    if not isinstance(raw_instances, list) or not raw_instances:
        raise ValueError(f"runtime template has no instances: {template_path}")
    if instance_count > len(raw_instances):
        raise ValueError(f"requested {instance_count} instances, but {template_path} only has {len(raw_instances)}")

    instances: list[dict[str, Any]] = []
    for raw in raw_instances[:instance_count]:
        if not isinstance(raw, dict):
            raise ValueError(f"invalid instance entry in {template_path}: {raw!r}")
        item = dict(raw)
        root = Path(str(item["root"]))
        if not root.is_absolute():
            root = (template_path.parent / root).resolve()
        item["root"] = str(root)
        instances.append(item)

    runtime_config = {"parallel": instance_count, "instances": instances}
    runtime_dir = output_dir / "_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    runtime_path = runtime_dir / f"instances_{instance_count}.yaml"
    runtime_path.write_text(yaml.safe_dump(runtime_config, sort_keys=False), encoding="utf-8")
    return runtime_path


def add_arg(command: list[str], flag: str, value: str | int | float | Path | None) -> None:
    if value is None:
        return
    command.extend([flag, str(value)])


def command_line(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def build_command(args: argparse.Namespace, runtime_config: Path, output_dir: Path) -> list[str]:
    python_bin = str(args.python)
    command = [
        python_bin,
        str(ROOT / "scripts" / "run_from_yaml.py"),
        "--config",
        str(args.base_config),
    ]
    if args.print_command:
        command.append("--print-command")
    command.append("--")

    add_arg(command, "--config", runtime_config)
    add_arg(command, "--tasks", args.tasks)
    add_arg(command, "--task-indices", args.task_indices)
    add_arg(command, "--episodes-per-task", args.episodes_per_task)
    add_arg(command, "--parallel", args.instances)
    add_arg(command, "--output-dir", output_dir)
    add_arg(command, "--max-steps", args.max_steps)
    add_arg(command, "--capture-timeout", args.capture_timeout)

    add_arg(command, "--task-mode", args.task_mode)
    add_arg(command, "--controlled-agent", args.controlled_agent)
    add_arg(command, "--atomic-role", args.atomic_role)
    add_arg(command, "--policy", "ai")

    add_arg(command, "--agent-b-provider", args.provider)
    add_arg(command, "--agent-b-model", args.model)
    add_arg(command, "--agent-b-api-base-url", args.api_base_url)
    add_arg(command, "--agent-b-api-key", args.api_key)
    add_arg(command, "--agent-b-api-key-env", args.api_key_env)
    add_arg(command, "--agent-temperature", args.temperature)
    add_arg(command, "--agent-max-tokens", args.max_tokens)
    add_arg(command, "--agent-api-max-retries", args.max_retries)
    add_arg(command, "--agent-api-retry-delay", args.retry_delay)

    if args.dry_run:
        command.append("--dry-run")
    if args.extra:
        extra = args.extra[1:] if args.extra and args.extra[0] == "--" else args.extra
        command.extend(extra)
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run low-level It-Taketwo evaluation with 16/24 Minecraft instances against "
            "a vLLM or API OpenAI-compatible endpoint."
        )
    )
    parser.add_argument("--instances", type=int, choices=(16, 24), default=16, help="Number of Minecraft instances to use.")
    parser.add_argument("--engine", choices=("vllm", "api"), default="vllm", help="Label used in the default output dir.")
    parser.add_argument("--model", required=True, help="Model name sent to the endpoint.")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000/v1", help="OpenAI-compatible /v1 base URL.")
    parser.add_argument("--api-key", default="EMPTY", help="API key value. Use EMPTY for local vLLM.")
    parser.add_argument("--api-key-env", default=None, help="Read API key from this environment variable.")
    parser.add_argument(
        "--provider",
        default="openai_compatible",
        help="Agent provider. Use openai_compatible for vLLM/API, or closed_api/gpt55 for closed model clients.",
    )

    parser.add_argument("--task-indices", default="78,73,63,31", help="Comma/range task indices passed to rollout.")
    parser.add_argument("--episodes-per-task", type=int, default=4)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--max-steps", type=int, default=32)
    parser.add_argument("--capture-timeout", type=float, default=120)
    parser.add_argument("--output-dir", type=Path, default=None)

    parser.add_argument("--base-config", type=Path, default=DEFAULT_BASE_CONFIG)
    parser.add_argument("--instance-template", type=Path, default=DEFAULT_INSTANCE_TEMPLATE)
    parser.add_argument("--python", default=DEFAULT_PYTHON)

    parser.add_argument("--task-mode", default="single_agent")
    parser.add_argument("--controlled-agent", default="AgentB")
    parser.add_argument("--atomic-role", default="elevator_door_approach")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--retry-delay", type=float, default=1.0)

    parser.add_argument("--dry-run", action="store_true", help="Ask rollout to print planned episodes without running them.")
    parser.add_argument("--validate-only", action="store_true", help="Print the resolved command and generated runtime config path.")
    parser.add_argument("--print-command", action="store_true", help="Print the command before running.")
    parser.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args passed to mc_rollout/launch.py after --.")

    ns = parser.parse_args()
    ns.base_config = resolve_path(ns.base_config)
    ns.instance_template = resolve_path(ns.instance_template)
    ns.tasks = resolve_path(ns.tasks)
    if ns.output_dir is None:
        name = f"parallel_{ns.engine}_{safe_name(ns.model)}_{ns.instances}inst_{timestamp()}"
        ns.output_dir = ROOT / "runs" / name
    else:
        ns.output_dir = resolve_path(ns.output_dir)
    return ns


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    runtime_config = build_runtime_config(args.instance_template, args.instances, args.output_dir)
    command = build_command(args, runtime_config, args.output_dir)

    print(f"runtime_config: {runtime_config}", flush=True)
    print(f"output_dir: {args.output_dir}", flush=True)
    print("command: " + command_line(command), flush=True)
    if args.validate_only:
        return 0

    env = os.environ.copy()
    env.setdefault("JAVA_HOME", "/usr")
    env.setdefault("IT_TAKETWO_QUIET_MC_LOGS", "1")
    return subprocess.call(command, cwd=str(ROOT), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
