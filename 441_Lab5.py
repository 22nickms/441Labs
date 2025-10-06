## Lab 5 - Pulse Width Modulation (PWM) and Threaded Callbacks ## 
##----------------------------------------------------------------##

## Part 1 time.time() function

import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)
p = 4
GPIO.setup(p, GPIO.OUT)

f = 0.2 # frequency in [Hz]

pwm = GPIO.PWM(p, 500) #creates a PWM object (p) with frequency of 500 Hz
pwm.start(0)

try:
	start = time.time() # Utilizes time.time() to initialize start time
	while True:
		t = time.time() - start # records current time elapsed
		b = (math.sin(2 * math.pi * f * t)) ** 2 # Brightness function
		duty = b * 100 # Duty cycle to measure from 0-100%
		pwm.ChangeDutyCycle(duty) # LEC 4 pwm 
except KeyboardInterrupt:
	print('\n Program Shutting Down')
	pass
finally:
	pwm.stop()
	GPIO.cleanup()
## ----------------------------------------------------------------##

## Part 2. Second LED

import RPi.GPIO as GPIO
import time
import math

GPIO.setmode(GPIO.BCM)
p = 4
p2 = 5 # Second LED
GPIO.setup(p, GPIO.OUT)
GPIO.setup(p2, GPIO.OUT)


phi = math.pi / 11 # phase angle in [radians]
f = 0.2 # frequency in [Hz]

pwm = GPIO.PWM(p, 500) #creates a PWM object (p) with frequency of 500 Hz
pwm.start(0)

try:
	start = time.time() # Utilizes time.time() to initialize start time
	while True: 
		t = time.time() - start # records current time elapsed 
