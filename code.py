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
    dsp_reset=board.GP20,
    i2s_clock=board.GP10,
    i2s_word=board.GP11,
    i2s_data=board.GP9,
    uart_tx=board.GP4,
    uart_rx=board.GP5
)

# Disable/enable touchscreen funcationality
touch_screen_enabled = False

# Initial mode
mode = 0

picorder.displayLCARS("atmos")
picorder.lcarsLabels("atmos")

print("Ready for input")

while True:
    try:
        if touch_screen_enabled:
            try:
                touch_x, touch_y, pressure = picorder.touch_screen.read_data()
                #print(str(touch_x) + ' ' + str(touch_y) + ' ' + str(pressure))

                if picorder.touch_screen.touched:
                    # When a touch is detected, we switch modes and do any 'set-up' required to go INTO the mode
                    if mode != 1 and (touch_x < 800 and touch_y > 3400):
                        mode = 1
                        picorder.playSound("snd_control_beep")
                        picorder.thermal_camera.background()

                    elif mode != 0 and (touch_x < 800 and touch_y < 800):
                        mode = 0
                        picorder.playSound("snd_engage_beep")
                        picorder.lcarsLabels("atmos")
                        picorder.displayLCARS("atmos")

                    elif mode !=2 and (touch_x > 2900 and touch_y > 3500):
                        mode = 2
                        picorder.playSound("snd_control_beep")
                        picorder.lcarsLabels("gps")
                        picorder.displayLCARS("gps")

                    else:
                        picorder.playSound("snd_tricorder")
                        print(str(mode) + " X:" + str(touch_x) + " / Y:" + str(touch_y))

            except Exception as err:
                print(str(err))
                pass

        else:
            pass

        if mode == 0:
            # display the LCARS interface
            picorder.displayLCARSreadings("atmos")

            if not picorder.button.value:
                #print("Change to 1")
                picorder.thermal_camera.background()
                mode = 1

        elif mode == 1:
            picorder.thermal_camera.render()

            if not picorder.button.value:
                #print("Change to 2")
                mode = 2
                picorder.displayLCARS("gps")
                picorder.lcarsLabels("gps")

        elif mode == 2:
            picorder.displayLCARSreadings("gps")

            if not picorder.button.value:
                #print("Change to 0")
                mode = 0
                picorder.displayLCARS("atmos")
                picorder.lcarsLabels("atmos")

    except KeyboardInterrupt:
        sys.exit(1)

    except Exception as err:
        # Ignore all other errors except CTRL-C
        print(str(err))

