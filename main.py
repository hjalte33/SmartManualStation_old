from pick_box import PickBox, PickByLight
from time import sleep
import yaml
import warnings
#import packml
import ua_server


def read_config(pin_path = 'pin_config.yaml', box_path = 'box_config.yaml'):
    # return list of boxes 
    boxes_to_return = {}

    try:
        # load the pin config file
        with open(pin_path ,'r') as yamlfile:
            pin_config = yaml.load(yamlfile)         
    except FileNotFoundError as f:
        raise('The box configuration file: %s, could not be found' %f)

    # loop throug the pin configurations for each connector
    for connector, args in pin_config.items():
        
        # Make sure the bothe pins are specified.
        # If they are defined do nothing
        if all(k in args for k in ('led_pin', 'pir_pin')):
            pass
        # Else give a warning about missing config params. 
        elif 'led_pin' not in args:
            warnings.warn('The connector config id "%s" does not have the mandatory key "led_pin". The entry is skiped' %connector)
            pin_config.pop(connector, None)
        elif 'pir_pin' not in args:
            warnings.warn('The connector config id "%s" does not have the mandatory key "pir_pin". ' %connector)
            pin_config.pop(connector, None)
        else: 
            warnings.warn('something went wrong in reading the pin config for connector id "%s". The entry is skiped' %connector)
            pin_config.pop(connector, None)

    # Try to load the box configuration. 
    try:
        # Load the box configuration 
        with open(box_path ,'r') as yamlfile:
            box_config = yaml.load(yamlfile)
        
        # Go throug the config box by box
        for box_id, args in box_config.items():
            # Try to fetch the pins
            try:
                print('Loading pir and led pins for box id %s ......' %box_id)
                pir_pin = pin_config[box_id]['pir_pin']
                led_pin = pin_config[box_id]['led_pin']
            except KeyError:
                warnings.warn('"pin config" for box id %s was not found. Are you sure the pin config is formatted correctly?' %box_id)
                
                # Go back to top and read next box config
                continue

            # Print the configs to terminal for easy debugging
            print(args)

            # Finally create the instance of the pick by light box
            new_box = PickBox(pir_pin,led_pin, box_id, args)

            # Push the newly created box the the list of boxes. 
            boxes_to_return[box_id] = new_box        
        return boxes_to_return

    except FileNotFoundError as f:
        raise ('The box configuration file: %s, could not be found, any new pick by light boxes must be configured at run time' %f)
    
    # finally return the list of boxes. 
    return boxes_to_return




if __name__ == "__main__":


    boxes = read_config()

    pbl = PickByLight(boxes, 'Asset_AAUSmartPickByLight')


    sleep(900)



