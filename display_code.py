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

