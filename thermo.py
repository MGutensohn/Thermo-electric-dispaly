#!/usr/bin/python
import logging
import logging.handlers
import argparse
import sys
import os
import time
import atexit

import spidev
import math
import threading

import socket

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

class LoggerHelper(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

def setup_logging():
    # Default logging settings
    LOG_FILE = "/var/log/TEDbtsrv.log"
    LOG_LEVEL = logging.INFO

    # Define and parse command line arguments
    argp = argparse.ArgumentParser(description="Thermo Electric Display Receiver")
    argp.add_argument("-l", "--log", help="log (default '" + LOG_FILE + "')")

    # Grab the log file from arguments
    args = argp.parse_args()
    if args.log:
        LOG_FILE = args.log

    # Setup the logger
    logger = logging.getLogger(__name__)
    # Set the log level
    logger.setLevel(LOG_LEVEL)
    # Make a rolling event log that resets at midnight and backs-up every 3 days
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE,
        when="midnight",
        backupCount=3)

    # Log messages should include time stamp and log level
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # Attach the formatter to the handler
    handler.setFormatter(formatter)
    # Attach the handler to the logger
    logger.addHandler(handler)

    # Replace stdout with logging to file at INFO level
    sys.stdout = LoggerHelper(logger, logging.INFO)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = LoggerHelper(logger, logging.ERROR)

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
motors = [mh.getMotor(1), mh.getMotor(2), mh.getMotor(3), mh.getMotor(4)]

# set the speed to start, from 0 (off) to 255 (max speed)
for motor in motors:
    motor.setSpeed(150)
    motor.run(Adafruit_MotorHAT.FORWARD);
    motor.run(Adafruit_MotorHAT.RELEASE);


#THERMAL READING CODE

max_temp_left = 37.0
max_temp_right = 37.0

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 500000

def read_celsius(adc_channel=0):
    if adc_channel == 0:
        cmd = 0b01100000
    else:
        cmd = 0b01110000
    reply_bytes = spi.xfer2([cmd, 0])
    reply = ((reply_bytes[0] & 3) << 8) + reply_bytes[1]

    volts = (reply * 3.3) / 1024 #calculate the voltage
    ohms = ((1/volts)*3300)-1000 #calculate the ohms of the thermististor

    lnohm = math.log1p(ohms) #take ln(ohms)

    a =  0.002197222470870
    b =  0.000161097632222
    c =  0.000000125008328

    t1 = (b*lnohm) # b[ln(ohm)]

    c2 = c*lnohm # c[ln(ohm)]

    t2 = math.pow(c2,3) # c[ln(ohm)]^3

    temp = 1/(a + t1 + t2) #calcualte temperature

    tempc = temp - 273.15 #K to C

    return tempc

def check_temp(hand):
    while True:
        if hand == 0:
            max = max_temp_left
        else:
            max = max_temp_right
        temp = read_celsius(hand)
        if temp >= max:
            motors[hand].run(Adafruit_MotorHAT.RELEASE)
            print "Exceeded " + str(max) + " *C"
            while True:
                if read_celsius(hand) < max - 1:
                    motors[hand].run(Adafruit_MotorHAT.BACKWARD)
                    motors[hand].setSpeed(255)
                    break
                time.sleep(0.5)


        time.sleep(0.5)


def set_temp (temp, hand=0):
    if temp == "hot":
        if hand == 0:
            max_temp_left = 37.0
        else:
            max_temp_right = 37.0
        motors[hand].run(Adafruit_MotorHAT.BACKWARD)
        motors[hand].setSpeed(255)
    elif temp == "warm":
        if hand == 0:
            max_temp_left = 35.0
        else:
            max_temp_right = 35.0
        motors[hand].run(Adafruit_MotorHAT.BACKWARD)
        motors[hand].setSpeed(127)
    elif temp == "cool":
        motors[hand].run(Adafruit_MotorHAT.FORWARD)
        motors[hand].setSpeed(127)
        motors[hand+2].run(Adafruit_MotorHAT.FORWARD)
        motors[hand+2].setSpeed(128)
    elif temp == "cold":
        motors[hand].run(Adafruit_MotorHAT.FORWARD)
        motors[hand].setSpeed(150)
        motors[hand+2].run(Adafruit_MotorHAT.FORWARD)
        motors[hand+2].setSpeed(128)
    else:
        motors[hand].run(Adafruit_MotorHAT.RELEASE)

def main():
    # Setup logging
    setup_logging()
    time.sleep(10)

    host = "192.168.7.2"
    port = 13000
    buffer_size = 1024

    temp_monitor_left = threading.Thread(target=check_temp, args=(0,))
    temp_monitor_right = threading.Thread(target=check_temp, args=(1,))

    temp_monitor_left.start()
    temp_monitor_right.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    setting = []
    while True:

        if len(setting) > 0:
            for motor in motors:
                motor.run(Adafruit_MotorHAT.RELEASE)
            set_temp(setting[0], 0)
            set_temp(setting[1], 1)
        print "listening on %s port: %s" % (host, port)
        try:
            # Read the data sent by the Unity
            data, addr = sock.recvfrom(buffer_size)
            if len(data) != 0:
                print "Received [%s]" % data
                setting = str(data).split(" ")
        except IOError:
            for motor in motors:
                motor.run(Adafruit_MotorHAT.RELEASE)
            pass

        except KeyboardInterrupt:
            for motor in motors:
                motor.run(Adafruit_MotorHAT.RELEASE)
            temp_monitor.join()
            sock.close()
            print "Server going down"
            break
main()
