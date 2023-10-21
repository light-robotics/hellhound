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
