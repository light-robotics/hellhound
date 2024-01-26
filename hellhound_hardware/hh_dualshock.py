import time
from enum import Enum
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hardware.dualshock import DualShock
from hellhound_hardware.neopixel_commands_setter import NeopixelCommandsSetter
from run.commands_writer import CommandsWriter
import configs.config as cfg


class HellHoundModes(Enum):
    CLIMBING  = 1
    RUN       = 2
    OBSTACLES = 3
    BATTLE    = 4
    TURN      = 5
    MOVE_BODY = 6

class HellHoundDualShock(DualShock):
    """
    To execute neopixel commands run ./run/neopixel_commands_reader.py before running this
    To execute servo commands run ./run/movement_processor.py AFTER running this
    """
    def __init__(self):
        self.neopixel = NeopixelCommandsSetter()
        self.connect()
        self.light_on = False
        self.wheels_locked = False
        self.climing_mode = 0
        self.mode = HellHoundModes.RUN
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
        pass
    
    def on_options_press(self):
        self.command_writer.write_command('exit', 0)
        time.sleep(0.5)
        self.command_writer.write_command('none', 1000)
    
    def on_share_press(self):
        pass

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

    def on_L3_up(self, value):
        pass
    
    def on_L3_down(self, value):
        pass

    def on_L3_left(self, value):
        pass

    def on_L3_right(self, value):
        pass
    
    def on_L3_press(self):
        pass
    
    def on_L3_y_at_rest(self):
        pass

    def on_L3_x_at_rest(self):
        pass
    
    def on_R3_up(self, value):
        self.command_writer.write_command('forward_two_legged', 300)

    def on_R3_down(self, value):
        pass
    
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
        self.command_writer.write_command('body_right', 800)
        
    def on_left_arrow_press(self):
        self.command_writer.write_command('body_left', 800)
              
    def on_up_arrow_press(self):
        self.command_writer.write_command('body_forward', 800)

    def on_down_arrow_press(self):
        self.command_writer.write_command('body_backward', 800)
        
    def on_up_down_arrow_release(self):
        self.command_writer.write_command('none', 500)

    def on_left_right_arrow_release(self):
        self.command_writer.write_command('none', 500)  
        
    def on_x_press(self):
        self.command_writer.write_command('down', 1000)
    
    def on_x_release(self):
        self.command_writer.write_command('none', 1000)

    def on_triangle_press(self):
        self.command_writer.write_command('up', 1000)
    
    def on_triangle_release(self):
        self.command_writer.write_command('none', 1000)

    def on_circle_press(self):
        pass
        # reposition wider

    def on_square_press(self):
        pass
        # reposition narrower
    
    def on_R3_press(self):
        self.command_writer.write_command('body_to_center', 500)

if __name__ == '__main__':
    HellHoundDualShock().start()
