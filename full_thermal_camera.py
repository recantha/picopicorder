# AMG8833 thermal camera on an ILI9341 320x240 screen
# Michael Horne, based on Jan Goolsbey's code for Adafruit
# https://learn.adafruit.com/pygamer-thermal-camera-amg8833?view=all

import time
import board
import displayio
import busio
from simpleio import map_range
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
import adafruit_amg88xx
import adafruit_ili9341

# Helper functions
def celsius_to_fahrenheit(deg_c=None):  # convert C to F; round to 1 degree C
    return round(((9 / 5) * deg_c) + 32)

def fahrenheit_to_celsius(deg_f=None):  # convert F to C; round to 1 degree F
    return round((deg_f - 32) * (5 / 9))

def element_grid(col0, row0):  # Determine display coordinates for column, row
    x = int(ELEMENT_SIZE * col0 + 30)  # x coord + margin
    y = int(ELEMENT_SIZE * row0 + 1)   # y coord + margin
    return x, y  # Return display coordinates

def update_image_frame():  # Get camera data and display
    minimum = MAX_SENSOR_C  # Set minimum to sensor's maximum C value
    maximum = MIN_SENSOR_C  # Set maximum to sensor's minimum C value

    sum_bucket = 0  # Clear bucket for building average value

    for row1 in range(0, 8):  # Parse camera data list and update display
        for col1 in range(0, 8):
            value = map_range(image[7 - row1][7 - col1],
                              MIN_SENSOR_C, MAX_SENSOR_C,
                              MIN_SENSOR_C, MAX_SENSOR_C)
            color_index = int(map_range(value, MIN_RANGE_C, MAX_RANGE_C, 0, 7))
            image_group[((row1 * 8) + col1) + 1].fill = element_color[color_index]
            sum_bucket = sum_bucket + value  # Calculate sum for average
            minimum = min(value, minimum)
            maximum = max(value, maximum)
    return minimum, maximum, sum_bucket

# Establish I2C interface for the AMG8833 Thermal Camera
i2c_scl = board.GP1
i2c_sda = board.GP0
i2c = busio.I2C(i2c_scl, i2c_sda)
amg8833 = adafruit_amg88xx.AMG88XX(i2c)

# The image sensor's design-limited temperature range
MIN_SENSOR_C = 0
MAX_SENSOR_C = 80
MIN_SENSOR_F = celsius_to_fahrenheit(MIN_SENSOR_C)
MAX_SENSOR_F = celsius_to_fahrenheit(MAX_SENSOR_C)

# Convert default alarm and min/max range values from config file
MIN_RANGE_F =  60
MAX_RANGE_F = 120
MIN_RANGE_C = fahrenheit_to_celsius(MIN_RANGE_F)
MAX_RANGE_C = fahrenheit_to_celsius(MAX_RANGE_F)

# The board's integral display size (as informed by product page adafru.it/1770)
WIDTH  = 320
HEIGHT = 240

ELEMENT_SIZE = WIDTH // 10  # Size of element_grid blocks in pixels

# Define colors
BLACK   = 0x000000
RED     = 0xFF0000
ORANGE  = 0xFF8811
YELLOW  = 0xFFFF00
GREEN   = 0x00FF00
CYAN    = 0x00FFFF
BLUE    = 0x0000FF
VIOLET  = 0x9900FF
WHITE   = 0xFFFFFF
GRAY    = 0x444455

# Block colors for the thermal image grid
element_color = [GRAY, BLUE, GREEN, YELLOW, ORANGE, RED, VIOLET, WHITE]

# Tell displayio to clean up after any previous usage
displayio.release_displays()

# Define ILI9341 screen as an SPI-interfaced display
tft_cs = board.GP17
tft_dc = board.GP21
tft_res = board.GP20
spi_mosi = board.GP19
spi_clk = board.GP18
spi_miso = board.GP16

spi = busio.SPI(clock=spi_clk, MOSI=spi_mosi, MISO=spi_miso)

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=WIDTH, height=HEIGHT)

# Initially, just show a bright green background to prove the display is working
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

# Wait so it doesn't immediately get overwritten
time.sleep(1)

# Define the group for the thermal display
image_group = displayio.Group(max_size=77)
display.show(image_group)

# Create a black background color fill layer; image_group[0]
color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = BLACK
background = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
image_group.append(background)

# Define the foundational thermal image element layers; image_group[1:64]
#   image_group[#]=(row * 8) + column
for row in range(0, 8):
    for col in range(0, 8):
        pos_x, pos_y = element_grid(col, row)
        # outline is normally None and stroke is 0
        element = Rect(x=pos_x, y=pos_y, width=ELEMENT_SIZE, height=ELEMENT_SIZE, fill=None, outline=None, stroke=0)
        image_group.append(element)

# Main loop
while True:
    image = amg8833.pixels  # Get camera data list
    v_min, v_max, v_sum = update_image_frame()
