import random

## Bug Class
class Bug:
    def __init__(self, __shifter, timestep=0.1, x=3, isWrapOn=True):
        self.__shifter = __shifter
        self.x = x
        self.timestep = timestep
        self.isWrapOn = isWrapOn
        self.move = False

    def step(self):
        total_leds = 8
        pattern = 1 << self.x
        self.__shifter.shiftByte(pattern)

        # random left (-1) or right (+1)
        s = random.choice([-1, 1])
        self.x += s

        if self.isWrapOn:
            self.x = self.x % total_leds
        else:
            if self.x < 0:
                self.x = 0
            elif self.x > total_leds - 1:
                self.x = total_leds - 1

    def stop(self):
        self.move = False
        self.__shifter.shiftByte(0)  # turn off LEDs
