import RPi.GPIO as GPIO
import time

## Shifter Class
class Shifter:
    def __init__(self, serial_pin, latch_pin, clock_pin):
        self.__serial = serial_pin
        self.__clock = clock_pin
        self.__latch = latch_pin
        self.__setup()

    def __setup(self):
        GPIO.setup(self.__serial, GPIO.OUT)
        GPIO.setup(self.__latch, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.__clock, GPIO.OUT, initial=GPIO.LOW)

    def __ping(self, pin):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0)
        GPIO.output(pin, GPIO.LOW)

    def shiftByte(self, value):
        GPIO.output(self.__latch, GPIO.LOW)
        for i in range(8):
            bit_val = (value >> i) & 0x01
            GPIO.output(self.__serial, bit_val)
            self.__ping(self.__clock)
        GPIO.output(self.__latch, GPIO.HIGH)
