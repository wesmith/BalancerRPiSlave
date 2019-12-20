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

    accl = lsm6.read_device('accel', 6)
    gyro = lsm6.read_device('gyro',  6)

    '''
    ax = np.short(accl[0] + (accl[1] << 8))
    ay = np.short(accl[2] + (accl[3] << 8))
    az = np.short(accl[4] + (accl[5] << 8))
    mag = np.sqrt(ax**2 + ay**2 + az**2)
    print('accel x: {:+5.3f}, y: {:+5.3f}, z: {:+5.3f}'.format(ax/mag, ay/mag, az/mag))
    '''
    
    vals = np.array([np.short(accl[j] + (accl[j+1] << 8)) for j in [0,2,4]])
    #mag  = np.sqrt((vals*vals).sum())
    #vals = vals/mag
    print('accel x: {:+10d}, y: {:+10d}, z: {:+10d}'.format(vals[0], vals[1], vals[2]))
    #print('accel x: {:+5.3f}, y: {:+5.3f}, z: {:+5.3f}'.format(vals[0], vals[1], vals[2]))    
                  
    time.sleep(0.01)

    
