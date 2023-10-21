import time
from enum import Enum
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hardware.dualshock import DualShock
from deviant_hardware.neopixel_commands_setter import NeopixelCommandsSetter
from run.commands_writer import CommandsWriter
import configs.config as cfg


class DeviantModes(Enum):
    CLIMBING  = 1
    RUN       = 2
    OBSTACLES = 3
    BATTLE    = 4
    TURN      = 5
    MOVE_BODY = 6

class DeviantDualShock(DualShock):
    """
    To execute neopixel commands run deviant/run/neopixel_commands_reader.py before running this
    To execute servo commands run deviant/run/movement_processor.py AFTER running this
    """
    def __init__(self):
        self.neopixel = NeopixelCommandsSetter()
        self.connect()
        self.light_on = False
        self.wheels_locked = False
        self.climing_mode = 0
        self.mode = DeviantModes.RUN
        self.command_writer = CommandsWriter()

    def connect(self):
        self.neopixel.issue_command('rainbow_blue')
        super().__init__()
        self.neopixel.issue_command('blink_blue')
        time.sleep(3)
        self.neopixel.issue_command('shutdown')

    def start(self):
        super().listen()

    def on_playstation_button_press(self):
        if self.wheels_locked:
            self.wheels_locked = False
            self.command_writer.write_wheels_command('unlock_wheels', 0)
        else:
            self.wheels_locked = True
            self.command_writer.write_wheels_command('lock_wheels', 0)
    
    def on_options_press(self):
        self.command_writer.write_command('exit', 0)
        time.sleep(0.5)
        self.command_writer.write_command('none', 1000)
    
    def on_share_press(self):
        #self.command_writer.write_command('reset', 1000)
        self.command_writer.write_command('legs_up_down', 300)

    def on_R1_press(self):
        if self.light_on:
            self.light_on = False
            self.neopixel.issue_command('light_off')
            print('Turn the lights off')
        else:
            self.light_on = True
            self.neopixel.issue_command('light_on')
            print('Turn the lights on')        
    
    def on_R2_press(self, value):
        if not self.light_on:
            # -32k to 32k -> 50 -> 255
            value1 = value + 32768
            value2 = int(50 + value1/320)
            print(value2)
            self.neopixel.issue_command('light', value=value2)
            print(f'Flashlight for {value} power')
    
    def on_R2_release(self):
        self.light_on = False
        self.neopixel.issue_command('light_off')
        print('Flashlight off')

    def on_L1_press(self):
        if self.light_on:
            self.light_on = False
            self.neopixel.issue_command('light_off')
            print('Turn the lights off')
        else:
            self.light_on = True
            self.neopixel.issue_command('dipped_headlights')
            print('Turn the dim lights on')   
    
    def on_L2_press(self, value):
        self.light_on = True
        self.neopixel.issue_command('rampage')
        print('Rampage')

    @staticmethod
    def convert_value_to_speed(value):
        """
        max_speed = 100, min_speed = 2000
        abs(value) from 0 to 32768
        """
        
        value = abs(value)
        if value < 12000:
            return 1500 # > 1000 will be ignored for moving
        """
        if value < 20000:
            return 400
        if value < 25000:
            return 300
        if value < 30000:
            return 250
        """
        return 1000

    @staticmethod
    def convert_value_to_wheels_speed(value):
        """
        max_speed = 1000, min_speed = 250
        abs(value) from 0 to 32768
        """
        
        value = abs(value)
        if value < 12000:
            return 250 # > 1000 will be ignored for moving
        if value < 20000:
            return 400
        if value < 25000:
            return 600
        if value < 30000:
            return 800

        return 1000
    
    def on_L3_up(self, value):
        if self.mode in [DeviantModes.RUN, DeviantModes.CLIMBING, DeviantModes.OBSTACLES, DeviantModes.BATTLE]:
            self.command_writer.write_wheels_command('forward', self.convert_value_to_wheels_speed(value))
        elif self.mode == DeviantModes.TURN:
            self.command_writer.write_wheels_command('turn', self.convert_value_to_wheels_speed(value))
    
    def on_L3_down(self, value):
        if self.mode in [DeviantModes.RUN, DeviantModes.CLIMBING, DeviantModes.OBSTACLES, DeviantModes.BATTLE]:
            self.command_writer.write_wheels_command('backwards', self.convert_value_to_wheels_speed(value))
        elif self.mode == DeviantModes.TURN:
            self.command_writer.write_wheels_command('turn_ccw', self.convert_value_to_wheels_speed(value))

    def on_L3_left(self, value):
        self.command_writer.write_wheels_side_command('left', self.convert_value_to_wheels_speed(value))

    def on_L3_right(self, value):
        self.command_writer.write_wheels_side_command('right', self.convert_value_to_wheels_speed(value))
    
    def on_L3_press(self):
        pass
    
    def on_L3_y_at_rest(self):
        #self.command_writer.write_command('none', 250)
        #if self.mode in [DeviantModes.RUN, DeviantModes.CLIMBING, DeviantModes.BATTLE]:
        self.command_writer.write_wheels_command('forward', 0)
        #elif self.mode == DeviantModes.TURN:
        #    self.command_writer.write_wheels_command('turn', 0)

    def on_L3_x_at_rest(self):
        #self.command_writer.write_command('none', 250)
        #if self.mode in [DeviantModes.RUN, DeviantModes.CLIMBING, DeviantModes.BATTLE]:
        #self.command_writer.write_wheels_command('forward', 0)
        self.command_writer.write_wheels_side_command('forward', 0)
        #if self.mode == DeviantModes.TURN:
        #    self.command_writer.write_wheels_command('turn', 0)
    
    def on_R3_up(self, value):
        if self.mode in [DeviantModes.RUN, DeviantModes.TURN]:
            self.command_writer.write_command('forward_two_legged', 200)
        elif self.mode in [DeviantModes.CLIMBING]:
            self.command_writer.write_command('forward_one_legged', 750)
        #elif self.mode in [DeviantModes.BATTLE]:
        #    self.command_writer.write_command('spear_up', 500)

    def on_R3_down(self, value):
        pass
        #if self.mode in [DeviantModes.BATTLE]:
        #    self.command_writer.write_command('spear_down', 500)
    
    def on_R3_left(self, value):
        pass
    
    def on_R3_right(self, value):
        pass

    def on_R3_press(self):
        pass
    
    def on_R3_y_at_rest(self):
        self.command_writer.write_command('none', 250)
    
    def on_R3_x_at_rest(self):
        self.command_writer.write_command('none', 250)

    def on_right_arrow_press(self):
        if self.mode in [DeviantModes.MOVE_BODY]:
            self.command_writer.write_command('body_right', 800)
        elif self.mode in [DeviantModes.OBSTACLES]:
            self.command_writer.write_command('reposition_wider_8', 500)
        elif self.mode in [DeviantModes.CLIMBING]:
            self.command_writer.write_command('climb_2', 350)

    def on_left_arrow_press(self):
        if self.mode in [DeviantModes.MOVE_BODY]:
            self.command_writer.write_command('body_left', 800)
        elif self.mode in [DeviantModes.OBSTACLES]:
            self.command_writer.write_command('reposition_narrower_8', 500)
        elif self.mode in [DeviantModes.CLIMBING]:
            if self.climing_mode == 0:
                self.climing_mode = 1
                self.command_writer.write_command('climb_1', 700)
            elif self.climing_mode == 1:
                self.climing_mode = 2
                self.command_writer.write_command('climb_2', 700)
            elif self.climing_mode == 2:
                self.climing_mode = 3
                self.command_writer.write_command('climb_3', 700)
            elif self.climing_mode == 3:
                self.climing_mode = 0
                self.command_writer.write_command('climb_4', 700)
      
    def on_up_arrow_press(self):
        if self.mode in [DeviantModes.MOVE_BODY]:
            self.command_writer.write_command('body_forward', 800)
        else:
            self.command_writer.write_command('up', 1000)
        #elif self.mode == DeviantModes.TURN:
        #    self.command_writer.write_command('up_6', 1000)
        #elif self.mode == DeviantModes.CLIMBING:
        #    self.command_writer.write_command('climb_12_1', 1000)

    def on_down_arrow_press(self):
        if self.mode in [DeviantModes.MOVE_BODY]:
            self.command_writer.write_command('body_backward', 800)
        else:
            self.command_writer.write_command('down', 1000)
        #elif self.mode == DeviantModes.TURN:
        #    self.command_writer.write_command('down_6', 1000)

    def on_up_down_arrow_release(self):
        self.command_writer.write_command('none', 500)

    def on_left_right_arrow_release(self):
        self.command_writer.write_command('none', 500)  
        
    def on_x_press(self):
        self.mode = DeviantModes.OBSTACLES
        self.neopixel.issue_command('steady', color='green')
        self.command_writer.write_wheels_command('forward', 0)
        #self.command_writer.write_wheels_command('forward', 0)
        self.command_writer.write_command('actualize_wheels', 300)
        print('Switched mode to OBSTACLES')

    def on_triangle_press(self):
        self.mode = DeviantModes.RUN
        self.neopixel.issue_command('steady', color='cyan')
        self.command_writer.write_wheels_command('forward', 0)
        self.command_writer.write_command('actualize_wheels', 300)
        print('Switched mode to RUN')

    def on_circle_press(self):
        self.mode = DeviantModes.TURN
        self.neopixel.issue_command('steady', color='green')
        self.command_writer.write_wheels_command('turn', 0)
        self.command_writer.write_command('actualize_wheels', 300)
        print('Switched mode to TURN')

    def on_square_press(self):
        self.mode = DeviantModes.CLIMBING
        self.neopixel.issue_command('steady', color='blue')    
        self.command_writer.write_wheels_command('climbing', 0)
        self.command_writer.write_command('actualize_wheels', 300)
        print('Switched mode to CLIMBING')
    
    def on_R3_press(self):
        if self.mode == DeviantModes.MOVE_BODY:
            self.command_writer.write_command('body_to_center', 500)
        else:
            self.mode = DeviantModes.MOVE_BODY
            print('Switched mode to MOVE_BODY')

if __name__ == '__main__':
    DeviantDualShock().start()
