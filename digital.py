#!/usr/bin/python3
#encoding=utf-8

import time
import random
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


class Digital():
    #seg_idx = {'a': 4, 'b': 27, 'c': 26, 'd': 13, 'e': 6, 'f': 17, 'g': 22, 'dp': 19}
    seg_idx = {'a': 7, 'b': 13, 'c': 37, 'd': 33, 'e': 31, 'f': 11, 'g': 15, 'dp': 35}

    def __init__(self, postive_idx):
        self.postive = MyGPIO(postive_idx, init_with_high=True)
        self.seg_a = MyGPIO(Digital.seg_idx['a'], init_with_high=True)
        self.seg_b = MyGPIO(Digital.seg_idx['b'], init_with_high=True)
        self.seg_c = MyGPIO(Digital.seg_idx['c'], init_with_high=True)
        self.seg_d = MyGPIO(Digital.seg_idx['d'], init_with_high=True)
        self.seg_e = MyGPIO(Digital.seg_idx['e'], init_with_high=True)
        self.seg_f = MyGPIO(Digital.seg_idx['f'], init_with_high=True)
        self.seg_g = MyGPIO(Digital.seg_idx['g'], init_with_high=True)
        self.seg_dp = MyGPIO(Digital.seg_idx['dp'], init_with_high=True)
        self.all_segs = {
                            'a': self.seg_a, 'b': self.seg_b, 'c': self.seg_c, 'd': self.seg_d,
                            'e': self.seg_e, 'f': self.seg_f, 'g': self.seg_g, 'dp': self.seg_dp
                        }

    def off(self): # 对于关闭，只需将正极拉低即可
        self.postive.low()

    def show_segs(self, segs=list()): # 显示一个数字时，先将所有seg清空，再显示具体的
        for seg in self.all_segs:
            self.all_segs[seg].high()

        self.postive.high() # 正极拉高
        for seg in segs:
            self.all_segs[seg].low() # 负极拉低

    def wait(self):
        time.sleep(10)

    def show(self, num):
        segs = []
        if num == 0:
            segs = ['a', 'b', 'c', 'd', 'e', 'f']
        elif num == 1:
            segs = ['b', 'c']
        elif num == 2:
            segs = ['a', 'b', 'g', 'e', 'd']
        elif num == 3:
            segs = ['a', 'b', 'g', 'c', 'd']
        elif num == 4:
            segs = ['f', 'g', 'b', 'c']
        elif num == 5:
            segs = ['a', 'f', 'g', 'c', 'd']
        elif num == 6:
            segs = ['a', 'f', 'e', 'd', 'c', 'g']
        elif num == 7:
            segs = ['a', 'b', 'c']
        elif num == 8:
            segs = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        elif num == 9:
            segs = ['a', 'b', 'c', 'd', 'f', 'g']

        self.show_segs(segs)


class MultiDigital():
    def __init__(self, idx1, idx2, idx3, idx4):
        self.d1 = Digital(idx1)
        self.d2 = Digital(idx2)
        self.d3 = Digital(idx3)
        self.d4 = Digital(idx4)

    def show_a(self, num):
        self.d2.off()
        self.d3.off()
        self.d4.off()
        self.d1.show(num)

    def show_b(self, num):
        self.d1.off()
        self.d3.off()
        self.d4.off()
        self.d2.show(num)

    def show_c(self, num):
        self.d1.off()
        self.d2.off()
        self.d4.off()
        self.d3.show(num)

    def show_d(self, num):
        self.d1.off()
        self.d2.off()
        self.d3.off()
        self.d4.show(num)

    def show_num(self, num, show_time):
        num %= 10000
        n1 = int(num / 1000)
        n2 = int(num % 1000 / 100)
        n3 = int(num % 100 / 10)
        n4 = int(num % 10)

        print(n1, n2, n3, n4)
        sleep_seconds = 0.005
        while show_time > 0:
            self.show_a(n1)
            time.sleep(sleep_seconds)

            self.show_b(n2)
            time.sleep(sleep_seconds)

            self.show_c(n3)
            time.sleep(sleep_seconds)

            self.show_d(n4)
            time.sleep(sleep_seconds)

            show_time -= sleep_seconds * 4

class DigitalCount():
    def __init__(self):
        self.digitials = MultiDigital(32, 36, 38, 40)

    def run(self):
        last_time = time.time()
        count = 0
        while True:
            time_now = time.time()
            self.digitials.show_num(count, time_now + 0.05 - last_time)
            count += 1
            last_time = time.time()
        

def main():
    #digitals = MultiDigital()
    #while True:
    #    digitals.show_num(random.randint(0, 10000), 0.5)
    count = DigitalCount()
    count.run()

if __name__ == "__main__":
    main()
