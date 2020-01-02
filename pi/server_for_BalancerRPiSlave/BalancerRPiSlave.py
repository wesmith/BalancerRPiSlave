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
DATA_START_TIME = 3.0  # time to start collecting data: seconds after program start
DATA_STOP_TIME  = 10.0 # time to stop collectiong data: seconds after program start
# next: use z accelerometer to set start time of data collection: if z > 800 it is balancing

print('Running BalancerRPiSlave.py')
start_time = time.time()

data  = []
saved = False

while(True):
#while(k < 100):
    
    now   = time.time()
    dtime = now - start_time
    
    accl = list(lsm6.read_device('accel'))
    gyro = list(lsm6.read_device('gyro'))
    
    #batt = star.read_battery_millivolts()
    encs   = list(star.read_encoders())
    motors = list(star.read_motors())

    star.write_gyro_rate(*gyro) # full vector
    star.write_accel(*accl)     # full vector

    if (dtime > DATA_START_TIME) and (dtime < DATA_STOP_TIME):
        #data.append(np.hstack([dtime, accl, gyro]))
        # save time, motorX, motorY, encoderX, encoderY, gyro_rate_y
        data.append(np.hstack([dtime, motors, encs, gyro[1]]))

    if (dtime > (DATA_STOP_TIME + 1)) and (not saved):
        fname = time.strftime('%Y%m%d-%H%M%S')
        print('saving data in {}'.format(fname))
        data  = np.array(data)
        saved = True
        np.save(fname, data)
    
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
    #time.sleep(SLEEP)

