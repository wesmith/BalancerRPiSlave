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

SLEEP = 0.001

print('Running BalancerRPiSlave.py')

k    = 0
data = []

while(True):
#while(k < 100):
    print(k)

    accl = list(lsm6.read_device('accel'))
    gyro = list(lsm6.read_device('gyro'))
    
    #batt = star.read_battery_millivolts()
    #encs = star.read_encoders()

    star.write_gyro_rate(*gyro) # full vector
    star.write_accel(*accl)     # full vector

    if (k > 3000) and (k < 6000):
        print(k)
        data.append(np.hstack([accl, gyro]))

    if k == 7000:
        data = np.array(data)
        print(data)
    
    '''
    try:
        print('batt: {} mV   encoders: {} {}'.format(batt[0], *encs))
    except:
        pdb.set_trace()
    '''

    '''
    txt = 'accl x,y,z: {:+4d}  {:+4d}  {:+4d}   gyro x,y,z: {:+6d}  {:+6d}  {:+6d}'.\
          format(*np.hstack([accl, gyro]))
    print(txt)
    '''
    k += 1
    time.sleep(SLEEP)

#data = np.array(data)
#print (data)
