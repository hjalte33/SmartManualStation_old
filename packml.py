from opcua import ua, Server, uamethod
from opcua.common.type_dictionary_buider import DataTypeDictionaryBuilder, get_ua_class
import time

class PackMLServer:

    def __init__(self):
        self.server = Server('./opcua_cache')

        self.server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/PickByLight')
        self.server.set_server_name("Pick By Light Server")

        # idx name will be used later for creating the xml used in data type dictionary
        # setup our own namespace, not really necessary but should as spec
        self._idx_name = 'http://examples.freeopcua.github.io'
        self.idx = self.server.register_namespace(self._idx_name)
        #set all possible endpoint policies for clienst to connect through
        self.server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign]
        )
        self.dict_builder = DataTypeDictionaryBuilder(self.server, self.idx, self._idx_name, 'PackMLBaseObjectType')


        # get Objects node, this is where we should put our custom stuff
        objects = self.server.get_objects_node()
        # add a PackMLObjecs folder
        self.pml_folder = objects.add_folder(self.idx, "PackMLObjects")

        # Get the base type object
        types = self.server.get_node(ua.ObjectIds.BaseObjectType)
        # Create a new type for PackMLObjects
        self.PackMLBaseObjectType = types.add_object_type(self.idx, "PackMLBaseObjectType")
        self.Admin = self.pml_folder.add_object(self.idx, "Admin", self.PackMLBaseObjectType.nodeid)
        self.Status = self.pml_folder.add_object(self.idx, "Status", self.PackMLBaseObjectType.nodeid)

    def start_server(self):
        self.server.start()

    def create_structure(self, name):
        # save the created data type
        return self.dict_builder.create_data_type(name)

    def complete_creation(self):
        self.dict_builder.set_dict_byte_string()
    
    def create_object(self, name):
        return self.server.nodes.base_object_type.add_object(self.idx, name)

    def create_method(self, name, func, inputs, outputs):
        pass

    def get_pml_folder(self):
        return self.server.get_node("PackMLObjects")



pml_server = PackMLServer()

# add one basic structure. This should probaly be moved the the packml server class. 
basic_struct_name = 'basic_parameter'
basic_struct = pml_server.create_structure(basic_struct_name)
basic_struct.add_field('ID', ua.VariantType.Int32)
basic_struct.add_field('Name', ua.VariantType.String)
basic_struct.add_field('Unit', ua.VariantType.String)
basic_struct.add_field('Value', ua.VariantType.Int32)

# this operation will write the OPC dict string to our new data type dictionary
# namely the 'MyDictionary'
pml_server.complete_creation()

# create new nodes
# status_node = pml_server.server.nodes.base_object_type.add_object(idx, 'Status').set_modelling_rule(True)
# admin_node = pml_server.server.nodes.base_object_type.add_object(idx, 'Admin').set_modelling_rule(True)


# get the working classes
pml_server.server.load_type_definitions()

# Create one test structure
basic_var = pml_server.server.nodes.objects.add_variable(ua.NodeId(namespaceidx=pml_server.idx), 'BasicStruct',
                                                        ua.Variant(None, ua.VariantType.Null),
                                                        datatype=basic_struct.data_type)

basic_var.set_writable()
basic_msg = get_ua_class(basic_struct_name)()
basic_msg.ID = 3
basic_msg.Gender = True
basic_msg.Comments = 'Test string'
basic_var.set_value(basic_msg)




pml_server.start_server()


    
try:
    pml_server.start_server()
    while True:
        time.sleep(1)
finally:
    # close connection, remove subcsriptions, etc
    pml_server.server.stop()