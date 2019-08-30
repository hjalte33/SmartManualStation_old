from opcua import ua, Server
import time

class PackML:
    def __init__(self):
        # constructor
        self.server = Server('./opcua_cache')

        self.server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/SampleServer')
        
        # setup our own namespace, not really necessary but should as spec
        uri = "http://examples.freeopcua.github.io"
        self.idx = self.server.register_namespace(uri)

        # get Objects node, this is where we should put our nodes
        self.objects = self.server.get_objects_node()

        # populating our address space
        self.myobj = self.objects.add_object(self.idx, "MyObject")
        self.myvar = self.myobj.add_variable(self.idx, "MyVariable", 6.7)
        self.myvar.set_writable()    # Set MyVariable to be writable by clients

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
            my_opc.myvar.set_value(count)
    finally:
        #close connection, remove subcsriptions, etc
        my_opc.server.stop()


        