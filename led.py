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
        GPIO.output(self.idx, GPIO.HIGH)

    def low(self):
        GPIO.output(self.idx, GPIO.LOW)


class Led():
    def __init__(self, idx):
        self.gpio = MyGPIO(idx, False)

    def turn_on(self):
        self.gpio.high()

    def turn_off(self):
        self.gpio.low()


class LedArray():
    def __init__(self, idxs=list()):
        self.leds = list()
        for idx in idxs:
            self.leds.append(Led(idx))

    def flash(self, interval_seconds=1, time_seconds=10):
        while time_seconds > 0:
            for led in self.leds:
                led.turn_on()
            time.sleep(interval_seconds)

            for led in self.leds:
                led.turn_off()
            time.sleep(interval_seconds)
            time_seconds -= interval_seconds * 2

    def marquee(self, interval_seconds=1, time_seconds=10):
        while time_seconds > 0:
            for led in self.leds:
                led.turn_on()
                time.sleep(interval_seconds)
                led.turn_off()
                time_seconds -= interval_seconds
        

def main():
    idxs = [32, 36, 38, 40]
    leds = LedArray(idxs)
    leds.flash(interval_seconds=0.5, time_seconds=10)
    leds.marquee(interval_seconds=0.1, time_seconds=10)


if __name__ == "__main__":
     main()
