#include "BalancerRPiSlave.h"

int32_t gYZero;
int32_t angle; // millidegrees
int32_t angleRate; // degrees/s
int32_t distanceLeft;
int32_t speedLeft;
int32_t driveLeft;
int32_t distanceRight;
int32_t speedRight;
int32_t driveRight;
int16_t motorSpeed;
bool isBalancingStatus = false;
bool balanceUpdateDelayedStatus;


bool isBalancing()
{
  return isBalancingStatus;
}

bool balanceUpdateDelayed()
{
  return balanceUpdateDelayedStatus;
}

void balanceSetup()  // no-op now
{
  // All LSM6 readings now done by the RPi. The 32U4 has no knowledge of the LSM6.
  // Gyro is already calibrated in slave.buffer.gyro_rate
}

// This function contains the core algorithm for balancing a
// Balboa 32U4 robot.
void balance()
{
  // Adjust toward angle=0 with timescale ~10s, to compensate for
  // gyro drift.  More advanced AHRS systems use the
  // accelerometer as a reference for finding the zero angle, but
  // this is a simpler technique: for a balancing robot, as long
  // as it is balancing, we know that the angle must be zero on
  // average, or we would fall over.
  angle = angle * 999 / 1000;

  // This variable measures how close we are to our basic
  // balancing goal - being on a trajectory that would cause us
  // to rise up to the vertical position with zero speed left at
  // the top.  This is similar to the fallingAngleOffset used
  // for LED feedback and a calibration procedure discussed at
  // the end of Balancer.ino.
  //
  // It is in units of millidegrees, like the angle variable, and
  // you can think of it as an angular estimate of how far off we
  // are from being balanced.
  int32_t risingAngleOffset = angleRate * ANGLE_RATE_RATIO + angle;

  // Combine risingAngleOffset with the distance and speed
  // variables, using the calibration constants defined in
  // Balance.h, to get our motor response.  Rather than becoming
  // the new motor speed setting, the response is an amount that
  // is added to the motor speeds, since a *change* in speed is
  // what causes the robot to tilt one way or the other.
  motorSpeed += (
    + ANGLE_RESPONSE * risingAngleOffset
    + DISTANCE_RESPONSE * (distanceLeft + distanceRight)
    + SPEED_RESPONSE * (speedLeft + speedRight)
    ) / 100 / GEAR_RATIO;

  if (motorSpeed > MOTOR_SPEED_LIMIT)
  {
    motorSpeed = MOTOR_SPEED_LIMIT;
  }
  if (motorSpeed < -MOTOR_SPEED_LIMIT)
  {
    motorSpeed = -MOTOR_SPEED_LIMIT;
  }

  // Adjust for differences in the left and right distances; this
  // will prevent the robot from rotating as it rocks back and
  // forth due to differences in the motors, and it allows the
  // robot to perform controlled turns.
  int16_t distanceDiff = distanceLeft - distanceRight;

  motors.setSpeeds(
    motorSpeed + distanceDiff * DISTANCE_DIFF_RESPONSE / 100,
    motorSpeed - distanceDiff * DISTANCE_DIFF_RESPONSE / 100);
}

void lyingDown()
{
  // Reset things so it doesn't go crazy.
  motorSpeed = 0;
  distanceLeft = 0;
  distanceRight = 0;
  motors.setSpeeds(0, 0);

  if (angleRate > -2 && angleRate < 2)
  {
    // Use the accelerometer to measure the robot's rest angle when the angle rate is very low.
    // This is necessary for condition 1) below and useful for condition 2) below. 
    // A low rate occurs when 1) the robot is lying down (0 rate), or 2) when it is balancing stably
    // (close to 0 rate). 
    // 1) When the robot is lying down, this thus sets the robot's starting angle to 90 deg (x, y of
    // the Pololu board are parallel to the ground, z is up, so that 
    // z accel is +g (scaled), and x accel is 0, thus atan2(1,0) = 90 deg). This is a necessary requirement
    // for balancing to start, as the robot is tipped up beyond the START_BALANCING_ANGLE from its initial value
    // of 90 deg. 
    // 2) When the robot is balancing stably, the robot angle is reset to 0 deg or close to 0 deg (x is now pointing up, 
    // y and z are parallel to the ground: atan2(0,1) = 0 deg). This is less critical than 1) above, and facilitates 
    // a reset of angle when balancing, removing gyro biases. 
    // The atan2 function returns a result in radians; multiply by 180000/pi to convert it
    // to millidegrees.

    // WS getting accel from slave.buffer now
    // angle = atan2(imu.a.z, imu.a.x) * 57296;
    angle = atan2(slave.buffer.accel[2], slave.buffer.accel[0]) * 57296;

    distanceLeft = 0;
    distanceRight = 0;
  }
}

void integrateGyro()
{
  // Convert from full-scale 1000 deg/s to deg/s.
  //angleRate = (imu.g.y - gYZero) / 29;
  angleRate = slave.buffer.gyro_rate[1];  // WS y_rate, calibration already done on RPi

  angle += angleRate * UPDATE_TIME_MS;
}

void integrateEncoders()
{
  static int16_t lastCountsLeft;
  int16_t countsLeft = encoders.getCountsLeft();
  speedLeft = (countsLeft - lastCountsLeft);
  distanceLeft += countsLeft - lastCountsLeft;
  lastCountsLeft = countsLeft;

  static int16_t lastCountsRight;
  int16_t countsRight = encoders.getCountsRight();
  speedRight = (countsRight - lastCountsRight);
  distanceRight += countsRight - lastCountsRight;
  lastCountsRight = countsRight;
}

void balanceDrive(int16_t leftSpeed, int16_t rightSpeed)
{
  driveLeft = leftSpeed;
  driveRight = rightSpeed;
}

void balanceDoDriveTicks()
{
  distanceLeft -= driveLeft;
  distanceRight -= driveRight;
  speedLeft -= driveLeft;
  speedRight -= driveRight;
}

void balanceResetEncoders()
{
  distanceLeft = 0;
  distanceRight = 0;
}

void balanceUpdateSensors()
{
  slave.updateBuffer();  // WS get data from RPi 
  integrateGyro();
  integrateEncoders();
}

void balanceUpdate()
{
  static uint16_t lastMillis;
  uint16_t ms = millis();
  static uint8_t count = 0;

  // Perform the balance updates at 100 Hz.
  if ((uint16_t)(ms - lastMillis) < UPDATE_TIME_MS) { return; }
  balanceUpdateDelayedStatus = ms - lastMillis > UPDATE_TIME_MS + 1;
  lastMillis = ms;

  balanceUpdateSensors();
  balanceDoDriveTicks();

  if (isBalancingStatus)
  {
    balance();

    // Stop trying to balance if we have been farther from
    // vertical than STOP_BALANCING_ANGLE for 5 counts.
    if (abs(angle) > STOP_BALANCING_ANGLE)
    {
      if (++count > 5)
      {
        isBalancingStatus = false;
        count = 0;
      }
    }
    else
    {
      count = 0;
    }
  }
  else
  {
    lyingDown();

    // Start trying to balance if we have been closer to
    // vertical than START_BALANCING_ANGLE for 5 counts.
    if (abs(angle) < START_BALANCING_ANGLE)
    {
      if (++count > 5)
      {
        isBalancingStatus = true;
        count = 0;
      }
    }
    else
    {
      count = 0;
    }
  }
}
