## Lab 5 - Pulse Width Modulation (PWM) and Threaded Callbacks ## 
##----------------------------------------------------------------##

## Part 1 time.time() function

import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)
p = 2
GPIO.setup(p, GPIO.OUT)
p2 = 3
GPIO.setup(p2, GPIO.OUT)

f = 0.2 # frequency in [Hz]
phi = math.pi / 11 # phase angle in [rad]

pwm = GPIO.PWM(p, 500) #creates a PWM object (p) with frequency of 500 Hz
pwm.start(0)

try:
	start = time.time() # Utilizes time.time() to initialize start time
	while True:
		t = time.time() - start # records current time elapsed
		b = (math.sin(2 * math.pi * f * t - phi)) ** 2 # Brightness function
		duty = b * 100 # Duty cycle to measure from 0-100%
		pwm.ChangeDutyCycle(duty) # LEC 4 pwm 
except KeyboardInterrupt:
	print('\n Program Shutting Down')
	pass
finally:
	pwm.stop()
	GPIO.cleanup()
## ----------------------------------------------------------------##

