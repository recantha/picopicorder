# 0x77 is the BME680 (with the trace cut to add 1 to the I2C address)

import time
import board
import busio
import adafruit_bme680
 
i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x77)

# Standard sea level pressure
bme680.seaLevelhPa = 1013
temperature_offset = -5

while True:
    print("\nTemperature: %0.1f C" % (bme680.temperature + temperature_offset))
    print("Gas: %d ohm" % bme680.gas)
    print("Humidity: %0.1f %%" % bme680.relative_humidity)
    print("Pressure: %0.3f hPa" % bme680.pressure)
    print("Altitude = %0.2f meters" % bme680.altitude)

    time.sleep(1)
