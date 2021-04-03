# 0x10 is the VEML6075 sensor
import time
import board
import busio
import adafruit_veml6075

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
veml = adafruit_veml6075.VEML6075(i2c, integration_time=100)

while True:
    print(str(veml.uv_index) + ' ' +  str(veml.uva) + ' ' + str(veml.uvb))