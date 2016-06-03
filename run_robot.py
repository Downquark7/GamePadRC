#!/usr/bin/env python
__author__ = 'anton'

import evdev
import ev3dev.auto as ev3
import threading
import time


#Helpers
def clamp(n, (minn, maxn)):
    """
    Given a number and a range, return the number, or the extreme it is closest to.
    :param n: number
    :return: number
    """
    return max(min(maxn, n), minn)


def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    val: float or int
    src: tuple
    dst: tuple
    example: print scale(99, (0.0, 99.0), (-1.0, +1.0))
    """
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

def scalestick(value):
    return scale(value,(0,255),(-100,100))

def dc_clamp(value):
    return clamp(value,(-100,100))

print "Finding ps3 controller..."
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    if device.name == 'PLAYSTATION(R)3 Controller':
        ps3dev = device.fn


gamepad = evdev.InputDevice(ps3dev)



forward_speed = 0
turn_speed = 0
#lift_speed = 0
#other_speed = 0
running = True

class MotorThread(threading.Thread):
    def __init__(self):
        self.a_motor = ev3.LargeMotor(ev3.OUTPUT_A)
        self.b_motor = ev3.LargeMotor(ev3.OUTPUT_B)
        self.c_motor = ev3.LargeMotor(ev3.OUTPUT_C)
        self.d_motor = ev3.LargeMotor(ev3.OUTPUT_D)
        threading.Thread.__init__(self)

    def run(self):
        print "Engines running!"
        while running:
            self.a_motor.run_forever(duty_cycle_sp = dc_clamp(forward_speed + turn_speed))
            self.b_motor.run_forever(duty_cycle_sp = dc_clamp(forward_speed + turn_speed))
            self.c_motor.run_forever(duty_cycle_sp = dc_clamp(forward_speed - turn_speed))
            self.d_motor.run_forever(duty_cycle_sp = dc_clamp(forward_speed - turn_speed))

        self.a_motor.stop()
        self.b_motor.stop()
        self.c_motor.stop()
        self.d_motor.stop()


if __name__ == "__main__":
    motor_thread = MotorThread()
    motor_thread.setDaemon(True)
    motor_thread.start()

    for event in gamepad.read_loop(): #this loops infinitely
        if event.type == 3: #A stick is moved
            
            if event.code == 1: #Y axis on left stick
                forward_speed = scalestick(event.value)
                if abs(forward_speed) < 15:
                    forward_speed = 0
            '''
            if event.code == 0: #X axis on left stick
                lift_speed = scalestick(event.value)
                if abs(lift_speed) < 15: #deadzone
                    lift_speed = 0
            '''
            if event.code == 2: #X axis on right stick
                turn_speed = scalestick(event.value)
                if abs(turn_speed) < 15: #deadzone
                    turn_speed = 0
            '''
            if event.code == 5: #Y axis on right stick
                right_speed = -scalestick(event.value)
            '''

        if event.type == 1 and event.code == 302 and event.value == 1:
            print "X button is pressed. Break."
            running = False
            time.sleep(1) # Wait for the motor thread to finish
            break
