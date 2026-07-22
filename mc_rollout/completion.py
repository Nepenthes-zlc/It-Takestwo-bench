from __future__ import annotations

from typing import Any, Callable

from game_functions import agent_center_in_region_center_fraction, agent_on_pressure_plate, agent_over_region, agent_reached_opposite_bank, query_agent_pose

TARGET_CENTER_AREA_FRACTION = 2.0 / 3.0


def _player_b_goal_region(task: dict[str, Any]) -> list[Any] | None:
    player_b = task.get("players", {}).get("player_b", {})
    goal = player_b.get("goal", {}) if isinstance(player_b, dict) else {}
    region = goal.get("target_region") if isinstance(goal, dict) else None
    return region if isinstance(region, list) else None


def _player_a_goal_region(task: dict[str, Any]) -> list[Any] | None:
    player_a = task.get("players", {}).get("player_a", {})
    goal = player_a.get("goal", {}) if isinstance(player_a, dict) else {}
    region = goal.get("target_region") if isinstance(goal, dict) else None
    return region if isinstance(region, list) else None


def _agent_b_below_failure_threshold(task: dict[str, Any], pose: dict[str, Any] | None) -> bool:
    pos = pose.get("pos") if isinstance(pose, dict) else None
    if not isinstance(pos, list) or len(pos) < 2:
        return False
    for condition in task.get("failure_conditions", []) or []:
        if condition.get("type") != "player_below_y":
            continue
        walking_y = condition.get("walking_y", condition.get("y_below"))
        minimum_drop = max(0.0, float(condition.get("minimum_drop", condition.get("tolerance", 1.5))))
        if walking_y is not None and float(pos[1]) < float(walking_y) - minimum_drop:
            return True
    return False




def _player_bridge_region(task: dict[str, Any], player_key: str) -> list[Any] | None:
    player = task.get("players", {}).get(player_key, {})
    goal = player.get("goal", {}) if isinstance(player, dict) else {}
    region = goal.get("bridge_region") if isinstance(goal, dict) else None
    return region if isinstance(region, list) else None



def _bridge_occupancy_region(region: list[Any] | None, end_margin: float = 0.3) -> list[float] | None:
    if not isinstance(region, list) or len(region) < 6:
        return None
    x0, y0, z0, x1, y1, z1 = [float(value) for value in region[:6]]
    min_x, max_x = min(x0, x1), max(x0, x1)
    min_z, max_z = min(z0, z1), max(z0, z1)
    width = max_x - min_x + 1.0
    depth = max_z - min_z + 1.0
    if depth >= width:
        min_z += end_margin
        max_z -= end_margin
    else:
        min_x += end_margin
        max_x -= end_margin
    return [min_x, y0, min_z, max_x, y0, max_z]


def _agent_center_over_region(pose: dict[str, Any], region: list[Any] | None) -> bool:
    pos = pose.get("pos") if isinstance(pose, dict) else None
    if not isinstance(pos, list) or len(pos) < 3 or not isinstance(region, list) or len(region) < 6:
        return False
    x, y, z = float(pos[0]), float(pos[1]), float(pos[2])
    x0, y0, z0, x1, y1, z1 = [float(value) for value in region[:6]]
    if abs(y - y0) > 1.01 and abs(y - y1) > 1.01:
        return False
    return min(x0, x1) <= x <= max(x0, x1) + 1.0 and min(z0, z1) <= z <= max(z0, z1) + 1.0

