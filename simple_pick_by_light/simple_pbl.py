import RPi.GPIO as GPIO
import yaml
import warnings
from datetime import datetime, timedelta
from time import sleep
from threading import Thread, Event
from opcua import ua, Server, Node



if not GPIO.getmode():
    GPIO.setmode(GPIO.BOARD)
elif GPIO.getmode() == GPIO.BOARD:
    raise Warning('GPIO.mode was already set to BOARD somewhere else.')
elif GPIO.getmode() == GPIO.BOARD:
    raise Exception('GPIO.mode is set to BCM mode. This library needs BOARD mode. I didn\'t try to change it ')
else:
    raise Exception('GPIO.mode is set to some unknown mode. This library needs BOARD mode. I didn\'t try to change it ')


  
class PickBox:
    """Simple class holding all the basic functions needed for a single pick box
    
    Raises:
        ValueError: raise exception if wrong args are passed. 
    """
    def __init__(self, parent,  pir_pin, led_pin, box_id, **kwargs):
        # Set identification attributes
        self.parent = parent
        self.pir_pin = pir_pin
        self.led_pin = led_pin
        self.box_id = box_id

        # Set Status attributes 
        self.selected = False
        self.pir_activity = False
        self.pir_ready = True
        self.wrong_pick = False

        # Set more attributes if passed to the pick box. 
        whitelist = ['name', 'content_id', 'quantity']
        for key, value in kwargs.items():
            if key in whitelist:
                setattr(self, key, value)
            else:
                raise ValueError("unexpected kwarg value", key)    
        
        # GPIO setup
        GPIO.setwarnings(False)
        GPIO.setup(self.pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.led_pin, GPIO.OUT)

        # Add interupt and callback function when there's a change on the pir pin. 
        GPIO.add_event_detect(self.pir_pin, GPIO.BOTH, callback=self.pir_callback)
    
    # Automatically update ua parameters when status attributes changes
    def __setattr__(self, name, value):
        if name == 'selected':
            self.update_ua_status('Selected', value)
        elif name == 'pir_activity':
            self.update_ua_status('PirActivity', value)
        elif name == 'wrong_pick':
            self.update_ua_status('WrongPick', value)
        super(PickBox, self).__setattr__(name, value)


    def pir_callback(self,pin):
        """Callback for activity on the pir sensor.
            This callback starts another sleeper thread that 
            sleeps a set amount of time too "cool down" the sensor
        
        Arguments:
            pin {int} -- pin number that triggered the callback 
        """
        if self.pir_ready:
            Thread(target=self.pir_sleeper, daemon=True, args=(pin,)).start()
        pass

    def pir_sleeper(self,pin):
        """Thread that sleeps while the pir is stabalizing.
        
        Arguments:
            pin {int} -- pin of trigger
        """ 
        if 1 == GPIO.input(self.pir_pin):
            print('Pir detected on box: %s' % self.box_id)
            self.pir_activity = True
            self.pir_ready = False
            self.selected = False
            sleep(5)  
        if 0 == GPIO.input(self.pir_pin):
            self.pir_activity = False
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
        node_id = 'Status.Boxes.%s.%s' % (self.box_id, name)
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

