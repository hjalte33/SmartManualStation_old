from opcua import ua, Server, Node
import simple_pbl


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


# create instance of Simple Pick By Light
aau_pbl = SimplePBL(ua_server = ua_server)

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
ua_server.start()

# create subscriptions 
# TODO change this into a function that loops through a list of commands. 

# set box_idx to command tags
b_idx = 'Command.Boxes'

# Create UA subscriber node for the box
sub = ua_server.create_subscription(100, aau_pbl)
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