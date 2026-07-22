from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MC_ROLLOUT_DIR = PROJECT_ROOT / "mc_rollout"
if str(MC_ROLLOUT_DIR) not in sys.path:
    sys.path.insert(0, str(MC_ROLLOUT_DIR))

from action_space import ALLOWED_ACTIONS  # noqa: E402
from game_functions import load_task_list  # noqa: E402
from launch import DEFAULT_TASKS  # noqa: E402


def resolve_project_path(path: str | Path) -> Path:
    value = Path(path).expanduser()
    if not value.is_absolute():
        value = PROJECT_ROOT / value
    return value.resolve()

MULTIAGENT_SYSTEM_PROMPT = (
    "You are the shared policy model for two Minecraft agents. "
    "During rollout you will be asked separately as AgentA and AgentB. "
    "For each request, act only as the named agent and return compact JSON only."
)

MULTIAGENT_USER_TEMPLATE = """Task: {task_description}
Scene id: {scene_id}
Task id: {task_id}

Allowed actions for each agent: {allowed_actions}

AgentA role and goal: {agent_a_role_goal}
AgentB role and goal: {agent_b_role_goal}
{failure_guidance}
The runtime will ask for one agent at a time using that agent's own first-person image.
When asked as one agent, respond with exactly one JSON object: {{"action":"<action>","reason":"<detailed reason with visual evidence, target position, teammate/marker state, and action rationale>"}}.
"""

SINGLE_AGENT_SYSTEM_PROMPT = (
    "You are controlling one Minecraft agent. Return JSON only."
)

SINGLE_AGENT_USER_TEMPLATE = """Task: {task_description}
Your role: {role}
Your goal: {atomic_goal}
{failure_guidance}
Reward rule: {reward_rule}

Scene id: {scene_id}
Task id: {task_id}
{scene_colors}Allowed actions: {allowed_actions}

Respond with exactly one JSON object: {{"action":"<action>","reason":"<2-3 short sentences: say whether the target is visible, where it is relative to the view center, and why you should turn/look or move forward now>"}}. Move forward only when the target is near the center of view. If the target is visible on the left, use turn_left; if it is visible on the right, use turn_right; if the target is visible above the center of the view, use look_up; if it is visible below the center of the view, use look_down. If the target is not visible in the view, keep turning left/right until you find and center it, then move forward. Do not use generic reasons such as press the pressure plate. If the view is filled by a blank wall, use backward to step away from the wall and regain a wider view before deciding where to go.
"""


SINGLE_AGENT_DOOR_USER_TEMPLATE = """Goal: find the black elevator door and move to the floor directly in front of it or into the doorway.

Scene colors: floor, walls, and ceiling are {floor_color}. The elevator door is {door_color}.
Mechanism: stepping on the pressure plate opens the door. If the door is open, look for the rectangular doorway opening in the door frame and move to that doorway opening.
Allowed actions: {allowed_actions}

Return exactly one JSON object with all four fields:
{{"action":"<action>","door_position":"left|right|up|down|center|none","door_state":"open|closed|none","reason":"<detailed visual reason that is consistent with action, door_position, and door_state>"}}

Output rules:
- door_position must describe the black door or rectangular doorway opening in the current image: left, right, up, down, center, or none.
- door_state must be open if you can see the rectangular doorway opening, closed if you can see the black closed door, and none if the door/opening is not visible.
- If the black door or doorway opening is not visible, set door_position to none and door_state to none.
- The JSON must be internally consistent: action must match door_position, and reason must agree with door_position, door_state, and action.

Use the image to decide:
- If door_position is left, use turn_left.
- If door_position is right, use turn_right.
- If door_position is up, use look_up.
- If door_position is down, use look_down.
- If door_position is center, use forward.
- If door_position is none, use turn_left or turn_right to search.
- If the view is mostly a blank wall, use backward once to regain a wider view.
"""

ATOMIC_ROLE_BY_AGENT = {
    "AgentA": "pressure_plate_hold",
    "AgentB": "elevator_door_approach",
}

ATOMIC_GOAL_BY_ROLE = {
    "pressure_plate_hold": "Find the 3x3 floor pressure-plate region and step onto any tile in it.",
    "pressure_plate": "Find the 3x3 floor pressure-plate region and step onto any tile in it.",
    "elevator_door_approach": "Walk up to the elevator door and step onto the floor right in front of it (or into the doorway).",
    "second_room_entry": "Walk up to the elevator door and step onto the floor right in front of it (or into the doorway).",
}

