from shifter1 import Shifter
from bug_class import Bug
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

# Pin definitions
dataPin = 23
latchPin = 24
clockPin = 25
s1 = 17
s2 = 27
s3 = 22

# Setup input pins
GPIO.setup(s1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Create Shifter and Bug objects
ss = Shifter(dataPin, latchPin, clockPin)
bug = Bug(ss)

# --- GPIO Callbacks ---
def s1_status(channel):
    bug.move = not bug.move

def s2_status(channel):
    bug.isWrapOn = not bug.isWrapOn

def s3_status(channel):
    if GPIO.input(s3):
        bug.timestep /= 3
    else:
        bug.timestep *= 3

# --- Event detection ---
GPIO.add_event_detect(s1, GPIO.RISING, callback=s1_status, bouncetime=300)
GPIO.add_event_detect(s2, GPIO.RISING, callback=s2_status, bouncetime=300)
GPIO.add_event_detect(s3, GPIO.BOTH, callback=s3_status, bouncetime=300)

# --- Main loop ---
try:
    while True:
        if bug.move:
            bug.step()
            sleep(bug.timestep)
        else:
            sleep(0.05)
except KeyboardInterrupt:
    bug.stop()
    GPIO.cleanup()
