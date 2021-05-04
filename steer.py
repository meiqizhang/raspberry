#!/usr/bin/python3
#encoding=utf-8

import time
import random
import RPi.GPIO as GPIO

class MyGPIO():
    init_count = 0
    mode = GPIO.BCM

    def __init__(self, idx, init_with_high):
        if MyGPIO.init_count == 0:
            GPIO.setmode(MyGPIO.mode)
        MyGPIO.init_count += 1
        self.idx = idx
        initial = GPIO.HIGH if init_with_high else GPIO.LOW
        GPIO.setup(self.idx, GPIO.OUT, initial=initial)

    def __del__(self):
        MyGPIO.init_count -= 1
        if MyGPIO.init_count == 0:
            GPIO.cleanup()

    def high(self):
        GPIO.output(self.idx, GPIO.HIGH)

    def low(self):
        GPIO.output(self.idx, GPIO.LOW)


class MyPWM(MyGPIO):
    def __init__(self, idx, frequency):
        super(MyPWM, self).__init__(idx, init_with_high=False)
        self.pwm = GPIO.PWM(idx, frequency)
        self.pwm.start(0)

    def chanage_duty_cycle(self, cycle):
        self.pwm.ChangeDutyCycle(cycle)

class Steer(object):
    frequency = 50 # 50HZ

    def angle2frequency(self, alpha):
        return int(alpha / 18. + 2.5)

    def __init__(self, idx):
        self.obj = MyPWM(idx, Steer.frequency)
        times = 10
        while times > 0:
            self.turn_angle(random.randint(0, 180))
            time.sleep(0.3)
            times -= 1
        self.turn_angle(90)
        time.sleep(1)

    def turn_angle(self, alpha):
        print("turn to %d angle" % alpha)
        self.obj.chanage_duty_cycle(self.angle2frequency(alpha))

def main():
    idx = 5
    steer = Steer(idx)
    while True:
        alpha = random.randint(0, 180)
        steer.turn_angle(alpha)
        time.sleep(1)

if __name__ == "__main__":
     main()