ATOMIC_REWARD_RULE_BY_ROLE = {
    "pressure_plate_hold": "Reward is 1.0 when you first step onto any tile in the 3x3 pressure-plate region. Before contact, distance progress can give up to 0.5, correct view-turning can give up to 0.25, and moving forward while the target is clearly off-center is penalized.",
    "pressure_plate": "Reward is 1.0 when you first step onto any tile in the 3x3 pressure-plate region. Before contact, distance progress can give up to 0.5, correct view-turning can give up to 0.25, and moving forward while the target is clearly off-center is penalized.",
    "elevator_door_approach": "Reward is 1.0 once you stand on the door-front pad (the door cells or the floor row directly in front of them); otherwise distance progress toward the door gives up to 0.5. Walking into a wall (a forward/backward that does not move you) is penalized, so back away from walls instead of pushing into them.",
    "second_room_entry": "Reward is 1.0 once you stand on the door-front pad (the door cells or the floor row directly in front of them); otherwise distance progress toward the door gives up to 0.5. Walking into a wall (a forward/backward that does not move you) is penalized, so back away from walls instead of pushing into them.",
}


def normalize_task_mode(value: str) -> str:
    mode = str(value or "multiagent").strip().lower().replace("-", "_")
    if mode in {"multi", "multi_agent", "multiagent"}:
        return "multiagent"
    if mode in {"single", "single_agent", "singleagent", "atomic"}:
        return "single_agent"
    raise ValueError(f"unsupported task mode: {value!r}")


def normalize_agent(value: str) -> str:
    agent = str(value or "AgentA").strip()
    lowered = agent.lower().replace("_", "")
    if lowered in {"agenta", "a", "playera"}:
        return "AgentA"
    if lowered in {"agentb", "b", "playerb"}:
        return "AgentB"
    raise ValueError(f"unsupported controlled agent: {value!r}")


def parse_atomic_agents(value: str) -> list[str]:
    agents = [normalize_agent(item) for item in str(value or "AgentA").replace(";", ",").split(",") if item.strip()]
    return agents or ["AgentA"]


def player_record(task: dict[str, Any], agent_name: str) -> dict[str, Any]:
    key = "player_a" if agent_name == "AgentA" else "player_b"
    value = task.get("players", {}).get(key, {})
    return value if isinstance(value, dict) else {}


def schema_role_goal(task: dict[str, Any], agent_name: str) -> tuple[str, str]:
    player = player_record(task, agent_name)
    role = str(player.get("role") or "participant").replace("_", " ")
    goal = player.get("goal") if isinstance(player.get("goal"), dict) else {}
    description = str(
        goal.get("description")
        or task.get("task_description")
        or task.get("description")
        or "Complete your assigned part of the task."
    )
    return role, description


def failure_guidance(task: dict[str, Any]) -> str:
    descriptions = [
        str(condition.get("description"))
        for condition in task.get("failure_conditions", []) or []
        if isinstance(condition, dict) and condition.get("description")
    ]
    return "Avoid these failure conditions: " + " ".join(descriptions) if descriptions else ""


def is_legacy_elevator_role(task: dict[str, Any], agent_name: str, atomic_role: str) -> bool:
    return (
        agent_name == "AgentB"
        and task.get("task_template") == "elevator_hold_door"
        and atomic_role in {"elevator_door_approach", "second_room_entry", "elevator_entry"}
    )


def default_task_atomic_role(task: dict[str, Any], agent_name: str) -> str:
    if task.get("task_template") == "elevator_hold_door":
        return ATOMIC_ROLE_BY_AGENT[agent_name]
    return str(player_record(task, agent_name).get("role") or ATOMIC_ROLE_BY_AGENT[agent_name])


# scene_id -> {floor,wall,ceiling,door,plate} color words, loaded from the scene manifest.
SCENE_COLORS: dict[str, dict[str, str]] = {}

_COLOR_OVERRIDES = {
    "polished_blackstone_pressure_plate": "black",
    "blackstone": "black",
    "stone_pressure_plate": "gray",
    "birch_pressure_plate": "tan",
    "quartz_block": "white",
    "gold_block": "gold",
    "lapis_block": "blue",
    "glowstone": "yellow",
}


def block_color_word(block: str | None) -> str:
    if not block:
        return "unknown"
    name = str(block).split(":")[-1]
    for key, word in _COLOR_OVERRIDES.items():
        if key in name:
            return word
    if name.endswith("_concrete"):
        return name[: -len("_concrete")].replace("_", " ")
    return name.replace("_", " ")


