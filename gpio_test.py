import RPi.GPIO as GPIO
from time import sleep
import yaml
import warnings

if not GPIO.getmode():
    GPIO.setmode(GPIO.BOARD)

elif GPIO.getmode() == GPIO.BCM:
    raise Warning('GPIO.mode was already set to BCM somewhree else.')
elif GPIO.getmode() == GPIO.BOARD:
    raise Exception('GPIO.mode is set to BOARD mode. This library needs BCM mode. didn\'t try to change it ')
else:
    raise Exception('GPIO.mode is set to some unknown mode. This library needs BCM mode. didn\'t try to change it ')





def test(pin_path = 'pin_config.yaml', box_path = 'box_config.yaml'):
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

    
    for connector, args in pin_config.items():
        GPIO.setup(args['led_pin'], GPIO.OUT)
        sleep(0.2)
        GPIO.output(args['led_pin'], GPIO.HIGH)
        print(args['led_pin'])

if __name__ == "__main__":
    test()
    GPIO.output(35,GPIO.HIGH)
    sleep(30)
    
    GPIO.cleanup()
