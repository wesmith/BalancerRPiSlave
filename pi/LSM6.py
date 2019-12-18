# Copyright Pololu Corporation.  For more information, see https://www.pololu.com/

'''
WSmith copied this file from Pololu's a_star.py, to create a class to
read the LSM6 accelerometer/magnetometer chip on the Pololu Balboa board,
from the RPi.
'''      

import smbus
import struct
import time

class LSM6:
  def __init__(self):
    self.bus = smbus.SMBus(1)
    self.address  = 0x6b  # LSM6 I2C address
    self.IDreg    = 0x0f  # register containing device ID
    self.ID       = 0x69  # device ID
    txt = 'LSM6: address {}, IDreg {}, ID {}'.\
            format(self.address, self.IDreg, self.ID)
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
    val = self.read_unpack(self.IDreg, 1, 'B')
    if (val == self.ID):
      print ('LSM6 identified successfully')
    else:
      txt = 'LSM6 error: tried address {}, IDreg {}, ID should be {}, found {}'.\
            format(self.address, self.IDreg, self.ID, val)
      print (txt)

      
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
