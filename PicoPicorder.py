# Sys imports
import board
import displayio
import busio
import terminalio

# Display imports
import adafruit_imageload
from adafruit_display_text import label
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label

# Component imports
import adafruit_ili9341 # Big screen
import adafruit_stmpe610 # Touch screen

# Instance imports
from Colours import Colours
from ThermalCamera import ThermalCamera

class Picorder:
    WIDTH = 320
    HEIGHT = 240

    def __init__(self, spi_clock, spi_mosi, spi_miso, i2c_scl, i2c_sda, dsp_command, dsp_chip_select, dsp_reset):
        # Create your bus objects
        self.spi = busio.SPI(clock=spi_clock, MOSI=spi_mosi, MISO=spi_miso)
        self.i2c = busio.I2C(scl=i2c_scl, sda=i2c_sda)

        self.colours = Colours()

        # Create objects for display
        self.display_bus = displayio.FourWire(self.spi, command=dsp_command, chip_select=dsp_chip_select, reset=dsp_reset)
        self.main_screen = adafruit_ili9341.ILI9341(self.display_bus, width=self.WIDTH, height=self.HEIGHT)
        self.touch_screen = adafruit_stmpe610.Adafruit_STMPE610_I2C(self.i2c, address=0x41)

        self.splash = displayio.Group(max_size=10)
        self.main_screen.show(self.splash)

        self.thermal_camera = ThermalCamera(width=self.WIDTH, height=self.HEIGHT, i2c=self.i2c, display_bus=self.display_bus, display=self.main_screen)

        self.okuda_font = bitmap_font.load_font("fonts/okuda.bdf")
        self.setupLCARS()

    def displayBackground(self, colour):
        color_bitmap = displayio.Bitmap(320, 240, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = colour
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.splash.append(bg_sprite)

    def displayText(self, x, y, text_to_display, colour):
        # Draw a label
        text_group = displayio.Group(max_size=10, scale=1, x=x, y=y)
        text_area = label.Label(terminalio.FONT, text=text_to_display, color=colour)
        text_group.append(text_area)  # Subgroup for text scaling
        self.splash.append(text_group)

    def setupLCARS(self):
        self.lcars = displayio.Group(max_size=9)
        image, palette = adafruit_imageload.load("img/picorder_graphic_dec.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)
        self.lcars_grid = displayio.TileGrid(image, pixel_shader=palette)
        self.lcars.append(self.lcars_grid)

        row_offset = 36
        first_row_y = 58

        self.lcars_label_1 = label.Label(self.okuda_font, x=48, y=first_row_y, max_glyphs=32, color=0)
        self.lcars.append(self.lcars_label_1)

        self.lcars_label_2 = label.Label(self.okuda_font, x=48, y=first_row_y+(1*row_offset), max_glyphs=32, color=0)
        self.lcars.append(self.lcars_label_2)

        self.lcars_label_3 = label.Label(self.okuda_font, x=48, y=first_row_y+(2*row_offset), max_glyphs=32, color=0)
        self.lcars.append(self.lcars_label_3)

        self.lcars_label_4 = label.Label(self.okuda_font, x=48, y=first_row_y+(3*row_offset), max_glyphs=32, color=0)
        self.lcars.append(self.lcars_label_4)

        self.lcars_label_5 = label.Label(self.okuda_font, x=48, y=first_row_y+(4*row_offset), max_glyphs=32, color=0)
        self.lcars.append(self.lcars_label_5)

    def displayLCARS(self):
        self.main_screen.show(self.lcars)

    def lcarsDisplayText(self, label_field_name=None, label_field_text=None, value_field_name=None, value_field_text=None):
        if label_field_text != None:
            if label_field_name == "label_1":
                self.lcars_label_1.text = label_field_text
            elif label_field_name == "label_2":
                self.lcars_label_2.text = label_field_text
            elif label_field_name == "label_3":
                self.lcars_label_3.text = label_field_text
            elif label_field_name == "label_4":
                self.lcars_label_4.text = label_field_text
            elif label_field_name == "label_5":
                self.lcars_label_5.text = label_field_text

    def lcarsLabels(self, screen_number):
        if screen_number == 1:
            self.lcarsDisplayText(label_field_name="label_1", label_field_text="TEMPERATURE")
            self.lcarsDisplayText(label_field_name="label_2", label_field_text="AIR QUALITY")
            self.lcarsDisplayText(label_field_name="label_3", label_field_text="UVA")
            self.lcarsDisplayText(label_field_name="label_4", label_field_text="UVB")
            self.lcarsDisplayText(label_field_name="label_5", label_field_text="PRESSURE")
