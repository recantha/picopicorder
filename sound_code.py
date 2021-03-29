import array
import math
import time
import board
import digitalio
#import rp2pio
#import adafruit_pioasm
import audiocore

# Generate one period of sine wav.
length = 8000 // 440

# signed 16 bit
s16 = array.array("h", [0] * length)
for i in range(length):
    s16[i] = int(math.sin(math.pi * 2 * i / length) * (2 ** 15))

program = """
.program i2s_with_hold
.side_set 2

; Load the next set of samples
                    ;        /--- LRCLK
                    ;        |/-- BCLK
                    ;        ||
    pull noblock      side 0b01 ; Loads OSR with the next FIFO value or X
    mov x osr         side 0b01 ; Save the new value in case we need it again

    set y 14          side 0b01
bitloop1:
    out pins 1        side 0b10 [2]
    jmp y-- bitloop1  side 0b11 [2]
    out pins 1        side 0b10 [2]

    set y 14          side 0b11 [2]
bitloop0:
    out pins 1        side 0b00 [2]
    jmp y-- bitloop0  side 0b01 [2]
    out pins 1        side 0b00 [2]
"""

program_RPF = """
.program audio_i2s
.side_set 2

                    ;        /--- LRCLK
                    ;        |/-- BCLK
                    ;        ||
    pull noblock      side 0b01 ; Loads OSR with the next FIFO value or X
    mov x osr         side 0b01 ; Save the new value in case we need it again
bitloop1:           ;        ||
    out pins, 1       side 0b10
    jmp x-- bitloop1  side 0b11
    out pins, 1       side 0b00
    set x, 14         side 0b01

bitloop0:
    out pins, 1       side 0b00
    jmp x-- bitloop0  side 0b01
    out pins, 1       side 0b10
public entry_point:
    set x, 14         side 0b11
"""

"""
assembled = adafruit_pioasm.assemble(program)

dac = rp2pio.StateMachine(
    assembled,
    frequency=800000 * 6,
    first_out_pin=board.GP11,
    first_sideset_pin=board.GP10,
    sideset_pin_count=2,
    auto_pull=False,
    out_shift_right=False,
    pull_threshold=32,
    wait_for_txstall=False,
)
# BCLK=11, LRC=12, DIN=10
wave_file = open("StreetChicken.wav", "rb")
wave = audiocore.WaveFile(wave_file)

dac.write(s16)
time.sleep(1)
dac.stop()

print("done")

"""


""" Known-good-ish
import time
import array
import math
import audiocore
import board
import audiobusio

sample_rate = 8000
tone_volume = .1  # Increase or decrease this to adjust the volume of the tone.
frequency = 440  # Set this to the Hz of the tone you want to generate.
length = sample_rate // frequency  # One freqency period
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = int((math.sin(math.pi * 2 * frequency * i / sample_rate) *
                        tone_volume + 1) * (2 ** 15 - 1))
 
audio = audiobusio.I2SOut(bit_clock=board.GP10, word_select=board.GP11, data=board.GP9)
sine_wave_sample = audiocore.RawSample(sine_wave, sample_rate=sample_rate)

#wave_file = open("StreetChicken.wav", "rb")
wave_file = open("tricorder_2.wav", "rb")
wave = audiocore.WaveFile(wave_file)

print("Playing audio")
audio.play(wave, loop=True)
i = 0
while i < 10:
    time.sleep(0.1)
    i = i + 1

zero_wave = array.array("H", [0] * length)
for i in range(length):
    zero_wave[i] = 0
zero_sample = audiocore.RawSample(zero_wave, sample_rate=sample_rate)
audio.play(zero_sample, loop=True)
i=0
while i < 50:
    time.sleep(0.1)
    i = i + 1

print("Done Zeroing")

audio.play(wave, loop=True)
i = 0
while i < 10:
    time.sleep(0.1)
    i = i + 1

print("re-played")
#from audiomp3 import MP3Decoder
#mp3 = open("tricorder2.mp3", "rb")
#decoder = MP3Decoder(mp3)
#audio.play(decoder, loop=True)
#while i < 200:
#    time.sleep(0.1)
#    i = i + 1
"""

import board
import audiocore
import audiobusio
import time

print("Playing 10 times StreetChicken.wav")

f = open("tricorder_2.wav", "rb")
wav = audiocore.WaveFile(f)
i2s = audiobusio.I2SOut(bit_clock=board.GP10, word_select=board.GP11, data=board.GP9)

for i in range(10):
    start=time.monotonic()
    i2s.play(wav)
    i=0
    while i2s.playing:
        time.sleep(0.01)
#    while i < 100:
#        i=i+1
#        time.sleep(0.1)
#        pass
    i2s.stop()
    stop = time.monotonic()
    print("Total length = ", stop, "-", start, "=", stop-start)

#GPIO26 to DIN (serial data)
#GPIO27 is connected to the BCK input (bit clock)
#GPIO28 to LRCK (left or right clock)

#class audiobusio.I2SOut(
#   bit_clock: microcontroller.Pin,
#   word_select: microcontroller.Pin,
#   data: microcontroller.Pin,
#   *,
#   left_justified: bool)