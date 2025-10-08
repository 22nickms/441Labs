## Lab 5 - Pulse Width Modulation (PWM) and Threaded Callbacks ## 
# Import Modules
import RPi.GPIO as GPIO
import time # import time module
import math # import math module

GPIO.setmode(GPIO.BCM) # References GPIO Numbers

# Assignment of GPIO pins to LED pins
GPIO_pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 0] # List of 10 LED pins
for i in GPIO_pins: 
	GPIO.setup(i, GPIO.OUT)

# Threaded Callbacks Setup
button_GPIO = 14 # Button GPIO Pin 14
GPIO.setup(button_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Declaration of key variables in Brightness Equation (f, phi)
f = 0.2 # frequency in [Hz]
phi_plus = math.pi / 11 # incremental step in [rad]
sign_phaselag = 1 

# PWM Declaration with Base Frequency
bf = 500 # Base Frequency [Hz]
GPIO_pwm = [GPIO.PWM(i, bf) for i in GPIO_pins] # GPIO_pwm : i el to bf 
for pwm in GPIO_pwm:
	pwm.start(0)

# Button Callback Function
def buttonCallback(channel):
	global sign_phaselag # Placed in the function so it can be varied
	sign_phaselag *= -1 # Changes sign (direction of wave)
GPIO.add_event_detect(button_GPIO, GPIO.BOTH, callback=buttonCallback, bouncetime=250) 
# Add event syntax --> Uses GPIO.BOTH for both LOW-HIGH and HIGH-LOW signal triggers

# try-except-finally block to run traversing LED path
try:
	start = time.time() # Utilizes time.time() to initialize start time
	while True:
		t = time.time() - start
		i = 0 # Initialize counter variable
		for pwm in GPIO_pwm:
			phi = i * phi_plus # Incremental Phi
			b = (math.sin(2 * math.pi * f * t - phi*sign_phaselag)) ** 2 # Brightness Equation
			duty = b * 100  # Duty cycle for whole succession (0-100)
			pwm.ChangeDutyCycle(duty)  # Modulates ON signal time
			i += 1 # Counter Sequence until all elements are clocked
except KeyboardInterrupt:
	print('\n Exit')
	pass
finally:
	for pwm in GPIO_pwm:
		pwm.stop()
	GPIO.cleanup()
## ----------------------------------------------------------------##
