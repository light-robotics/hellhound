class leg:
    a = 15
    b = 17.6
    d = 5
    d2 = 3.5

class start:
    vertical = 20 # new. walking: 21; old. walking: 17 # one-leg moves: 25
    x_start = -3 # walking21: -5 old. -6 forward: < 0
    front_x_delta = 5 # walking21: 4 actual: 8
    incline = 0 # two-legged 0, one-legged 2. > 0 legs outside

class moves:
    up_down_cm = 1
    move_body_cm = 1
    fwd_body_1_leg_cm = 4
    fwd_body_2_leg_cm = 6
    side_move_2_leg_cm = 4
    leg_up = {
        1: 5,
        2: 5,
    }
    margin = 6

class speed:
    forward_two_legged = 150
    forward_one_legged = 1000