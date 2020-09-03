from hardware.port import Port
from hardware.box import Box

from threading import Thread
from datetime import datetime, timedelta
from itertools import zip_longest
from time import sleep
from collections import defaultdict
from typing import Callable

class PortState:
    def __init__(self, selected = False,
                       amount = 0,
                       callback : Callable[[int], None] = None, #dono if this works.
                       auto_light_off = True,
                ):
        self.selected = selected
        self.amount = amount
        self.callback = callback
        self.auto_light_off =  auto_light_off
        self.select_timestamp = datetime.fromtimestamp(0) # just some time long ago. 
        self.pick_timestamp = datetime.fromtimestamp(0)# just some time long ago
    
    @property
    def time_since_pick(self):
        return datetime.now() - self.pick_timestamp

    def update(self, **kwargs):
        for arg, value in kwargs.items():
            setattr(self,arg,value)


class RackController(Thread):
    def __init__ (self, ports, boxes = []):
        super().__init__(daemon = True)

        ports = self._port_sterilizer(ports)
        # create dict of all the port objects for the rack.
        self.ports = {port.port_number : port for port in ports}
        
        # Create a dict of all box objects. This "attaches" the boxes to the ports. 
        # Zip_longest pads with None if there's no boxes in the input list of boxes.
        self.boxes = {port.port_number : box for port, box in zip_longest(ports,boxes)}
        
        # Initialize the state of all boxes with default values. 
        self.ports_select_state = {port_number : PortState() for port_number in self.ports.keys()}
        
        self.wrong_activity_list = []
        self.light_last_cycle = datetime.now()
        self.rack_light_state = False   
        self.selected_light_period = timedelta(milliseconds = 1000)

    def run(self):
        while True:
            self._signal_selected_ports()
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
                    raise TypeError("Expected a list of ports or port numbers but got: ", type(port), port)
            return ports

    def _signal_selected_ports(self):
        # Filter out all the selected ports. We don't really care about none selected ports in this function. 
        every_selected = {port_number:state for port_number, state in self.ports_select_state.items() if state.selected}
        
        # If nothing is selected, prepare for on cycle right away so when something 
        # is selected then we turn on immediately. 
        if not every_selected:
            self.rack_light_state = True
            self.light_last_cycle = datetime.now()
            return

        # Check if it's time to cycle on/off
        if datetime.now() > self.light_last_cycle + self.selected_light_period:
            self.rack_light_state = not self.rack_light_state
            self.light_last_cycle = datetime.now()
        
        # Finally write the state to all the selected ports. 
        for port_number in every_selected:
            self.ports[port_number].set_light(self.rack_light_state)  

    def _wrong_activity_blinker(self,port_number):
        state = True
        while self.ports[port_number].activity:
            self.ports[port_number].set_light(state)
            state = not state
            sleep(0.333)  
        self.ports[port_number].set_light(False)
        self.wrong_activity_list.remove(port_number)

    def _monitor_activity(self):
        """Checks if there's activity on any of the ports and selects
            the appropriate function to run depending on the port_state.
        """
        # get every selected port. 
        every_selected = [port_number for port_number, state in self.ports_select_state.items() if state.selected]

        # If nothing is selected just stop doing any more checking. 
        if not every_selected:
            return

        # Go through ports and find activity
        for port_number, port_state in self.ports_select_state.items():
            # get the activity on the port. if no activity then just skip and take the next.
            if self.ports[port_number].activity is not True:
                continue # just skip the rest
            
            # If the port was marked as selected then go handle that. 
            if port_state.selected:
                self._handle_pick(port_number)
            # Else it must be a wrong pick 
            else:
                self._handle_wrong_activity(port_number)          

    def _handle_pick(self,port_number):
        try:
            port_state = self.ports_select_state[port_number]
            box = self.boxes[port_number]
            port = self.ports[port_number]
            
            # Deselect the port  #TODO use deselect function instead 
            port_state.selected = False
            
            # Set the timestamp for this pick
            port_state.pick_timestamp = datetime.now()

            # If auto light off is set then we turn off the light.
            if port_state.auto_light_off:
                port.set_light(False) # Turn off the light 

            # If the amount is there go ahead and remove it from inventory 
            if box.content_count >= port_state.amount:
                box.rm_items(port_state.amount)
            else:
                raise ValueError("Insufficient amount of items in box. Amount must somehow have changed since box was selected. This should normally not happen")
            
            # If we got a callback go ahead and call it 
            if port_state.callback is not None:
                port_state.callback(port_number)
                
        except KeyError as e:
            raise KeyError("Port {} not found. Must have been removed while selected.".format(port_number), e)

    def _handle_wrong_activity(self, port_number):
        # If no box is attached just ignore the sensor
        if not self.boxes.get(port_number):
            return 
        
        # if it's already in the list of wrong pick it is being taken care of. 
        if port_number in self.wrong_activity_list:
            return

        # Get the port and state to check if the activity is not just from 
        # a recent pick.    
        port = self.ports.get(port_number)
        port_state = self.ports_select_state.get(port_number)

        # If the cooldown time has not passed ignore this activity. The activity is just be from a recent pick.
        if port and port_state.time_since_pick < port.cooldown_time:
            return
        else:
            # add the port_number to the list of wrong activity
            self.wrong_activity_list.append(port_number)
            # Then start a little blinking thread to warn the user. 
            Thread(target=self._wrong_activity_blinker, daemon=True, args=(port_number,)).start()
            print("wrong pick", port_number)
        pass

    def select_port(self, port_number, amount = 1, callback = None, auto_light_off = True):
        # Check that the port is on this rack
        if port_number not in self.ports:
            raise KeyError("the port {} is not in this rack".format(port_number))

        # get the box on this port    
        box = self.boxes.get(port_number)

        if not box:
            raise ValueError("No box attached to this port.")

        #check if there's enough content. 
        if box.content_count >= amount: 
            kwargs = {"selected": True,
                      "amount" : amount, 
                      "callback": callback, 
                      "auto_light_off": auto_light_off,
                      "select_timestamp": datetime.now()}
            # Update port status
            self.ports_select_state[port_number].update(**kwargs)
            return True
        else:
            return False
    
    def deselect_all(self):
        for port_number in self.ports_select_state:
            port_ss = self.ports_select_state[port_number]
            port_ss.selected = False
            if port_ss.auto_light_off:
                self.ports[port_number].set_light(False) 

    def deselect_port(self, port_number):

        # if port not in this rack return false
        if port_number not in self.ports:
            return False
        
        # get the box on this port    
        box = self.boxes.get(port_number)

        if not box:
            raise ValueError("No box attached to this port.")

        # Update port status
        self.ports_select_state[port_number].selected = False

        # Take care of the final light state. 
        if self.ports_select_state[port_number].auto_light_off:
            self.ports[port_number].set_light(False)

        # for now always return true.
        return True

    def select_content_id(self, content_id, amount = 1, callback = None, auto_light_off = True):
        # TODO find the box on the rack with the given content id
        pass

    def select_box_id(self, box_id, amount = 1, callback = None, auto_light_off = True):
        # TODO find the port that has this box_id
        pass
    
    def attach_box_port(self, box, port_number):
        if port_number in self.boxes:
            self.boxes[port_number] = box
        else :
            raise KeyError('port number: ' + port_number + ' is not on this rack')
    
    def clear_port(self, port):
        self.attach_box_port(port, None)