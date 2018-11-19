import spidev
import time
import math
import bitstring

def read(adc_channel=0, spi_channel=0):
    spi = spidev.SpiDev()
    spi.open(0, spi_channel)
    spi.max_speed_hz = 1200000
    cmd = 128
    if adc_channel:
        cmd += 32
    reply_bytes = spi.xfer2([cmd, 0])
#    reply = ((reply_bytes[1] & 3) << 8) + reply_bytes[2]
    spi.close()
    return reply_bytes

while True:
    print "ADC: " + str(read())

