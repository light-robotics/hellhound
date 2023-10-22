import time
import sys
import os
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hardware.htd45h import HTD45H, read_values
import logging
import configs.config as config
import configs.code_config as code_config
import logging.config
logging.config.dictConfig(code_config.logger_config)

from cybernetic_core.kinematics import HHKinematics


servos_to_angles_mapping = {
    3  : "leg1_beta",
    4  : "leg1_alpha",
    5  : "leg1_tetta",
    9  : "leg2_beta",
    10 : "leg2_alpha",
    11 : "leg2_tetta",
    15 : "leg3_beta",
    16 : "leg3_alpha",
    17 : "leg3_tetta",
    21 : "leg4_beta",
    22 : "leg4_alpha",
    23 : "leg4_tetta",
}

def convert_kinematic_angles_to_ids(angles: Dict[str, Dict[str, float]]) -> Dict[id, float]:
    angles_to_ids_values = {}

    for servo_id, angle_name in servos_to_angles_mapping.items():
        angles_to_ids_values[servo_id] = angles.get(angle_name, 0)

    return angles_to_ids_values

def target_overshoot(current: float, target: float) -> float:
    overshoot_value = 0
    if abs(target - current) > 2:
        overshoot_value = 3
    elif abs(target - current) > 1:
        overshoot_value = 2
    
    overshoot_value = math.copysign(overshoot_value, target - current)

    return target + overshoot_value

