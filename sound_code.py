import board
import audiocore
import audiobusio
import time

print("Playing sample 10 times")

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
