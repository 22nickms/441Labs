import multiprocessing
import time
from RPi import GPIO
from time import sleep

# ----------------- Shifter Class -----------------
class Shifter:
    def __init__(self, data, latch, clock):
        self.dataPin = data
        self.latchPin = latch
        self.clockPin = clock

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dataPin, GPIO.OUT)
        GPIO.setup(self.latchPin, GPIO.OUT)
        GPIO.setup(self.clockPin, GPIO.OUT)

    def ping(self, p):
        GPIO.output(p, 1)
        sleep(0)
        GPIO.output(p, 0)

    def shiftByte(self, databyte):
        for i in range(8):
            GPIO.output(self.dataPin, databyte & (1 << i))
            self.ping(self.clockPin)
        self.ping(self.latchPin)


# ----------------- Stepper Class -----------------
class Stepper:
    num_steppers = 0
    shifter_outputs = 0
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001]  # CCW sequence
    delay = 1200                         # microseconds
    steps_per_degree = 4096/360          # 11.377... steps per degree

    def __init__(self, shifter, lock):
        self.s = shifter
        self.angle = multiprocessing.Value('d', 0.0)  # shared across processes
        self.step_state = 0
        self.shifter_bit_start = 4 * Stepper.num_steppers
        self.lock = lock                              # shared lock for safe shifting
        Stepper.num_steppers += 1

    def __sgn(self, x):
        return 0 if x == 0 else int(abs(x)/x)

    def __step(self, dir):

        # Update shift register output (critical section)
        with self.lock:
            self.step_state = (self.step_state + dir) % 8

            # Clear existing bits for this motor
            Stepper.shifter_outputs &= ~(0b1111 << self.shifter_bit_start)

            # Write new state
            Stepper.shifter_outputs |= (Stepper.seq[self.step_state] << self.shifter_bit_start)

            # Output to shift register
            self.s.shiftByte(Stepper.shifter_outputs)

        # Update angle (separately locked)
        with self.angle.get_lock():
            self.angle.value = (self.angle.value + dir / Stepper.steps_per_degree) % 360

    def __rotate(self, delta):
        numSteps = int(Stepper.steps_per_degree * abs(delta))
        dir = self.__sgn(delta)

        for _ in range(numSteps):
            self.__step(dir)
            time.sleep(Stepper.delay / 1e6)

    def rotate(self, delta):

        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start()

    def goAngle(self, angle):
        """Move to an absolute angle using the shortest path"""
        with self.angle.get_lock():
            current_angle = self.angle.value

        delta = angle - current_angle

        # Shortest path calculation
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        self.rotate(delta)

    def zero(self):
        with self.angle.get_lock():
            self.angle.value = 0.0



if __name__ == '__main__':
    s = Shifter(data=16, latch=20, clock=21)

    lock = multiprocessing.Lock()   # Shared lock for shift register output

    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    m1.zero()
    m2.zero()

    # Required test sequence from the assignment:
    m1.goAngle(90)
    m1.goAngle(-45)

    m2.goAngle(-90)
    m2.goAngle(45)

    m1.goAngle(-135)
    m1.goAngle(135)
    m1.goAngle(0)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nExiting...")
