#!/usr/bin/python3
#encoding=utf-8

import time
import RPi.GPIO as GPIO

class MyGPIO():
    init_count = 0
    mode = GPIO.BCM

    def __init__(self, idx, init_with_output, init_with_high=False):
        if MyGPIO.init_count == 0:
            GPIO.setmode(MyGPIO.mode)
        MyGPIO.init_count += 1

        if init_with_output: # 只有在输出的时候才可能会设置输出为高/低
            initial_status = GPIO.HIGH if init_with_high else GPIO.LOW
            GPIO.setup(idx, GPIO.OUT, initial=initial_status)
        else:
            GPIO.setup(idx, GPIO.IN)
        self.idx = idx

    def __del__(self):
        MyGPIO.init_count -= 1
        if MyGPIO.init_count == 0:
            GPIO.cleanup()

    def high(self):
        GPIO.output(self.idx, GPIO.HIGH)

    def low(self):
        GPIO.output(self.idx, GPIO.LOW)

    def input(self):
        return GPIO.input(self.idx)


class Measure():
    def __init__(self, idx1, idx2):
        self.trig = MyGPIO(idx1, init_with_output=True, init_with_high=False)
        self.echo = MyGPIO(idx2, init_with_output=False)

    def measure(self):
        self.trig.high()
        time.sleep(0.00001) #1us
        self.trig.low()

    	#start recording
        while self.echo.input() == 0:
            pass
        start=time.time()

    	#end recording
        while self.echo.input() == 1:
            pass
        end=time.time()
 
        #compute distance
        return round((end - start) * 343 / 2 * 100, 2)


def main():
    m = Measure(19, 26)
    while True:
        print(m.measure())
        time.sleep(1)

if __name__ == "__main__":
     main()
