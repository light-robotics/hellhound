from configs import code_config


class CommandsWriter:
    symbols = {
        'w' : 'forward',
        's' : 'backward',
        'r' : 'up',
        't' : 'down',
        'a' : 'turn_left',
        'd' : 'turn_right',
        'q' : 'strafe_left',
        'e' : 'strafe_right',
        'aw': 'turn_forward_left',
        'dw': 'turn_forward_right',
        'wq': 'forward_left',
        'we': 'forward_right',
        'x' : 'start',
        'z' : 'exit'
    }

    def __init__(self):
        self.command_file = code_config.movement_command_file
        self.side_command_file = code_config.side_movement_command_file
        self.wheels_command_file = code_config.wheels_command_file
        self.side_wheels_command_file = code_config.side_wheels_command_file
        self.command_id = 1
        self.side_command_id = 1
        self.write_command('none', 1000)
        self.write_side_command('none', 1000)
        self.write_wheels_command('forward', 0)
        self.write_wheels_side_command('forward', 0)

    def write_command(self, command: str, speed: int) -> None:
        if speed > 3000:
            print(f'Ignoring command {command}, {speed}')
        else:
            print(f'writing {command}, {speed} to command file')
            with open(self.command_file, 'w') as f:
                f.write(f'{self.command_id},{command},{speed}')
                self.command_id += 1

    def write_side_command(self, command: str, speed: int) -> None:
        if speed > 3000:
            print(f'Ignoring side command {command}, {speed}')
        else:
            print(f'writing {command}, {speed} to side command file')
            with open(self.side_command_file, 'w') as f:
                f.write(f'{self.side_command_id},{command},{speed}')
                self.side_command_id += 1

    def write_wheels_command(self, command: str, speed: str) -> None:
        with open(self.wheels_command_file, 'w') as f:
            f.write(f'{command},{speed}')

    def write_wheels_side_command(self, command: str, speed: str) -> None:
        with open(self.side_wheels_command_file, 'w') as f:
            f.write(f'{command},{speed}')

    def initiate_local_writer(self) -> None:
        try:
            while True:
                symbol = input('Enter command:\n')
                command = self.symbols.get(symbol, 'none')
                self.write_command(command, 500)
                if command == 'exit':
                    break

        except KeyboardInterrupt:
            self.write_command('exit')

if __name__ == '__main__':
    CommandsWriter().initiate_local_writer()
