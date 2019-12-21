'''
WSmith 12/19/19

Read the LSM6DS33 accelerometer/gyro chip on the Pololu Balboa board
from the RPi. All LSM6 settings are derived from Pololu Balancer.ino, 
Balance.cpp, and LSM6.cpp

NOTE: Unable to read block data on the RPi 3 with smbus as of 12/19/19:
      will read a byte at a time instead. 
'''      

import smbus
import time
import numpy as np

class LSM6:
  
  def __init__(self):
    self.bus         = smbus.SMBus(1)
    self.address     = 0x6b   # LSM6DS33 SAO_HIGH I2C address
    self.WHO_AM_I    = 0x0f   # register containing device ID
    self.DS33_WHO_ID = 0x69   # device ID
    self.sleep       = 0.0001 # WS made this a param: time to sleep in sec between write/read
                              # (this was 0.0001 in Pololu code: 100 us)
    self.length      = 6      # length in bytes of data vec (low, high byte, each for x,y,z)

    # accelerometer settings
    self.OUTX_L_XL      = 0x28  # data array start (low then high byte, each for x,y,z)
    self.CTRL1_XL       = 0x10  # buffer address
    self.CTRL1_XL_value = 0x80  # buffer value: 0x80 = 0b10000000 sets:
    # 1.66 kHz high-performance mode (ODR = 1000, first 4 digits; ODR is Output Data Rate)
    # +/-2 g full scale (FS_XL = 00: next 2 digits)
    # 400 Hz anti-aliasing filter bandwidth selection (BW_XL = 00: last 2 digits)
    # see LSM6DS33 datasheet p. 47

    # gyro settings
    self.OUTX_L_G      = 0x22  # data array start (low then high byte, each for x,y,z)    
    self.CTRL2_G       = 0x11  # buffer address
    self.CTRL2_G_value = 0x58  # buffer value: 0x58 = 0b01011000 sets:
    # 208 Hz (normal mode, ODR = 0101, first 4 digits)
    # 1000 deg per sec (FS_G = 10, next 2 digits)
    # gyro full-scale at 125 dps: 0 = disabled (next 1 digit)
    # last digit must be 0 in all cases
    # see datasheet p. 48
    self.calibrate   = 100          # number of iterations for gyro calibration
    self.gyro_offset = np.zeros(3)  # vector for gyro calibration
    self.gyro_scale  = 29           # Pololu says this scales from 1000 deg/s to deg/s: why 29?

    # common settings
    self.CTRL3_C       = 0x12  # buffer address
    self.CTRL3_C_value = 0x04  # buffer value: 0x04 = 0b00000100 sets:
    # 0 boot: 0 is normal mode
    # 0 block data update: 0 is continuous update
    # 0 interrupt activation level: 0 = interrupt output pads active high
    # 0 push-pull mode: 0 (open-drain mode: 1)
    # 0 SPI mode: 0 means 4-wire interface
    # 1 register address automatically incremented during multiple-byte access: 1
    #   NOTE: this is probably moot, since smbus block read not used here: RPI has block-read issues
    # 0 LSB at lower address when 0
    # 0 SW reset, 0 is normal mode
    # see datasheet p. 49

    self.choice = {'accel': self.OUTX_L_XL, 'gyro': self.OUTX_L_G}

    txt = 'initializing LSM6: I2C address {}, ID register {}, ID value {}'.\
            format(hex(self.address), hex(self.WHO_AM_I), hex(self.DS33_WHO_ID))
    print(txt)
    self.setup()
    

  def write_one_byte(self, register, value):
    self.bus.write_byte_data(self.address, register, value)
    time.sleep(self.sleep)

    
  def read_one_byte(self, register):
    self.bus.write_byte(self.address, register)
    time.sleep(self.sleep)
    return self.bus.read_byte(self.address)
  
    
  def read_multiple_bytes(self, register, length):
    # work-around for block read
    return [self.read_one_byte(register + k) for k in range(length)]


  def read_device(self, dev_name, calibrate=False):
    raw  = self.read_multiple_bytes(self.choice[dev_name], self.length)
    indx = np.arange(0, self.length, 2)
    vals = np.array([np.short(raw[j] + (raw[j+1] << 8)) for j in indx], dtype='float')
    # allow for different post-processing of accel or gyro values
    if dev_name == 'accel':
      mag = np.sqrt((vals*vals).sum())
      # normalized, scaled from 0 to 100, returned as signed int (0.5 for rounding)
      return (0.5 + 100 * vals/mag).astype(int) 
    else:
      if calibrate: # find gyro_offset using raw values
        return vals
      else:
        # remove offset, scale to Pololu 'angleRate', returned as signed int (0.5 for rounding)
        return (0.5 + (vals - self.gyro_offset) / self.gyro_scale).astype(int) 


  def setup(self):
    val = self.read_one_byte(self.WHO_AM_I)
    if (val == self.DS33_WHO_ID):
      print ('LSM6 identified successfully')
    else:
      txt = 'LSM6 error: tried address {}, ID register {}, ID should be {}, found {}'.\
            format(hex(self.address), hex(self.WHO_AM_I),
                   hex(self.DS33_WHO_ID), hex(val[0]))
      print (txt)
      return

    self.write_one_byte(self.CTRL1_XL, self.CTRL1_XL_value)
    self.write_one_byte(self.CTRL2_G,  self.CTRL2_G_value)
    self.write_one_byte(self.CTRL3_C,  self.CTRL3_C_value)

    time.sleep(1) # wait a second for readings to stabilize

    self.verify_write() # verify that registers have been set correctly

    self.calibrate_gyro()

    
  def verify_write(self):
    regs = [self.CTRL1_XL,       self.CTRL2_G,       self.CTRL3_C]
    vals = [self.CTRL1_XL_value, self.CTRL2_G_value, self.CTRL3_C_value]
    out  = self.read_multiple_bytes(self.CTRL1_XL, 3)
    if out == vals:
      print('Registers have been set correctly')
    else:
      for j, k in zip(regs, vals):
        txt = 'register {} should be {}'.format(hex(j), hex(k))
        print(txt)

      txt = 'TEST READ FAILED: actual register values are: {}'.\
            format([hex(out[0]), hex(out[1]), hex(out[2])])
      print(txt)

      
  def calibrate_gyro(self):
    print('Calibrating gyro')
    self.gyro_offset = \
        np.array([self.read_device('gyro', calibrate=True) \
                  for _ in range(self.calibrate)]).mean(axis=0)
    print('calibration values: x,y,z: {:+6.0f}  {:+6.0f}  {:+6.0f}'.format(*self.gyro_offset))