def evaluate_elevator_hold_door(
    task: dict[str, Any],
    poses: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    agent_a_on_plate = bool(poses.get("AgentA")) and agent_on_pressure_plate(task, poses["AgentA"])
    goal_region = _player_b_goal_region(task)
    agent_b_in_elevator = bool(poses.get("AgentB")) and agent_over_region(poses["AgentB"], goal_region)
    return {
        "task_success": bool(agent_a_on_plate and agent_b_in_elevator),
        "task_failed": False,
        "unsupported_conditions": [],
        "agent_a_on_pressure_plate": bool(agent_a_on_plate),
        "agent_b_in_elevator": bool(agent_b_in_elevator),
    }


def evaluate_pressure_path_reveal(
    task: dict[str, Any],
    poses: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    agent_a_on_plate = bool(poses.get("AgentA")) and agent_on_pressure_plate(task, poses["AgentA"])
    agent_b_on_opposite_bank = bool(poses.get("AgentB")) and agent_reached_opposite_bank(task, poses["AgentB"])
    task_failed = _agent_b_below_failure_threshold(task, poses.get("AgentB"))
    return {
        "task_success": bool(agent_b_on_opposite_bank and not task_failed),
        "task_failed": bool(task_failed),
        "unsupported_conditions": [],
        "agent_a_on_pressure_plate": bool(agent_a_on_plate),
        "agent_b_on_opposite_bank": bool(agent_b_on_opposite_bank),
    }


def evaluate_truck_driver(
    task: dict[str, Any],
    poses: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    goal_region = _player_a_goal_region(task)
    agent_a_in_target = bool(poses.get("AgentA")) and agent_center_in_region_center_fraction(poses["AgentA"], goal_region, TARGET_CENTER_AREA_FRACTION)
    return {
        "task_success": bool(agent_a_in_target),
        "task_failed": False,
        "unsupported_conditions": [],
        "agent_a_in_target_region": bool(agent_a_in_target),
        "agent_a_in_target_center_half_area": bool(agent_a_in_target),
        "agent_a_in_target_center_two_thirds_area": bool(agent_a_in_target),
    }


def evaluate_picture_center_alignment(
    task: dict[str, Any],
    poses: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    goal_region = _player_a_goal_region(task)
    agent_a_aligned = bool(poses.get("AgentA")) and agent_center_in_region_center_fraction(poses["AgentA"], goal_region, TARGET_CENTER_AREA_FRACTION)
    return {
        "task_success": bool(agent_a_aligned),
        "task_failed": False,
        "unsupported_conditions": [],
        "agent_a_aligned_over_target_region": bool(agent_a_aligned),
        "agent_a_aligned_over_target_center_half_area": bool(agent_a_aligned),
        "agent_a_aligned_over_target_center_two_thirds_area": bool(agent_a_aligned),
    }


def evaluate_maze_command_guidance(
    task: dict[str, Any],
    poses: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    goal_region = _player_a_goal_region(task)
    agent_a_in_goal = bool(poses.get("AgentA")) and agent_center_in_region_center_fraction(poses["AgentA"], goal_region, 1.0)
    return {
        "task_success": bool(agent_a_in_goal),
        "task_failed": False,
        "unsupported_conditions": [],
        "agent_a_in_maze_goal_region": bool(agent_a_in_goal),
    }


def evaluate_bridge_crossing(
    task: dict[str, Any],
    poses: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    goal_region_a = _player_a_goal_region(task)
    goal_region_b = _player_b_goal_region(task)
    bridge_region_a = _bridge_occupancy_region(_player_bridge_region(task, "player_a"))
    bridge_region_b = _bridge_occupancy_region(_player_bridge_region(task, "player_b"))
    agent_a_on_opposite_bank = bool(poses.get("AgentA")) and agent_over_region(poses["AgentA"], goal_region_a)
    agent_b_on_opposite_bank = bool(poses.get("AgentB")) and agent_over_region(poses["AgentB"], goal_region_b)
    agent_a_on_bridge = bool(poses.get("AgentA")) and _agent_center_over_region(poses["AgentA"], bridge_region_a)
    agent_b_on_bridge = bool(poses.get("AgentB")) and _agent_center_over_region(poses["AgentB"], bridge_region_b)
    bridge_collapsed = bool(agent_a_on_bridge and agent_b_on_bridge)
    return {
        "task_success": bool(agent_a_on_opposite_bank and agent_b_on_opposite_bank and not bridge_collapsed),
        "task_failed": bool(bridge_collapsed),
        "unsupported_conditions": [],
        "agent_a_on_opposite_bank": bool(agent_a_on_opposite_bank),
        "agent_b_on_opposite_bank": bool(agent_b_on_opposite_bank),
        "agent_a_on_bridge": bool(agent_a_on_bridge),
        "agent_b_on_bridge": bool(agent_b_on_bridge),
        "bridge_collapsed": bool(bridge_collapsed),
    }


TaskEvaluator = Callable[[dict[str, Any], dict[str, dict[str, Any] | None]], dict[str, Any]]
TASK_EVALUATORS: dict[str, TaskEvaluator] = {
    "elevator_hold_door": evaluate_elevator_hold_door,
    "pressure_path_reveal": evaluate_pressure_path_reveal,
    "truck_driver": evaluate_truck_driver,
    "truck_blind_navigation": evaluate_truck_driver,
    "picture_center_alignment": evaluate_picture_center_alignment,
    "high_platform_gold_guidance": evaluate_picture_center_alignment,
    "maze_command_guidance": evaluate_maze_command_guidance,
    "bridge": evaluate_bridge_crossing,
    "bridge_crossing": evaluate_bridge_crossing,
}


def evaluate_task_conditions(
    task: dict[str, Any],
    poses: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    task_template = str(task.get("task_template") or "").strip().lower()
    try:
        evaluator = TASK_EVALUATORS[task_template]
    except KeyError as exc:
        raise ValueError(f"unsupported task_template for completion: {task_template!r}") from exc
    return evaluator(task, poses)


def query_success_markers(
    runner: Any,
    commands: list[str],
    task: dict[str, Any],
    stamp: str,
    active_agents: tuple[str, ...] | list[str] | None = None,
) -> tuple[dict[str, Any], str]:
    del commands, stamp
    active = set(active_agents or ("AgentA", "AgentB"))
    poses = {
        agent: query_agent_pose(runner, agent) if agent in active else None
        for agent in ("AgentA", "AgentB")
    }
    condition_markers = evaluate_task_conditions(task, poses)
    task_template = str(task.get("task_template") or "").strip().lower()

    if task_template == "elevator_hold_door":
        agent_a_goal = condition_markers["agent_a_on_pressure_plate"]
        agent_b_goal = condition_markers["agent_b_in_elevator"]
        task_markers = {
            "pressure_plate_powered": agent_a_goal,
            "agent_b_at_door_front": agent_b_goal,
            "agent_b_fully_in_second_room": agent_b_goal,
            "door_block_air": agent_a_goal,
        }
    elif task_template == "pressure_path_reveal":
        agent_a_goal = condition_markers["agent_a_on_pressure_plate"]
        agent_b_goal = condition_markers["agent_b_on_opposite_bank"]
        task_markers = {
            "pressure_plate_powered": agent_a_goal,
            "agent_b_on_opposite_bank": agent_b_goal,
        }
    elif task_template in {"truck_driver", "truck_blind_navigation"}:
        agent_a_goal = condition_markers["agent_a_in_target_region"]
        agent_b_goal = agent_a_goal
        task_markers = {
            "agent_a_in_target_region": agent_a_goal,
        }
    elif task_template in {"picture_center_alignment", "high_platform_gold_guidance"}:
        agent_a_goal = condition_markers["agent_a_aligned_over_target_region"]
        agent_b_goal = agent_a_goal
        task_markers = {
            "agent_a_aligned_over_target_region": agent_a_goal,
        }
    elif task_template == "maze_command_guidance":
        agent_a_goal = condition_markers["agent_a_in_maze_goal_region"]
        agent_b_goal = agent_a_goal
        task_markers = {
            "agent_a_in_maze_goal_region": agent_a_goal,
        }
    elif task_template in {"bridge", "bridge_crossing"}:
        agent_a_goal = condition_markers["agent_a_on_opposite_bank"]
        agent_b_goal = condition_markers["agent_b_on_opposite_bank"]
        task_markers = {
            "agent_a_on_opposite_bank": agent_a_goal,
            "agent_b_on_opposite_bank": agent_b_goal,
        }
    else:
        raise ValueError(f"unsupported task_template for markers: {task_template!r}")

    markers: dict[str, Any] = {
        "agent_a_goal_reached": bool(agent_a_goal),
        "agent_b_goal_reached": bool(agent_b_goal),
        **condition_markers,
        **task_markers,
    }
    return markers, ""
