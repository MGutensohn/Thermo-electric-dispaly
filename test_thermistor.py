import spidev
import time
import math

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
    print "Channel " + str(adc_channel) + ": " + str(reply_bytes) + " reply: " + str(reply)

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

while True:
    print "ADC channel 0: " + str(read_celsius()) + " *C" + " channel 1: " + str(read_celsius(1)) + " *C"
    time.sleep(1)

