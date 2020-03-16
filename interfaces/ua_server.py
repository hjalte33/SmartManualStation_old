from opcua import ua, Server, Node
from time import sleep
from threading import Thread, Event
from logic import rack_controller
from datetime import datetime

class UAServer:
    def __init__(self,rack : rack_controller):
        self.rack = rack
        self._setup_nodes()
        self._generate_tags()

        self.ua_server.start()
        
        self._generate_subscriptions()
        Thread(target=self._var_updater, daemon=True).start()

    def _setup_nodes(self):        
        
        # Create server instance 
        self.ua_server = Server('./opcua_cache')
        self.ua_server.set_endpoint('opc.tcp://0.0.0.0:4840/UA/PickByLight')
        self.ua_server.set_server_name("Pick By Light Server")
        # idx name will be used later for creating the xml used in data type dictionary
        # setup our own namespace, not really necessary but should as spec
        idx_name = 'http://examples.freeopcua.github.io'
        self.idx =  self.ua_server.register_namespace(idx_name)
        
        # Set all possible endpoint policies for clients to connect through
        self.ua_server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic128Rsa15_SignAndEncrypt,
            ua.SecurityPolicyType.Basic128Rsa15_Sign,
            ua.SecurityPolicyType.Basic256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256_Sign])

        # get Objects node, this is where we should put our custom stuff
        objects =  self.ua_server.get_objects_node()
        # add a PackMLObjects folder
        pml_folder =  objects.add_folder(self.idx, "PackMLObjects")
        # Get the base type object
        types =  self.ua_server.get_node(ua.ObjectIds.BaseObjectType)
        # Create a new type for PackMLObjects
        PackMLBaseObjectType =  types.add_object_type(self.idx, "PackMLBaseObjectType")

        # Create objects for the pack tags using the above created packMLBasedObjectType
        self.Admin =  pml_folder.add_object('ns=2;s=Admin', "Admin", PackMLBaseObjectType.nodeid)
        self.Status =  pml_folder.add_object('ns=2;s=Status', "Status", PackMLBaseObjectType.nodeid)
        self.Command =  pml_folder.add_object('ns=2;s=Command', "Command", PackMLBaseObjectType.nodeid)

        # Create an object container for the rack
        self.RackStatus = self.Status.add_object('ns=2;s=Status.Rack', 'Rack')
        #BoxesCommonStatus = BoxesStatus.add_object('ns=2;s=Status.Boxes.Common', 'Common')

    def _generate_tags(self):
        # for all ports generate tags
        for port_number in self.rack.ports:
            # Make a folder with the port_number as the name
            b_obj = self.RackStatus.add_object('ns=2;s=Status.Rack.{}'.format(port_number), str(port_number))
            
            b_obj.add_variable("ns=2;s=Status.Rack.{}.Selected".format(port_number)             ,"Selected"         , bool())
            b_obj.add_variable("ns=2;s=Status.Rack.{}.Activity".format(port_number)             ,"Activity"         , bool())
            b_obj.add_variable("ns=2;s=Status.Rack.{}.ActivityTimestamp".format(port_number)    ,"ActivityTimestamp", datetime.fromtimestamp(0))
            b_obj.add_variable("ns=2;s=Status.Rack.{}.PickTimestamp".format(port_number)        ,"PickTimestamp"    , datetime.fromtimestamp(0))
            b_obj.add_variable("ns=2;s=Status.Rack.{}.LightState".format(port_number)           ,"LightState"       , bool())
            b_obj.add_variable("ns=2;s=Status.Rack.{}.BoxId".format(port_number)                ,"BoxId"            , str())
            b_obj.add_variable("ns=2;s=Status.Rack.{}.ContentId".format(port_number)            ,"ContentId"        , str())
            b_obj.add_variable("ns=2;s=Status.Rack.{}.ContentCount".format(port_number)         ,"ContentCount"     , int())

            '''
            create command tags for clients that does not support ua methods. 
            '''
        
        # create an object in the packml Command object called rack for all the commands. 
        b_obj = self.Command.add_object("ns=2;s=Command.Rack", 'Rack')
        # Create command tag for triggering the selection
        b_obj.add_variable("ns=2;s=Command.Rack.Select", 'Select', -1, ua.VariantType.Int16).set_writable()
        b_obj.add_variable("ns=2;s=Command.Rack.DeSelect", 'DeSelect', -1, ua.VariantType.Int16).set_writable()

    def _generate_subscriptions(self):
        # Create UA subscriber node for the box. Set self as handler.
        sub = self.ua_server.create_subscription(100, self)
 
        # Subscribe to the Select tag
        n = self.ua_server.get_node("ns=2;s=Command.Rack.Select")
        sub.subscribe_data_change(n)

        # Subscribe to the Deselect tag
        n = self.ua_server.get_node("ns=2;s=Command.Rack.DeSelect")
        sub.subscribe_data_change(n)
        pass

    def event_notification(self, event):
        print("Python: New event. No function implemented", event)

    def datachange_notification(self, node, val, data):
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
            print("New data change event", node, val)
            # get the node browse name. 
            node_id = node.get_browse_name().Name
            # If the trigger tag changes to true go in and update the status tag and set the trigger back to false.
            # Also read description above. 
            if node_id == "Select" :
                self.rack.select_port(val)
                node.set_value(-1)
            elif node_id == "Deselect" :
                self.rack.select_port(val)
                node.set_value(-1)

    def _var_updater(self):
        while True:
            sleep(0.1)
            # for all boxes update tags
            for port_number, port in self.rack.ports.items():
                    
                # get the object in the packml status object using our unique idx
                node = self.ua_server.get_node("ns=2;s=Status.Rack.{}.Activity".format(port_number))
                node.set_value(port.activity)          
                node = self.ua_server.get_node("ns=2;s=Status.Rack.{}.ActivityTimestamp".format(port_number))
                node.set_value(port.activity_timestamp) 
                node = self.ua_server.get_node("ns=2;s=Status.Rack.{}.LightState".format(port_number))
                node.set_value(port.get_light())        

            for port_number, box in self.rack.boxes.items():    
                node = self.ua_server.get_node("ns=2;s=Status.Rack.{}.BoxId".format(port_number))
                node.set_value(box.box_id)             
                node = self.ua_server.get_node("ns=2;s=Status.Rack.{}.ContentId".format(port_number))
                node.set_value(box.content_id)         
                node = self.ua_server.get_node("ns=2;s=Status.Rack.{}.ContentCount".format(port_number))
                node.set_value(box.content_count)        
            
            for port_number, select_state in self.rack.ports_select_state.items():
                node = self.ua_server.get_node("ns=2;s=Status.Rack.{}.Selected".format(port_number))          
                node.set_value(select_state.selected)
                node = self.ua_server.get_node("ns=2;s=Status.Rack.{}.PickTimestamp".format(port_number))  
                node.set_value(select_state.pick_timestamp)                   


    






