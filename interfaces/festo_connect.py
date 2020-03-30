#!/usr/bin/env python3
from time import sleep
from threading import Thread, Event
from opcua import ua, Client
from logic.rack_controller import RackController
import PySimpleGUIQt as sg



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
                Operation_number = self.client.get_node("ns=2;s=|var|CECC-LK.Application.FBs.stpStopper1.stAppControl.uiOpNo") # change to order id
                response = self.operation_number_handler(Operation_number.get_value())
                flag.set_value(ua.Variant(response, ua.VariantType.Int16))
                sleep(1)
    
    def draw_pic(self, color):
        sg.theme('Dark Blue 3')  # please make your windows colorful

        layout = [[sg.Text('pic the ' + color + ' cover', size=(80,5),font=('Helvetica', 20))],
                [sg.Submit(size=(40,5), font=('Helvetica', 20)), sg.Cancel(size=(40,5),font=('Helvetica', 20))]]

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

    def operation_number_handler(self, op_number):
        op_number = int(op_number)

        if op_number == 802:
            #blue
            self.rack.select_port(port_number=1, callback=self._rack_callback)
            return self.draw_pic("blue")
            

        elif op_number == 803:
            #black
            self.rack.select_port(port_number=2, callback=self._rack_callback)
            return self.draw_pic("blue")

        elif op_number == 804:
            #white
            self.rack.select_port(port_number=3, callback=self._rack_callback)
            return self.draw_pic("blue")
        
        else: 
            print("not a valid operation")
            return "404"



