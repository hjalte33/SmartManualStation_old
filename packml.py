from opcua import ua, Server
import time

class PackML:
    def __init__(self):
        # constructor
        self.server = Server('./opcua_cache')

        self.server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/PickByLight')
        self.server.set_server_name("Pick By Light Server")
        
        # setup our own namespace, not really necessary but should as spec
        uri = "http://examples.freeopcua.github.io"
        self.idx = self.server.register_namespace(uri)


        #set all possible endpoint policies for clienst to connect through
        self.server.set_security_policy([
                ua.SecurityPolicyType.NoSecurity,
                ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
                ua.SecurityPolicyType.Basic256Sha256_Sign])

        # create new nodes
        self.command_node = self.server.nodes.base_object_type.add_object(self.idx, 'Command')
        self.command_node.add_variable(self.idx, 'testing_this_node',1).set_modelling_rule(True)
        self.command_node.add_property(self.idx, 'a property test','the value')
        self.objects = self.server.get_objects_node()


    def add_object(self, name):
        return self.objects.add_object(self.idx, name)

    def create_node_var(self, name, data):
        pass

    def set_data(self, name, path, *arg):
        pass

    def start_server(self):
        self.server.start()        
 
if __name__ == "__main__": 
    my_opc = PackML()
    my_opc.start_server()
    
    try:
        count = 0
        while True:
            time.sleep(1)
            print('counting... %s' %count)
            count += 0.1
            my_opc.status_obj.set_value(count)
    finally:
        #close connection, remove subcsriptions, etc
        my_opc.server.stop()


        