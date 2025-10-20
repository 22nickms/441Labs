import shifter
import RPi.GPIO as GPIO
from time import sleep
import time
import random

## Bug Class
class Bug:
    def __init__(self, __shifter, timestep = 0.1, x = 3, isWrapOn = True):
        self.__shifter = __shifter
        self.x = self.timestep = timestep
        self.isWrapOn = isWrapOn

        self.__move = False

    def step(self):
        leds = 8
        pattern = 1 << self.x
        self.__shifter.shiftByte(pattern)
        s = random.choice([-1,1])
        self.x += s


        if self.isWrapOn:
            self.x = self.x % leds
        else:
            if self.x < 0:
                self.x = 0
            elif self.x > leds-1:
                self.x = leds-1

    def start(self):
        self.__move = True
        while self.__move:
            self.step()
            time.sleep(self.timestep)
    
    def stop(self):
        self.__move = False