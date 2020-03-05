
class Box:
    def __init__(self,box_id, content_id, content_count):
        self.box_id = box_id
        self.content_id = content_id
        self.content_count = content_count
    
    def add_items(self, amount = 1):
        self.content_count += 1
    
    def rm_items(self, amount = 1):
        self.content_count -= 1
    
    def get_content_id(self):
        return self.content_id
    
    def set_content_id(self, content_id):
        self.centent_id = content_id