import RPi.GPIO as GPIO
from opcua import ua, uamethod, Server
from opcua.common.type_dictionary_buider import DataTypeDictionaryBuilder, get_ua_class

import threading
import time
from datetime import datetime, timedelta

import re


if not GPIO.getmode():
    GPIO.setmode(GPIO.BOARD)
elif GPIO.getmode() == GPIO.BOARD:
    raise Warning('GPIO.mode was already set to BOARD somewhree else.')
elif GPIO.getmode() == GPIO.BOARD:
    raise Exception('GPIO.mode is set to BCM mode. This library needs BORD mode. I didn\'t try to change it ')
else:
    raise Exception('GPIO.mode is set to some unknown mode. This library needs BORD mode. I didn\'t try to change it ')


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
        self.selected = True
        self.on_time = 0.8
        self.off_time = 0.3
        self.finish_off = False
        self.count = 80000
        

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
        self._activity = threading.Event()
        self.bounce_time = 5000 #ms  takes the sensor about 5 sec to get stable readings. 

    @property
    def activity(self):
        return self._activity.is_set()

    @property
    def is_ready(self):    
        return not self._activity.is_set()

    def run(self): 
        GPIO.add_event_detect(self.pir_pin, GPIO.RISING, callback=self.callback)
        while True:
            self._activity.wait()
            time.sleep(self.bounce_time/1000)  
            if 0 == GPIO.input(self.pir_pin):
                self._activity.clear()
            pass

    def callback(self,pin):
        self._activity.set()    

class PickBox:
    def __init__(self,  pir_pin, led_pin, box_id, box_data:dict):
        self.box_id = box_id
        self.box_data = box_data
        self.box_data['id'] = self.box_id # double the info into the box data as well.
        self.__pir_pin = pir_pin
        self.__led_pin = led_pin
        self.selected = False
        self.b_idx = 'PickBox.' + str(box_id) 
        
        # GPIO setup
        GPIO.setup(self.__pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.__led_pin, GPIO.OUT)
        GPIO.setwarnings(False)

        # start the LED thread
        self.led_controller = LedThread(led_pin)
        self.led_controller.set_state(0)
        self.led_controller.start()

        # start the pir monitoring thread.
        self.pir_controller = PirThread(pir_pin)
        self.pir_controller.start()

    def create_select_node (self,node : ua.NodeReference):
        self.selected_node = node

    def set_content(self, content_id, content_count):
        self.box_data['content_id'] = content_id
        self.box_data['content_count'] = content_count
    
    def set_content_count(self, content_count):
        self.box_data['content_count'] = content_count

    def get_content(self):
        return (self.box_data['content_id'], self.box_data['content_count'])
    
    @run_async
    def select(self,timeout = None):
        # check if we are alreade selected 
        if self.selected : return True
        
        # else set flag 
        self.selected = True
        
        # Update opcua tag 
        self.selected_node.set_value(self.selected)

        #check if pir sensor is ready 
        if timeout:

            # remember when we start waiting for pir
            _time_before = datetime.now()
            _timeout  = _time_before + timedelta(seconds = timeout)

            # busy waiting for pir sensor (usually only short time so it doesn't matter it's busy waiting.)  
            while not self.pir_controller.is_ready:
                if datetime.now() >= _timeout:
                    # If main timeout while we wait for pir return false 
                    return False
                time.sleep(0.1)

            # calculate remaining timeout after waiting for pir sensor to get ready. 
            past_time = datetime.now() - _time_before
            timeout = timeout - past_time.total_seconds()

        # set LED parameters
        self.selected = True
        self.led_controler.on_time = 0.8
        self.led_controler.off_time = 0.3
        self.led_controler.finish_off = False
        self.led_controler.count = 80
        print('selected box %s, now waiting for pir sensor' % self.box_id)

        signal = self.pir_controller._activity.wait(timeout)
        if signal:
            print('pir detcted on box id: %s' % self.box_id)
        else:
            print('timeout: pir sensor on box id: %s' %self.box_id)
            pass 
        
        # set internal flag
        self.selected = False

        # Update opcua tag 
        self.selected_node.set_value(self.selected)
        
        # turn off LED
        self.led_controler.set_state(False)
        
        # Return success
        return signal

