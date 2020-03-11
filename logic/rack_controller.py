from hardware.port_dummy import Port
from hardware.box import Box
from threading import Thread
from datetime import datetime, timedelta
from itertools import zip_longest
from time import sleep


class RackController(Thread):
    def __init__ (self, ports, boxes = []):
        super().__init__(daemon = True)

        ports = self._port_sterilizer(ports)
        # create dict for the rack. Zip_longest pads with None if there's no boxes in the list of boxes.
        self.ports = {port.port_number : port for port in ports}
        self.boxes = {port.port_number : box for port, box in zip_longest(ports,boxes)}
        self.selected_ports = {}
        self.light_last_cycle = datetime.now()
        self.light_state = False

    def run(self):
        while True:
            self._light_selected_ports()
            self._monitor_activity()
            sleep(0.1)
            pass 

    def _port_sterilizer(self, ports):        
    # Detect if the ports are just a list of port numbers. If that's the case 
    # then convert it to a list of actual ports. 
        if type(ports[0]) == int:
            _ports = []
            [_ports.append(Port(port_number)) for port_number in ports]
            return _ports
        else:
            for port in ports:
                if type(port) != Port:
                    raise TypeError("Expected a list of ports but got: ", type(port), port)
            return ports

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
        for port_number in self.selected_ports:
            self.ports[port_number].set_light(self.light_state)  
    
    def _monitor_activity(self):
        # If nothing is selected, don't bother checking
        if not self.selected_ports:
            return
        
        for port_number in self.ports:   
            
            # if there's no activity i wont bother doing anything more
            if not self.ports[port_number].activity:
                continue
            
            if port_number in self.selected_ports:
                self._handle_pick(port_number)
            else:
                self._handle_wrong_pick(port_number)


    def _handle_pick(self,port_number):
        try:
            args = self.selected_ports[port_number]
            box = self.boxes[port_number]
            
            # If the amount is there go ahead and remove it from inventory 
            if box.content_count >= args["amount"]:
                box.rm_items(args["amount"])
            else:
                raise ValueError("Insufficient amount of items in box")
            
            # Should we just automatically deselct? 
            if args["auto_deselect"]:
                del self.selected_ports[port_number]

            # If we got a callback go ahead and call it 
            if args["callback"]:
                args["callback"](port_number)
        except KeyError as e:
            raise KeyError("Port {} not found. Must have been removed while selected.".format(port_number), e)


    def _handle_wrong_pick(self, port_number):
        print("wrong pick", port_number)


    def select_port(self, port_number, amount = 1, callback = None, auto_deselect = True):
        port = self.ports.get(port_number)
        box = self.boxes.get(port_number)
        #check if the box is there and that there's enough content. 
        if port and box and box.content_count >= amount: 
            kwargs = {"amount" : amount, "callback": callback, "auto_deselect": auto_deselect}
            # add port to the list of selected ports indexed by the port number. 
            self.selected_ports[port.port_number] = kwargs
            return True
        else:
            return False

    def select_content_id(self, content_id, amount = 1, callback = None, auto_deselect = True):
        # TODO find the box on the rack with the given content id
        pass

    def select_box_id(self, box_id, amount = 1, callback = None, auto_deselect = True):
        # TODO find the port that has this box_id
        pass
    
    def attach_box_port(self, box, port_number):
        if port_number in self.boxes:
            self.boxes[port_number] = box
        else :
            raise KeyError('port number: ' + port_number + ' is not on this rack')
    
    def clear_port(self, port):
        self.attach_box_port(port, None)