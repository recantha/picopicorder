# 0x29 is the VL53L0X time-of-flight time_of_flight_sensor

import board
import busio
import adafruit_vl53l0x
import time

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
time_of_flight_sensor = adafruit_vl53l0x.VL53L0X(i2c, address=0x29)

while True:
	print('Range: {}mm'.format(time_of_flight_sensor.range))
	time.sleep(0.2)