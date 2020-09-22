from time import sleep
from threading import Thread, Event
from opcua import ua, Client
from logic.rack_controller import RackController
import PySimpleGUI as sg



class FestoServer(Thread):
    def __init__(self, rack: RackController, festo_ip: str, ua_port = '4840'):
        super().__init__(daemon=True)
        self.rack = rack

        self.client = Client("opc.tcp://{}:{}".format(festo_ip, ua_port))
        self.client.connect()
        print("Festo OPC-UA Client Connected")

        self._select_event = Event()
        
    def run(self):
        while True:
            sleep(0.1)
            flag = self.client.get_node("ns=2;s=|var|CECC-LK.Application.Flexstation_globalVariables.FlexStationStatus") 
            status = flag.get_value()
            if status == 1:
                flag.set_value(ua.Variant(2, ua.VariantType.Int16))
                Operation_number = self.client.get_node("ns=2;s=|var|CECC-LK.Application.FBs.stpStopper1.stAppControl.uiOpNo").get_value() # change to order id
                Order_url = self.client.get_node("ns=2;s=|var|CECC-LK.Application.AppModul.stRcvData.sOderDes").get_value()
                response = self.operation_number_handler(Operation_number,Order_url)
                flag.set_value(ua.Variant(response, ua.VariantType.Int16))

                sleep(1)

    
    def draw_pic(self, color):
        sg.theme('Dark Blue 3')  # please make your windows colorful

        layout = [[sg.Text('pic the ' + color + ' cover', size=(50,10),font=('Helvetica', 20))],
            [sg.Submit(size=(10,5), font=('Helvetica', 20)), sg.Cancel(size=(10,5),font=('Helvetica', 20))]]

        window = sg.Window('smart manual station', layout)

        while True:
            event, values = window.read()
            print(event, values)
            if event is None or event == 'Cancel':
                return_val = 4
                self.rack.deselect_all()
                break
            elif event == "Submit" and self._select_event.is_set():
                return_val = 3
                break
        # Finally
        window.close()
        self._select_event.clear()
        return return_val

    def draw_work(self, text):
        sg.theme('Dark Blue 3')  # please make your windows colorful

        layout = [[sg.Text(text, size=(50,10),font=('Helvetica', 20))],
            [sg.Submit(size=(10,5), font=('Helvetica', 20)), sg.Cancel(size=(10,5),font=('Helvetica', 20))]]

        window = sg.Window('smart manual station', layout)

        while True:
            event, values = window.read()
            print(event, values)
            if event is None or event == 'Cancel':
                return_val = 4
                self.rack.deselect_all()
                break
            elif event == "Submit" and self._select_event.is_set():
                return_val = 3
                break
        # Finally
        window.close()
        self._select_event.clear()
        return return_val


    def _rack_callback(self, *args, **kwargs):
        self._select_event.set()

    def operation_number_handler(self, op_number,order_url):
        op_number = int(op_number)
        if op_number == 801:
            Operation_par = self.client.get_node("ns=2;s=|var|CECC-LK.Application.AppModul.stAppControl.auiPar").get_value()
            if Operation_par == 0: #black
                return self.draw_pic("black")
            elif Operation_par == 1:
                #white
                self.rack.select_port(port_number=1, callback=self._rack_callback)
                return self.draw_pic("white")
            elif Operation_par == 2:
                #blue
                self.rack.select_port(port_number=6, callback=self._rack_callback)
                return self.draw_pic("blue")          
        
        elif op_number == 802:
            #blue
            self.rack.select_port(port_number=6, callback=self._rack_callback)
            return self.draw_pic("blue")          
        
        elif op_number == 803:
            #black
            return self.draw_pic("black")

        elif op_number == 804:
            #white
            self.rack.select_port(port_number=1, callback=self._rack_callback)
            return self.draw_pic("white")

        elif op_number == 510:
            if "FuseLeft" in order_url:
                self.rack.select_port(port_number=3, callback=self._rack_callback)
                return self.draw_work("make sure a fuse is placed left (to the right for you)")
            elif "FuseRight" in order_url:
                self.rack.select_port(port_number=3, callback=self._rack_callback)
                return self.draw_work("make sure a fuse is placed right (to the left for you)")
            elif "BothFuses" in order_url:
                self.rack.select_port(port_number=3, callback=self._rack_callback)
                return self.draw_work("make sure both fuse are placed in the phone")
            elif "NoFuse" in order_url:
                self.rack.select_port(port_number=3, callback=self._rack_callback)
                return self.draw_work("make sure no fuses are placed")
                
            elif "Blue" in order_url and "Top" in order_url: 
                self.rack.select_port(port_number=6, callback=self._rack_callback)
                return self.draw_pic("blue")
            elif "White" in order_url and "Top" in order_url: 
                self.rack.select_port(port_number=1, callback=self._rack_callback)
                return self.draw_pic("white")
                

        else: 
            print("{} not a valid operation".format(op_number))
            return 404