class SimplePBL:
    """Pick by light setup. 
    """
    def __init__(self, server, pin_conf_path = 'pin_config.yaml', box_conf_path = 'box_config.yaml'):
        """Constructor for pick by light
        
        Arguments:
            server {ua.Server} -- a reference to a ua server.
        
        Keyword Arguments:
            pin_conf_path {str} -- path to pin config yaml file (default: {'pin_config.yaml'})
            box_conf_path {str} -- path to box config yaml file (default: {'box_config.yaml'})
        
        Raises:
            RuntimeError: If the referenced server is wrongly defined. 
        """
        # Check the server. 
        if type(server) == Server:
                self.server = server
        else:
            print('A ua server must be defined before using. ')
            raise RuntimeError

        self.boxes = self.get_boxes_from_config(pin_conf_path, box_conf_path)
        
        self.led_stop_blink = Event()
        led_args = {'period_on': 2000, 'period_off': 300, 'scan_freq': 10, 'stop_event':self.led_stop_blink}
        Thread(target = self.update_leds, daemon=True, kwargs=led_args).start()
        
        self.wrong_pick = Event()
        Thread(target = self.pir_monitor, daemon=True).start()

    # Automatically update ua parameters when status attributes changes
    def __setattr__(self, name, value):
        if name == 'selected':
            self.update_ua_status('Selected', value)
        super(SimplePBL, self).__setattr__(name, value)

    def datachange_notification(self, node: Node, val, data):
        """UA server callback on data change notifications
            This is a workaround for kepware that does not support 
            UA methods, so instead is has "trigger tags" that when 
            set to true it works like calling a method. 
            TODO make this more dynamic instead of hard coding the attributes. 
        
        Arguments:
            node {Node} -- [description]
            val {[type]} -- [description]
            data {[type]} -- [description]
        """

        # Print info
        print("Python: New data change event", node, val)
        
        # get the node browse name. 
        node_id = node.get_browse_name().Name

        # If the trigger tag changes to true go in and update the select tag and set
        # the trigger back to false. When setting it back to false this method gets
        # called again, that's why this if statement checks if the value is True 
        # so the method does not call itself continuously. 
        if node_id == "Select" :
            self.select_box(val)
            self.update_ua_var('Command.Boxes.Select', -1)
        # If the trigger tag changes to true go in and update the status tag and set the trigger back to false.
        # Also read description above. 
        if node_id == "ClearWrongPick" :
            self.wrong_pick = False
            self.update_ua_var('Command.Boxes.ClearWrongPick', -1)
        
        # If the trigger tag changes to true go in and update the status tag and set the trigger back to false.
        # Also read description above. 
        if node_id == "Deselect" :
            self.select_box(val, False)
            self.update_ua_var('Command.Boxes.Deselect', -1)


    def get_all_box_ids(self):
        """returns a list of all box ids
        """
        return[x.box_id for x in self.boxes]

    def get_box_by_id(self, box_id):
        """Return the first box with the given id. 
        
        Arguments:
            box_id {string} -- id of the box. usually an int.
        
        Raises:
            IndexError: if box id is not found
        
        Returns:
            PickBox -- Pick Box object. 
        """
        l = [x for x in self.boxes if x.box_id == box_id]
        if l: return l[0]
        else: raise IndexError

    def get_boxes_from_config(self, pin_conf_path, box_conf_path):
        """Private function.
           Read the pin and box config files and  phrases them.
           The function returns a list of pickBox objects.
        
        Arguments:
            pin_conf_path {string} -- path to pin conf yaml file
            box_conf_path {string} -- path to box conf yaml file.
        
        Returns:
            [pickBox] -- list of pickBox objects.
        """
        boxes_to_return = []
        try:
            # load the pin config file
            with open(pin_conf_path ,'r') as yamlfile:
                pin_config = yaml.load(yamlfile)         
        except FileNotFoundError as f:
            raise('The box configuration file: %s, could not be found' %f)

        # loop through the pin configurations for each connector
        # This loop verifies all settings make sense. 
        for connector, args in pin_config.items():
            
            # Make sure the both pins are specified.
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
            with open(box_conf_path ,'r') as yamlfile:
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

                # Finally create the master data for the pick by light box
                new_box = PickBox(self, pir_pin,led_pin, box_id, **args)

                # Push the newly created box the the list of boxes. 
                boxes_to_return.append(new_box)

        except FileNotFoundError as f:
            raise ('The box configuration file: %s, could not be found, any new pick by light boxes must be configured at run time' %f)

        return boxes_to_return

    def get_pick_box_attr(self, box_id, attr):
        # Search the boxes for this id 
        # We will only care about the first found object. 
        the_box = [x for x in self.boxes if x.box_id == box_id]
        
        try:
            return getattr(the_box[0],attr)

        # If the attribute does not exist don't worry, just return None. 
        # This makes sense if one box has information that other boxes does not have 
        # i don't want to have everything crash just because it's not pressent on other boxes.    
        except AttributeError:
            warnings.warn('attribute %s does not exist on box_id %s, returning None' % (attr, box_id))
            return None

    def update_leds(self, period_on, period_off, scan_freq, stop_event: Event):
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

        while not stop_event.wait(timeout=1/scan_freq):      
            if datetime.now() > leds_last_cycle + timedelta(milliseconds=period):
                leds_state = not leds_state
                period = period_on if leds_state else period_off
                leds_last_cycle = datetime.now()

            for box in self.boxes:
                if box.wrong_pick:
                    box.toggle_led()
                
                elif box.selected:
                    box.set_led(leds_state)
                else:
                    box.set_led(False)

    def pir_monitor(self):
        """Thread function that checks if any of the boxes are selected wrongly 
        """
        while True:
            sleep(0.5)
            to_set = []
            do_set = False
            for box in self.boxes:
                # If selected set flag to mark wrongly picked boxes
                # Only if some box is selected it makes sense to mark wrongly picked boxes.
                if box.selected: do_set = True
                # If activity on something not selected send to list of boxes to mark
                if box.pir_activity and not box.selected:
                    to_set.append(box)
            
            # Only if something was selected and any wrongly picked boxes, go ahead and set the flags. 
            if do_set and to_set:
                self.wrong_pick_boxes = [x.box_id for x in to_set]
                [setattr(x, 'wrong_pick',True) for x in to_set]
            else:
                [setattr(x, 'wrong_pick',False) for x in self.boxes]

    def set_pick_box_attr(self, box_id, attr, value):
        the_box = [x for x in self.boxes if x.box_id == box_id]
        if the_box:
            if hasattr(the_box[0],attr):
                setattr(the_box[0], attr, value)
            else:
                warnings.warn('attribute %s does not exist on box_id %s' % (attr, box_id))
        else: warnings.warn('box_id %s does not exist' % box_id)

    def select_box(self, box_id, val = True):
        self.set_pick_box_attr(box_id, "selected", val)

    def update_ua_status(self, name, value):
        node_id = 'Status.Boxes.%s.%s' % (self.box_id, name)
        self.update_ua_var(node_id,value)

    def update_ua_var(self, node_id, value):
        """Update any variable on the ua server.
        
        Arguments:
            node_id {string} -- node id for the tag. 
            value {} -- value of the tag. Make sure it matches the ua tag type.
        """
        try:
            node_id = 'ns=2;s=%s' % node_id
            node = self.server.get_node(node_id)
            node.set_value(value)
        except RuntimeError as e:
            warnings.warn('error setting ua var on node %s' % node_id)
            print(e) 

