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

    reading = (1023.0 / reply) - 1.0
    read = 10000 / reading

    steinhart = read / 10000
    steinhart = math.log1p(steinhart)
    steinhart /= 3950
    steinhart += 1.0 / (25 + 273.15)
    steinhart = 1.0 / steinhart
    steinhart -= 273.15
    return steinhart

while True:
    print "ADC: " + str(read_celsius()) + " Degrees Celsius"

