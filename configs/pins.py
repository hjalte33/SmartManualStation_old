import warnings 
import pkg_resources
import yaml

__pin_config = {}

def _load_pins (pin_conf_name = "default_pin_config.yaml"):
    resource_package = __name__
    try:
        # try to load the pin config file from the data folder
        data_path = '/'.join((pin_conf_name,))  
        yamlfile = pkg_resources.resource_string(resource_package, data_path)
        global __pin_config
        __pin_config = yaml.load(yamlfile)      

    except FileNotFoundError as f:
        raise FileNotFoundError('The pin configuration file: %s, could not be found' %f)

    # loop through the pin configurations for each connector
    # This loop verifies all settings make sense. 
    for connector, args in __pin_config.items():
        
        # Make sure the both pins are specified.
        # If they are defined do nothing
        if all(k in args for k in ('led_pin', 'pir_pin')):
            pass
        # Else give a warning about missing config params. 
        elif 'led_pin' not in args:
            warnings.warn('Port "%s" does not have the "led_pin" specified.' %connector)
            
        elif 'pir_pin' not in args:
            warnings.warn('Port "%s" does not have the mandatory key "pir_pin". The port it skiped.' %connector)
            __pin_config.pop(connector, None)
        else: 
            warnings.warn('something went wrong in reading the pin config for port "%s". The port is skiped' %connector)
            __pin_config.pop(connector, None)

def get_pins(port_number):
    """ruters the pins for a port number. If pin not defined result will be -1
    
    Arguments:
        port_number {int} -- id number for input port
    
    Returns:
        tuple -- (led_pin, pir_pin)
    """
    port_conf = __pin_config.get(port_number,{}) 
    led_pin = port_conf.get('led_pin', -1)
    pir_pin = port_conf.get('pir_pin', -1)
    return (led_pin, pir_pin)

def get_led_pin(port_number):
    port_conf = __pin_config.get(port_number,{})
    return port_conf.get('led_pin', -1)

def get_pir_pin(port_number):
    port_conf = __pin_config.get(port_number,{})
    return port_conf.get('pir_pin', -1)