class UA_server :
    # Create server instance 
    server = Server('./opcua_cache')

    server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/PickByLight')
    server.set_server_name("Pick By Light Server")

    # idx name will be used later for creating the xml used in data type dictionary
    # setup our own namespace, not really necessary but should as spec
    idx_name = 'http://examples.freeopcua.github.io'
    idx =  server.register_namespace(idx_name)

    # Set all possible endpoint policies for clients to connect through
    server.set_security_policy([
        ua.SecurityPolicyType.NoSecurity,
        ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
        ua.SecurityPolicyType.Basic128Rsa15_Sign,
        ua.SecurityPolicyType.Basic256_SignAndEncrypt,
        ua.SecurityPolicyType.Basic256_Sign])

    # get Objects node, this is where we should put our custom stuff
    objects =  server.get_objects_node()
    # add a PackMLObjects folder
    pml_folder =  objects.add_folder(idx, "PackMLObjects")
    # Get the base type object
    types =  server.get_node(ua.ObjectIds.BaseObjectType)
    # Create a new type for PackMLObjects
    PackMLBaseObjectType =  types.add_object_type(idx, "PackMLBaseObjectType")
    Admin =  pml_folder.add_object('ns=2;s=Admin', "Admin", PackMLBaseObjectType.nodeid)
    Status =  pml_folder.add_object('ns=2;s=Status', "Status", PackMLBaseObjectType.nodeid)
    Command =  pml_folder.add_object('ns=2;s=Command', "Command", PackMLBaseObjectType.nodeid)

    # Create an object for the boxes in both the command and status object 
    BoxesStatus = Status.add_object('ns=2;s=Status.Boxes', 'Boxes')
    BoxesCommonStatus = BoxesStatus.add_object('ns=2;s=Status.Boxes.Common', 'Common')


    # create instance of Simple Pick By Light
    aau_pbl = SimplePBL(server = server)

    # Get all boxes
    box_ids = aau_pbl.get_all_box_ids()

    # for all boxes generate tags
    for box_id in box_ids:
        b_idx = 'Status.Boxes.%s' %box_id
        # create an object in the packml status object using our unique box idx
        b_obj = BoxesStatus.add_object("ns=2;s=%s" % b_idx, str(box_id))
        
        # TODO make this a loop that looks up tags from a list of tags 
        # Create Status tags 
        s_idx = b_idx + ".Selected"
        b_obj.add_variable("ns=2;s=%s" % s_idx, 'Selected', False, ua.VariantType.Boolean)

        s_idx = b_idx + ".PirActivity"
        b_obj.add_variable("ns=2;s=%s" % s_idx, 'PirActivity', False, ua.VariantType.Boolean)    

        s_idx = b_idx + ".WrongPick"
        b_obj.add_variable("ns=2;s=%s" % s_idx, 'WrongPick', False, ua.VariantType.Boolean) 

    '''
    create command tags. This is because kepware does not support ua methods. 
    '''
    # change to command tags
    b_idx = 'Command.Boxes'
    # create an object in the packml Command object called Boxes for all the box commands. 
    b_obj = Command.add_object("ns=2;s=%s" % b_idx, 'Boxes')
    # Create command tag for triggering the selection
    s_idx = b_idx + ".Select"
    b_var = b_obj.add_variable("ns=2;s=%s" % s_idx, 'Select', False, ua.VariantType.Int16)
    b_var.set_writable()

    s_idx = b_idx + ".Deselect"
    b_var = b_obj.add_variable("ns=2;s=%s" % s_idx, 'Deselect', False, ua.VariantType.Int16)
    b_var.set_writable()

    s_idx = b_idx + ".ClearWrongPick"
    b_var = b_obj.add_variable("ns=2;s=%s" % s_idx, 'ClearWrongPick', False, ua.VariantType.Int16)
    b_var.set_writable()

    # Start the server 
    server.start()

    # create subscriptions 
    # TODO change this into a function that loops through a list of commands. 

    # set box_idx to command tags
    b_idx = 'Command.Boxes'

    # Create UA subscriber node for the box
    sub = server.create_subscription(100, aau_pbl)
    # Set String_idx to Select tag
    s_idx = b_idx + ".Select"
    # Subscribe to the Select tag
    n = server.get_node("ns=2;s=%s" % s_idx)
    sub.subscribe_data_change(n)

        # Set String_idx to Deselect tag
    s_idx = b_idx + ".Deselect"
    # Subscribe to the Deselect tag
    n = server.get_node("ns=2;s=%s" % s_idx)
    sub.subscribe_data_change(n)

        # Set String_idx to Clear Wrong Pick tag
    s_idx = b_idx + ".ClearWrongPick"
    # Subscribe to the Select tag
    n = server.get_node("ns=2;s=%s" % s_idx)
    sub.subscribe_data_change(n)



try:
    while True:
        sleep(10)
except KeyboardInterrupt:
    server.stop()
    GPIO.cleanup()
    print('interrupted!')




