## Lab 5 - Pulse Width Modulation (PWM) and Threaded Callbacks ## 
# Import Modules
import RPi.GPIO as GPIO
import time # import time module
import math # import math module

GPIO.setmode(GPIO.BCM)

# Assignment of GPIO pins to LED pins
GPIO_pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 0] # List of 10 LED pins
for i in GPIO_pins: 
	GPIO.setup(i, GPIO.OUT)

# Declaration of key variables in Brightness Equation (f, phi)
f = 0.2 # frequency in [Hz]
#phi = math.pi / 11 # phase angle in [rad]
phi_increase = math.pi / 11 # incremental step in [rad]

# PWM Declaration with Base Frequency
GPIO_pwm = [GPIO.PWM(i, 500) for i in GPIO_pins]
for pwm in GPIO_pwm:
	pwm.start(0)

# try-except-finally block to run traversing LED path
try:
	start = time.time() # Utilizes time.time() to initialize start time
	while True:
		t = time.time() - start
		for i, pwm in enumerate(GPIO_pwm):
			phi = i * phi_increase
			b = (math.sin(2 * math.pi * f * t - phi)) ** 2
			duty = b * 100
			pwm.ChangeDutyCycle(duty) # STOPPED HERE
except KeyboardInterrupt:
	print('\n Program Shutting Down')
	pass
finally:
	for pwm in GPIO_pwm:
		pwm.stop()
	GPIO.cleanup()
## ----------------------------------------------------------------##

