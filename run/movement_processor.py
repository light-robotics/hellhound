import time
import datetime
import copy
from typing import Callable, Optional, Union
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cybernetic_core.kinematics import DeviantKinematics
from cybernetic_core.virtual_deviant import VirtualDeviant
import configs.code_config as code_config
import configs.config as config
import logging.config

if not code_config.DEBUG:
    from deviant_hardware.deviant_servos import DeviantServos


class MovementProcessor:
    def __init__(self):
        logging.config.dictConfig(code_config.logger_config)
        self.logger = logging.getLogger('main_logger')
        self.logger.info('==================START==================')

        self.max_processed_command_id = 0
        self.max_processed_side_command_id = 0
        self.state = '0'

        self.vd = VirtualDeviant()

        if not code_config.DEBUG:
            self.ds = DeviantServos()
        
        self.speed = 500
        self.body_speed = 1000        

        # state is used for multi-phased moves
        # state 0 means start position
        # state f1 means legs 1 and 3 had been moved forward
        # state f2 means legs 2 and 4 had been moved forward

    def read_servos_command(self) -> Optional[Union[str, int]]:        
        with open(code_config.movement_command_file, 'r') as f:
            contents = f.readline().split(',')

        if len(contents) != 3:
            return None

        command_id = int(contents[0])
        command = contents[1].strip()

        # this commands are not excluded even if id is the same
        repeating_commands = [
            'forward_two_legged',
            'backward_two_legged',
            'strafe_left_two_legged',
            'strafe_right_two_legged', 
            #'up', 
            #'down',
            'body_forward',
            'body_backward',
            'body_left',
            'body_right',            
            'turn_right',
            'turn_left',
            'none'
            ]        

        if self.max_processed_command_id == 0:
            self.max_processed_command_id = command_id
        elif self.max_processed_command_id == command_id and \
            command not in repeating_commands:
            # command has already been processed
            #print(f'Command {contents} has already been processed')
            return 'none', 1000

        self.max_processed_command_id = command_id
        return command, int(contents[2])

    def read_servos_side_command(self) -> Optional[Union[str, int]]:        
        with open(code_config.side_movement_command_file, 'r') as f:
            contents = f.readline().split(',')

        if len(contents) != 3:
            return None

        command_id = int(contents[0])
        command = contents[1].strip()

        # this commands are not excluded even if id is the same
        repeating_commands = [
            'forward_two_legged',
            'backward_two_legged',
            'strafe_left_two_legged',
            'strafe_right_two_legged', 
            #'up', 
            #'down',
            'body_forward',
            'body_backward',
            'body_left',
            'body_right',            
            'turn_right',
            'turn_left'
            ]        

        if self.max_processed_side_command_id == 0:
            self.max_processed_side_command_id = command_id
        elif self.max_processed_side_command_id == command_id and \
            command not in repeating_commands:
            # command has already been processed
            #print(f'Command {contents} has already been processed')
            return None

        self.max_processed_side_command_id = command_id
        return command, int(contents[2])

    def read_wheels_command(self):
        with open(code_config.wheels_command_file, 'r') as f:
            contents = f.readline().split(',')
        
        if len(contents) != 2:
            return None
        
        return contents[0].strip(), int(contents[1])
    
    def read_wheels_side_command(self):
        with open(code_config.side_wheels_command_file, 'r') as f:
            contents = f.readline().split(',')
        
        if len(contents) != 2:
            return None
        
        return contents[0].strip(), int(contents[1])

    def execute_command(self, command: str, speed: int) -> None:
        if self.speed != speed:
            if not code_config.DEBUG:
                self.ds.set_speed(speed)
            self.speed = speed
            print(f'Setting speed to {speed}')

        # first we finish movements that are in progress
        if self.state == 'f1':
            if command == 'forward_two_legged':
                print(f'Forward 2. Legs 2 and 4 moved x2. {speed}')
                self.state = 'f2'
                self.run_sequence('forward_2')
            else:
                print(f'Forward 22. Legs 2 and 4 moved x1. {speed}')
                self.state = '0'
                self.run_sequence('forward_22')
        elif self.state == 'f2':
            if command == 'forward_two_legged':
                print(f'Forward 3. Legs 1 and 3 moved x2. {speed}')
                self.state = 'f1'
                self.run_sequence('forward_3')
            else:
                print(f'Forward 32. Legs 1 and 3 moved x1. {speed}')
                self.state = '0'
                self.run_sequence('forward_32')
        
        # then we make the next move
        if self.state == '0':
            if command == 'forward_two_legged':
                print(f'Forward 1. Legs 1 and 3 moved x1. {speed}')
                self.state = 'f1'
                self.run_sequence('forward_1')
            else:
                print(f'Executing command {command}')
                self.logger.info(f'Executing command {command}')
                if command == 'none':
                    time.sleep(0.3)
                    if False: # temporarily disabled
                        speed = 200
                        if self.speed != speed:
                            if not code_config.DEBUG:
                                self.ds.set_speed(speed)
                            self.speed = speed
                        self.run_sequence('keep_position')
                else:    
                    self.run_sequence(command)

    def execute_wheels_command(self, command: str, speed: int):
        self.ds.process_motors_command(command, speed)

    def move_function_dispatch(self, command: str) -> Callable:
        if command in ['forward_one_legged']:
            self.logger.info('Using function set_servo_values_paced_full_adjustment')
            return self.ds.set_servo_values_paced_full_adjustment
        elif command in [
            'forward_1', 
            'forward_2', 
            'forward_3', 
            'forward_22', 
            'forward_32', 
            'reposition_narrower_8',
            'legs_up_down']:
            self.logger.info('Using function set_servo_values_paced_wo_feedback')
            return self.ds.set_servo_values_paced_wo_feedback
        else:
            self.logger.info('Using function set_servo_values_paced_full_adjustment')
            return self.ds.set_servo_values_paced_full_adjustment
                        
    def run_sequence(self, command: str) -> None:                   
        self.logger.info(f'MOVE. Trying command {command}')
        before_sequence_time = datetime.datetime.now()
        self.vd.save_state()
        try:
            self.vd.reset_history()
            sequence = self.vd.get_sequence(command)            

            if sequence is None:
                self.logger.info(f'MOVE. Command aborted')
                self.vd.load_state()
                return
            self.logger.info(f'[TIMING] Sequence calculation took : {datetime.datetime.now() - before_sequence_time}')
            self.logger.info('Sequence:'+'\n'.join([str(x) for x in sequence]))
        except Exception as e:
            print(f'MOVE Failed. Could not process command - {str(e)}')
            self.logger.info(f'MOVE Failed. Could not process command - {str(e)}')
            self.vd.load_state()
            time.sleep(0.3)
            return
        #self.logger.info(f'MOVE Started')    
        start_time = datetime.datetime.now()

        if not code_config.DEBUG:
            move_function = self.move_function_dispatch(command)

        for move_snapshot in sequence:
            angles = move_snapshot.angles_snapshot
            #self.logger.info(f'Moving to {angles}. Move type: {move_snapshot.move_type}')
            if not code_config.DEBUG:
                move_function(angles)
            else:
                time.sleep(1.0)
            # time.sleep(5.0)
        self.logger.info(f'[TIMING] Step took : {datetime.datetime.now() - start_time}')

    def move(self):
        prev_wheels_command = ''
        prev_wheels_side_command = ''
        try:
            while True:
                servos_command_read = self.read_servos_command()
                servos_side_command_read = self.read_servos_side_command()
                wheels_command_read = self.read_wheels_command()
                wheels_side_command_read = self.read_wheels_side_command()
                
                if servos_command_read is None and \
                    wheels_command_read is None and \
                      servos_side_command_read is None and \
                        wheels_side_command_read is None:
                    time.sleep(0.1)
                    continue

                if wheels_command_read is not None:
                    wheels_command, wheels_speed = wheels_command_read
                    if not code_config.DEBUG:
                        new_wheels_command = f'{wheels_command}-{wheels_speed}'
                        if prev_wheels_command != new_wheels_command:
                            self.logger.info(f'Command. Wheels. {wheels_command, wheels_speed}')
                            self.execute_wheels_command(wheels_command, wheels_speed)
                            prev_wheels_command = new_wheels_command

                if wheels_side_command_read is not None:
                    # TODO
                    wheels_side_command, wheels_side_speed = wheels_side_command_read
                    if not code_config.DEBUG:
                        new_wheels_side_command = f'{wheels_side_command}-{wheels_side_speed}'
                        if prev_wheels_side_command != new_wheels_side_command:
                            self.logger.info(f'Side Command. Wheels. {wheels_side_command, wheels_side_speed}')
                            # self.execute_wheels_command(wheels_side_command, wheels_side_speed)
                            prev_wheels_side_command = new_wheels_side_command


                if servos_side_command_read is not None:
                    servos_side_command, servos_side_speed = servos_side_command_read
                    self.logger.info(f'Side Command. Servos. {servos_side_command, servos_side_speed}')
                    # TODO

                if servos_command_read is not None:
                    servos_command, servos_speed = servos_command_read
                    self.logger.info(f'Command. Servos. {servos_command, servos_speed}')
                    if servos_command == 'exit':
                        self.execute_wheels_command('forward', 0)
                        break
                    
                    self.execute_command(servos_command, servos_speed)

        except KeyboardInterrupt:
            print('Movement stopped')

if __name__ == '__main__':
    MP = MovementProcessor()
    MP.move()
