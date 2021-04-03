# AMG8833 thermal camera on an ILI9341 320x240 screen
# Michael Horne, based on Jan Goolsbey's code for Adafruit
# https://learn.adafruit.com/pygamer-thermal-camera-amg8833?view=all

import time
import board
import displayio
from simpleio import map_range

from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect

import adafruit_amg88xx
import adafruit_ili9341

from Colours import Colours

class ThermalCamera:
    # Helper functions
    def celsius_to_fahrenheit(self, deg_c=None):  # convert C to F; round to 1 degree C
        return round(((9 / 5) * deg_c) + 32)

    def fahrenheit_to_celsius(self, deg_f=None):  # convert F to C; round to 1 degree F
        return round((deg_f - 32) * (5 / 9))

    def __init__(self, width, height, i2c, display_bus, display):
        # The board's integral display size (as informed by product page adafru.it/1770)
        self.WIDTH = width
        self.HEIGHT = height
        self.ELEMENT_SIZE = self.WIDTH // 10  # Size of element_grid blocks in pixels
        self.i2c = i2c
        self.display = display
        self.colours = Colours()

        # Block colors for the thermal image grid
        self.element_colors = [
            self.colours.GRAY,
            self.colours.BLUE,
            self.colours.GREEN,
            self.colours.YELLOW,
            self.colours.ORANGE,
            self.colours.RED,
            self.colours.VIOLET,
            self.colours.WHITE
        ]

        # The image sensor's design-limited temperature range
        self.MIN_SENSOR_C = 0
        self.MAX_SENSOR_C = 80
        self.MIN_SENSOR_F = self.celsius_to_fahrenheit(self.MIN_SENSOR_C)
        self.MAX_SENSOR_F = self.celsius_to_fahrenheit(self.MAX_SENSOR_C)

        # Convert default alarm and min/max range values from config file
        self.MIN_RANGE_F =  60
        self.MAX_RANGE_F = 120
        self.MIN_RANGE_C = self.fahrenheit_to_celsius(self.MIN_RANGE_F)
        self.MAX_RANGE_C = self.fahrenheit_to_celsius(self.MAX_RANGE_F)

        # Define the sensor
        self.amg8833 = adafruit_amg88xx.AMG88XX(self.i2c)

    def element_grid(self, col0, row0):  # Determine display coordinates for column, row
        x = int(self.ELEMENT_SIZE * col0 + 30)  # x coord + margin
        y = int(self.ELEMENT_SIZE * row0 + 1)   # y coord + margin
        return x, y  # Return display coordinates

    def background(self):
        # PLEASE NOTE
        # This needs to be run before calling render

        # Define the group for the thermal display
        self.image_group = displayio.Group(max_size=77)

        # Create a black background color fill layer; image_group[0]
        color_bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = self.colours.BLACK
        background = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.image_group.append(background)

        # Define the foundational thermal image element layers; image_group[1:64]
        #   image_group[#]=(row * 8) + column
        for row in range(0, 8):
            for col in range(0, 8):
                pos_x, pos_y = self.element_grid(col, row)
                # outline is normally None and stroke is 0
                element = Rect(x=pos_x, y=pos_y, width=self.ELEMENT_SIZE, height=self.ELEMENT_SIZE,
                    fill=None, outline=None, stroke=0
                )
                self.image_group.append(element)

        self.display.show(self.image_group)

    def render(self):
        image = self.amg8833.pixels  # Get camera data list

        for row1 in range(0, 8):  # Parse camera data list and update display
            for col1 in range(0, 8):
                value = map_range(image[7 - row1][7 - col1],
                                  self.MIN_SENSOR_C, self.MAX_SENSOR_C,
                                  self.MIN_SENSOR_C, self.MAX_SENSOR_C)
                color_index = int(map_range(value, self.MIN_RANGE_C, self.MAX_RANGE_C, 0, 7))
                self.image_group[((row1 * 8) + col1) + 1].fill = self.element_colors[color_index]
