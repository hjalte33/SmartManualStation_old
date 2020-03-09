import RPi.GPIO as GPIO
import simple_pick_by_light.simple_pbl as pbl
import simple_pick_by_light.ua_server as ua_server
import simple_pick_by_light.festo_connect as festo
from time import sleep


if __name__ == "__main__":

    pbl.init()
    ua_server.init()
    festo.init()


    try:
        
        while True:
            sleep(5)
    except KeyboardInterrupt:
        ua_server.ua_server.stop()
        GPIO.cleanup()
        print('interrupted!')
        festo.FestoServer.s.close()



