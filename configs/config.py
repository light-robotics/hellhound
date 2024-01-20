deviant = {    
    # parameters for moving further, when moving with feedback
    "servos": {
        "diff_from_target_limit": 1.0,
        "diff_from_prev_limit": 0.25
    },
    # issue next command a little faster, than previous is finished executing
    # when moving without feedback
    "movement_command_advance_ms" : 0.05,
    "movement_overshoot_coefficient" : 0.2,
}

moves = {
    "up_or_down_cm": 2,
    "move_body_cm": 2,
    "forward_body_1_leg_cm": 4,
    "forward_body_2_leg_cm": 3,
    "leg_up": {
        1: 3,
        2: 3,
    }
}