from __future__ import annotations

# Movement durations are controlled by TickGate/action_ticks in Python, not by
# wall-clock sleeps inside SocketPuppet. Commands with {ticks} are formatted by
# mc_rollout.game_functions.puppet_command_for_action.
ACTION_TO_PUPPET = {
    "wait": "stop",
    "forward": "w_ticks {ticks}",
    "backward": "s_ticks {ticks}",
    # "strafe_left": "a_ticks {ticks}",
    # "strafe_right": "d_ticks {ticks}",
    "jump": "jump_ticks {ticks}",
    "turn_left": "turn -20 0",
    "turn_right": "turn 20 0",
    "look_up": "turn 0 -15",
    "look_down": "turn 0 15",
}

# Jump is intentionally excluded from policy actions for the door/pressure-plate rollout.
# Keeping the low-level mapping lets manual tests still call it explicitly if needed.
ALLOWED_ACTIONS = [action for action in ACTION_TO_PUPPET if action != "jump"]
