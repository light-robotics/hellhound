import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hardware.htd45h import HTD45H, read_all_servos, read_values

if __name__ == '__main__':
    m1 = HTD45H(Port='/dev/ttyAMA0') # 1-6
    m2 = HTD45H(Port='/dev/ttyAMA2') # 7-12
    m3 = HTD45H(Port='/dev/ttyAMA3') # 13-18
    m4 = HTD45H(Port='/dev/ttyAMA1') # 19-24
    
    for i in [9, 10, 11]:
        m1.read_values(i)
    for i in [15, 16, 17]:
        m2.read_values(i)
    for i in [21, 22, 23]:
        m3.read_values(i)
    for i in [3, 4, 5]:
        m4.read_values(i)