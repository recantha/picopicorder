# AMG8833 thermal camera on an ILI9341 320x240 screen
# Michael Horne, based on Jan Goolsbey's code for Adafruit
# https://learn.adafruit.com/pygamer-thermal-camera-amg8833?view=all
# https://learn.adafruit.com/improved-amg8833-pygamer-thermal-camera/circuitpython-code

import time
import displayio
import ulab
from time import sleep

from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect

import adafruit_amg88xx

from iron_spectrum import index_to_rgb

from Colours import Colours

class ThermalCamera:
    # Helper functions
    def celsius_to_fahrenheit(self, deg_c=None):  # convert C to F; round to 1 degree C
        return round(((9 / 5) * deg_c) + 32)

    def fahrenheit_to_celsius(self, deg_f=None):  # convert F to C; round to 1 degree F
        return round((deg_f - 32) * (5 / 9))

    def __init__(self, width, height, i2c, display_bus, display, reverse, font):
        # The board's integral display size (as informed by product page adafru.it/1770)
        self.WIDTH = width
        self.HEIGHT = height
        self.i2c = i2c
        self.display = display
        self.colours = Colours()
        self.reverse = reverse
        self.font = font

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

        # New stuff
        self.ALARM_F = 120
        self.ALARM_C = self.fahrenheit_to_celsius(self.ALARM_F)

        self.grid_size = 8
        self.sensor_data = ulab.array(range(self.grid_size * self.grid_size)).reshape((self.grid_size, self.grid_size))  # Color index narray
        self.grid_data = ulab.zeros(((2 * self.grid_size) - 1, (2 * self.grid_size) - 1))  # 15x15 color index narray
        #self.histogram = ulab.zeros((2 * self.grid_size) - 1)  # Histogram accumulation narray

        self.GRID_AXIS = (2 * self.grid_size) - 1  # Number of cells along the grid x or y axis
        self.GRID_SIZE = self.HEIGHT  # Maximum number of pixels for a square grid
        self.GRID_X_OFFSET = self.WIDTH - self.GRID_SIZE  # Right-align grid with display boundary
        self.CELL_SIZE = self.GRID_SIZE // self.GRID_AXIS  # Size of a grid cell in pixels

        self.PALETTE_SIZE = 100  # Number of colors in spectral palette (must be > 0)

        self.param_colors = [("ALARM", self.colours.WHITE), ("RANGE", self.colours.RED), ("RANGE", self.colours.CYAN)]

        # Define the sensor
        self.amg8833 = adafruit_amg88xx.AMG88XX(self.i2c)

    def spectrum(self):  # Load a test spectrum into the grid_data array
        for row in range(0, self.GRID_AXIS):
            for col in range(0, self.GRID_AXIS):
                self.grid_data[row][col] = ((row * self.GRID_AXIS) + col) * 1 / 235
        return

    def update_image_frame(self):  # Get camera data and update display
        for row in range(0, self.GRID_AXIS):
            for col in range(0, self.GRID_AXIS):
                color_index = self.grid_data[self.GRID_AXIS - 1 - row][self.GRID_AXIS - 1 - col]
                color = index_to_rgb(round(color_index * self.PALETTE_SIZE, 0) / self.PALETTE_SIZE)
                if color != self.image_group[((row * self.GRID_AXIS) + col)].fill:
                    self.image_group[((row * self.GRID_AXIS) + col)].fill = color
        return

    def ulab_bilinear_interpolation(self):  # 2x bilinear interpolation
        # Upscale sensor data array; by @v923z and @David.Glaude
        self.grid_data[1::2, ::2] = self.sensor_data[:-1, :]
        self.grid_data[1::2, ::2] += self.sensor_data[1:, :]
        self.grid_data[1::2, ::2] /= 2
        self.grid_data[::, 1::2] = self.grid_data[::, :-1:2]
        self.grid_data[::, 1::2] += self.grid_data[::, 2::2]
        self.grid_data[::, 1::2] /= 2

        return

    def background(self):
        try:
            # ### Define the display group ###
            self.image_group = displayio.Group(scale=1)

            # Define the foundational thermal image grid cells; image_group[0:224]
            #   image_group[#] = image_group[ (row * GRID_AXIS) + column ]
            for row in range(0, self.GRID_AXIS):
                for col in range(0, self.GRID_AXIS):
                    cell_x = (col * self.CELL_SIZE) + self.GRID_X_OFFSET
                    cell_y = row * self.CELL_SIZE
                    cell = Rect(
                        x=cell_x,
                        y=cell_y,
                        width=self.CELL_SIZE,
                        height=self.CELL_SIZE,
                        fill=None,
                        outline=None,
                        stroke=0,
                    )
                    self.image_group.append(cell)

            # ###--- PRIMARY PROCESS SETUP ---###
            self.display_image = True
            self.orig_max_range_f = 0  # Establish temporary range variables
            self.orig_min_range_f = 0

            # Activate display
            self.display.show(self.image_group)

        except Exception as err:
            print("Error in background()")
            print(str(err))

            while True:
                pass

    def render(self):
        try:
            reverse = True

            sensor = self.amg8833.pixels  # Get sensor_data data

            # This clever bit of code, taken from https://thispointer.com/python-reverse-a-list-sub-list-or-list-of-list-in-place-or-copy/
            # reverses the lists-of-lists along both "axis" if you want to think of it like that
            # Useful if your render is "upside down and back-to-front"!
            if reverse:
                sensor = [elem[::-1] for elem in sensor][::-1]

            self.sensor_data = ulab.array(sensor)  # Copy to narray

            for row in range(0, 8):
                for col in range(0, 8):
                    self.sensor_data[col, row] = min(max(self.sensor_data[col, row], 0), 80)

            # Normalize temperature to index values and interpolate
            self.sensor_data = (self.sensor_data - self.MIN_RANGE_C) / (self.MAX_RANGE_C - self.MIN_RANGE_C)
            self.grid_data[::2, ::2] = self.sensor_data  # Copy sensor data to the grid array

            self.ulab_bilinear_interpolation()  # Interpolate to produce 15x15 result

            # Display image or histogram
            self.update_image_frame()

        except Exception as err:
            print("Error in render()")
            print(str(err))

            while True:
                pass
