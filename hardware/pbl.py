from .box import Box, BoxState

class PBL:
    def __init__(self, boxes ):
        self.box_ids = self._box_sanitize(boxes) 
        self.ports = {}

    def _box_sanitize(self, boxes):
        out_dict = {}
        if type(boxes) is list:
            {b.box_id : b for b in boxes}
            {b.port_id : b for b in boxes}
        return boxes

    def _update_ports(self):
        self.ports = {box.box_state.port : box for box in self.box_ids if box.box_state.port > -1}

    def select_box(self, port = -1, box_id = ""):
        by_port = None
        by_id = None
        try:
            if port != -1:
                by_port = self.ports[port]
            if box_id:    
                by_id = self.box_ids[box_id]

            if by_port and by_id:
                same = by_port is by_id
                if same:
                    by_port.select()
                else:
                    raise KeyError((port,box_id))
            elif by_port:
                by_port.select()
            elif by_id:
                by_id.select()

        except KeyError as err:
            print ("box {} could not be selected".format(err))

    def load_pbl_state(self, file_path):
        pass

    def export_pbl_state(self, file_name, file_path):
        return [box.box_state.__dict__ for box in self.box_ids.values]

    def add_box(self, box: Box):
        pass

    def rm_box(self, box_id):
        pass

    def set_port(self, box_id):
        pass

    def disable_box(self, box_id):
        self.set_box_state(box_id = box_id, port = -1)
        
    def set_box_state(self, obj = None, **params):
        try:
            if type(obj) is BoxState:
                box_id = obj.box_id
                old_port = self.box_ids[box_id].port
                new_port = obj.port
                # update the state.
                self.box_ids[box_id].box_state = obj
                # update the boxes dict.
                self.box_ids[new_port] = self.box_ids.pop(old_port)

            elif type(obj) is Box and "box_state" in params:
                obj.box_state = params["box_state"]
                new_id = params["box_state"].box_id
                self.box_ids[new_id] 
            elif type(obj) is Box:
                obj.box_state.update(**params)
            else:
                if box_id not in params:
                    raise KeyError("Box_id not in these params: " **params)
                box_id = params[box_id]
                self.box_ids[box_id].box_state.update(**params)
        except KeyError as err:
            print("cannot set box state", err)


    def get_box_state(self, box_id):
        return self.box_ids[box_id].box_state
    
    def update_box_id(self, old_box_id, new_box_id):
        # TODO
        raise Exception("not implemented update_box_id yet")

