from hardware import box
import pkg_resources
import yaml


__boxes = {}

def _load_boxes(boxes_conf_name = "boxes_config.yaml"):
    resource_package = __name__
    try:
        # try to load the pin config file from the data folder
        data_path = '/'.join((boxes_conf_name,))  
        yamlfile = pkg_resources.resource_string(resource_package, data_path)
        from_file = yaml.load(yamlfile)      
        print(from_file)
        if type(from_file) == dict:
            for item in from_file.values():
                __boxes[item["box_id"]] = box.Box(item["box_id"],item["content_id"],item["content_count"])

    except FileNotFoundError as f:
        raise FileNotFoundError('The boxes configuration file: %s, could not be found', f)
    except KeyError as f:
        raise KeyError("boxes_config.yaml has a format error: ", f)
    



def save_boxes(boxes_conf_name = "boxes_config.yaml"):
    to_save = {i: box.__dict__ for i, box in __boxes.items()}
    resource_package = __name__
    try:
        # try to load the pin config file from the data folder
        data_path = '/'.join((boxes_conf_name,))  
        yamlfile = pkg_resources.resource_filename(resource_package, data_path)
        with open(yamlfile, 'w') as outfile:
            yaml.dump(to_save, outfile, default_flow_style=False) 

    except Exception as e:
        print(e)     


def _box_generator(num_of_boxes):
    from random import randint
    import uuid
    for _ in range(num_of_boxes):
        myid = uuid.uuid4()
        add_box(box.Box(myid.hex,randint(0,1000),randint(1,100)))

def add_box(box):
    __boxes[box.box_id] = box

def rm_box(box):
    del __boxes[box.box_id] 