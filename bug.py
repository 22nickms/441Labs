import Shifter
import Bug
import RPi.GPIO as GPIO
from time import sleep
import random   

GPIO.setmode(GPIO.BCM)

dataPin = 23
latchPin = 24
clockPin = 25

ss = Shifter(dataPin, latchPin, clockPin) 
bug = Bug.Bug(ss)

s1 = 5
s2 = 6
s3 = 13

GPIO.setup(s1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def s1_call(s1):
    bug.active = not bug.active

def s2_call(s2):
    bug.isWrapOn = not bug.isWrapOn

def s3_call(s3):
    if GPIO.input(s3):
        bug.timestep = bug.timestep / 3
    else:
        bug.timestep = bug.timestep * 3
    
GPIO.add_event_detect(s1, GPIO.RISING, callback=s1_call, bouncetime=300)
GPIO.add_event_detect(s2, GPIO.RISING, callback=s2_call, bouncetime=300)
GPIO.add_event_detect(s3, GPIO.BOTH, callback=s3_call, bouncetime=300)

try:
    while True:
        if bug.active:
            bug.step()
            sleep(bug.timestep)
        else: 
            sleep(delay)
except KeyboardInterrupt:
    bug.stop()
    GPIO.cleanup()
    print("Exiting program")