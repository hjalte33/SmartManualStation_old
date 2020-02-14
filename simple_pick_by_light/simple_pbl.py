import RPi.GPIO as GPIO
import yaml
import warnings
from datetime import datetime, timedelta
from time import sleep
from threading import Thread, Event
#from opcua import ua, Server, Node
import pkg_resources

GPIO.setwarnings(False)

if not GPIO.getmode():
    GPIO.setmode(GPIO.BOARD)
    print('setting GPIO to board mode')
elif GPIO.getmode() == GPIO.BOARD:
    raise Warning('GPIO.mode was already set to BOARD somewhere else.')
elif GPIO.getmode() == GPIO.BOARD:
    raise Exception('GPIO.mode is set to BCM mode. This library needs BOARD mode. I didn\'t try to change it ')
else:
    raise Exception('GPIO.mode is set to some unknown mode. This library needs BOARD mode. I didn\'t try to change it ')

#************************************************************************#
#            Global Variables                                            #
#************************************************************************#

pin_config = {} # Dict for the pin config. Indexed by port number
boxes = {} # Dict of boxes. indexed by port number

# List for all selected ports
selected = []

# Could be any dot-separated package/module name or a "Requirement"
resource_package = __name__ 

#************************************************************************#
#            Global Variables                                            #
#************************************************************************#

def init(pin_conf_name = 'pin_config.yaml', box_conf_name = 'box_config.yaml'):
    """Module initialiser

    Keyword Arguments:
        pin_conf_path {str} -- path to config file (default: {'./pin_config.yaml'})
        box_conf_path {str} -- path to config file (default: {'./box_config.yaml'})

    """

    _load_pin_config(pin_conf_name)
    _load_box_config(box_conf_name)
           
    # Start thread for updating the LEDs
    led_args = {'period_on': 2000, 'period_off': 300, 'scan_freq': 10}
    Thread(target = _update_leds, daemon=True, kwargs=led_args).start()
    
    # Start thread for the pir monitors. 
    wrong_pick = Event()
    Thread(target = _pir_monitor, daemon=True).start()

def _load_pin_config (pin_conf_name):
    try:
        # try to load the pin config file from the data folder
        data_path = '/'.join(('data', pin_conf_name))  # Do not use os.path.join()
        yamlfile = pkg_resources.resource_string(resource_package, data_path)
        global pin_config
        pin_config = yaml.load(yamlfile)      

    except FileNotFoundError as f:
        warnings.warn('The pin configuration file: %s, could not be found' %f)
        raise(f)

    # loop through the pin configurations for each connector
    # This loop verifies all settings make sense. 
    for connector, args in pin_config.items():
        
        # Make sure the both pins are specified.
        # If they are defined do nothing
        if all(k in args for k in ('led_pin', 'pir_pin')):
            pass
        # Else give a warning about missing config params. 
        elif 'led_pin' not in args:
            warnings.warn('Port "%s" does not have the "led_pin" specified.' %connector)
            
        elif 'pir_pin' not in args:
            warnings.warn('Port "%s" does not have the mandatory key "pir_pin". The port it skiped.' %connector)
            pin_config.pop(connector, None)
        else: 
            warnings.warn('something went wrong in reading the pin config for port "%s". The port is skiped' %connector)
            pin_config.pop(connector, None)

def _load_box_config(box_conf_name):
    # Try to load the box configuration. 
    try:
        # Load the box configuration 
        data_path = '/'.join(('data', box_conf_name))  # Do not use os.path.join()
        yamlfile = pkg_resources.resource_string(resource_package, data_path)   
        box_config = yaml.load(yamlfile)
        
        # Go through the config box by box
        for port_number, args in box_config.items():
            # Print the configs to terminal for easy debugging
            print(args)

            # Finally create the master data for the pick by light box
            new_box = Box(port_number, **args)

            # Push the newly created box the the list of boxes. 
            global boxes
            boxes[port_number] = new_box

    except FileNotFoundError as f:
        raise ('The box configuration file: %s, could not be found, any new pick by light boxes must be configured at run time' %f)

# TODO
def _save_box_config(save_path, overwrite = False):
    pass

def get_pins(port_number):
    """ruters the pins for a port number. If pin not defined result will be -1
    
    Arguments:
        port_number {int} -- id number for input port
    
    Returns:
        tuple -- (led_pin, pir_pin)
    """
    port_conf = pin_config.get(port_number,{})
    led_pin = port_conf.get('led_pin', -1)
    pir_pin = port_conf.get('pir_pin', -1)
    return (led_pin, pir_pin)

def get_all_box_names():
    """returns a list of all box ids
    """
    return[x.name for x in boxes]

def get_box_by_port(port_number):
    """Return the box associated with the given port. 
    
    Arguments:
        port_number {int} -- id of the port.
    
    Raises:
        IndexError: if no box is associated with the given port number.
    
    Returns:
        PickBox -- Pick Box object. 
    """
    return(boxes[port_number])

def get_box_attr(port_number, attr):
    return getattr(boxes[port_number],attr, None)

