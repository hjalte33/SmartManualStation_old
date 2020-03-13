from datetime import datetime, timedelta
from random import randint
from time import sleep
from threading import Thread

class Port:
    def __init__(self,port_number):
        self.port_number = port_number
        self.activity_timestamp = datetime.now() - timedelta(minutes=10) # arbritraty time in the past. 
        self.cooldown_time = timedelta(seconds = 5)
        self._light_state = 0
        
        Thread(target=self._pir_dummy_thread, daemon=True).start()

    @property
    def activity(self):
        return datetime.now() < self.activity_timestamp + self.cooldown_time

    @property
    def time_since_activity(self):
        return datetime.now() - self.activity_timestamp

    def set_light(self, state):
        self._light_state = state
        print("The light on port: ", self.port_number, " is set to:" , self._light_state)
    
    def get_light(self) -> bool:
        return self._light_state
    
    def _pir_dummy_thread(self):
        while True:
            sleep(randint(5,30))
            print("wohoo! there's something going on heeer: ", self.port_number)
            self.activity_timestamp = datetime.now()






