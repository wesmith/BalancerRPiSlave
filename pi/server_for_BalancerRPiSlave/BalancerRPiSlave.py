#!/usr/bin/env python3

# WESmith 12/22/19

# implement a non-flask testbed for communicating the lsm6 info from the RPi to the Balboa 32U4.

import a_star_mod as st
import LSM6       as ls
import numpy      as np
import time
import pdb

star = st.AStar()
lsm6 = ls.LSM6()

while(True):

    accl = lsm6.read_device('accel')
    gyro = lsm6.read_device('gyro')
    
    #batt = star.read_battery_millivolts()
    #encs = star.read_encoders()

    try:
        star.write_gyro_rate(gyro) # full vector
        star.write_accel(accl)     # full vector
    except:
        pdb.set_trace()
    
    '''
    try:
        print('batt: {} mV   encoders: {} {}'.format(batt[0], *encs))
    except:
        pdb.set_trace()
    '''
    
    txt = 'accl x,y,z: {:+4d}  {:+4d}  {:+4d}   gyro x,y,z: {:+6d}  {:+6d}  {:+6d}'.\
          format(*np.hstack([accl, gyro]))
    print(txt)

    time.sleep(0.01)