class HellHoundServos:
    def __init__(self):
        self.m1 = HTD45H(Port='/dev/ttyAMA0') # 5-8   # 1-4
        self.m2 = HTD45H(Port='/dev/ttyAMA2') # 9-12  # 5-8
        self.m3 = HTD45H(Port='/dev/ttyAMA3') # 13-16 # 9-12
        self.m4 = HTD45H(Port='/dev/ttyAMA1') # 1-4   # 13-16
        self.speed = 500
        self.min_speed = 700
        self.max_speed = 0 # 130 # 0 is instant, 10000 is very slow

        self.diff_from_target_limit = config.deviant["servos"]["diff_from_target_limit"] # when it's time to start next movement
        self.diff_from_prev_limit = config.deviant["servos"]["diff_from_prev_limit"] # 1.0 # start next movement if we're stuck

        self.logger = logging.getLogger('main_logger')
        
        # 0.16 sec / 60 degrees for 7.4V+
        # 0.18 sec / 60 degrees for 6V+
        # my max speed is for 45 degrees
        # that means that max speed should be 120 for 7.4V+ and 135 for 6V+
        self.servo_ids = [3, 4, 5, 9, 10, 11, 15, 16, 17, 21, 22, 23]

    def get_board_by_id(self, id: int) -> HTD45H:
        if id in [9, 10, 11]:
            return self.m1
        if id in [15, 16, 17]:
            return self.m2
        if id in [21, 22, 23]:
            return self.m3
        if id in [3, 4, 5]:
            return self.m4

    def get_current_angles(self) -> Dict[int, float]:
        current_angles = {}
        for id in self.servo_ids:
            angle_name = servos_to_angles_mapping[id]
            current_angles[angle_name] = self.get_board_by_id(id).read_angle(id)
        return current_angles

    def send_command_to_servos(self, angles, rate=1000):
        #adapted_angles = self.adapt_delta_angle(angles)
        angles_converted = convert_kinematic_angles_to_ids(angles)
        #self.logger.info(f'DS. send_command_to_servos. {angles_converted, rate}')
        for id in self.servo_ids:
            self.get_board_by_id(id).move_servo_to_angle(id, angles_converted[id], rate)

    def print_status(self):
        j = 1
        for m in [self.m1, self.m2, self.m3, self.m4]:
            for _ in range(6):
                m.read_values(j)
                j += 1
    
    def set_speed(self, new_speed):
        if new_speed > 10000 or new_speed < self.max_speed:
            raise Exception(f'Invalid speed value {new_speed}. Should be between {self.max_speed} and 10000')
        self.speed = new_speed
        #self.logger.info(f'HellHoundServos. Speed set to {self.speed}')

    def get_angles_diff(self, target_angles, test_angles=None):
        if test_angles is None:
            test_angles = self.get_current_angles()

        angles_diff = {}
        for angle, value in target_angles.items():
            angles_diff[angle] = value - test_angles[angle]

        max_angle_diff = max([abs(x) for x in angles_diff.values()])
        #self.logger.info(f'[DIFF] Max : {max_angle_diff}. Avg : {sum([abs(x) for x in angles_diff.values()])/len(angles_diff)}. Sum : {sum([abs(x) for x in angles_diff.values()])}')
        #self.logger.info(f'Angles diff: {angles_diff}')
        return angles_diff, max_angle_diff

    def set_servo_values_paced_full_adjustment(self, angles):
        _, max_angle_diff = self.get_angles_diff(angles)
        rate = round(max(self.speed * max_angle_diff / 45, self.max_speed)) # speed is normalized
        #self.logger.info(f'max_angle_diff: {max_angle_diff}, self.speed : {self.speed}, self.speed * max_angle_diff / 45 : {self.speed * max_angle_diff / 45}')
        prev_angles = self.get_current_angles()

        self.send_command_to_servos(angles, rate)
        #self.logger.info(f'Command sent. Rate: {rate}, angles: {angles}')
        time.sleep(0.8 * rate / 1000)
        #time.sleep(0.05)
        adjustment_done = False
        adjusted_angles = None
        
        for s in range(50):
            self.logger.info(f'Step {s}')
            
            current_angles = self.get_current_angles()
            self.logger.info(f'current angles: {current_angles}')
            # if diff from prev angles or target angles is small - continue
            self.logger.info('Target, then prev')
            diff_from_target = self.get_angles_diff(angles, current_angles)
            diff_from_prev = self.get_angles_diff(current_angles, prev_angles)

            self.logger.info(f'Diff from prev  : {diff_from_prev[0]}')
            self.logger.info(f'Diff from target: {diff_from_target[0]}')
     
            if diff_from_target[1] < self.diff_from_target_limit:                
                self.logger.info(f'Ready to move further')
                break
            
            elif diff_from_prev[1] < self.diff_from_prev_limit and \
                    not adjustment_done:

                if diff_from_target[1] > 2 * self.diff_from_target_limit:
                    print('-----------ALARM-----------')
                    self.logger.info('-----------ALARM-----------')
                
                self.logger.info(f'Command sent : {angles}')
                if diff_from_target[1] > self.diff_from_target_limit * 3:
                    self.logger.info(f'We"re in trouble, too large diff : {diff_from_target[1]}')
                    break
                else:
                    adjusted_angles = {}
                    for angle, target in angles.items():
                        adjusted_angles[angle] = round(target + (1.5 * diff_from_target[0][angle]), 1)
                    self.logger.info(f'Adjusting to : {adjusted_angles}')
                    adjustment_done = True
                    self.send_command_to_servos(adjusted_angles, round(rate/4))
                    time.sleep(0.03)
                    break

            elif diff_from_prev[1] < self.diff_from_prev_limit and \
                    adjustment_done:
                self.logger.info(f'Unreachable. Moving further')
                break

            prev_angles = dict(current_angles)

        #self.logger.info('Function set_servo_values_paced_full_adjustment')

        self.log_movement_result(angles, adjusted_angles)

        #diff_from_target = self.get_angles_diff(angles, current_angles)
        #self.logger.info(f'Final Diff from target: max: {diff_from_target[1]}, {diff_from_target[0]}')

    def set_servo_values_paced_single_adjustment(self, angles):
        _, max_angle_diff = self.get_angles_diff(angles)
        rate = round(max(self.speed * max_angle_diff / 45, self.max_speed)) # speed is normalized
        #self.logger.info(f'max_angle_diff: {max_angle_diff}, self.speed : {self.speed}, self.speed * max_angle_diff / 45 : {self.speed * max_angle_diff / 45}')

        self.send_command_to_servos(angles, rate)
        #self.logger.info(f'Command sent. Rate: {rate}, angles: {angles}')
        time.sleep(0.95 * rate / 1000)

        current_angles = self.get_current_angles()
        #self.logger.info(f'current angles: {current_angles}')

        diff_from_target = self.get_angles_diff(angles, current_angles)
        #self.logger.info(f'Diff from target: {diff_from_target[0]}')

        adjusted_angles = {}
        for angle, target in angles.items():
            adjusted_angles[angle] = round(target + (1.5 * diff_from_target[0][angle]), 1)

        #self.logger.info(f'Adjusting to : {adjusted_angles}')
        self.send_command_to_servos(adjusted_angles, round(rate/2))
        time.sleep(0.2 * rate / 1000)
    
        #current_angles = self.get_current_angles()
        #self.logger.info(f'current angles: {current_angles}')

    def set_servo_values_paced_wo_feedback(self, angles):
        _, max_angle_diff = self.get_angles_diff(angles)
        rate = round(max(self.speed * max_angle_diff / 45, self.max_speed)) # speed is normalized
        #self.logger.info(f'max_angle_diff: {max_angle_diff}, self.speed : {self.speed}, self.speed * max_angle_diff / 45 : {self.speed * max_angle_diff / 45}')
        
        self.send_command_to_servos(angles, rate)
        #self.logger.info(f'Command sent. Rate: {rate}, angles: {angles}')
        time.sleep(rate*1.5 / 1000)

        #self.logger.info('Function set_servo_values_paced_wo_feedback')
        self.log_movement_result(angles)
    
    def paced_wof_overshoot(self, angles):
        current_angles = self.get_current_angles()
        # calculate new target
        new_target = {}
        for angle, value in angles.items():
            new_target[angle] = target_overshoot(current_angles[angle], value)
        
        diff_from_target = self.get_angles_diff(new_target, current_angles)
        #self.logger.info(f'Diff from target: {diff_from_target[0]}')
        rate = round(max(self.speed * diff_from_target[1] / 45, self.max_speed)) # speed is normalized
        #self.logger.info(f'max_angle_diff: {diff_from_target[1]}, self.speed : {self.speed}, rate : {rate}')

        self.send_command_to_servos(new_target, rate)
        #self.logger.info(f'Command sent. Rate: {rate}, angles: {new_target}')
        time.sleep(rate / 1000)

        self.log_movement_result(angles, new_target)
    
    def log_movement_result(self, target, adjusted=None):
        current_angles = self.get_current_angles()
        all_diffs = []
        for k, v in target.items():
            diff = v - current_angles[k]
            all_diffs.append(abs(diff))
            if adjusted:
                self.logger.info(f'Angle {k:>10}. Diff: {diff:5.2f}. Current: {current_angles[k]}. Target: {v}. Adjusted: {adjusted[k]}')
            else:
                self.logger.info(f'Angle {k:>10}. Diff: {diff:5.2f}. Current: {current_angles[k]}. Target: {v}.')
        self.logger.info(f'Diff. Sum: {sum(all_diffs):3.2f}. Max: {max(all_diffs):3.2f}')

if __name__ == '__main__':
    hh = HellHoundServos()
    hh.set_speed(500)
        
    angles = {
        'leg1_tetta': 0.0, 
        'leg1_alpha': 60.0, 
        'leg1_beta': 90.0,
        'leg2_tetta': 0.0, 
        'leg2_alpha': 60.0, 
        'leg2_beta': 90.0,
        'leg3_tetta': 0.0, 
        'leg3_alpha': 60.0, 
        'leg3_beta': 90.0, 
        'leg4_tetta': 0.0, 
        'leg4_alpha': 60.0, 
        'leg4_beta': 90.0,
    }

    hh_kin = HHKinematics()
    hh_kin.move_forward(2, 6)
    print(hh_kin.sequence)

    for item in hh_kin.sequence:
        hh.set_servo_values_paced_wo_feedback(item.angles_snapshot)
    
    #sequence = [[0.0, 60.0, 100.0, -10.0, 0.0, 60.0, 100.0, -10.0, 0.0, 60.0, 100.0, -10.0, 0.0, 60.0, 100.0, -10.0]]
        
    #for angles in sequence:     
    #    dvnt.set_servo_values_paced(angles)
    