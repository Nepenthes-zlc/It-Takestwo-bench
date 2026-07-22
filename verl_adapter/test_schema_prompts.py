from __future__ import annotations

import copy
import json
from pathlib import Path

from verl_adapter.build_dataset import build_prompt, make_row
from verl_adapter.mc_env import format_agent_observation

ROOT = Path(__file__).resolve().parents[1]


def load_task(index: int) -> dict:
    data = json.loads((ROOT / "assert/ConstructScene/generated/generated_tasks.json").read_text())
    return copy.deepcopy(data["tasks"][index])


def online_observation(task: dict) -> dict:
    return {
        "task_mode": "multiagent",
        "description": task["task_description"],
        "task_schema": {
            "task_template": task["task_template"],
            "players": task["players"],
            "failure_conditions": task.get("failure_conditions", []),
        },
        "active_agents": ["AgentA", "AgentB"],
        "markers": {},
    }


def test_multiagent_dataset_prompt_uses_schema_for_future_task():
    task = load_task(50)
    task["task_template"] = "future_unknown_coop_type"
    task["players"]["player_b"]["role"] = "artifact_carrier"
    task["players"]["player_b"]["goal"]["description"] = "Carry the artifact into the marked goal region."
    content = build_prompt(task)[1]["content"]
    assert "path holder" in content
    assert "artifact carrier" in content
    assert "Carry the artifact into the marked goal region." in content
    assert "Player B has fallen below the normal walking level." in content
    assert "elevator" not in content.lower()


def test_single_agent_dataset_prompt_uses_selected_player_schema():
    task = load_task(50)
    content = build_prompt(task, "single_agent", "AgentB")[1]["content"]
    assert "path crosser" in content
    assert "Cross the revealed path and reach the gold marker" in content
    assert "Player B has fallen below the normal walking level." in content
    assert "door_position" not in content
    assert "elevator" not in content.lower()


def test_dataset_row_defaults_to_schema_role():
    task = load_task(50)
    row = make_row(task, 50, "train", 0, "AgentB", 0, 32, "single_agent", "AgentB")
    assert row["extra_info"]["atomic_role"] == "path_crosser"


def test_online_observation_uses_generic_protocol_for_future_task():
    task = load_task(50)
    task["task_template"] = "future_unknown_coop_type"
    text = format_agent_observation(online_observation(task), "AgentB")
    assert "path crosser" in text
    assert "Cross the revealed path and reach the gold marker" in text
    assert "fallen below the normal walking level" in text
    assert "door_position" not in text
    assert "elevator" not in text.lower()


def test_existing_elevator_agent_b_keeps_door_protocol():
    task = load_task(0)
    text = format_agent_observation(online_observation(task), "AgentB")
    assert "elevator entry" in text
    assert "door_position" in text
    assert "door_state" in text


def test_existing_elevator_rows_keep_legacy_atomic_roles():
    task = load_task(0)
    row_a = make_row(task, 0, "train", 0, "AgentA", 0, 32, "single_agent", "AgentA")
    row_b = make_row(task, 0, "train", 1, "AgentB", 0, 32, "single_agent", "AgentB")
    assert row_a["extra_info"]["atomic_role"] == "pressure_plate_hold"
    assert row_b["extra_info"]["atomic_role"] == "elevator_door_approach"


def test_mock_env_uses_schema_role_and_generic_reward_aliases():
    from verl_adapter.mc_env import MinecraftEnvConfig, MinecraftRolloutEnv

    env = MinecraftRolloutEnv(
        MinecraftEnvConfig(
            rollout_yaml=Path("yaml/lowlevel_train_episode.yaml"),
            task_index=50,
            mock=True,
            task_mode="single_agent",
            controlled_agent="AgentB",
            save_trace=False,
            use_images=False,
        )
    )
    observation = env.observe()
    assert env.atomic_role == "path_crosser"
    breakdown = observation["reward_breakdown"]
    assert "agent_a_to_goal" in breakdown["progress"]
    assert "agent_b_to_goal" in breakdown["progress"]
    assert "agent_a_to_goal" in breakdown["distances"]
    assert "agent_b_to_goal" in breakdown["distances"]
