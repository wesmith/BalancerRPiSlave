# Copyright Pololu Corporation.  For more information, see https://www.pololu.com/

'''
WSmith copied this file from Pololu's a_star.py, to create a class to
read the LSM6DS33 accelerometer/gyro chip on the Pololu Balboa board
from the RPi.
'''      

import smbus
import struct
import time

class LSM6:
  def __init__(self):
    self.bus = smbus.SMBus(1)
    self.address     = 0x6b  # LSM6DS33 SAO_HIGH I2C address
    self.WHO_AM_I    = 0x0f  # register containing device ID
    self.DS33_WHO_ID = 0x69  # device ID
    self.CTRL1_XL    = 0X10  # accelerometer buffer
    self.CTRL2_G     = 0X11  # gyro          buffer
    self.CTRL3_C     = 0X12  # common        buffer
    self.OUTX_L_G    = 0x22  # gyro          array start (low then high byte, each for x,y,z)
    self.OUTX_L_XL   = 0x28  # accelerometer array start (low then high byte, each for x,y,z)
    
    txt = 'LSM6: address {}, IDreg {}, ID {}'.\
            format(hex(self.address), hex(self.WHO_AM_I), hex(self.DS33_WHO_ID))
    print(txt)
    self.setup()

  def read_unpack(self, address, size, format):
    # A delay of 0.0001 (100 us) after each write is enough to account
    # for the worst-case situation.

    self.bus.write_byte(self.address, address)
    time.sleep(0.0001)
    byte_list = [self.bus.read_byte(self.address) for _ in range(size)]
    return struct.unpack(format, bytes(byte_list))

  def write_pack(self, address, format, *data):
    data_array = list(struct.pack(format, *data))
    self.bus.write_i2c_block_data(self.address, address, data_array)
    time.sleep(0.0001)

  def setup(self):
    val = self.read_unpack(self.WHO_AM_I, 1, 'B')  # 'B': unsigned char: see python struct info
    if (val[0] == self.DS33_WHO_ID):
      print ('LSM6 identified successfully')
    else:
      txt = 'LSM6 error: tried address {}, IDreg {}, ID should be {}, found {}'.\
            format(hex(self.address), hex(self.WHO_AM_I),
                   hex(self.DS33_WHO_ID), hex(val[0]))
      print (txt)
      return

    # all settings derived from Pololu Balancer.ino, Balance.cpp, and LSM6.cpp
    
    # accelerometer settings: 0b10000000 = 0x80 sets:
    # 1.66 kHz high-performance mode (ODR = 1000, first 4 digits),
    # (ODR means Output Data Rate)
    # +/-2 g full scale (FS_XL = 00: next 2 digits)
    # 400 Hz anti-aliasing filter bandwidth selection (BW_XL = 00: last 2 digits)
    # see LSM6DS33 datasheet p. 47
    self.write_pack(self.CTRL1_XL, 'B', 0x80)

    # gyro settings: 0b01011000 = 0x58
    # 208 Hz (normal mode, ODR = 0101, first 4)
    # 1000 deg per sec (FS_G = 10, next 2)
    # gyro full-scale at 125 dps: 0 = disabled (next 1 digit)
    # last digit must be 0 in all cases
    # see datasheet p. 48
    self.write_pack(self.CTRL2_G, 'B', 0x58)

    # common settings: 0b00000100 = 0x04
    # 0 boot: 0 is normal mode
    # 0 block data update: 0 is continuous update
    # 0 interrupt activation level: 0 = interrupt output pads active high
    # 0 push-pull mode: 0 (open-drain mode: 1)
    # 0 SPI mode: 0 means 4-wire interface
    # 1 register address automatically incremented during multiple-byte access: 1
    # 0 LSB at lower address when 0
    # 0 SW reset, 0 is normal mode
    # see datasheet p. 49
    self.write_pack(self.CTRL3_C, 'B', 0x40)

    time.sleep(1) # wait a second for readings to stabilize

  def verifyWrite(self):
    # verify that registers have been set correctly
    regs = [self.CTRL1_XL, self.CTRL2_G, self.CTRL3_C]
    vals = [0x80, 0x58, 0x40]
    for j,k in zip(regs, vals):
      ctrl = self.read_unpack(j, 1, 'B')
      txt = 'register {} should be {}, it is {}'.\
            format(hex(j), k, hex(ctrl[0]))
    print(txt)
          
  def getData(self, name):
    dd = {'accel': self.OUTX_L_XL, 'gyro': self.OUTX_L_G}
    
    # 'h' is short integer (2 bytes each): must verify endian-order is correct
    lit_end = self.read_unpack(dd[name], 6, '<3h')  # get using little-endian
    big_end = self.read_unpack(dd[name], 6, '>3h')  # get using big-endian
    raw     = self.read_unpack(dd[name], 6, '6b')   # 'b' is signed char
    return lit_end, big_end, raw
    
      
'''
  def leds(self, red, yellow, green):
    self.write_pack(0, 'BBB', red, yellow, green)

  def motors(self, left, right):
    self.write_pack(6, 'hh', left, right)

  def read_buttons(self):
    return self.read_unpack(3, 3, "???")

  def read_battery_millivolts(self):
    return self.read_unpack(10, 2, "H")

  def read_analog(self):
    return self.read_unpack(12, 12, "HHHHHH")

  def read_encoders(self):
    return self.read_unpack(39, 4, 'hh')

  def test_read8(self):
    self.read_unpack(0, 8, 'cccccccc')

  def test_write8(self):
    self.bus.write_i2c_block_data(self.address, 0, [0,0,0,0,0,0,0,0])
    time.sleep(0.0001)
'''
