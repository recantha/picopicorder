# Sys imports
import board
import displayio
import busio
import terminalio
from digitalio import DigitalInOut, Direction, Pull
import time
import gc

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
import adafruit_bme680
import adafruit_veml6075
import adafruit_gps

# Instance imports
from Colours import Colours
from ThermalCamera import ThermalCamera
from Matrix import Matrix

sounds_enabled = False
if sounds_enabled:
    import audiocore
    import audiobusio


class Picorder:
    WIDTH = 320
    HEIGHT = 240
    SEA_LEVEL_NORMAL = 1013

    def __init__(self, spi_clock, spi_mosi, spi_miso, i2c_scl, i2c_sda, dsp_command, dsp_chip_select, dsp_reset,
        i2s_clock, i2s_word, i2s_data,
        uart_tx, uart_rx
    ):
        # Turn on the Pico's on-board LED
        print("Setting up power blinky")
        self.setupPowerBlinky()
        time.sleep(1)
        print("Done power blinky")

        try:
            # Create your bus objects
            self.spi = busio.SPI(clock=spi_clock, MOSI=spi_mosi, MISO=spi_miso)
            self.display_bus = displayio.FourWire(self.spi, command=dsp_command, chip_select=dsp_chip_select, reset=dsp_reset)
            self.main_screen = adafruit_ili9341.ILI9341(self.display_bus, width=self.WIDTH, height=self.HEIGHT)

            self.i2c = busio.I2C(scl=i2c_scl, sda=i2c_sda)
            self.uart = busio.UART(tx=uart_tx, rx=uart_rx, baudrate=9600, timeout=10)

            if sounds_enabled:
                self.i2s = audiobusio.I2SOut(bit_clock=i2s_clock, word_select=i2s_word, data=i2s_data)

            self.colours = Colours()

            # Create objects for display
            self.setupBlinkies()
            self.setupButtons()

            try:
                self.touch_screen = adafruit_stmpe610.Adafruit_STMPE610_I2C(self.i2c, address=0x41)

            except Exception as err:
                self.led.value = False
                print("No touch screen could be enabled")

            #self.splash = displayio.Group(max_size=10)
            #self.main_screen.show(self.splash)

            # Define sensor devices
            self.thermal_camera = ThermalCamera(width=self.WIDTH, height=self.HEIGHT, i2c=self.i2c, display_bus=self.display_bus, display=self.main_screen)
            self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(self.i2c, address=0x77)
            self.bme680.seaLevelhPa = self.SEA_LEVEL_NORMAL
            self.veml = adafruit_veml6075.VEML6075(self.i2c, integration_time=100)
            self.gps = adafruit_gps.GPS(self.uart, debug=False)
            self.matrix = Matrix(i2c=self.i2c)

            self.okuda_font = bitmap_font.load_font("fonts/okuda.pcf")
            self.okuda_font.load_glyphs(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 %.')

            self.loadSounds()
            self.setupGPS()
            self.setupLCARS()

        except Exception as err:
            self.blinkError(err)
            time.sleep(2)

    def displayText(self, x, y, text_to_display, colour):
        # Draw a label
        text_group = displayio.Group(max_size=10, scale=1, x=x, y=y)
        text_area = label.Label(terminalio.FONT, text=text_to_display, color=colour)
        text_group.append(text_area)  # Subgroup for text scaling
        self.splash.append(text_group)

    def setupLCARS(self):
        try:
            self.lcars = displayio.Group(max_size=10)

            lcars_image, lcars_palette = adafruit_imageload.load("img/picorder_graphic_dec.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

            self.lcars_grid = displayio.TileGrid(lcars_image, pixel_shader=lcars_palette)
            self.lcars.append(self.lcars_grid)

            # Define positions
            row_offset = 37
            first_row_y = 58
            x_value_for_labels = 48
            x_value_for_values = 222
            y_value = first_row_y

            # Define label space
            self.lcars_labels = {}

            # 5 spaces for labels and values
            for i in range(1,6):
                # Each label
                self.lcars_labels['label_' + str(i)] = label.Label(self.okuda_font, x=x_value_for_labels, y=y_value, max_glyphs=32, color=0)
                self.lcars.append(self.lcars_labels['label_' + str(i)])

                # Each value
                self.lcars_labels['value_' + str(i)] = label.Label(self.okuda_font, x=x_value_for_values, y=y_value, max_glyphs=32, color=0)
                self.lcars.append(self.lcars_labels['value_' + str(i)])

                y_value = first_row_y + (i*row_offset)

        except Exception as err:
            # Ignore all other errors except CTRL-C
            print("Error in setupLCARS: " + repr(err))

    def displayLCARS(self, lcars_type):
        self.main_screen.show(self.lcars)

    def lcarsDisplayText(self, name=None, text_to_display=None):
        if name != None and text_to_display != None:
            self.lcars_labels[name].text = text_to_display

    def lcarsLabels(self, lcars_type):
        if lcars_type == "atmos":
            self.lcarsDisplayText(name="label_1", text_to_display="TEMPERATURE")
            self.lcarsDisplayText(name="label_2", text_to_display="AIR QUALITY")
            self.lcarsDisplayText(name="label_3", text_to_display="UV INDEX")
            self.lcarsDisplayText(name="label_4", text_to_display="HUMIDITY")
            self.lcarsDisplayText(name="label_5", text_to_display="PRESSURE")

        elif lcars_type == "gps":
            self.lcarsDisplayText(name="label_1", text_to_display="TIME")
            self.lcarsDisplayText(name="label_2", text_to_display="LATITUDE")
            self.lcarsDisplayText(name="label_3", text_to_display="LONGITUDE")
            self.lcarsDisplayText(name="label_4", text_to_display="ALTITUDE")
            self.lcarsDisplayText(name="label_5", text_to_display="SPEED")

        # Set-up value labels to display '0' to start with
        self.lcarsDisplayText(name="value_1", text_to_display="0")
        self.lcarsDisplayText(name="value_2", text_to_display="0")
        self.lcarsDisplayText(name="value_3", text_to_display="0")
        self.lcarsDisplayText(name="value_4", text_to_display="0")
        self.lcarsDisplayText(name="value_5", text_to_display="0")

    def displayLCARSreadings(self, lcars_type):
        if lcars_type == "atmos":
            temperature_offset = -5

            self.lcarsDisplayText(name="value_1", text_to_display=str(round(self.bme680.temperature + temperature_offset, 1)) + ' C')
            self.lcarsDisplayText(name="value_2", text_to_display=str(self.bme680.gas))
            self.lcarsDisplayText(name="value_3", text_to_display=str(round(self.veml.uv_index, 2)))
            self.lcarsDisplayText(name="value_4", text_to_display=str(round(self.bme680.relative_humidity, 1)) + '%')
            self.lcarsDisplayText(name="value_5", text_to_display=str(round(self.bme680.pressure, 0)))

        elif lcars_type == "gps":
            current = time.monotonic()

            if current - self.gps_last_print >= 1.0:
                self.gps_last_print = current

                # Debug
                # print("Fix? " + str(self.gps.has_fix) + " Sats: " + str(self.gps.satellites))

                if not self.gps.has_fix:
                    self.lcarsDisplayText(name="value_1", text_to_display="WAIT")

                else:
                    self.lcarsDisplayText(name="value_1", text_to_display=str(self.gps.timestamp_utc.tm_hour + ":" + self.gps.timestamp_utc.tm_min))
                    self.lcarsDisplayText(name="value_2", text_to_display=str(round(self.gps.latitude, 2)))
                    self.lcarsDisplayText(name="value_3", text_to_display=str(round(self.gps.longitude, 2)))
                    self.lcarsDisplayText(name="value_4", text_to_display=str(self.gps.altitude_m))
                    self.lcarsDisplayText(name="value_5", text_to_display=str(self.gps.speed_knots))

                # Get firmware version
                '''
                self.gps.send_command(b"PMTK605")
                data = self.gps.read(32)
                if data is not None:
                    data_string = "".join([chr(b) for b in data])
                    print(data_string, end="\n")
                '''

            # Slow it down a bit. Bear in mind this affects the main loop's tick-over
            time.sleep(1)

    def loadSounds(self):
        # Load the sounds, if enabled
        if sounds_enabled:
            self.sounds = {}

            snd_control_beep_file = open("snd/control_beep.wav", "rb")
            self.sounds['snd_control_beep'] = audiocore.WaveFile(snd_control_beep_file)

            snd_engage_beep_file = open("snd/engage_beep.wav", "rb")
            self.sounds['snd_engage_beep'] = audiocore.WaveFile(snd_engage_beep_file)

            snd_startup_file = open("snd/tricorder_short.wav", "rb")
            self.sounds['snd_startup'] = audiocore.WaveFile(snd_startup_file)

    def playSound(self, sound_name):
        # sound_name needs to be one of the sounds loaded in loadSounds()
        if sounds_enabled:
            if not self.i2s.playing:
                self.i2s.play(self.sounds[sound_name])

                #while self.i2s.playing:
                #    time.sleep(0.01)

                #self.i2s.stop()

    def setupGPS(self):
        self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        self.gps.send_command(b"PMTK220,1000")
        self.gps_last_print = time.monotonic()

    def setupBlinkies(self):
        self.led = DigitalInOut(board.GP15)
        self.led.direction = Direction.OUTPUT
        self.led.value = True

    def setupButtons(self):
        self.button = DigitalInOut(board.GP14)
        self.button.direction = Direction.INPUT
        self.button.pull = Pull.UP

    def setupPowerBlinky(self):
        self.power_led = DigitalInOut(board.GP25)
        self.power_led.direction = Direction.OUTPUT
        self.power_led.value = True

    def blinkError(self, err):
        print("Error - " + str(err))
        for i in range(6):
            self.power_led.value = True
            time.sleep(0.5)
            self.power_led.value = False
            time.sleep(0.5)