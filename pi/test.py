#!/usr/bin/python3

# test.py
# WESmith 12/18/19
# test LSM6 class

import LSM6  as ls
import numpy as np
import time

lsm6 = ls.LSM6()

time.sleep(1)

#for k in range(100):
while(True):

    accl = lsm6.read_device('accel')
    gyro = lsm6.read_device('gyro')

    txt = 'accel x,y,z: {:+5.3f}  {:+5.3f}  {:+5.3f}   gyro x,y,z: {:+6.0f}  {:+6.0f}  {:+6.0f}'.\
          format(*np.hstack([accl, gyro]))
    print(txt)

    time.sleep(0.01)

    
