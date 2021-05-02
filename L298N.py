#!/usr/bin/python
#encoding=utf-8

import time
import RPi.GPIO as GPIO

class MyGPIO():
    init_count = 0
    mode = GPIO.BOARD

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
        print("put %d high" % self.idx)
        GPIO.output(self.idx, GPIO.HIGH)

    def low(self):
        print("put %d low" % self.idx)
        GPIO.output(self.idx, GPIO.LOW)


class Wheel():
    def __init__(self, p_idx, n_idx, enable_idx):
        self.p = MyGPIO(p_idx, init_with_high=True)
        self.n = MyGPIO(n_idx, init_with_high=True)
        self.enable = MyGPIO(enable_idx, init_with_high=False)
        self.pwma = GPIO.PWM(enable_idx, 80)
        self.pwma.start(10)


    def forward(self):
        self.p.high()
        self.n.low()
        self.pwma.ChangeDutyCycle(99)

def main():
    wheel = Wheel(35, 37, 40)
    wheel.forward()
    time.sleep(20)

if __name__ == "__main__":
     main()
