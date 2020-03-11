from hardware.port_dummy import Port
from hardware.box import Box
from threading import Thread
from datetime import datetime, timedelta
from itertools import zip_longest


class RackController(Thread):
    def __init__ (self,name, ports, boxes = []):
        self._port_sterilizer(ports)
        # create dict for the rack. Zip_longest pads with None if there's no boxes in the list of boxes.
        self.ports = {port.port_number : port for port in ports}
        self.boxes = {port.port_number : box for port, box in zip_longest(ports,boxes)}
        self.name = name
        self.selected_ports = []
        self.light_last_cycle = datetime.now()
        self.light_state = False

    def run(self):
        self._light_selected_ports()
        pass 

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

    selected_light_period = timedelta(milliseconds = 1000)
    def _light_selected_ports(self):
        # If nothing is selected, prepare for on cycle right away 
        if not self.selected_ports:
            self.light_state = True
            self.light_last_cycle = datetime.now()
            return

        # Check if it's time to cycle on/off
        if datetime.now() > self.light_last_cycle + type(self).selected_light_period:
            self.light_state = not self.light_state
            self.light_last_cycle = datetime.now()
        
        # Finally write the state to all the ports. 
        for port_dict in self.selected_ports:
            port_dict["port"].set_light(self.light_state)  
    
    def _get_activities(self):
        out_list = []
        for port in self.ports.values():
            if port.activity:
                out_list.append(port)


    def select_port(self, port_number, amount = 1, callback = None, auto_deselect = True):
        port = self.ports.get(port_number)
        box = self.boxes.get(port_number)
        #check if the box is there and that there's enough content. 
        if port and box and box.content_count >= amount: 
            kwargs = {"port":port, "amount" : amount, "callback": callback, "auto_deselect": auto_deselect}
            self.selected_ports.append(kwargs)
            return True
        else:
            return False

    def select_content_id(self, content_id, amount = 1, callback = None, auto_deselect = True):
        # TODO find the box on the rack with the given content id
        pass

    def select_box_id(self, box_id, amount = 1, callback = None, auto_deselect = True):
        # TODO find the port that has this box_id
        pass
    
    def attach_box_port(self, box, port):
        if port in self.boxes.keys():
            self.boxes[port] = box
        else :
            raise KeyError('port number: ' + port + ' is not on this rack')
    
    def clear_port(self, port):
        self.attach_box_port(port, None)