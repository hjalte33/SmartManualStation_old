#!/usr/bin/env python3
from time import sleep
from threading import Thread, Event
from simple_pick_by_light import simple_pbl as pbl
from simple_pick_by_light.simple_pbl import Box
from opcua import ua, Client
import PySimpleGUI as sg

client = Client("opc.tcp://172.20.8.1:4840")

class FestoServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        # setup tcpip server that the festo line can connect to. 

        client.connect()
        print("Client Connected")
        
        

    def run(self):
        while True:
            sleep(0.1)
            flag = client.get_node("ns=2;s=|var|CECC-LK.Application.Flexstation_globalVariables.FlexStationStatus") 
            status = flag.get_value()
            if status == 1:
                flag.set_value(ua.Variant(2, ua.VariantType.Int16))
                Operation_number = client.get_node("ns=2;s=|var|CECC-LK.Application.FBs.stpStopper1.stAppControl.uiOpNo") # change to order id
                response = operation_number_handler(Operation_number.get_value())
                flag.set_value(ua.Variant(3, ua.VariantType.Int16))
                sleep(1)


def init():
    # start Festo Server 
    server = FestoServer()
    server.start()


def draw_pic(color):
    sg.theme('Dark Blue 3')  # please make your windows colorful

    layout = [[sg.Text('pic the ' + color + ' cover', size=(80,5),font=('Helvetica', 20))],
            [sg.Submit(size=(40,5), font=('Helvetica', 20)), sg.Cancel(size=(40,5),font=('Helvetica', 20))]]

    window = sg.Window('smart manual station', layout)

    event, values = window.read()
    window.close()

    print(values)  # the first input element is values[0]
    pass

def operation_number_handler(op_number):
    op_number = int(op_number)

    if op_number == 802:
        #blue
        pbl.select_box(1)
        draw_pic("blue")
        pbl.wait_for_pick(1)

    elif op_number == 803:
        #black
        pbl.select_box(2)
        draw_pic("black")
        pbl.wait_for_pick(2)

    elif op_number == 804:
        #white
        pbl.select_box(3)
        draw_pic("white")
        pbl.wait_for_pick(3)
    else: 
        print("not a valid operation")
        return "404"
    return "3"


