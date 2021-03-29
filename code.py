import board
import busio
import time
from adafruit_is31fl3731.matrix_11x7 import Matrix11x7
import adafruit_framebuf

def matrix_test_pattern(matrix):
	for y in range(7):
	    for x in range(11):
	        matrix.pixel(x, y, 100)
	        time.sleep(0.01)
	        matrix.fill(0)

def display_on_matrix(matrix, text_to_show):
    # Create a framebuffer for our display
    buffer_array = bytearray(32)  # 2 bytes tall x 16 wide = 32 bytes (9 bits is 2 bytes)
    frame_buffer = adafruit_framebuf.FrameBuffer(
        buffer_array, matrix.width, matrix.height, adafruit_framebuf.MVLSB
    )

    frame = 0  # start with frame 0

    for i in range(len(text_to_show) * 9):
        frame_buffer.fill(0)
        frame_buffer.text(text_to_show, -i + matrix.width, 0, color=1, font_name='fonts/font5x8.bin')

        # to improve the display flicker we can use two frame
        # fill the next frame with scrolling text, then show it.
        matrix.frame(frame, show=False)

        # turn all LEDs off
        matrix.fill(0)

        # Loop through the matrix and set pixels according to the text
        for x in range(matrix.width):
            bite = buffer_array[x]
            for y in range(matrix.height):
                bit = 1 << y & bite
                # if bit > 0 then set the pixel brightness
                if bit:
                    matrix.pixel(x, y, 50)

        # now that the frame is filled, show it.
        matrix.frame(frame, show=True)
        frame = 0 if frame else 1

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
matrix = Matrix11x7(i2c)

matrix_test_pattern(matrix)
display_on_matrix(matrix, "Hello world")

print("Done")