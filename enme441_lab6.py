from shifter import Shifter
import RPi.GPIO as GPIO
import time
import random


    
































pos = 0
led = 8
delay = 0.05

try:
    while True:
        pattern = 1 << pos
        shifter.shiftByte(pattern)

        randstep = random.choice([-1,1])
        pos += randstep 

        if pos < 0:
            pos = 0
        if pos > 7:
            pos = 7
        time.sleep(delay)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Exit program")

