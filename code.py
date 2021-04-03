import board
import displayio
import busio
import sys
import terminalio
from simpleio import map_range

import adafruit_ili9341 # Big screen
import adafruit_amg88xx
import adafruit_stmpe610

import adafruit_imageload
from adafruit_display_text import label
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

import time
from Colours import Colours

#import i2c_scanner

from PicoPicorder import Picorder

# First of all, unlock the pins and buses related to the display(s)
displayio.release_displays()
picorder = Picorder(
    spi_clock=board.GP18,
    spi_mosi=board.GP19,
    spi_miso=board.GP16,
    i2c_scl=board.GP1,
    i2c_sda=board.GP0,
    dsp_command=board.GP21,
    dsp_chip_select=board.GP17,
    dsp_reset=board.GP20
)

# Test the display
#picorder.displayBackground(picorder.colours.PURPLE)
#picorder.displayText(10, 10, "Hello world", picorder.colours.RED)
#time.sleep(1)

picorder.displayLCARS()
picorder.lcarsLabels(1)

mode = 0
while True:
    try:
        touch_x, touch_y, pressure = picorder.touch_screen.read_data()
        if picorder.touch_screen.touched:
            # When a touch is detected, we switch modes and do any 'set-up' required to go INTO the mode
            if mode != 1 and (touch_x < 600 and touch_y > 3400):
                print("Change to mode 1")
                mode = 1
                picorder.thermal_camera.background()

            elif mode != 0 and (touch_x < 800 and touch_y < 800):
                print("Change to mode 0")
                mode = 0
                picorder.displayLCARS()

            else:
                print(str(mode) + " X:" + str(touch_x) + " / Y:" + str(touch_y))

            #print(str(touch_x) + " " + str(touch_y) + " / " + str(stmpe610.buffer_size))

    except KeyboardInterrupt:
        sys.exit(1)

    except Exception as err:
        # Ignore all other errors except CTRL-C
        print(str(err))
        pass

    if mode == 0:
        # display the LCARS interface
        pass

    elif mode == 1:
        picorder.thermal_camera.render()


import busio
import board
import digitalio
from adafruit_stmpe610 import Adafruit_STMPE610_SPI

print("Go Ahead... Touch my Screen!")


temperature_label.text = "Hello world"


while True:
    try:
        if stmpe610.touched and not stmpe610.buffer_empty:
            touch_x, touch_y, pressure = stmpe610.read_data()

            if touch_x < 600 and touch_y > 3400:
                print("Touch top left")

            #print(str(touch_x) + " " + str(touch_y) + " / " + str(stmpe610.buffer_size))

    except KeyboardInterrupt:
        sys.exit(1)

    except Exception as err:
        # Ignore all other errors except CTRL-C
        pass

#time.sleep(2)

#thermal_image_group = displayio.Group(max_size=77)
#main_screen.show(thermal_image_group)
#displayBackground(thermal_image_group, colours.BLACK)

# Define the foundational thermal image element layers; image_group[1:64]
#   image_group[#]=(row * 8) + column
'''
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
'''