#!/usr/bin/env python3
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
        
    def run(self):
        while True:
            sleep(0.1)
            flag = self.client.get_node("ns=2;s=|var|CECC-LK.Application.Flexstation_globalVariables.FlexStationStatus") 
            status = flag.get_value()
            if status == 1:
                flag.set_value(ua.Variant(2, ua.VariantType.Int16))
                Operation_number = self.client.get_node("ns=2;s=|var|CECC-LK.Application.FBs.stpStopper1.stAppControl.uiOpNo") # change to order id
                response = self.operation_number_handler(Operation_number.get_value())
                flag.set_value(ua.Variant(3, ua.VariantType.Int16))
                sleep(1)
    
    def draw_pic(self, color):
        sg.theme('Dark Blue 3')  # please make your windows colorful

        layout = [[sg.Text('pic the ' + color + ' cover', size=(80,5),font=('Helvetica', 20))],
                [sg.Submit(size=(40,5), font=('Helvetica', 20)), sg.Cancel(size=(40,5),font=('Helvetica', 20))]]

        window = sg.Window('smart manual station', layout)

        event, values = window.read()
        window.close()

        print(values)  # the first input element is values[0]
        pass

    def operation_number_handler(self, op_number):
        op_number = int(op_number)

        if op_number == 802:
            #blue
            self.rack.select_port(port_number=1, callback=)
            self.draw_pic("blue")
            pbl.wait_for_pick(1)

        elif op_number == 803:
            #black
            pbl.select_box(2)
            self.draw_pic("black")
            pbl.wait_for_pick(2)

        elif op_number == 804:
            #white
            pbl.select_box(3)
            self.draw_pic("white")
            pbl.wait_for_pick(3)
        else: 
            print("not a valid operation")
            return "404"
        return "3"


