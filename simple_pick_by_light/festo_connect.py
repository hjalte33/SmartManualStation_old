from time import sleep
from threading import Thread, Event
from simple_pick_by_light import simple_pbl as pbl
from simple_pick_by_light.simple_pbl import Box

# setup tcpip server that the festo line can connect to. 
...

def init():
    # if any init code here 
    ...

    # start var update 
    updater = VarUpdater()
    updater.start()

def operation_number_handler(op_number):
    if op_number = 801:
        ... # select something
    elif op_number = 802:
        ... # do something else



class VarUpdater(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._stopev = False

    def stop(self):
        self._stopev = True

    def run(self):
        while not self._stopev:
            
            # for all boxes update tags
            for port, box in pbl.boxes.items():              
                # go through the public attributes on each box.  
                for attr, p_type in Box.public_attributes:     
 
            # update frequenzy 500 ms
            sleep(0.5)