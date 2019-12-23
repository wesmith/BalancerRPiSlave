// BalancerRPiSlave.ino
// WSmith modified this from Balancer.ino and BalboaRPiSlaveDemo.ino, 
// 12/22/19
// Run the Balboa balancer as an I2C slave from an RPi I2C master.
// See Balancer.ino comments (deleted here) for more info 
// about the balancer.

#include "BalancerRPiSlave.h"

// I2C slave setup
// Custom data structure used for interpreting the buffer.
// Keep this under 64 bytes total.  If the
// data format is changed, make sure to update the corresponding 
// code in a_star.py on the Raspberry Pi.

// had to define this in .h file with 'extern' to compile
PololuRPiSlave<struct Data, 20> slave; 

Balboa32U4Motors motors;
Balboa32U4Encoders encoders;
Balboa32U4Buzzer buzzer;
Balboa32U4ButtonA buttonA;
Balboa32U4ButtonB buttonB;
Balboa32U4ButtonC buttonC;

void setup()
{
  // Uncomment these lines if the motors are reversed.
  // motors.flipLeftMotor(true);
  // motors.flipRightMotor(true);

  // Set up the slave at I2C address 20 (0x14)
  slave.init(20);
  
  // WS go thru update, write cycle with buffer to ensure initialization
  slave.updateBuffer();  
  slave.finalizeWrites();
  
  Serial.begin(9600);  // WS

  ledYellow(0);
  ledRed(1);
  ledRed(0);
}

const char song[] PROGMEM =
  "!O6 T240"
  "l32ab-b>cl8r br b-bb-a a-r gr g-4 g4"
  "a-r gr g-gg-f er e-r d4 e-4"
  "gr msd8d8ml d-4d4"
  "l32efg-gl8r msd8d8ml d-4d4"
  "<bcd-d e-efg- ga-ab- a4 gr";

void playSong()
{
  if (!buzzer.isPlaying())
  {
    buzzer.playFromProgramSpace(song);
  }
}

void driveAround()
{
  uint16_t time = millis() % 8192;
  uint16_t leftSpeed, rightSpeed;
  if (time < 1900)
  {
    leftSpeed = 20;
    rightSpeed = 20;
  }
  else if (time < 4096)
  {
    leftSpeed = 25;
    rightSpeed = 15;
  }
  else if (time < 4096 + 1900)
  {
    leftSpeed = 20;
    rightSpeed = 20;
  }
  else
  {
    leftSpeed = 15;
    rightSpeed = 25;
  }

  balanceDrive(leftSpeed, rightSpeed);
}

void standUp()
{
  motors.setSpeeds(0, 0);
  buzzer.play("!>grms>g16>g16>g2");
  ledGreen(1);
  ledRed(1);
  ledYellow(1);
  while (buzzer.isPlaying());
  motors.setSpeeds(-MOTOR_SPEED_LIMIT, -MOTOR_SPEED_LIMIT);
  delay(400);
  motors.setSpeeds(150, 150);
  for (uint8_t i = 0; i < 20; i++)
  {
    delay(UPDATE_TIME_MS);
    balanceUpdateSensors();
    if(angle < 60000)
    {
      break;
    }
  }
  motorSpeed = 150;
  balanceResetEncoders();
}

void loop()
{
  // Call updateBuffer() before using the buffer, to get the latest
  // data including recent master writes.
  // for now just call this in balanceUpdateSensors() WS
  //slave.updateBuffer();

  static bool enableSong = false;
  static bool enableDrive = false;

  balanceUpdate();

  if (isBalancing())
  {
    if (enableSong)   { playSong(); }
    if (enableDrive)  { driveAround(); }
  }
  else
  {
    buzzer.stopPlaying();
    balanceDrive(0, 0); // reset driving speeds

    if (buttonA.getSingleDebouncedPress())
    {
      enableSong = false;
      enableDrive = false;
      standUp();
    }
    else if (buttonB.getSingleDebouncedPress())
    {
      enableSong = false;
      enableDrive = true;
      standUp();
    }
    else if (buttonC.getSingleDebouncedPress())
    {
      enableSong = true;
      enableDrive = true;
      standUp();
    }
  }

  // Illuminate the red LED if the last full update was too slow.
  ledRed(balanceUpdateDelayed());

  // the following variable for diagnostics
  int32_t fallingAngleOffset = angleRate * ANGLE_RATE_RATIO - angle;

  /*
  Serial.print("Angle: ");  // WS print variables
  Serial.print(angle/1000);
  Serial.print("  fallingAngleOffset: ");
  Serial.print(fallingAngleOffset/1000);
  Serial.print("  estimate of ANGLE_RATE_RATIO: ");
  Serial.println(float(angle) / float(angleRate));
  */
  /*
  // the following printout is successful WS
  char txt[60];
  sprintf(txt, "Gyro rates X %4d  Y %4d  Z %4d   Accel X %4d  Y %4d  Z %4d", 
  slave.buffer.gyro_rate[0], slave.buffer.gyro_rate[1], slave.buffer.gyro_rate[2],
  slave.buffer.accel[0],     slave.buffer.accel[1],     slave.buffer.accel[2]);
  Serial.println(txt);
  */

  if (fallingAngleOffset > 0)
  {
    ledYellow(1);
    ledGreen(0);
  }
  else
  {
    ledYellow(0);
    ledGreen(1);
  }
  // When WRITING is finished, call finalizeWrites() to make modified
  // data available to the I2C master.
  // turn this off for now WS
  //slave.finalizeWrites();
}
