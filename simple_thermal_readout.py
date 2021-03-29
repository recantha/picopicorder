import os
import time
import board
import displayio
import busio
import adafruit_amg88xx
import adafruit_ili9341

i2c_scl = board.GP1
i2c_sda = board.GP0
i2c = busio.I2C(i2c_scl, i2c_sda)
amg = adafruit_amg88xx.AMG88XX(i2c)

while True:
    for row in amg.pixels:
        print(['{0:.1f}'.format(temp) for temp in row])
        print("")
    print("\n")
    time.sleep(1)


