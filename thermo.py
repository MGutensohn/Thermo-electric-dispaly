#!/usr/bin/python
import logging
import logging.handlers
import argparse
import sys
import os
import time
import atexit

from bluetooth import *
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
    argp = argparse.ArgumentParser(description="Raspberry PI Bluetooth Server")
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

def main():
    # Setup logging
    setup_logging()

    # We need to wait until Bluetooth init is done
    time.sleep(10)

    # Make device visible
    os.system("hciconfig hci0 piscan")

    # Create a new server socket using RFCOMM protocol
    sock = BluetoothSocket(RFCOMM)
    # # Bind to any port
    # server_sock.bind(("", PORT_ANY))
    # # Start listening
    # server_sock.listen(1)

    # Get the port the server socket is listening
    # port = server_sock.getsockname()[1]

    # The service UUID to advertise
    uuid = "f8a8bae3-3eba-493f-89e9-c221964b449b"
    # Start advertising the service
    # advertise_service(server_sock, "TEDBtSrv",
    #                    service_id=uuid,
    #                    service_classes=[uuid, SERIAL_PORT_CLASS],
    #                    profiles=[SERIAL_PORT_PROFILE])
    
    while True:
        # print "Waiting for connection on RFCOMM channel %d" % port

        service_matches = find_service( uuid = uuid )

        if len(service_matches) == 0:
            continue
        first_match = service_matches[0]

        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]

        print "connecting to \"%s\" on %s" % (name, host)
        try:
            sock = None

            # This will block until we get a new connection
            # client_sock, client_info = server_sock.accept()
            # print "Accepted connection from ", client_info

            sock.connect((host, port))

            # Read the data sent by the client
            data = sock.recv(1024)
            if len(data) == 0:
                break
            else:
                print "Received [%s]" % data

                setting = str(data).split(" ")

                for i in range(4):
                    if setting[i] == "hot":
                        motors[i].run(Adafruit_MotorHAT.BACKWARD)
                        motors[i].setSpeed(160)
                        time.sleep(0.1)
                        motors[i].run(Adafruit_MotorHAT.RELEASE)
                        time.sleep(0.5)
                    elif setting[i] == "warm":
                        motors[i].run(Adafruit_MotorHAT.BACKWARD)
                        motors[i].setSpeed(100)
                        time.sleep(0.1)
                        motors[i].run(Adafruit_MotorHAT.RELEASE)
                        time.sleep(1)
                    elif setting[i] == "cool":
                        motors[i].run(Adafruit_MotorHAT.FORWARD)
                        motors[i].setSpeed(127)
                    elif setting[i] == "cold":
                        motors[i].run(Adafruit_MotorHAT.FORWARD)
                        motors[i].setSpeed(255)
                    else:
                        motors[i].run(Adafruit_MotorHAT.RELEASE)
                setting = []  

                client_sock.send("Received")

                          
        except IOError:
            for motor in motors:
                    motor.run(Adafruit_MotorHAT.RELEASE)
            pass

        except KeyboardInterrupt:

            if client_sock is not None:
                client_sock.close()

            server_sock.close()

            print "Server going down"
            break

main()
