import simple_pick_by_light.simple_pbl as pbl
import simple_pick_by_light.ua_server as ua_server
from time import sleep





if __name__ == "__main__":

    pbl.init()
    ua_server.init()


    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        ua_server.ua_server.stop()
        GPIO.cleanup()
        print('interrupted!')



