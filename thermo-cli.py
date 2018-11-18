#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

import sys
import time
import atexit

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

################################# DC motor test!
myMotor = mh.getMotor(1)

# set the speed to start, from 0 (off) to 255 (max speed)
myMotor.setSpeed(150)
myMotor.run(Adafruit_MotorHAT.FORWARD);
# turn on motor
myMotor.run(Adafruit_MotorHAT.RELEASE);

while True:
    if sys.argv[1] == "hot":
        myMotor.run(Adafruit_MotorHAT.BACKWARD)
        myMotor.setSpeed(int(sys.argv[2]))
        time.sleep(0.5)
        myMotor.run(Adafruit_MotorHAT.RELEASE);
    elif sys.argv[1] == "cold":
        myMotor.run(Adafruit_MotorHAT.FORWARD)
        myMotor.setSpeed(int(sys.argv[2]))
