#!/usr/bin/python3

# test.py
# WESmith 12/18/19
# test LSM6 class

import LSM6 as ls
import time

lsm6 = ls.LSM6()

lsm6.verifyWrite()
time.sleep(1)

#for k in range(100):
while(True):

    accl = lsm6.getRaw('accel', 6)
    gyro = lsm6.getRaw('gyro',  6)
    #print('{}: {}   {}: {}'.format('accel', accl, 'gyro', gyro))

    ''' # this works, but not producing signed results
    ax = int(accl[0]) + (int(accl[1]) << 8)
    ay = int(accl[2]) + (int(accl[3]) << 8)
    az = int(accl[4]) + (int(accl[5]) << 8)
    print('x accel: {}, y accel: {}, z accel {}'.format(ax, ay, az))
    '''

    # this works, but not producing signed results
    ax = accl[0] + (accl[1] << 8)
    ay = accl[2] + (accl[3] << 8)
    az = accl[4] + (accl[5] << 8)
    print('x accel: {}, y accel: {}, z accel {}'.format(ax, ay, az))
                  
    '''
    for k in ['accel']:
        ll, bb, rrs, rru = lsm6.getData(k)
        print('{}: raw_s {}  raw_u {}'.format(k, rrs, rru))
    '''

    #print('{}: little {}, big {}, raw {}'.\
    #      format(name, ll, bb, rr))
    
    time.sleep(0.1)

    
