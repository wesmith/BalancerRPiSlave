#!/usr/bin/python3

# test.py
# WESmith 12/18/19
# test LSM6 class

import LSM6 as ls
import time

lsm6 = ls.LSM6()

lsm6.setup()

while(True):

    name = 'accel'
    ll, bb, rr = lsm6.getData(name)

    print('{}: little {}, big {}, raw {}'.\
          format(name, ll, bb, rr))
    time.sleep(0.5)

    