def load_scene_colors(manifest_path: Path) -> None:
    SCENE_COLORS.clear()
    if not manifest_path.is_file():
        return
    with manifest_path.open("r", encoding="utf-8") as fh:
        manifest = json.load(fh) or {}
    for scene in manifest.get("scenes", []):
        floor = block_color_word(scene.get("floor_block"))
        wall = block_color_word(scene.get("wall_block"))
        ceiling = block_color_word(scene.get("ceiling_block") or scene.get("wall_block"))
        SCENE_COLORS[str(scene.get("scene_id"))] = {
            "floor": floor,
            "wall": wall,
            "ceiling": ceiling,
            "door": block_color_word(scene.get("elevator_block")),
            "plate": block_color_word(scene.get("pressure_plate_block")),
        }


def scene_color_line(scene_id: str | None, controlled_agent: str | None) -> str:
    colors = SCENE_COLORS.get(str(scene_id))
    if not colors:
        return ""
    target = (
        f"The pressure plate is {colors['plate']} - look for the {colors['plate']} tiles."
        if controlled_agent == "AgentA"
        else f"The elevator door is {colors['door']} - look for the {colors['door']} region."
    )
    return (
        f"Scene colors (use these to find your target in the image): "
        f"floor is {colors['floor']}, walls are {colors['wall']}, ceiling is {colors['ceiling']}; "
        f"the elevator door is {colors['door']}; the pressure plate is {colors['plate']}. "
        f"{target}\n"
    )


def door_prompt_colors(scene_id: str | None) -> dict[str, str]:
    colors = SCENE_COLORS.get(str(scene_id)) or {}
    return {
        "floor_color": colors.get("floor", "light-colored"),
        "door_color": colors.get("door", "black"),
    }