def _update_leds(period_on, period_off, scan_freq):
    """Led update function. This function should be startet as a thread to update leds.
        The update is made "globally" so all the LEDs will blink in sync. 
    
    Arguments:
        period {float} -- time in milliseconds on/off for the leds
        scan_freq {float} -- scan frequency for how often to push updates to the leds
        stop_event {Event} -- event to stop the function immediately 
    """
    leds_last_cycle = datetime.now()
    leds_state = False
    period = period_on
    stop_event = Event()

    while not stop_event.wait(timeout=1/scan_freq):      
        if datetime.now() > leds_last_cycle + timedelta(milliseconds=period):
            leds_state = not leds_state
            period = period_on if leds_state else period_off
            leds_last_cycle = datetime.now()

        for port, box in boxes.items():
            if box.wrong_pick:
                box.toggle_led()
            
            elif box.selected:
                box.set_led(leds_state)
            else:
                box.set_led(False)

def _pir_monitor():
    """Thread function that checks if any of the boxes are selected wrongly 
    """
    while True:
        sleep(0.5)
        activities = [port for port, box in boxes.items() if box.pir_activity]
    
        for port in activities:
            # If selected set flag to mark wrongly picked boxes
            # Only if some box is selected it makes sense to mark wrongly picked boxes.
            if not boxes[port].selected:
                boxes[port].wrong_pick = True
            else:
                boxes[port].wrong_pick = False
            # If activity on something not selected send to list of boxes to mark
        
        if not activities:
            {setattr(boxes[port], 'wrong_pick', False) for port in boxes}

def set_box_attr(port_number, attr, value):
    if hasattr(boxes[port_number], attr):
        setattr(boxes[port_number], attr, value)
    else:
        warnings.warn('attribute %s does not exist on box_id %s' % (attr, box_id))

def select_box(port_number, val = True):
    set_box_attr(port_number, "selected", val)



class Box:
    """Simple class holding all the basic functions needed for a single pick box
    
    Raises:
        ValueError: raise exception if wrong args are passed. 
    """

    # parameters exposed to servers eg. opc-ua.
    # TODO include datatype. 
    public_attributes = (('selected',bool), 
                         ('pir_activity',bool), 
                         ('name',str), 
                         ('quantity', int), 
                         ('content_id', str), 
                         ('wrong_pick', bool))

    def __init__(self,  port_number, **kwargs):
        # Set identification attributes
        self.led_pin, self.pir_pin = get_pins(port_number)
        self.port_number = port_number

        # Set Status attributes 
        self.selected = False
        self.pir_activity = False
        self.pir_ready = True
        self.wrong_pick = False

        self.set_params(**kwargs)
        
        # GPIO setup
        GPIO.setup(self.pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.led_pin, GPIO.OUT)

        # Add interupt and callback function when there's a change on the pir pin. 
        GPIO.add_event_detect(self.pir_pin, GPIO.BOTH, callback=self.pir_callback)
    
        # Dict containing lists of the content ids per port.
        # example for port number 1 containing 3 item ids 
        #   1:[aaaa,bbbb,cccc]   
        content = {}

    def __getattr__(self, name):
        """intercepting requests to undefinde attributes. If attribute not set, 
        but exists as a valid box attribute return None other wise throw error.
        This way the attributes does not need to be defined one by one. 
        """
        if name in Box.public_attributes:
            return None

    def set_params (self,**kwargs):
        # Set more attributes if passed to the pick box.

        # quickly convert the parameters into a dict for easier access. 
        attr_types = {item[0]: item[1] for item in Box.public_attributes}

        for key, value in kwargs.items():
            if key in attr_types.keys():
                try:
                    type_func = attr_types[key]                               
                    setattr(self, key, type_func(value))
                except ValueError:
                   raise ValueError("Type does not match", key)
            else:
                raise ValueError("unexpected kwarg value", key)    

    def pir_callback(self,pin):
        """Callback for activity on the pir sensor.
            This callback starts another sleeper thread that 
            sleeps a set amount of time too "cool down" the sensor
        
        Arguments:
            pin {int} -- pin number that triggered the callback 
        """
        if self.pir_ready:
            Thread(target=self.pir_sleeper, daemon=True, args=(pin,)).start()

    def pir_sleeper(self,pin):
        """Thread that sleeps while the pir is stabalizing.
        
        Arguments:
            pin {int} -- pin of trigger
        """ 
        pin_status = GPIO.input(self.pir_pin)
        if pin_status == 1:
            print('Pir detected on box: %s' % self.port_number)
            self.pir_activity = True
            self.pir_ready = False
            self.selected = False
            sleep(5) 
            # update the pin status  
            pin_status = GPIO.input(self.pir_pin)
        
        # always check again if pin status is 0 
        if pin_status == 0:
            self.pir_activity = False
        # finally set the pin ready flag 
        self.pir_ready = True

    def toggle_led(self):
        led_next = not GPIO.input(self.led_pin)
        GPIO.output(self.led_pin, led_next)
    
    def set_led(self, state):
        GPIO.output(self.led_pin, state)
    
    def get_led(self) -> bool:
        GPIO.input(self.led_pin)

    def update_ua_status(self, name, value):
        """update a status tag for this box.
        
        Arguments:
            name {string} -- status tag name.
            value {} -- Value of the tag. Make sure it matches the ua tag type.
        """
        node_id = 'Status.Boxes.%s.%s' % (self.port_number, name)
        self.update_ua_var(node_id,value)
    
    def update_ua_var(self, node_id, value):
        """Update any variable on the ua server.
        
        Arguments:
            node_id {string} -- node id for the tag. 
            value {} -- value of the tag. Make sure it matches the ua tag type.
        """
        try:
            node_id = 'ns=2;s=%s' % node_id
            node = self.parent.server.get_node(node_id)
            node.set_value(value)
        except RuntimeError as e:
            warnings.warn('error setting ua var on node %s' % node_id)
            print(e) 





