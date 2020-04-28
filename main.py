#!/usr/bin/env python3

from logic import rack_controller as rc
from configs import boxes_warehouse
from time import sleep
from interfaces import virtual_pbl, ua_server, festo_connect

if __name__ == "__main__":

    # Get some shiny boxes from warehouse
    boxes = boxes_warehouse.get_boxes()
    boxes = [box for box in boxes.values()]
    boxes = boxes[0:5]

    rack = rc.RackController([1,2,3,4,5], boxes)
    rack.start()
    
    my_server = ua_server.UAServer(rack)
    my_festo = festo_connect.FestoServer(rack,"localhost").start()
    my_virtual = virtual_pbl.VirtualPBL(rack).start()


    
    try:
        while True:
            
            sleep(1)
    except KeyboardInterrupt:
        my_virtual.stop()
        print('interrupted!')




