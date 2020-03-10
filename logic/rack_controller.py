from threading import Thread


class RackController(Thread):
    def __init__ (self,rack_hardware):
        self._rh = rack_hardware
        self.wanted_box_ids = []
    def run(self):

        pass

    
    def _get_activities(self):
        out_list = []
        for port in self._rh.get_ports():
            if port.activity:
                out_list.append(port)


    def select_port(self, port):
        # TODO find what's on the port and push that box_id to 
        # the wanted_box_ids list
        pass

    def select_


    
