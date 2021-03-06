#!/usr/bin/env python3

# WESmith 12/22/19

# implement a non-flask testbed for communicating lsm6 info from the RPi to the Balboa 32U4
# NOTE: the Balboa balancer must be in its horizontal position (x-axis horizontal,
#       z-axis up) when this script is started, so that accl[0] (the x-axis g vector) is
#       close to zero

import a_star_mod as st
import LSM6       as ls
import numpy      as np
import time
import pdb

star = st.AStar()
lsm6 = ls.LSM6()  # this automatically calibrates gyro

DATA_TIME  = 10.0 # time in seconds to acquire data
DELAY_TIME =  2.0 # time to delay data acquisition after balancing starts
X_ACCEL    =  700 # the value of x_accel at which balancing has presumably commenced
                  # (Balboa x axis is pointed vertically when perfectly balancing:
                  #  this value is then close to 1000; it is close to 0 when Balboa is horiz)
data = []

#SLEEP = 0.001

print('Running BalancerRPiSlave.py')

while(True):
    
    accl = list(lsm6.read_device('accel'))
    gyro = list(lsm6.read_device('gyro'))
    
    #batt = star.read_battery_millivolts()
    encs   = list(star.read_encoders())
    motors = list(star.read_motors())

    star.write_gyro_rate(*gyro) # full vector
    star.write_accel(*accl)     # full vector

    if (accl[0] < X_ACCEL): # initialize or reset: not balancing
        START_TIMER = True
        START_DATA  = False
        #print('**** INITIALIZING/RESETTING ****\n')

    if (accl[0] > X_ACCEL) and START_TIMER:
        start_time  = time.time()
        START_TIMER = False
        START_DATA  = True
        print('\n**** ACQUIRING DATA IN {} SECONDS ****'.format(DELAY_TIME))

    if START_DATA:
        dtime = time.time() - start_time
        #data.append(np.hstack([dtime, accl, gyro]))
        # save time, motorX, motorY, encoderX, encoderY, gyro_rate_y
        #data.append(np.hstack([dtime, motors, encs, gyro[1]]))
        # is this faster?
        if dtime > DELAY_TIME:
            data.append([dtime, motors[0], motors[1], encs[0], encs[1], gyro[1]])
        if dtime > (DELAY_TIME + DATA_TIME):
            START_DATA = False
            fname = 'data/{}'.format(time.strftime('%Y%m%d-%H%M%S'))
            print('**** SAVING DATA IN {} ****'.format(fname))
            np.save(fname, data)
            print('**** SAVE COMPLETE ****\n')
            data = []  # reset if another unbalance/balance cycle is started
    
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

