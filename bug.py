from shifter1 import Shifter
from bug_class import Bug
import RPi.GPIO as GPIO
from time import sleep
import random   

GPIO.setmode(GPIO.BCM)

dataPin = 23
latchPin = 24
clockPin = 25

ss = Shifter(dataPin, latchPin, clockPin) 
bug = Bug(ss)

s1 = 17
s2 = 27
s3 = 22

GPIO.setup(s1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(s3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def s1_status(s1):
    bug.move = not bug.move ## Turns bug on and off

def s2_status(s2):
    bug.isWrapOn = not bug.isWrapOn ## wrap state switch

def s3_status(s3): ## speed switch
    if GPIO.input(s3):
        bug.timestep = bug.timestep / 3
    else:
        bug.timestep = bug.timestep * 3
    
GPIO.add_event_detect(s1, GPIO.RISING, callback=s1_status, bouncetime=300)
GPIO.add_event_detect(s2, GPIO.RISING, callback=s2_status, bouncetime=300)
GPIO.add_event_detect(s3, GPIO.BOTH, callback=s3_status, bouncetime=300)

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
    print("Exiting program")