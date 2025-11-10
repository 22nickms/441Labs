import RPi.GPIO as GPIO
import time
import random

## Shifter Class
class shifter:
	def __init__(self, serial_pin, latch_pin, clock_pin):
		self.serial = serial_pin 
		self.clock = clock_pin
		self.latch = latch_pin
		self.start()

	def start(self):
		GPIO.setup(self.serial, GPIO.OUT)
		GPIO.setup(self.latch, GPIO.OUT, initial=0)
		GPIO.setup(self.clock, GPIO.OUT, initial=0)

	def _ping(self,p):
		GPIO.output(p,1)
		time.sleep(0)
		GPIO.output(p,0)

	def shiftByte(self,b):
		for i in range(8):
			GPIO.output(self.serial, b & (1<<i))
			self.__ping(self.clock)
		self._ping(self.latch)

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


