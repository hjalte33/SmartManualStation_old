from pick_box import PickBox, PickByLight
from time import sleep
import yaml
import warnings
#import packml
import ua_server





if __name__ == "__main__":


    boxes = read_config()

    pbl = PickByLight(boxes, 'Asset_AAUSmartPickByLight')


    sleep(900)



