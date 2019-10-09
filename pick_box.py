
import RPi.GPIO as GPIO
from opcua import ua, Server
import threading
import time
from datetime import datetime, timedelta
import packml

if not GPIO.getmode():
    GPIO.setmode(GPIO.BCM)
elif GPIO.getmode() == GPIO.BCM:
    raise Warning('GPIO.mode was already set to BCM somewhree else.')
elif GPIO.getmode() == GPIO.BOARD:
    raise Exception('GPIO.mode is set to BOARD mode. This library needs BCM mode. didn\'t try to change it ')
else:
    raise Exception('GPIO.mode is set to some unknown mode. This library needs BCM mode. didn\'t try to change it ')




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
            time.sleep(0.1)
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
        self.activity = threading.Event()
        self.bounce_time = 4000 #ms  takes the sensor about 5 sec to get stable readings. 

    @property
    def is_ready(self):    
        return not self.activity.is_set()

    def run(self): 
        GPIO.add_event_detect(self.pir_pin, GPIO.RISING, callback=self.callback)
        while True:
            self.activity.wait()
            time.sleep(self.bounce_time/1000)  
            if 0 == GPIO.input(self.pir_pin):
                self.activity.clear()
            pass

    def callback(self,pin):
        self.activity.set()    
       

class PickBox:
    def __init__(self, pir_pin, led_pin, box_id = None, box_name = None, content_id = None, content_count = None):
        self.box_id = box_id
        self.box_name = box_name
        self.content_id = content_id
        self.content_count = content_count
        self.__pir_pin = pir_pin
        self.__led_pin = led_pin
        self.selected = False
        
        # GPIO setup
        GPIO.setup(self.__pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.__led_pin, GPIO.OUT)
        GPIO.setwarnings(False)

        # start the LED thread
        self.led_controler = LedThread(led_pin)
        self.led_controler.set_state(0)
        self.led_controler.start()

        # start the pir monitoring thread.
        self.pir_controller = PirThread(pir_pin)
        self.pir_controller.start()

    def set_content(self, content_id, content_count):
        self.content_id = content_id
        self.content_count = content_count
    
    def set_content_count(self, content_count):
        self.content_count = content_count

    def get_content(self):
        return (self.content_id, self.content_count)
    
    @run_async
    def select(self,amount=1,timeout = None):
        if type(timeout) == ua.Variant:
            timeout = timeout.Value

        # check if we are alreade selected 
        if self.selected : return True
        
        # else set flag 
        self.selected = True

        #check if pir sensor is ready 
        if timeout:

            # remember when we start waiting for pir
            _time_before = datetime.now()
            _timeout  = _time_before + timedelta(seconds = timeout)

            # busy waiting for pir sensor (usually only short time so it doesn't matter it's busy waiting.)
            while not self.pir_controller.is_ready:
                if datetime.now() >= _timeout:
                    return False
                time.sleep(0.1)

            # calculate remaining timeout after waiting for pir sensor to get ready. 
            past_time = datetime.now() - _time_before
            timeout = timeout - past_time.total_seconds()

        # set LED parameters
        self.selected = True
        self.led_controler.on_time = 0.5
        self.led_controler.off_time = 0.5
        self.led_controler.finish_off = False
        self.led_controler.count = 20
        print('selected box %s, now waiting for pir sensor' % self.box_id)
        
        #update opc-ua
        self.a_var.set_value(True)

        signal = self.pir_controller.activity.wait(timeout)
        if signal:
            print('pir detcted on box id: %s' % self.box_id)
        else:
            print('timeout: pir sensor on box id: %s' %self.box_id)
            pass 
        # set internal flag
        self.selected = False
        
        # update opc-ua
        self.a_var.set_value(False)
        
        # turn off LED
        self.led_controler.set_state(False)
        
        # Return success
        return signal

    def calibrate(self):
        pass

class PickByLight:
    def __init__(self,boxes, thingworx_name):
        self.boxes = boxes
        self.thingworx_name = thingworx_name
        self.packml_instance = PackML()

        #create an OPC name
        opc_name = self.thingworx_name
       
        # create an obejct in the pacml using our unique name
        self.packml_obj = self.packml_instance.add_object(opc_name)

        # create a variable inside the newly created object.
        self.a_var = self.packml_obj.add_variable(self.packml_instance.idx, 'selected', False)

        #create a method on opcua
        select_method = self.packml_obj.add_method(self.packml.idx,'select', self.select, [ua.VariantType.Int64], [ua.VariantType.Boolean])
    
    def get_box_by_name(self, name):
        pass
    
    def get_box_by_id(self, id):
        pass

    def set_box_by_id(self, id, **kwargs):
        pass

    def set_box_by_name(self, name, **kwargs):
        pass

    def selet_box_by_name(self, name):
        pass

    def select_box_by_id(self, id):
        pass





if __name__ == '__main__':
    from time import sleep
    from packml import PackML
    packml = PackML()
    instance = PickBox(packml,pir_pin = 20,led_pin = 21)
    packml.start_server()
    instance.select(timeout=10)
    sleep (30)
    packml.server.stop()
