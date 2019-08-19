
import RPi.GPIO as GPIO

if not GPIO.getmode():
    GPIO.setmode(GPIO.BCM)

import threading
import time
from functools import reduce

class LedThread(threading.Thread):
    def __init__(self, led_pin):
        '''constructor'''
        threading.Thread.__init__(self)
        self.daemon = True
        self.led_pin = led_pin
        self.on_time = 1
        self.off_time = 1
        self.count = 0
        self.run_time = 0
        self.finish_off = False
        self.led_state = GPIO.input(self.led_pin)
   
    def set_state(self, state):
        self.count = self.run_time = 0
        GPIO.output(self.led_pin, state)

    def run(self):
        while True:
            self.cal_count()

            if self.count > 0 :
                if self.led_state:
                    GPIO.output(self.led_pin, GPIO.LOW)
                    self.led_state = False
                    time.sleep(self.off_time)
                else:
                    GPIO.output(self.led_pin, GPIO.HIGH)
                    self.led_state = True
                    time.sleep(self.on_time)
                self.count -= 1

    def cal_count(self):
        if self.run_time:
            cycles = (self.on_time + self.off_time) / self.run_time
            self.count = cycles * 2

        #check if the count and the finish condition matches         
        if self.finish_off != self.led_state and self.count % 2 != 0:
            self.count += 1
        
        # clear the runtime command
        self.run_time = 0

class PirThread(threading.Thread):
    def __init__(self,pir_pin):
        '''constructor'''
        threading.Thread.__init__(self)
        self.daemon = True
        self.pir_pin = pir_pin
        self.sample_frequency = 100
        self.trigger = False

        from math import floor 
        self.window_len = floor(self.sample_frequency/2)
        self.window = [0 for i in range(self.window_len)]
    
    def cyclic(self, max_len):
        index = 0
        while True:
            index += 1
            if index >= max_len:
                index = 0
            yield index

    def run(self):
        for i in self.cyclic(self.window_len):
            self.window[i] = GPIO.input(self.pir_pin) 
            sleep(1/self.sample_frequency)
            trigger = round(reduce(lambda a, b: a + b, self.window) / self.window_len )
            print(trigger)


class PickBox:

    def __init__(self, pir_pin, led_pin, position_id = 0):
        self.position_id = position_id
        self.__pir_pin = pir_pin
        self.__led_pin = led_pin

        GPIO.setup(self.__pir_pin, GPIO.IN)
        GPIO.setup(self.__led_pin, GPIO.OUT)
        GPIO.setwarnings(False)

        self.led_controler = LedThread(led_pin)
        self.led_controler.start()
        self.led_controler.set_state(False)

        self.pir_controler = PirThread(pir_pin)
        self.pir_controler.start()

    def set_content(self, content_id):
        pass
    
    def get_content(self):
        return True #the content

    def get_trigger(self):
        pass
    
    def select(self):
        pass

    def calibrate(self):
        pass


if __name__ == '__main__':
    from time import sleep
    instance = PickBox(17,18)
    sleep(15)