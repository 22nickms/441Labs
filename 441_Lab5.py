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

pwm1 = GPIO.PWM(p, 500) #creates a PWM object (p) with a frequency of 500 Hz
pwm2 = GPIO.PWM(p2, 500)
pwm1.start(0)
pwm2.start(0)

try:
	start = time.time() # Utilizes time.time() to initialize start time
	while True:
		t = time.time() - start # records current time elapsed
		b1 = (math.sin(2 * math.pi * f * t)) ** 2 # Brightness function
		duty1 = b1 * 100 # Duty cycle to measure from 0-100%
		pwm1.ChangeDutyCycle(duty1) # LEC 4 pwm 

		b2 = (math.sin(2 * math.pi * f * t - phi)) ** 2
		duty2 = b2 * 100
		pwm2.ChangeDutyCycle(duty2)
except KeyboardInterrupt:
	print('\n Program Shutting Down')
	pass
finally:
	pwm1.stop()
	pwm2.stop()
	GPIO.cleanup()
## ----------------------------------------------------------------##




