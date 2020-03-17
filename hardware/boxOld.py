from configs import pins
import RPi.GPIO as GPIO
from time import sleep
import os,binascii

class NewBox:
    def __init__(self, box_id = ""):
        self.content = {}
        self.box_id = binascii.b2a_hex(os.urandom(8)) # generate 8 random charaters 


class BoxLogic:
    def __init__(self, hardware, **kwargs):
        self.port_number  = -1
        self.box_id   = binascii.b2a_hex(os.urandom(8)) # generate 8 random charaters 
        self.selected     = False
        self.pir_activity = False
        self.wrong_pick   = False
        self.content_count = {}     # dict containing the content ids and the amounts.
                                    # example for containing 3 item with various amounts 
                                    # {"aaaa" : 5, "bbbb" : 3, "cccc" : 10} 
        
        # if kwargs passed in overwrite the defaults 
        if kwargs: self.update(**kwargs)
    
    def update(self,**kwargs):
        for key, value in kwargs.items():
            if not hasattr(self,key):
                raise AttributeError("attribute not part of BoxState: ", key, value)                            
            else:
                setattr(self, key, value)


class BoxOld:
    """Simple class holding all the basic functions needed for a single pick box
    
    Raises:
        ValueError: raise exception if wrong args are passed. 
    """
    def __init__(self):
        # Set identification attributes
        self.box_state = box_state

        #get the pins from the global pins list.
        self.led_pin, self.pir_pin = pins.get_pins(box_state.port_number)      

        # GPIO setup
        GPIO.setup(pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(led_pin, GPIO.OUT)

        # Add interupt and callback function when there's a change on the pir pin. 
        GPIO.add_event_detect(self.pir_pin, GPIO.BOTH, callback=self._pir_callback)

    def _pir_callback(self,pin):
        #TODO check if the sleeper can actually work directly in this callback. 
        """Callback for activity on the pir sensor.
            This callback starts another sleeper thread that 
            sleeps a set amount of time too "cool down" the sensor
        
        Arguments:
            pin {int} -- pin number that triggered the callback 
        """
        if self.pir_ready:
            Thread(target=self.pir_sleeper, daemon=True, args=(pin,)).start()

    def pir_sleeper(self,pin):
        """Thread that sleeps while the pir is stabalizing.
        
        Arguments:
            pin {int} -- pin of trigger
        """ 
        pin_status = GPIO.input(self.pir_pin)
        if pin_status == 1:
            print('Pir detected on box: %s' % self.port_number)
            self.pir_activity = True
            self.pir_ready = False
            self.selected = False
            sleep(5) 
            # update the pin status  
            pin_status = GPIO.input(self.pir_pin)
        
        # always check again if pin status is 0 
        if pin_status == 0:
            self.pir_activity = False
        # finally set the pin ready flag 
        self.pir_ready = True

    def toggle_led(self):
        led_next = not GPIO.input(self.led_pin)
        GPIO.output(self.led_pin, led_next)
    
    def set_led(self, state):
        GPIO.output(self.led_pin, state)
    
    def get_led(self) -> bool:
        GPIO.input(self.led_pin)
    
    def get_id(self):
        return self.box_state.id





