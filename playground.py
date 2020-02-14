from time import sleep

#################################################################

class Dummy:
    def __getattr__(self, name):
        print ('iran')
        return "heyy"
    
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(32, GPIO.OUT)

#i = Dummy()
#setattr(i,'something','goodday')
#print (i.something)

################################################################
import RPi.GPIO as GPIO

#i = Dummy()

GPIO.output(32, True)

sleep(10)
GPIO.cleanup()



