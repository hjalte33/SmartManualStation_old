
import RPi.GPIO as GPIO

if not GPIO.getmode():
    GPIO.setmode(GPIO.BCM)

import threading
import time

class PickBox:

    def __init__(self, pir_pin, led_pin, position_id = 0):
        self.position_id = position_id
        self.pir_pin = pir_pin
        self.led_pin = led_pin

        GPIO.setup(self.pir_pin, GPIO.IN)
        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.setwarnings(False)

        # create the led thread, keep a reference to it for when we need to exit
        self.__thread = threading.Thread(name='led_blink',target=self.__led_thread, daemon=True)
        # start the thread
        self.__thread.start()

    def set_content(self, content_id):
        pass
    
    def get_content(self):
        return True #the content

    def get_trigger(self):
        pass
    
    def blink(self ): 
        pass

    def __led_thread(self, frequency = 5, seconds = 0, finish_off = True):
        t = threading.current_thread()
        t_end = time.time() + seconds
        while getattr(t,"stop",True):
            GPIO.output(self.led_pin, GPIO.HIGH)
            if not finish_off and seconds and time.time() > t_end:
                break

            time.sleep(1/frequency)
            GPIO.output(self.led_pin, GPIO.LOW)

            if finish_off and seconds and time.time() > t_end:
                break
            time.sleep(1/frequency)

    def calibrate(self):
        pass
