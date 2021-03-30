import board
import displayio
import busio
import terminalio
from simpleio import map_range

import adafruit_ili9341 # Big screen
import adafruit_amg88xx
from adafruit_display_text import label
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect

import time
from Colours import Colours

# Functions for controlling the screen directly
def displayBackground(image_group, colour):
    color_bitmap = displayio.Bitmap(320, 240, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = colour
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    image_group.append(bg_sprite)

def displayText(x, y, text_to_display, colour):
    # Draw a label
    text_group = displayio.Group(max_size=10, scale=1, x=x, y=y)
    text_area = label.Label(terminalio.FONT, text=text_to_display, color=colour)
    text_group.append(text_area)  # Subgroup for text scaling
    splash.append(text_group)

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

    for row in range(0, 8):  # Parse camera data list and update display
        for col in range(0, 8):
            value = map_range(image[7 - row][7 - col],
                              MIN_SENSOR_C, MAX_SENSOR_C,
                              MIN_SENSOR_C, MAX_SENSOR_C)
            color_index = int(map_range(value, MIN_RANGE_C, MAX_RANGE_C, 0, 7))
            thermal_image_group[((row * 8) + col) + 1].fill = element_color[color_index]
            sum_bucket = sum_bucket + value  # Calculate sum for average
            minimum = min(value, minimum)
            maximum = max(value, maximum)

    return minimum, maximum, sum_bucket

# First of all, unlock the pins and buses related to the display(s)
displayio.release_displays()

# Create your bus objects
spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16)
i2c = busio.I2C(board.GP1, board.GP0)

# Create objects for display
display_bus = displayio.FourWire(spi, command=board.GP21, chip_select=board.GP17, reset=board.GP20)
main_screen = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
splash = displayio.Group(max_size=10)
main_screen.show(splash)

# Create colours object
colours = Colours()

##################
# THERMAL SENSOR #
##################
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

# Block colors for the thermal image grid
element_color = [
    colours.GRAY, colours.BLUE, colours.GREEN, colours.YELLOW, colours.ORANGE, colours.RED, colours.VIOLET, colours.WHITE
]


# Main calls
displayBackground(splash, colours.GREEN)
displayText(0, 5, "Hello world", colours.BLACK)

time.sleep(2)

thermal_image_group = displayio.Group(max_size=77)
main_screen.show(thermal_image_group)

displayBackground(thermal_image_group, colours.BLACK)

# Define the foundational thermal image element layers; image_group[1:64]
#   image_group[#]=(row * 8) + column
for row in range(0, 8):
    for col in range(0, 8):
        pos_x, pos_y = element_grid(col, row)
        # outline is normally None and stroke is 0
        element = Rect(x=pos_x, y=pos_y, width=ELEMENT_SIZE, height=ELEMENT_SIZE, fill=None, outline=None, stroke=0)
        thermal_image_group.append(element)

run_mode = 0
while True:
    if run_mode == 0:
        image = amg8833.pixels  # Get camera data list
        v_min, v_max, v_sum = update_image_frame()