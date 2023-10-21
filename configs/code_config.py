import os


DEBUG = False # in DEBUG mode command to servos is not issued

project_dir = os.path.join(os.path.dirname(__file__), '..')
main_log_file = os.path.join(project_dir, 'logs', 'main.log')
lidar_log_file = os.path.join(project_dir, 'logs', 'lidar.log')
lidar_data_log_file = os.path.join(project_dir, 'logs', 'lidar_data.log')
pathfinding_log_file = os.path.join(project_dir, 'logs', 'pathfinding.log')
angles_log_file = os.path.join(project_dir, 'logs', 'angles.log')

movement_command_file = os.path.join(project_dir, 'commands', 'movement_command.txt')
side_movement_command_file = os.path.join(project_dir, 'commands', 'side_movement_command.txt')
wheels_command_file = os.path.join(project_dir, 'commands', 'wheels_command.txt')
side_wheels_command_file = os.path.join(project_dir, 'commands', 'side_wheels_command.txt')
neopixel_command_file = os.path.join(project_dir, 'commands', 'neopixel_command.txt')

lidar_data_file = os.path.join(project_dir, 'data', 'lidar_data.log')

cache_dir = os.path.join(project_dir, 'cache')

logger_config = {
    'version': 1,
    'formatters': {
        'default_formatter': {
            'format': '[%(asctime)s][%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'main_file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': main_log_file
        },
        'lidar_file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': lidar_log_file
        },
        'lidar_data_file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': lidar_data_log_file
        },
        'pathfinding_file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': pathfinding_log_file
        },
        'angles_file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'default_formatter',
            'filename': angles_log_file
        }
    },
    'loggers': {
        'main_logger': {
            'handlers': ['main_file_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'lidar_logger': {
            'handlers': ['lidar_file_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'lidar_data_logger': {
            'handlers': ['lidar_data_file_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'pathfinding_logger': {
            'handlers': ['pathfinding_file_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'angles_logger': {
            'handlers': ['angles_file_handler'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
