#!/usr/bin/python3

# test.py
# WESmith 12/18/19
# test LSM6 class

import LSM6 as ls

lsm6 = ls.LSM6()

lsm6.setup()

while(True):

    ll, bb = lsm6.getGyro()

    print('z-gyro: little {}, big {}'.format(ll[0], bb[0]))
