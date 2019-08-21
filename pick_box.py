
import RPi.GPIO as GPIO

if not GPIO.getmode():
    GPIO.setmode(GPIO.BCM)
elif GPIO.getmode() == GPIO.BCM:
    raise Warning('GPIO.mode was already set to BCM somewhree else.')
elif GPIO.getmode() == GPIO.BOARD:
    raise Exception('GPIO.mode is set to BOARD mode. This library needs BCM mode. didn\'t try to change it ')
else:
    raise Exception('GPIO.mode is set to some unknown mode. This library needs BCM mode. didn\'t try to change it ')

import threading
import time


def run_async(func):
	"""
		run_async(func)
			function decorator, intended to make "func" run in a separate
			thread (asynchronously).
			Returns the created Thread object

			E.g.:
			@run_async
			def task1():
				do_something

			@run_async
			def task2():
				do_something_too

			t1 = task1()
			t2 = task2()
			...
			t1.join()
			t2.join()
	"""
	from threading import Thread
	from functools import wraps

	@wraps(func)
	def async_func(*args, **kwargs):
		func_hl = Thread(target = func, args = args, kwargs = kwargs, daemon=True)
		func_hl.start()
		return func_hl

	return async_func

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

    def blink(self,**kwarg):
        raise Warning('blink function not implemented yet. Doing nothing.')

    def run(self):
        while True:
            self.cal_count()
            sleep(0.1)
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
    def __init__(self,pir_pin,threshold = 0.3):
        '''constructor'''
        threading.Thread.__init__(self)
        self.daemon = True
        self.pir_pin = pir_pin
        self.threshold = threshold
        self.activity_count = 0.0
        self.sleep_time = 100 #ms


    def run(self):
        GPIO.add_event_detect(self.pir_pin, GPIO.BOTH, callback=self.pin_callback, bouncetime=self.sleep_time)
        while self.activity_count < self.threshold:
            sleep(1 - self.activity_count)
            if self.activity_count > 0 : 
                self.activity_count -= 0.1 
            
    def pin_callback(self,pin):
        self.activity_count += 0.1
       

class PickBox:
    def __init__(self, pir_pin, led_pin, box_id = 0):
        self.box_id = box_id
        self.__pir_pin = pir_pin
        self.__led_pin = led_pin

        GPIO.setup(self.__pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.__led_pin, GPIO.OUT)
        GPIO.setwarnings(False)

        self.led_controler = LedThread(led_pin)
        self.led_controler.start()
        self.led_controler.set_state(False)

        self.content_id = ""
        self.content_count = 0

    def set_content(self, content_id, content_count):
        self.content_id = content_id
        self.content_count = content_count
    
    def set_content_count(self, content_count):
        self.content_count = content_count

    def get_content(self):
        return (self.content_id, self.content_count)
    
    #@run_async
    def select(self,amount=1):
        self.led_controler.on_time = 0.5
        self.led_controler.off_time = 0.5
        self.led_controler.finish_off = False
        self.led_controler.count = 20
        print('selected box %s, now waiting for pir sensor', self.position_id)
        pir_wait = PirThread(self.__pir_pin, 0.2)
        pir_wait.start()
        pir_wait.join()
        print('pir detcted')
        self.led_controler.set_state(False)

    def calibrate(self):
        pass


if __name__ == '__main__':
    from time import sleep
    instance = PickBox(17,18)
    instance.select()
