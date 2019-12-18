#!/usr/bin/python3

# test.py
# WESmith 12/18/19
# test LSM6 class

import LSM6 as ls
import time

lsm6 = ls.LSM6()

lsm6.setup()

while(True):

    ll, bb, rr = lsm6.getGyro()

    print('z-gyro: little {}, big {}, raw low {}, raw high {}'.\
          format(ll[2], bb[2], r[4], r[5]))
    time.sleep(0.5)

    
