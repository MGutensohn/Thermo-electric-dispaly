import spidev
import time
import math
import bitstring

def read_celsius(adc_channel=0, spi_channel=0):
    spi = spidev.SpiDev()
    spi.open(0, spi_channel)
    spi.max_speed_hz = 1200000
    cmd = 128
    if adc_channel:
        cmd += 32
    reply_bytes = spi.xfer2([1, cmd, 0])
    reply = ((reply_bytes[1] & 3) << 8) + reply_bytes[2]
    spi.close()

    volts = (reply * 3.3) / 1024 #calculate the voltage
    ohms = ((1/volts)*3300)-1000 #calculate the ohms of the thermististor

    lnohm = math.log1p(ohms) #take ln(ohms)

    #a, b, & c values from http://www.thermistor.com/calculators.php
    #using curve R (-6.2%/C @ 25C) Mil Ratio X
    a =  0.002197222470870
    b =  0.000161097632222
    c =  0.000000125008328

    #Steinhart Hart Equation
    # T = 1/(a + b[ln(ohm)] + c[ln(ohm)]^3)

    t1 = (b*lnohm) # b[ln(ohm)]

    c2 = c*lnohm # c[ln(ohm)]

    t2 = math.pow(c2,3) # c[ln(ohm)]^3

    temp = 1/(a + t1 + t2) #calcualte temperature

    tempc = temp - 273.15 - 4 #K to C

    return tempc

while True:
    print "ADC: " + str(read_celsius()) + " Degrees Celsius"
    time.sleep(1)

