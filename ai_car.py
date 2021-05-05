#!/usr/bin/python3
#encoding=utf-8

import time
import random
import RPi.GPIO as GPIO



class MyGPIO():
    init_count = 0
    mode = GPIO.BCM

    def __init__(self, idx, init_with_output, init_with_high=False):
        self.idx = idx
        if idx is None:
            return

        if MyGPIO.init_count == 0:
            GPIO.setmode(MyGPIO.mode)
        MyGPIO.init_count += 1

        if init_with_output: # 只有在输出的时候才可能会设置输出为高/低
            initial_status = GPIO.HIGH if init_with_high else GPIO.LOW
            GPIO.setup(idx, GPIO.OUT, initial=initial_status)
        else:
            GPIO.setup(idx, GPIO.IN)

    def __del__(self):
        if self.idx is None:
            return
        MyGPIO.init_count -= 1
        if MyGPIO.init_count == 0:
            GPIO.cleanup()

    def high(self):
        if self.idx is not None:
            GPIO.output(self.idx, GPIO.HIGH)

    def low(self):
        if self.idx is not None:
            GPIO.output(self.idx, GPIO.LOW)

    def input(self):
        if self.idx is not None:
            return GPIO.input(self.idx)

class MyPWM(MyGPIO):
    def __init__(self, idx, frequency):
        super(MyPWM, self).__init__(idx, init_with_output=True, init_with_high=False)
        self.pwm = GPIO.PWM(idx, frequency)
        self.pwm.start(0)

    def chanage_duty_cycle(self, cycle):
        self.pwm.ChangeDutyCycle(cycle)

class DistanceManager(object):
    steer_frequency = 50 # 50HZ
    def __init__(self, idx, idx_r=None, idx_g=None, idx_b=None, idx_trig=None, idx_ping=None):
        self.steer = MyPWM(idx, DistanceManager.steer_frequency)
        self.led_r = MyGPIO(idx_r, True)
        self.led_g = MyGPIO(idx_g, True)
        self.led_b = MyGPIO(idx_b, True)
        self.delt = 12

        self.trig = MyGPIO(idx_trig, init_with_output=True, init_with_high=False)
        self.echo = MyGPIO(idx_ping, init_with_output=False)

        leds = [self.led_r, self.led_g, self.led_b]
        times = 8
        while times > 0:
            self.turn_angle(random.randint(0, 180))
            for led in leds:
                led.low()
            leds[random.randint(0, 2)].high()
            time.sleep(0.2)
            times -= 1
        self.turn_angle(90)
        [led.low() for led in leds]
        self.led_r.high()
        time.sleep(0.2)

    def set_delt(self):
        pass

    def angle2frequency(self, alpha):
        alpha += self.delt
        if alpha < 0:
            alpha = 0
        alpha %= 180

        return round(alpha / 18. + 2.5)

    def calc_distance(self, alpha):
        self.turn_angle(alpha)
        time.sleep(0.2)

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
        end = time.time()
        return round((end - start) * 343 / 2 * 100, 2)

    def turn_angle(self, alpha):
        self.steer.chanage_duty_cycle(self.angle2frequency(alpha))

class Wheel():
    def __init__(self, p_idx, n_idx, ctrl_idx=None):
        self.p = MyGPIO(p_idx, init_with_output=True, init_with_high=True)
        self.n = MyGPIO(n_idx, init_with_output=True, init_with_high=True)
        self.ctrl = MyPWM(ctrl_idx, frequency=50)
        self.speed = 0

    def set_speed(self, speed):
        self.speed = speed

    def stop(self):
        self.p.high()
        self.n.high()

    def forward(self, speed):  # 正向
       self.p.high()
       self.n.low()
       self.ctrl.chanage_duty_cycle(speed)

    def reverse(self, speed):
        self.p.low()
        self.n.high()
        self.ctrl.chanage_duty_cycle(speed)

    def fire(self):
        while True:
            pass

class Car(object):
    def __init__(self, w1_idxs, w2_idxs, w3_idxs, w4_idxs, steer_idx=None, idx_trig=None, idx_ping=None,
                       steer_led_r=None, steer_led_g=None, steer_led_b=None):
        self.w1 = Wheel(w1_idxs[0], w1_idxs[1], 27)
        self.w2 = Wheel(w2_idxs[0], w2_idxs[1], 22)
        self.w3 = Wheel(w3_idxs[0], w3_idxs[1], 17)
        self.w4 = Wheel(w4_idxs[0], w4_idxs[1], 4)

        if steer_idx is not None:
            self.distance_manager = DistanceManager(steer_idx, idx_trig=idx_trig, idx_ping=idx_ping, idx_r=steer_led_r, idx_g=steer_led_g, idx_b=steer_led_b)

    def forward(self, speed):
        self.w1.forward(speed)
        self.w2.forward(speed)
        self.w3.forward(speed)
        self.w4.forward(speed)

    def turn_left(self):
        speed = 90
        self.w1.reverse(speed)
        self.w3.reverse(speed)
        self.w2.forward(speed)
        self.w4.forward(speed)

    def turn_right(self):
        speed = 90
        self.w1.forward(speed)
        self.w3.forward(speed)
        self.w2.reverse(speed)
        self.w4.reverse(speed)

    def stop(self):
        self.w1.stop()
        self.w2.stop()
        self.w3.stop()
        self.w4.stop()

    def run(self):
        dist = self.distance_manager.calc_distance(145)
        print(dist)
        #return

        while True:
            min_dist = 0xFFFF
            angles = [10, 30, 50, 70, 110, 130, 150, 90]
            self.stop()
            for alpha in angles:
                dist = self.distance_manager.calc_distance(alpha)
                print("turn %d angle, dist=%d" % (alpha, dist))
                time.sleep(0.1)
                if dist < min_dist:
                    min_dist = dist

            print("min dist=%.2fcm" % (min_dist))

            if min_dist > 20:
                if min_dist > 100: # 15cm
                    self.forward(90)
                elif min_dist > 50:
                    self.forward(60)
                else:
                    self.forward(30)
                time.sleep(0.8)
            else:
                # check left
                dist = self.distance_manager.calc_distance(1)
                self.turn_right()
                time.sleep(0.5)


def main():
    #w = Wheel(18, 23, 4)
    #w.forward(50)
    #time.sleep(10)

    w1 = [12, 16]
    w2 = [21, 20]
    w3 = [25, 24]
    w4 = [18, 23]

    steer_idx = 5
    steer_led_r = 13
    steer_led_g = 6
    idx_trig = 19
    idx_ping = 26

    car = Car(w1, w2, w3, w4, steer_idx, steer_led_r=steer_led_r, steer_led_g=steer_led_g, idx_trig=19, idx_ping=26)
    car.run()


if __name__ == "__main__":
    main()
