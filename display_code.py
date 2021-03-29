# Adapted from WildestPixel's Gist: https://gist.github.com/wildestpixel/86ac1063bc456213f92972fcd7c7c2e1
# which was itself adapted from http://helloraspberrypi.blogspot.com/2021/01/raspberry-pi-picocircuitpython-st7789.html
# VEML6075 section from https://learn.adafruit.com/adafruit-veml6075-uva-uvb-uv-index-sensor/overview

import os
import board
import time
import terminalio
import busio
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import adafruit_st7789
import adafruit_veml6075
import adafruit_bme680
#import adafruit_is31fl3731
from adafruit_is31fl3731.matrix_11x7 import Matrix11x7 as Display
import adafruit_framebuf
from adafruit_display_text import label
import displayio
import adafruit_ili9341
import adafruit_amg88xx


#print("==============================")
#print(os.uname())
#print("Hello Raspberry Pi Pico/CircuitPython ST7789 SPI IPS Display")
#print(adafruit_st7789.__name__ + " version: " + adafruit_st7789.__version__)
#print()

displayio.release_displays()

tft_cs = board.GP17
tft_dc = board.GP21
tft_res = board.GP20
spi_mosi = board.GP19
spi_clk = board.GP18
spi_miso = board.GP16

spi = busio.SPI(clock=spi_clk, MOSI=spi_mosi, MISO=spi_miso)

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

splash = displayio.Group(max_size=10)
display.show(splash)

color_bitmap = displayio.Bitmap(320, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00  # Bright Green

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)

splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(280, 200, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0xAA0088  # Purple
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=20, y=20)
splash.append(inner_sprite)

# Draw a label
text_group = displayio.Group(max_size=10, scale=3, x=57, y=120)
text = "Hello world!"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

print("Finished")




while True:
    pass


"""
# I2C scan
i2c = busio.I2C(scl=board.GP21, sda=board.GP20)
display = Display(i2c)

def scrollText(buf, fb, display, text_to_show):
    frame = 0

    for i in range(len(text_to_show) * 9):
        fb.fill(0)
        fb.text(text_to_show, -i + display.width, 0, color=1)

        display.frame(frame, show=False)
        display.fill(0)

        for x in range(display.width):
            bite = buf[x]
            for y in range(display.height):
                bit = 1 << y & bite
                if bit:
                    display.pixel(x, y, 50)

        display.frame(frame, show=True)
        frame = 0 if frame else 1


buf = bytearray(32)  # 2 bytes tall x 16 wide = 32 bytes (9 bits is 2 bytes)
fb = adafruit_framebuf.FrameBuffer(
    buf, display.width, display.height, adafruit_framebuf.MVLSB
)

while True:
    scrollText(buf, fb, display, "Hello world")
    pass


while True:
    for y in range(7):
        for x in range(11):
            display.pixel(x, y, 100)
            time.sleep(0.1)
            display.fill(0)

while not i2c.try_lock():
    pass

print("I2C addresses found:", [hex(device_address) for device_address in i2c.scan()])
i2c.unlock()

display = adafruit_is31fl3731.Matrix11x7(i2c)



print("Finished")




displayio.release_displays()

tft_cs = board.GP17
tft_dc = board.GP16
#tft_res = board.GP30
spi_mosi = board.GP19
spi_clk = board.GP18

spi = busio.SPI(spi_clk, MOSI=spi_mosi)

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_st7789.ST7789(display_bus, width=135, height=240, rowstart=40, colstart=53)
display.rotation = 180

splash = displayio.Group(max_size=10)
display.show(splash)

color_bitmap = displayio.Bitmap(135, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFF0000

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

print("Done splash")



# VEML6075
veml = adafruit_veml6075.VEML6075(i2c, integration_time=100)

print("UV index:", veml.uv_index)
print("UVA:", veml.uva)
print("UVB:", veml.uvb)
print("IT:", veml.integration_time)

# BME680 - Air Quality sensor
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x76)
print('Temperature: {} degrees C'.format(bme680.temperature))
print('Gas: {} ohms'.format(bme680.gas))
print('Humidity: {}%'.format(bme680.humidity))
print('Pressure: {}hPa'.format(bme680.pressure))

'''
REGISTERS = (0, 256)
REGISTER_SIZE = 2

while not i2c.try_lock():
    pass

result = bytearray(REGISTER_SIZE)
for register in range(*REGISTERS):
    try:
        i2c.writeto(0xf, bytes([register]))
        i2c.readfrom_into(0xf, result)
    except OSError:
        continue  # Ignore registers that don't exist!
    print('Address {0}: {1}'.format(hex(register), ' '.join([hex(x) for x in result])))

i2c.unlock()
'''
'''
rotary = I2CDevice(i2c, 0xf)
with rotary:
    rotary.write(bytes([0x05]), end=False)
    result = bytearray(2)
    rotary.readinto(result)
    print(result)
'''

# Release any resources currently in use for the displays
displayio.release_displays()

tft_cs = board.GP17
tft_dc = board.GP21
#tft_res = board.GP20
spi_mosi = board.GP19
spi_clk = board.GP18

spi = busio.SPI(spi_clk, MOSI=spi_mosi)

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_st7789.ST7789(display_bus, width=135, height=240, rowstart=40, colstart=53)
display.rotation = 180

# Make the display context
splash = displayio.Group(max_size=10)
display.show(splash)

color_bitmap = displayio.Bitmap(135, 240, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00

bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(133, 238, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x0000FF
inner_sprite = displayio.TileGrid(inner_bitmap,
                                  pixel_shader=inner_palette, x=1, y=1)
splash.append(inner_sprite)

# Draw a label
text_group1 = displayio.Group(max_size=10, scale=1, x=20, y=40)
text1 = "wildestpixel"
text_area1 = label.Label(terminalio.FONT, text=text1, color=0xFF0000)
text_group1.append(text_area1)  # Subgroup for text scaling
# Draw a label
text_group2 = displayio.Group(max_size=10, scale=1, x=20, y=60)
text2 = "CircuitPython"
text_area2 = label.Label(terminalio.FONT, text=text2, color=0xFFFFFF)
text_group2.append(text_area2)  # Subgroup for text scaling

# Draw a label
text_group3 = displayio.Group(max_size=10, scale=1, x=20, y=100)
text3 = adafruit_st7789.__name__
text_area3 = label.Label(terminalio.FONT, text=text3, color=0x0000000)
text_group3.append(text_area3)  # Subgroup for text scaling
# Draw a label
text_group4 = displayio.Group(max_size=10, scale=2, x=20, y=120)
text4 = adafruit_st7789.__version__
text_area4 = label.Label(terminalio.FONT, text=text4, color=0x000000)
text_group4.append(text_area4)  # Subgroup for text scaling

splash.append(text_group1)
splash.append(text_group2)
splash.append(text_group3)
splash.append(text_group4)

time.sleep(3.0)

rot = 0
while True:
    time.sleep(5.0)
#    rot = rot + 90
#    if (rot>=360):
#        rot =0
#    display.rotation = rot
"""