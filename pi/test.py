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

    '''
    vals = np.array([np.short(accl[j] + (accl[j+1] << 8)) for j in [0,2,4]], dtype='float')
    mag  = np.sqrt((vals*vals).sum())
    vals = vals/mag
    '''
    #print('accel x: {:+5.3f}, y: {:+5.3f}, z: {:+5.3f}'.format(accl[0], accl[1], accl[2]))
    print('accel x: {:+5.3f}, y: {:+5.3f}, z: {:+5.3f}'.format(*accl))    

    time.sleep(0.01)

    
