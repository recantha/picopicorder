# 0x76 is the BMP280

import time
import board
import busio
import adafruit_bmp280
 
i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

bmp280.sea_level_pressure = 1013.25

while True:
    print("\nTemperature: %0.1f C" % bmp280.temperature)
    print("Pressure: %0.1f hPa" % bmp280.pressure)
    print("Altitude = %0.2f meters" % bmp280.altitude)
    time.sleep(2)