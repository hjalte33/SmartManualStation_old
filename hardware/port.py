from datetime import datetime, timedelta
from configs import pins
import RPi.GPIO as GPIO

class Port:
    def __init__(self,port_number):
        self.port_number = port_number
        self.activity_timestamp = datetime()
        self._cooldown_time = timedelta(5)
        
        # GPIO setup
        GPIO.setup(self.pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.led_pin, GPIO.OUT)

        # Add interupt and callback function when there's a change on the pir pin. 
        GPIO.add_event_detect(self.pir_pin, GPIO.HIGH, callback=self._pir_callback)
        pass

    def _pir_callback(self,pin):
        # if 5 sec passed since last activity
        if datetime.now() > self.activity_timestamp + self._cooldown_time:
            print('Pir detected high at port %s' % self.port_number)
            self.activity_timestamp = datetime.now()

    @property
    def activity(self):
        if datetime.now() < self.activity_timestamp + self._cooldown_time:
            return True
        else:
            return False

    @property
    def led_pin(self):
        pins.get_led_pin(self.port_number)
    
    @property
    def pir_pin(self):
        pins.get_pir_pin(self.port_number)

    @property
    def time_since_activity(self):
        return datetime.now() - self.activity_timestamp
    
    def set_led(self, state):
        GPIO.output(self.led_pin, state)
    
    def get_led(self) -> bool:
        GPIO.input(self.led_pin)  