class PickByLight:
    def __init__(self,boxes, thingworx_name):
        self.boxes = boxes
        self.thingworx_name = thingworx_name  
        self.ua_server_setup()
        self.ua_parameter_dict = {}
        self.ua_method_dict = {}
        self._generate_tags()
        self.start_server()
        self._generate_subscriptions()

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

    def select_box_by_id(self, parent, id):
        try:
            self.boxes[id].select()
        except KeyError:
            print('404 box not found')  
    
    def start_server(self):
        self.server.start()

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        # reset the value 
        node.set_value(False)

        if val is True: 
            # get the node identifier string
            node_id = node.nodeid.Identifier
            
            #extract the boxid
            search = re.search('PickBox\\.(\\d)',node_id, re.IGNORECASE)
            box_id = search.group(1)

            # call the select method for the given box 
            self.boxes[int(box_id)].select()

    def event_notification(self, event):
        print("Python: New event", event)

    def _generate_subscriptions(self):
        for method_name, node in self.ua_method_dict.items():
            sub = self.server.create_subscription(200, self)
            handle = sub.subscribe_data_change(self.ua_method_dict[method_name])

    def _generate_tags(self):
        """private function that generates tags for all the pick boxes
        """
        # for boxid, box in all boxes list
        for b_id, box in self.boxes.items():

            # create an obejct in the pacml status object using our unique box idx
            b_obj = self.Status.add_object("ns=2;s=%s" % box.b_idx, box.b_idx)

            # create variables inside the newly created object.
            s_idx = box.b_idx + ".Selected"
            box.selected_node = b_obj.add_variable("ns=2;s=%s" % s_idx, 'Selected', box.selected, ua.VariantType.Boolean)
            box.selected_node.set_writable()

            # Create a tag for triggering the selection
            s_idx = box.b_idx + ".SelectMethod"
            b_var = b_obj.add_variable("ns=2;s=%s" % s_idx, 'SelectMethod', False, ua.VariantType.Boolean)
            b_var.set_writable()
            self.ua_method_dict[s_idx] = b_var

    def ua_server_setup(self):
        self.server = Server('./opcua_cache')

        self.server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/PickByLight')
        self.server.set_server_name("Pick By Light Server")

        # idx name will be used later for creating the xml used in data type dictionary
        # setup our own namespace, not really necessary but should as spec
        _idx_name = 'http://examples.freeopcua.github.io'
        self.idx =  self.server.register_namespace(_idx_name)
        
        #set all possible endpoint policies for clienst to connect through
        self.server.set_security_policy([
           	ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
            ua.SecurityPolicyType.Basic128Rsa15_Sign,
            ua.SecurityPolicyType.Basic256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256_Sign])

        # get Objects node, this is where we should put our custom stuff
        objects =  self.server.get_objects_node()
        # add a PackMLObjecs folder
        self.pml_folder =  objects.add_folder(self.idx, "PackMLObjects")
        # Get the base type object
        types =  self.server.get_node(ua.ObjectIds.BaseObjectType)
        # Create a new type for PackMLObjects
        self.PackMLBaseObjectType =  types.add_object_type(self.idx, "PackMLBaseObjectType")
        self.Admin =  self.pml_folder.add_object(self.idx, "Admin", self.PackMLBaseObjectType.nodeid)
        self.Status =  self.pml_folder.add_object(self.idx, "Status", self.PackMLBaseObjectType.nodeid)
        

        ## Create a method on opcua TODO insert the cerrect callback function.
        #self.select_method = self.pml_folder.add_method(self.idx,'select_box_by_id', self.select_box_by_id, [ua.VariantType.Int64], [ua.VariantType.Boolean])



if __name__ == '__main__':
    pass