from datetime import datetime, timedelta
from configs import pins
import RPi.GPIO as GPIO

class Port:
    def __init__(self,port_number):
        self.port_number = port_number
        self.activity_timestamp = datetime()
        self._cooldown_time = timedelta(5)
        
        # GPIO setup
        GPIO.setup(self._pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._led_pin, GPIO.OUT)

        # Add interupt and callback function when there's a change on the pir pin. 
        GPIO.add_event_detect(self._pir_pin, GPIO.HIGH, callback=self._pir_callback)
        pass

    @property
    def activity(self):
        if datetime.now() < self.activity_timestamp + self._cooldown_time:
            return True
        else:
            return False

    @property
    def time_since_activity(self):
        return datetime.now() - self.activity_timestamp
    
    def set_led(self, state):
        GPIO.output(self._led_pin, state)
    
    def get_led(self) -> bool:
        GPIO.input(self._led_pin)  


    def _pir_callback(self,pin):
        # if 5 sec passed since last activity
        if datetime.now() > self.activity_timestamp + self._cooldown_time:
            print('Pir detected high at port %s' % self.port_number)
            self.activity_timestamp = datetime.now()
    @property
    def _led_pin(self):
        pins.get_led_pin(self.port_number)
    
    @property
    def _pir_pin(self):
        pins.get_pir_pin(self.port_number)