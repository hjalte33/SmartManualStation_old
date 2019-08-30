from pick_box import PickBox
from time import sleep
import yaml
import warnings
from packml import PackML

pin_config = {}
boxes = {}
packml = PackML()

def read_config(pin_path = 'pin_config.yaml', box_path = 'box_config.yaml'):
    try:
        # load the pin config file
        with open(pin_path ,'r') as yamlfile:
            pin_config = yaml.load(yamlfile)         
    except FileNotFoundError as f:
        warning.warn('The box configuration file: %s, could not be found, default values are used' %f)

    # loop throug the pin configurations for each connector
    for connector, args in pin_config.items():
        # Make sure the bothe pins are specified.
        if all(k in args for k in ('led_pin', 'pir_pin')):
            # Copy the config to global dict.
            pin_config[connector] = args
        
        # Give a warning about missing config params. 
        elif 'led_pin' not in args:
            warnings.warn('The config id "%s" does not have the mandatory key "led_pin". The entry is skiped' %connector)
        else:
            warnings.warn('The config id "%s" does not have the mandatory key "pir_pin". The entry is skiped' %connector)
    
    try:
        # Load the box configuration 
        with open(box_path ,'r') as yamlfile:
            box_config = yaml.load(yamlfile)
        
        # Go throug the config box by box
        for box_id, args in box_config.items():
            # Fetch the pins
            pir_pin = pin_config[box_id]['pir_pin']
            led_pin = pin_config[box_id]['led_pin']
            
            # Chechk for box name and content config
            if 'box_name' in args:
                box_name = args['box_name']
            if 'content_count' in args:
                content_count = args['content_count']
            if 'content_id' in args:
                content_id = args['content_id']
            # Finally create the instance of the pick by light box
            new_box = PickBox(packml, pir_pin,led_pin, box_id, box_name, content_id, content_count)

            # Push the newly created box the the list of boxes. 
            boxes[box_id] = new_box

    except FileNotFoundError as f:
        raise ('The box configuration file: %s, could not be found, any new pick by light boxes must be configured at run time' %f)





read_config()
print(boxes)
packml.start_server()

# for key , box in boxes.items():
#     print(box.get_content())
#     box.select()
#     sleep(8)

import sys, time

x = 1
while True:
    try:
        selected = input('select 1-3 box')
        tmp = boxes[int(selected)]
        tmp.select()

    except KeyboardInterrupt:
        print ("Bye")
        packml.server.stop()
        sys.exit()




