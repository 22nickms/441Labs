import multiprocessing
import time
from RPi import GPIO
from time import sleep

class Stepper:
    num_steppers = 0
    shifter_outputs = 0
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001]  # CCW sequence
    delay = 1200
    steps_per_degree = 4096/360

    def __init__(self, shifter, lock):
        self.s = shifter
        self.angle = multiprocessing.Value('d', 0.0)   # shared value
        self.step_state = 0
        self.shifter_bit_start = 4 * Stepper.num_steppers
        self.lock = lock   # <-- You MUST keep this

        Stepper.num_steppers += 1

    def __sgn(self, x):
        return 0 if x == 0 else int(abs(x)/x)

    def __step(self, dir):
        self.step_state = (self.step_state + dir) % 8

        Stepper.shifter_outputs &= ~(0b1111 << self.shifter_bit_start)  
        Stepper.shifter_outputs |= (Stepper.seq[self.step_state] << self.shifter_bit_start)

        self.s.shiftByte(Stepper.shifter_outputs)

        with self.angle.get_lock():
            self.angle.value = (self.angle.value + dir / Stepper.steps_per_degree) % 360

    def __rotate(self, delta):
        with self.lock:    # cleaner version of acquire/release
            numSteps = int(Stepper.steps_per_degree * abs(delta))
            dir = self.__sgn(delta)
            for _ in range(numSteps):
                self.__step(dir)
                time.sleep(Stepper.delay / 1e6)

    def rotate(self, delta):
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    def goAngle(self, angle):
        with self.angle.get_lock():
            current_angle = self.angle.value

        delta = angle - current_angle

        # choose shortest rotation
        if delta > 180: delta -= 360
        elif delta < -180: delta += 360

        self.rotate(delta)

    def zero(self):
        # reset angle safely
        with self.angle.get_lock():
            self.angle.value = 0.0