def build_prompt(
    task: dict[str, Any],
    task_mode: str = "multiagent",
    controlled_agent: str | None = None,
    atomic_role: str | None = None,
) -> list[dict[str, str]]:
    task_mode = normalize_task_mode(task_mode)
    if task_mode == "single_agent":
        controlled_agent = normalize_agent(controlled_agent or "AgentA")
        schema_role, schema_goal = schema_role_goal(task, controlled_agent)
        atomic_role = atomic_role or default_task_atomic_role(task, controlled_agent)
        if is_legacy_elevator_role(task, controlled_agent, atomic_role):
            content = SINGLE_AGENT_DOOR_USER_TEMPLATE.format(
                allowed_actions=", ".join(ALLOWED_ACTIONS),
                **door_prompt_colors(task.get("scene_id")),
            )
        else:
            content = SINGLE_AGENT_USER_TEMPLATE.format(
                task_description=task.get("task_description") or task.get("description") or "",
                scene_id=task.get("scene_id", ""),
                task_id=task.get("id", ""),
                allowed_actions=", ".join(ALLOWED_ACTIONS),
                controlled_agent=controlled_agent,
                atomic_role=atomic_role,
                role=schema_role,
                atomic_goal=ATOMIC_GOAL_BY_ROLE.get(atomic_role, schema_goal),
                reward_rule=ATOMIC_REWARD_RULE_BY_ROLE.get(atomic_role, "Reward is based on reaching your schema-defined goal without triggering a failure condition."),
                failure_guidance=failure_guidance(task),
                scene_colors=scene_color_line(task.get("scene_id"), controlled_agent) if atomic_role in ATOMIC_GOAL_BY_ROLE else "",
            )
        return [
            {"role": "system", "content": SINGLE_AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ]

    agent_a_role, agent_a_goal = schema_role_goal(task, "AgentA")
    agent_b_role, agent_b_goal = schema_role_goal(task, "AgentB")
    content = MULTIAGENT_USER_TEMPLATE.format(
        task_description=task.get("task_description") or task.get("description") or "",
        scene_id=task.get("scene_id", ""),
        task_id=task.get("id", ""),
        allowed_actions=", ".join(ALLOWED_ACTIONS),
        agent_a_role_goal=f"Role: {agent_a_role}. Goal: {agent_a_goal}",
        agent_b_role_goal=f"Role: {agent_b_role}. Goal: {agent_b_goal}",
        failure_guidance=failure_guidance(task),
    )
    return [
        {"role": "system", "content": MULTIAGENT_SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


def make_row(
    task: dict[str, Any],
    task_index: int,
    split: str,
    row_index: int,
    agent_name: str,
    seed: int,
    train_instance_count: int,
    task_mode: str = "multiagent",
    controlled_agent: str | None = None,
    atomic_role: str | None = None,
) -> dict[str, Any]:
    task_mode = normalize_task_mode(task_mode)
    controlled_agent = normalize_agent(controlled_agent or "AgentA") if task_mode == "single_agent" else None
    atomic_role = atomic_role or (default_task_atomic_role(task, controlled_agent) if controlled_agent else None)
    extra_info = {
        "split": split,
        "index": row_index,
        "task_index": task_index,
        "task_id": task.get("id"),
        "scene_id": task.get("scene_id"),
        "random_seed": seed + row_index,
        "instance_index": row_index % max(1, train_instance_count) + 1,
        "task_mode": task_mode,
    }
    if task_mode == "single_agent":
        extra_info.update(
            {
                "controlled_agent": controlled_agent,
                "atomic_role": atomic_role,
                "scene_colors": SCENE_COLORS.get(str(task.get("scene_id")), {}),
            }
        )
    return {
        "data_source": "it_taketwo_minecraft",
        "agent_name": agent_name,
        "prompt": build_prompt(task, task_mode, controlled_agent, atomic_role),
        "ability": "minecraft_rollout",
        "reward_model": {"style": "rule", "ground_truth": "success"},
        "extra_info": extra_info,
    }


def build_rows(
    tasks: list[dict[str, Any]],
    size: int,
    split: str,
    agent_name: str,
    seed: int,
    shuffle: bool,
    train_instance_count: int,
    task_mode: str = "multiagent",
    atomic_agents: list[str] | None = None,
) -> list[dict[str, Any]]:
    if not tasks:
        raise ValueError("No Minecraft tasks were loaded")
    task_mode = normalize_task_mode(task_mode)
    indices = list(range(len(tasks)))
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(indices)
    atomic_agents = atomic_agents or ["AgentA"]
    if task_mode == "single_agent":
        row_specs = [(task_index, controlled_agent) for task_index in indices for controlled_agent in atomic_agents]
    else:
        row_specs = [(task_index, None) for task_index in indices]
    rows = []
    for row_index in range(size):
        task_index, controlled_agent = row_specs[row_index % len(row_specs)]
        atomic_role = ATOMIC_ROLE_BY_AGENT[controlled_agent] if controlled_agent else None
        rows.append(
            make_row(
                tasks[task_index],
                task_index,
                split,
                row_index,
                agent_name,
                seed,
                train_instance_count,
                task_mode=task_mode,
                controlled_agent=controlled_agent,
                atomic_role=atomic_role,
            )
        )
    return rows

def write_parquet(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, str(path))
    print(f"wrote {len(rows)} rows -> {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build verl parquet data for the It-Taketwo Minecraft AgentLoop.")
    parser.add_argument("--tasks", default=str(DEFAULT_TASKS), help="Task JSON file used by mc_rollout.")
    parser.add_argument("--output-dir", default="data/verl_minecraft", help="Directory for train.parquet and val.parquet.")
    parser.add_argument("--train-size", type=int, default=4)
    parser.add_argument("--val-size", type=int, default=1)
    parser.add_argument("--agent-name", default="minecraft_agent")
    parser.add_argument("--seed", type=int, default=20260609)
    parser.add_argument("--train-instance-count", type=int, default=4)
    parser.add_argument("--task-mode", default="multiagent", choices=["multiagent", "single_agent"])
    parser.add_argument("--atomic-agents", default="AgentA", help="Comma-separated controlled agents for single_agent mode.")
    parser.add_argument("--scene-manifest", default=None, help="Scene manifest JSON for block colors (default: sibling scene_manifest.json of --tasks).")
    parser.add_argument("--shuffle", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks_path = resolve_project_path(args.tasks)
    tasks = load_task_list(tasks_path)
    manifest_path = resolve_project_path(args.scene_manifest) if args.scene_manifest else tasks_path.parent / "scene_manifest.json"
    load_scene_colors(manifest_path)
    output_dir = resolve_project_path(args.output_dir)
    atomic_agents = parse_atomic_agents(args.atomic_agents)
    train_rows = build_rows(
        tasks,
        args.train_size,
        "train",
        args.agent_name,
        args.seed,
        args.shuffle,
        args.train_instance_count,
        task_mode=args.task_mode,
        atomic_agents=atomic_agents,
    )
    val_rows = build_rows(
        tasks,
        args.val_size,
        "val",
        args.agent_name,
        args.seed + 100000,
        args.shuffle,
        args.train_instance_count,
        task_mode=args.task_mode,
        atomic_agents=atomic_agents,
    )
    write_parquet(train_rows, output_dir / "train.parquet")
    write_parquet(val_rows, output_dir / "val.parquet")


if __name__ == "__main__":
    main()
