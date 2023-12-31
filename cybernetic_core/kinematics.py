import logging.config
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import configs.code_config as code_config
import configs.kinematics_config as cfg
from cybernetic_core.geometry.inverse_kinematics import calculate_leg_angles
from cybernetic_core.geometry.lines import Point
from cybernetic_core.cybernetic_utils.moves import Move, MoveSnapshot


class Leg:
    def __init__(self, O: Point, C: Point):
        logging.config.dictConfig(code_config.logger_config)
        self.logger = logging.getLogger('angles_logger') #logging.getLogger('main_logger')
        self.O = O
        self.C = C
        self.update_angles()

    def update_angles(self):
        self.tetta, self.alpha, self.beta = calculate_leg_angles(self.O, self.C)

    def move_mount_point(self, delta_x, delta_y, delta_z):
        self.O.move(delta_x, delta_y, delta_z)
        self.update_angles()
    
    def move_end_point(self, delta_x, delta_y, delta_z):
        self.C.move(delta_x, delta_y, delta_z)
        self.update_angles()

class HHKinematics:
    def __init__(self):
        logging.config.dictConfig(code_config.logger_config)
        self.logger = logging.getLogger('main_logger')
        self.legs = self.initiate_legs()
        self.angles_history = []
        self.add_angles_snapshot('init')

    def add_angles_snapshot(self, move_type: str = 'unknown'):
        angles = {
            "leg1_alpha": self.legs[1].alpha,
            "leg1_beta": self.legs[1].beta,
            "leg1_tetta": self.legs[1].tetta,
            "leg2_alpha": self.legs[2].alpha,
            "leg2_beta": self.legs[2].beta,
            "leg2_tetta": self.legs[2].tetta,
            "leg3_alpha": self.legs[3].alpha,
            "leg3_beta": self.legs[3].beta,
            "leg3_tetta": self.legs[3].tetta,
            "leg4_alpha": self.legs[4].alpha,
            "leg4_beta": self.legs[4].beta,
            "leg4_tetta": self.legs[4].tetta,
        }

        self.angles_history.append(MoveSnapshot(move_type, angles))

    def reset_history(self):
        self.angles_history = []

    @property
    def sequence(self):
        sequence = []
        for move in self.angles_history:
            sequence.append(MoveSnapshot(move.move_type, move.angles_snapshot))
        return sequence

    def initiate_legs(self):
        x_start = cfg.start.x_start
        x_delta_front = cfg.start.front_x_delta
        O1 = Point(0, 0, cfg.start.vertical)
        C1 = Point(x_start + x_delta_front, -cfg.leg.d - cfg.start.incline, 0)
        self.logger.info('[Init] Initiating leg 1')
        Leg1 = Leg(O1, C1)

        O2 = Point(0, 0, cfg.start.vertical)
        C2 = Point(x_start + x_delta_front, -cfg.leg.d + cfg.start.incline, 0)
        self.logger.info('[Init] Initiating leg 2')
        Leg2 = Leg(O2, C2)

        O3 = Point(0, 0, cfg.start.vertical)
        C3 = Point(x_start, -cfg.leg.d + cfg.start.incline, 0)
        self.logger.info('[Init] Initiating leg 3')
        Leg3 = Leg(O3, C3)

        O4 = Point(0, 0, cfg.start.vertical)
        C4 = Point(x_start, -cfg.leg.d - cfg.start.incline, 0)
        self.logger.info('[Init] Initiating leg 4')
        Leg4 = Leg(O4, C4)

        self.logger.info('[Init] Initialization successful')

        return {1: Leg1, 2: Leg2, 3: Leg3, 4: Leg4}

    def _leg_movement(self, leg_num, leg_delta):
        self.logger.info(f'Move. Leg {leg_num} for {leg_delta}')
        leg = self.legs[leg_num]

        leg.move_end_point(leg_delta[0], leg_delta[1], leg_delta[2])

    def body_movement(self, delta_x, delta_y, delta_z, snapshot=True):
        self.logger.info(f'Body movement [{delta_x}, {delta_y}, {delta_z}]')
        if delta_x == delta_y == delta_z == 0:
            return

        for leg_num, leg in self.legs.items():
            self.logger.info(f'Moving mount point for {leg_num} : {[delta_x, delta_y, delta_z]}')
            leg.move_mount_point(delta_x, delta_y, delta_z)

        if snapshot:
            self.add_angles_snapshot('body')

    def move_forward_one_legged(self, legs_up_value, legs_forward_value):
        up_move = [legs_forward_value, 0, legs_up_value]
        down_move = [0, 0, -legs_up_value]

        self._leg_movement(1, up_move)
        self.add_angles_snapshot('endpoint')
        self._leg_movement(1, down_move)
        self.add_angles_snapshot('endpoint')

        self._leg_movement(3, up_move)
        self.add_angles_snapshot('endpoint')
        self._leg_movement(3, down_move)
        self.add_angles_snapshot('endpoint')

        self.body_movement(0.5 * legs_forward_value, 0, 0)

        self._leg_movement(2, up_move)
        self.add_angles_snapshot('endpoint')
        self._leg_movement(2, down_move)
        self.add_angles_snapshot('endpoint')

        self._leg_movement(4, up_move)
        self.add_angles_snapshot('endpoint')
        self._leg_movement(4, down_move)
        self.add_angles_snapshot('endpoint')

        self.body_movement(0.5 * legs_forward_value, 0, 0)

    def move_forward_2(self, legs_up_value, legs_forward_value):
        up_move = [legs_forward_value, 0, legs_up_value]
        up_move_2 = [2*legs_forward_value, 0, legs_up_value]
        down_move = [0, 0, -legs_up_value]

        for leg_num in [1, 3]:
            self._leg_movement(leg_num, up_move)
        self.add_angles_snapshot('endpoint')
        for leg_num in [1, 3]:
            self._leg_movement(leg_num, down_move)
        self.add_angles_snapshot('endpoint')

        self.body_movement(legs_forward_value, 0, 0)

        for leg_num in [2, 4]:
            self._leg_movement(leg_num, up_move_2)
        self.add_angles_snapshot('endpoint')
        for leg_num in [2, 4]:
            self._leg_movement(leg_num, down_move)
        self.add_angles_snapshot('endpoint')

        self.body_movement(legs_forward_value, 0, 0)

        for leg_num in [1, 3]:
            self._leg_movement(leg_num, up_move_2)
        self.add_angles_snapshot('endpoint')
        for leg_num in [1, 3]:
            self._leg_movement(leg_num, down_move)
        self.add_angles_snapshot('endpoint')

        self.body_movement(legs_forward_value, 0, 0)

        for leg_num in [2, 4]:
            self._leg_movement(leg_num, up_move_2)
        self.add_angles_snapshot('endpoint')
        for leg_num in [2, 4]:
            self._leg_movement(leg_num, down_move)
        self.add_angles_snapshot('endpoint')

        self.body_movement(legs_forward_value, 0, 0)

        for leg_num in [1, 3]:
            self._leg_movement(leg_num, up_move)
        self.add_angles_snapshot('endpoint')
        for leg_num in [1, 3]:
            self._leg_movement(leg_num, down_move)
        self.add_angles_snapshot('endpoint')

    def move_forward(self, legs_up_value, legs_forward_value):
        up_move = [legs_forward_value, 0, legs_up_value]
        up_move_2 = [2*legs_forward_value, 0, legs_up_value]
        back_move = [-legs_forward_value, 0, 0]
        back_move_2 = [-2*legs_forward_value, 0, 0]
        down_move = [0, 0, -legs_up_value]
        for leg_num in [1, 3]:
            self._leg_movement(leg_num, up_move)
        self.add_angles_snapshot('endpoint')
        for leg_num in [1, 3]:
            self._leg_movement(leg_num, down_move)
        self.add_angles_snapshot('endpoint')

        #self.body_movement(-legs_forward_value/2, 0, 0)
        

        for leg_num in [2, 4]:
            self._leg_movement(leg_num, up_move_2)
        # self.add_angles_snapshot('endpoint')

        for leg_num in [1, 3]:
            self._leg_movement(leg_num, back_move_2)
        self.add_angles_snapshot('endpoint')
        
        
        for leg_num in [2, 4]:
            self._leg_movement(leg_num, down_move)
        self.add_angles_snapshot('endpoint')


        #self.body_movement(-legs_forward_value/2, 0, 0)
        #self.body_movement(-legs_forward_value/2, 0, 0)

        for leg_num in [1, 3]:
            self._leg_movement(leg_num, up_move)      
        self.add_angles_snapshot('endpoint')

        for leg_num in [1, 3]:
            self._leg_movement(leg_num, down_move)
        #self.add_angles_snapshot('endpoint')
        for leg_num in [2, 4]:
            self._leg_movement(leg_num, back_move_2)
        self.add_angles_snapshot('endpoint')

        #self.body_movement(-legs_forward_value/2, 0, 0)

    def test_leg_up(self, leg_up_value):
        for leg_num in [1, 3]:
            self._leg_movement(leg_num, [0, 0, leg_up_value])
        self.add_angles_snapshot('endpoint')
        for leg_num in [1, 3]:
            self._leg_movement(leg_num, [0, 0, -leg_up_value])
        self.add_angles_snapshot('endpoint')
        
        for leg_num in [2, 4]:
            self._leg_movement(leg_num, [0, 0, leg_up_value])
        self.add_angles_snapshot('endpoint')
        for leg_num in [2, 4]:
            self._leg_movement(leg_num, [0, 0, -leg_up_value])
        self.add_angles_snapshot('endpoint')

    def test_leg_up_1(self, leg_up_value, move_body_side, move_body_forward):
        self.body_movement(-move_body_forward, move_body_side, 0)
        leg_num = 1
        self._leg_movement(leg_num, [0, 0, leg_up_value])
        self.add_angles_snapshot('endpoint')
        #return
        self._leg_movement(leg_num, [0, 0, -leg_up_value])
        self.add_angles_snapshot('endpoint')
        self.body_movement(move_body_forward, -move_body_side, 0)
    
    def jump(self, jump_value):
        self.body_movement(0, 0, jump_value)
        self.body_movement(0, 0, -jump_value)
    
    def forward_jump(self, forward_value=5, backward_lean_value=7, up_value=12, down_value=6, down2_value=3):
        self.body_movement(-backward_lean_value, 0, 0)

        self._leg_movement(1, [0, 0, -down_value])
        self._leg_movement(2, [0, 0, -down_value])
        self.add_angles_snapshot('endpoint')

        self._leg_movement(1, [forward_value, 0, up_value])
        self._leg_movement(2, [forward_value, 0, up_value])
        self.add_angles_snapshot('endpoint')

        self._leg_movement(1, [0, 0, -down2_value])
        self._leg_movement(2, [0, 0, -down2_value])
        self.add_angles_snapshot('endpoint')

        self.body_movement(backward_lean_value, 0, 0)

    def test_leg_fwd_1(self, leg_up_value, move_body_side, move_body_forward, leg_fwd_value):
        self.body_movement(-move_body_forward, move_body_side, 0)
        leg_num = 1
        self._leg_movement(leg_num, [0, 0, leg_up_value])
        self.add_angles_snapshot('endpoint')
        self._leg_movement(leg_num, [leg_fwd_value, 0, 0])
        self.add_angles_snapshot('endpoint')
        self._leg_movement(leg_num, [-leg_fwd_value, 0, 0])
        self.add_angles_snapshot('endpoint')
        #return
        self._leg_movement(leg_num, [0, 0, -leg_up_value])
        self.add_angles_snapshot('endpoint')
        self.body_movement(move_body_forward, -move_body_side, 0)



if __name__ == '__main__':
    hh_kin = HHKinematics()
    hh_kin.body_movement(0, 0, 5)
    print(hh_kin.sequence)
