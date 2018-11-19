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

    volts = (reply * 3.3) /1024
    ohms = ((1/volts) * 3300)-1000
    lnohms = math.log1p(ohms)

    a = 0.002197222470870
    b = 0.000161097632222
    c = 0.000000125008328

    t1 = (b*lnohms)
    c2 = c*lnohms
    t2 = math.pow(c2,3)

    kelvin = 1/(a + t1 + t2)
    celsius = kelvin - 273.15 - 4
    return celsius

while True:
    print "ADC: " + str(read_celsius()) + "Degrees Celsius"

