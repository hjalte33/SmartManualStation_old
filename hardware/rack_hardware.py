from itertools import zip_longest
from hardware.port_dummy import Port

class RackHardware:
    def __init__(self,name, ports, boxes = [] ):

        self._port_sterilizer(ports)
        
        # create dict for the rack. Zip_longest pads with None if there's no boxes in the list of boxes.
        self.ports = {port.port_number : {"port":port, "box":box} for port, box in zip_longest(ports,boxes)}
        self.name = name

    def _port_sterilizer(self, ports):        
    # Detect if the ports are just a list of port numbers. If that's the case 
    # then convert it to a list of actual ports. 
        if ports[0] == int:
            _ports = []
            [_ports.append(Port(port_number)) for port_number in ports]
            ports = _ports
        else:
            for port in ports:
                if type(port) != Port:
                    raise TypeError("Expected a list of ports but got: ", type(port), port)

    def get_port_numbers(self):
        return self.ports.keys()

    def get_port(self,port_number):
        return self.ports[port_number]["port"]
    
    def get_box(self, port_number):
        return self.ports[port_number]["box"]
    
    def get_boxes(self):
        return [val["box"] for val in self.ports.values()]
    
    def get_ports(self):
        return [val["port"] for val in self.ports.values()]
    
    def attach_box_port(self, box, port):
        if port in self.ports:
            self.ports[port] = box
        else :
            raise KeyError('port number: ' + port + ' is not on this rack')
    
    def clear_port(self, port):
        self.attach_box_port(port, None)



