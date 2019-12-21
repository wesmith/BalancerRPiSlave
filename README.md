BalancerRPiSlave

Run the Balboa balancer board from a Raspberry Pi, with balancing enabled. The Balboa's
32U4 chip acts as the I2C slave of the RPi in this configuration. Normally, when the Balboa
board is in stand-alone (ie, without the RPi) balancing mode, the 32U4 is the I2C master,
reading the Balboa's LSM6 accelerometer/gyro to get the y-angle rate. When the 32U4 is
acting as an RPi slave, however, it is not possible for the 32U4 to also be the I2C master of
the LSM6. Thus it is necessary to read the LSM6 from the RPi and communicate the angle rate
to the Balboa I2C slave. The purpose of this project is to enable this functionality.

The LSM6.py class has been successfully tested in reading the Balboa board's LSM6
accelerometer/gyro, using test.py running on an RPi 3 connected to the Balboa board.
