from logic import rack_controller as rc
from configs import boxes_warehouse
from time import sleep


if __name__ == "__main__":

    # Get some shiny boxes from warehouse
    boxes = boxes_warehouse.get_boxes()
    boxes = [box for box in boxes.values()]
    boxes = boxes[0:5]

    rack = rc.RackController([1,2,3,4,5], boxes)
    rack.start()
    
    try:
        while True:
            port_number = int(input("type in port to select"))
            rack.select_port(port_number)
            sleep(1)
    except KeyboardInterrupt:
        print('interrupted!')



