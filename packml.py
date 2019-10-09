from opcua import ua, Server
import time

server = Server('./opcua_cache')

server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/PickByLight')
server.set_server_name("Pick By Light Server")
        
# setup our own namespace, not really necessary but should as spec
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)


#set all possible endpoint policies for clienst to connect through
server.set_security_policy([
    ua.SecurityPolicyType.NoSecurity,
    ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
    ua.SecurityPolicyType.Basic256Sha256_Sign])

# create new nodes
command_node = server.nodes.base_object_type.add_object(idx, 'Command')
command_node.add_variable(idx, 'testing_this_node',1).set_modelling_rule(True)
command_node.add_property(idx, 'a property test','the value')
objects = server.get_objects_node()



server.start()        
 

      