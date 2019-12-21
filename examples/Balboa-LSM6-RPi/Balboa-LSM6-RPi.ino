// Balboa-LSM6-RPi, identical to BalboaRPiSlaveDemo.ino at present (12/20/19).
// This program is enabling the Balboa's 32U4 chip as an I2C slave, and the python
// script server.py for this program (different than server.py for
// BalboaRPiSlaveDemo.ino) will access the 32U4 and also the Balboa's LSM6
// accel/gyro, independently of the 32U4, via I2C. The goal of this development is to
// ultimately run the Balboa as a balancer from the RPi. The RPi will communicate
// the LSM6 gyro information to the 32U4 chip. The 32U4 chip cannot be both
// a master to the LSM6 chip and a slave to the RPi, hence this arrangement with the
// RPi controlling both the 32U4 and the LSM6.
// WESmith 12/20/19

#include <Servo.h>
#include <Balboa32U4.h>
#include <PololuRPiSlave.h>

/* This example program shows how to make the Balboa 32U4 balancing
 * robot into a Raspberry Pi I2C slave.  The RPi and Balboa can
 * exchange data bidirectionally, allowing each device to do what it
 * does best: high-level programming can be handled in a language such
 * as Python on the RPi, while the Balboa takes charge of motor
 * control, analog inputs, and other low-level I/O.
 *
 * The example and libraries are available for download at:
 *
 * https://github.com/pololu/pololu-rpi-slave-arduino-library
 *
 * You will need the corresponding Raspberry Pi code, which is
 * available in that repository under the pi/ subfolder.  The Pi code
 * sets up a simple Python-based web application as a control panel
 * for your Raspberry Pi robot.
 */

// Custom data structure that we will use for interpreting the buffer.
// We recommend keeping this under 64 bytes total.  If you change the
// data format, make sure to update the corresponding code in
// a_star.py on the Raspberry Pi.

struct Data
{
  bool yellow, green, red;
  bool buttonA, buttonB, buttonC;

  int16_t leftMotor, rightMotor;
  uint16_t batteryMillivolts;
  uint16_t analog[6];

  bool playNotes;
  char notes[14];

  int16_t leftEncoder, rightEncoder;
};

// set up template: PololuRPiSlave<class BufferType, unsigned int pi_delay_us>
// pi_delay_us was set to 5; WS increased to 20 for RPI 3b: that worked 12/13/19
PololuRPiSlave<struct Data, 20> slave; 

PololuBuzzer buzzer;
Balboa32U4Motors motors;
Balboa32U4ButtonA buttonA;
Balboa32U4ButtonB buttonB;
Balboa32U4ButtonC buttonC;
Balboa32U4Encoders encoders;

void setup()
{
  // Set up the slave at I2C address 20.
  slave.init(20);

  // Play startup sound.
  buzzer.play("v10>>g16>>>c16");
}

void loop()
{
  // Call updateBuffer() before using the buffer, to get the latest
  // data including recent master writes.
  slave.updateBuffer();

  // Write various values into the data structure.
  slave.buffer.buttonA = buttonA.isPressed();
  slave.buffer.buttonB = buttonB.isPressed();
  slave.buffer.buttonC = buttonC.isPressed();

  // Change this to readBatteryMillivoltsLV() for the LV model.
  slave.buffer.batteryMillivolts = readBatteryMillivolts();

  for(uint8_t i=0; i<6; i++)
  {
    slave.buffer.analog[i] = analogRead(i);
  }

  // READING the buffer is allowed before or after finalizeWrites().
  ledYellow(slave.buffer.yellow);
  ledGreen(slave.buffer.green);
  ledRed(slave.buffer.red);
  motors.setSpeeds(slave.buffer.leftMotor, slave.buffer.rightMotor);

  // Playing music involves both reading and writing, since we only
  // want to do it once.
  static bool startedPlaying = false;
  
  if(slave.buffer.playNotes && !startedPlaying)
  {
    buzzer.play(slave.buffer.notes);
    startedPlaying = true;
  }
  else if (startedPlaying && !buzzer.isPlaying())
  {
    slave.buffer.playNotes = false;
    startedPlaying = false;
  }

  slave.buffer.leftEncoder = encoders.getCountsLeft();
  slave.buffer.rightEncoder = encoders.getCountsRight();

  // When you are done WRITING, call finalizeWrites() to make modified
  // data available to I2C master.
  slave.finalizeWrites();
}