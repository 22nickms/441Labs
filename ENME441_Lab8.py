# stepper_class_shiftregister_multiprocessing.py
#
# Stepper class
#
# Because only one motor action is allowed at a time, multithreading could be
# used instead of multiprocessing. However, the GIL makes the motor process run 
# too slowly on the Pi Zero, so multiprocessing is needed.

import time # delay function
import multiprocessing # multiple motor calibiration and control
from multiprocessing import Value # shared var
from shifter import Shifter   # our custom Shifter class with a shift register

class Stepper:
    """
    Supports operation of an arbitrary number of stepper motors using
    one or more shift registers.
  
    A class attribute (shifter_outputs) keeps track of all
    shift register output values for all motors.  In addition to
    simplifying sequential control of multiple motors, this schema also
    makes simultaneous operation of multiple motors possible.
   
    Motor instantiation sequence is inverted from the shift register outputs.
    For example, in the case of 2 motors, the 2nd motor must be connected
    with the first set of shift register outputs (Qa-Qd), and the 1st motor
    with the second set of outputs (Qe-Qh). This is because the MSB of
    the register is associated with Qa, and the LSB with Qh (look at the code
    to see why this makes sense).
 
    An instance attribute (shifter_bit_start) tracks the bit position
    in the shift register where the 4 control bits for each motor
    begin.
    """

    # Class attributes:
    num_steppers = 0      # track number of Steppers instantiated
    shifter_outputs = multiprocessing.Value("i", 0)  # track shift register outputs for all motors
    seq = [0b0001,0b0011,0b0010,0b0110,0b0100,0b1100,0b1000,0b1001] # CCW sequence

    delay = 1500  # delay between motor steps [us] 
    steps_per_degree = 4096/360  # 4096 steps/rev * 1/360 rev/deg

    def __init__(self, shifter, lock):
        self.s = shifter  # shift register
        self.angle = multiprocessing.Value('d', 0.0) # current output shaft angle
        self.step_state = 0 # track position in sequence
        self.shifter_bit_start = 4 * Stepper.num_steppers # starting bit position
        self.lock = lock  # multiprocessing lock

        Stepper.num_steppers += 1 # increment the instance count

    # Signum function:
    def __sgn(self, x):
        if x == 0:
            return(0)
        else: 
            return(int(abs(x)/x))

    # Move a single +/-1 step in the motor sequence:
    def __step(self, dir):
        '''
        For moving One Motor sequentially.
        self.step_state += dir    # increment/decrement the step
        self.step_state %= 8      # ensure result stays in [0,7]
        Stepper.shifter_outputs |= 0b1111<<self.shifter_bit_start
        Stepper.shifter_outputs &= Stepper.seq[self.step_state]<<self.shifter_bit_start
        self.s.shiftByte(Stepper.shifter_outputs)
        self.angle += dir/Stepper.steps_per_degree
        self.angle %= 360         # limit to [0,359.9+] range
        '''
        # Call m1.rotate() and m2.rotate() to move simultaneously

        self.step_state += dir # increment/decrement the step
        self.step_state %= 8 # In coil activation sequence range of [0,7]
        p = Stepper.seq[self.step_state] << self.shifter_bit_start

        with self.lock:
            value = Stepper.shifter_outputs.value
            value &= ~(0b1111 << self.shifter_bit_start) # clears motor's 4 bits (AND)
            value |= p  # set motor bits (OR)
            Stepper.shifter_outputs.value = value
            self.s.shiftByte(value) # updates shift register

            self.angle.value += dir/Stepper.steps_per_degree # Angle updated
            self.angle.value %= 360 # limited range of rotation

    # Rotation function (private)
    def __rotate(self, delta):
        numSteps = int(Stepper.steps_per_degree * abs(delta))  # find the right # of steps
        dir = self.__sgn(delta)  # Direction of rotation (+1 CCW, -1 CW)

        for _ in range(numSteps): # Step through the sequence
            self.__step(dir) 
            time.sleep(Stepper.delay / 1e6) # delay between steps

    # Rotation function (public used for multiprocessing)
    def rotate(self, delta): 
        time.sleep(0.05) # Brief pause 
        p = multiprocessing.Process(target=self.__rotate, args=(delta,))
        p.start() 
        return p 

    # Move to an absolute angle taking the shortest possible path:
    def goAngle(self, angle):
         delta = (angle - self.angle.value) % 360 # Difference is positive
         if delta > 180:  # shortest path correction
            delta -= 360
         elif delta < -180: # shortest path correction
             delta += 360
    
         return(self.__rotate, (delta,))

    # Set the motor zero point
    def zero(self):
        self.angle.value = 0.0 # multiprocessed value

# Example use:

if __name__ == '__main__':

    s = Shifter(data=16, latch=20, clock=21)   # Set up Shifter

    # Use multiprocessing.Lock 
    lock = multiprocessing.Lock() # lock for shift register

    # Stepper Objects
    m1 = Stepper(s, lock)
    m2 = Stepper(s, lock)

    # Zero the motors:
    m1.zero() # Zero Position for Motor 1
    m2.zero() # Zero Position for Motor 2

    # Move both motors to specified angles
    move1 = m1.goAngle(90) # Move m1 to 90 deg CCW
    move2 = m2.goAngle(-90) # Move m2 to -90 deg CW
    move1.join() # m1 waiting period
    move2.join() # m2 waiting period

    # 
    move1 = m1.goAngle(-45) # Move m1 to -45 deg CW
    move2 = m2.goAngle(45) # Move m2 to 45 deg CCW
    move1.join() # m1 waiting period
    move2.join() # m2 waiting period
    
    # 1st Motor finishes seq
    move1 = m1.goAngle(-135) # Move m1 to -135 deg CW (rel to 0 deg)
    move1.join() # m1 waiting period

    move1 = m1.goAngle(135) # Move m1 to 135 deg CCW (rel to 0 deg)
    move1.join() # m1 waiting period

    move1 = m1.goAngle(0) # Move m1 to 0 deg (rel to 0 deg)
    move1.join() # m1 waiting period


    # While the motors are running in their separate processes, the main
    # code can continue doing its thing: 
    try:
        while True:
            pass
    except:
        print('\nend')