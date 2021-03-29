# 0x69 is the AMG8833
# 0x57 is the Pulse Oximeter

import time
import board
import busio
 
i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
 
while not i2c.try_lock():
    pass
 
try:
    while True:
        print("I2C addresses found:", [hex(device_address)
              for device_address in i2c.scan()])
        time.sleep(2)
 
finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
    i2c.unlock()