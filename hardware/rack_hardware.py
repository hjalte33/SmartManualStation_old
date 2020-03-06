from itertools import zip_longest

class RackHardware:
    def __init__(self,name, ports, boxes = [], ):
        # create dict for the rack. Zip_longest pads with None if there's no boxes in the list of boxes.
        self.ports = {port.port_number:{"port":port, "box":box} for port, box in zip_longest(ports,boxes)}
        self.name = name

    def get_ports(self):
        return self.ports.keys()
    
    def get_boxes(self):
        return [val["box"] for val in self.ports.values()]
    
    def attach_box_port(self, port, box):
        if hasattr(self.ports, port):
            self.ports[port] = box
        else :
            raise KeyError('port number not on this rack')
    
    def clear_port(self, port):
        self.attach_box_port(port, None)



