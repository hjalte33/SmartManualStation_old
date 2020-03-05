
class Rack:
    def __init__(self, ports):
        self.attached_boxes = {p:None for p in ports}
    
    @property
    def ports(self):
        self.attached_boxes.keys()

    def get_ports(self):
        return self.attached_boxes.keys()
    
    def get_boxes(self):
        return self.attached_boxes.items()
    
    def set_port(self, port, box):
        if hasattr(self.attached_boxes, port):
            self.attached_boxes[port] = box
        else :
            raise KeyError('port number not on this rack')

