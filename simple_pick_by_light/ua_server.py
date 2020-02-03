from opcua import ua, Server, Node
import simple_pbl as pbl



class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    """
    def event_notification(self, event):
        print("Python: New event. No function implemented", event)

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

        # avoid triggereing it all again when resetting the tags to -1
        if val != -1 :
            
            # Print info
            print("Python: New data change event", node, val)
            
            # get the node browse name. 
            node_id = node.get_browse_name().Name

            # If the trigger tag changes to true go in and update the select tag and set
            # the trigger back to false. When setting it back to false this method gets
            # called again, that's why this if statement checks if the value is True 
            # so the method does not call itself continuously. 
            if node_id == "Select" :
                pbl.select_box(val)
                node.set_value(-1)

            # If the trigger tag changes to true go in and update the status tag and set the trigger back to false.
            # Also read description above. 
            if node_id == "ClearWrongPick" :
                #TODO pbl.wrong_pick = False
                node.set_value(-1)
            
            # If the trigger tag changes to true go in and update the status tag and set the trigger back to false.
            # Also read description above. 
            if node_id == "Deselect" :
                pbl.select_box(val, False)
                node.set_value(-1)


# Create server instance 
ua_server = Server('./opcua_cache')

ua_server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/PickByLight')
ua_server.set_server_name("Pick By Light Server")

# idx name will be used later for creating the xml used in data type dictionary
# setup our own namespace, not really necessary but should as spec
idx_name = 'http://examples.freeopcua.github.io'
idx =  ua_server.register_namespace(idx_name)

# Set all possible endpoint policies for clients to connect through
ua_server.set_security_policy([
    ua.SecurityPolicyType.NoSecurity,
    ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
    ua.SecurityPolicyType.Basic128Rsa15_Sign,
    ua.SecurityPolicyType.Basic256_SignAndEncrypt,
    ua.SecurityPolicyType.Basic256_Sign])

# get Objects node, this is where we should put our custom stuff
objects =  ua_server.get_objects_node()
# add a PackMLObjects folder
pml_folder =  objects.add_folder(idx, "PackMLObjects")
# Get the base type object
types =  ua_server.get_node(ua.ObjectIds.BaseObjectType)
# Create a new type for PackMLObjects
PackMLBaseObjectType =  types.add_object_type(idx, "PackMLBaseObjectType")

# Create objects for the pack tags using the above created packMLBasedObjectType
Admin =  pml_folder.add_object('ns=2;s=Admin', "Admin", PackMLBaseObjectType.nodeid)
Status =  pml_folder.add_object('ns=2;s=Status', "Status", PackMLBaseObjectType.nodeid)
Command =  pml_folder.add_object('ns=2;s=Command', "Command", PackMLBaseObjectType.nodeid)

# Create an object for the boxes in both the command and status object 
BoxesStatus = Status.add_object('ns=2;s=Status.Boxes', 'Boxes')
BoxesCommonStatus = BoxesStatus.add_object('ns=2;s=Status.Boxes.Common', 'Common')


def init():
        
    # for all boxes generate tags
    for port in pbl.boxes:
        b_idx = 'Status.Boxes.%s' %port
        # create an object in the packml status object using our unique box idx
        b_obj = BoxesStatus.add_object("ns=2;s=%s" % b_idx, str(port))
        
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
    ua_server.start()

    # create subscriptions 
    # TODO change this into a function that loops through a list of commands. 

    # set box_idx to command tags
    b_idx = 'Command.Boxes'

    # Create UA subscriber node for the box
    sub = ua_server.create_subscription(100, SubHandler)
    # Set String_idx to Select tag
    s_idx = b_idx + ".Select"
    # Subscribe to the Select tag
    n = ua_server.get_node("ns=2;s=%s" % s_idx)
    sub.subscribe_data_change(n)

        # Set String_idx to Deselect tag
    s_idx = b_idx + ".Deselect"
    # Subscribe to the Deselect tag
    n = ua_server.get_node("ns=2;s=%s" % s_idx)
    sub.subscribe_data_change(n)

        # Set String_idx to Clear Wrong Pick tag
    s_idx = b_idx + ".ClearWrongPick"
    # Subscribe to the Select tag
    n = ua_server.get_node("ns=2;s=%s" % s_idx)
    sub.subscribe_data_change(n)



def update_ua_status(name, value):
    node_id = 'Status.Boxes.%s.%s' % (self.box_id, name)
    self.update_ua_var(node_id,value)

def update_ua_var(node_id, value):
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

class VarUpdater(Thread):
    def __init__(self, var):
        Thread.__init__(self)
        self._stopev = False
        self.var = var

    def stop(self):
        self._stopev = True

    def run(self):
        while not self._stopev:
            v = time.time()
            self.var.set_value(v)
            time.sleep(1)






