from datetime import datetime, timedelta
from random import randint
from time import sleep
from threading import Thread

class Port:
    def __init__(self,port_number):
        self.port_number = port_number
        self.activity_timestamp = datetime()
        self._cooldown_time = timedelta(5)
        self._led_state = 0
        
        Thread(target=self._pir_dummy_thread, daemon=True).start()

    @property
    def activity(self):
        if datetime.now() < self.activity_timestamp + self._cooldown_time:
            return True
        else:
            return False

    @property
    def time_since_activity(self):
        return datetime.now() - self.activity_timestamp
    
    def set_signal(self, state):
        _led_state = state
        print("led on port: ", self.port_number, " set to:" , self._led_state)
    
    def get_signal(self) -> bool:
        return self._led_state
    
    def _pir_dummy_thread(self):
        sleep(randint(3,30))
        print("wohoo! there's something going on heeer: ", self.port_number)
        self.activity_timestamp = datetime.now()






