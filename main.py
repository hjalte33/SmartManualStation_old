#!/usr/bin/python3

from logic import rack_controller as rc
from configs import boxes_warehouse

import argparse
import logging

from interfaces import virtual_pbl, ua_server, festo_connect

if __name__ == "__main__":



    parser = argparse.ArgumentParser(
        description='Manual Smart Station'
    )
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)


    # Get some shiny boxes from warehouse
    boxes = boxes_warehouse.get_boxes()
    boxes = [box for box in boxes.values()]
    boxes = boxes[0:6]

    rack = rc.RackController([1,2,3,4,5,6], boxes)
    rack.start()
    
    my_server = ua_server.UAServer(rack)
    #my_virtual = virtual_pbl.VirtualPBL(rack).start()
    my_festo = festo_connect.FestoServer(rack,"172.20.13.1").start()


    
    try:
        from time import sleep
        while True:
            
            sleep(1)
    except KeyboardInterrupt:
        my_virtual.stop()
        print('interrupted!')




