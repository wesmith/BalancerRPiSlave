#!/usr/bin/python3

# test.py
# WESmith 12/18/19
# test LSM6 class

import LSM6 as ls
import time

lsm6 = ls.LSM6()

lsm6.verifyWrite()

#for k in range(30):
while(True):

    for k in ['accel']:
        ll, bb, rrs, rru = lsm6.getData(k)
        print('{}: raw_s {}  raw_u {}'.format(k, rrs, rru))


    #print('{}: little {}, big {}, raw {}'.\
    #      format(name, ll, bb, rr))
    
    time.sleep(0.2)

    
