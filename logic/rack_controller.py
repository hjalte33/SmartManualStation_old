from threading import Thread


class RackController(Thread):
    def __init__ (self,rack_hardware):
        self._rh = rack_hardware
        self.wanted_ports = []
    def run(self):

        pass

    wanted_led_state = False
    def _blink_wanted_leds(self):
        for port in _rh.get_ports():
            port.set_led(wanted_led_state)
    
    def _get_activities(self):
        out_list = []
        for port in self._rh.get_ports():
            if port.activity:
                out_list.append(port)


    def select_port(self, *port_numbers):
        self.wanted_ports.extend(port_numbers)
        pass

    def select_content_id(self, *content_ids):
        # TODO find the box on the rack with the given content id
        pass

    def select_box_id(self, *box_ids):
        # TODO find the port that has this box_id
        pass
    



    
