'''Records scans to a given file in the form of numpy array.
Usage example:
$ ./record_scans.py out.npy'''
import logging
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging.config

from rplidar import RPLidar

import configs.code_config as code_config


class ExtRPLidar(RPLidar):
    def __init__(self, PORT_NAME:str = '/dev/ttyUSB0'):
        super().__init__(PORT_NAME)        
        logging.config.dictConfig(code_config.logger_config)
        self.logger=logging.getLogger('lidar_logger')

    def record_scan(self):
        data=[]
        try:
            print('Recording measurments... Press Crl+C to stop.')
            for scan in self.iter_scans():
                data.append(scan)
        except KeyboardInterrupt:
            print('Stoping.')
        self.stop()
        self.stop_motor()
        self.disconnect()
        with open(code_config.lidar_data_file, 'w') as f:
            f.write(str(data))
        

if __name__ == '__main__':
    ExtRPLidar().record_scan()
