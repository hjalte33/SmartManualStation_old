from opcua import ua, Server, uamethod
from opcua.common.type_dictionary_buider import DataTypeDictionaryBuilder, get_ua_class
import time


server = Server('./opcua_cache')

server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/PickByLight')
server.set_server_name("Pick By Light Server")

# idx name will be used later for creating the xml used in data type dictionary
# setup our own namespace, not really necessary but should as spec
_idx_name = 'http://examples.freeopcua.github.io'
idx = server.register_namespace(_idx_name)
#set all possible endpoint policies for clienst to connect through
server.set_security_policy([
    ua.SecurityPolicyType.NoSecurity,
    ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
    ua.SecurityPolicyType.Basic256Sha256_Sign]
)
dict_builder = DataTypeDictionaryBuilder(server, idx, _idx_name, 'PackMLBaseObjectType')


# get Objects node, this is where we should put our custom stuff
objects = server.get_objects_node()
# add a PackMLObjecs folder
pml_folder = objects.add_folder(idx, "PackMLObjects")

# Get the base type object
types = server.get_node(ua.ObjectIds.BaseObjectType)
# Create a new type for PackMLObjects
PackMLBaseObjectType = types.add_object_type(idx, "PackMLBaseObjectType")
Admin = pml_folder.add_object(idx, "Admin", PackMLBaseObjectType.nodeid)
Status = pml_folder.add_object(idx, "Status", PackMLBaseObjectType.nodeid)



# def create_structure(self, name):
#     # save the created data type
#     return dict_builder.create_data_type(name)

# def complete_creation(self):
#     dict_builder.set_dict_byte_string()

# def create_object(self, name):
#     return server.nodes.base_object_type.add_object(idx, name)

# def create_method(self, name, func, inputs, outputs):
#     pass

# def get_pml_folder(self):
#     return server.get_node("PackMLObjects")



# add one basic structure. This should probaly be moved the the packml server class. 
basic_struct_name = 'basic_parameter'
basic_struct = dict_builder.create_data_type(basic_struct_name)
basic_struct.add_field('ID', ua.VariantType.Int32)
basic_struct.add_field('Name', ua.VariantType.String)
basic_struct.add_field('Unit', ua.VariantType.String)
basic_struct.add_field('Value', ua.VariantType.Int32)

# this operation will write the OPC dict string to our new data type dictionary
# namely the 'MyDictionary'
dict_builder.set_dict_byte_string()

# create new nodes
# status_node = pml_server.server.nodes.base_object_type.add_object(idx, 'Status').set_modelling_rule(True)
# admin_node = pml_server.server.nodes.base_object_type.add_object(idx, 'Admin').set_modelling_rule(True)


# get the working classes
server.load_type_definitions()


#server.start()


    
# try:
#     while True:
#         time.sleep(1)
# finally:
#     # close connection, remove subcsriptions, etc
#     server.stop()