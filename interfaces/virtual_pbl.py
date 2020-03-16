#!/usr/bin/env python3
import PySimpleGUI as sg
import time
import random
from logic import rack_controller as rc
from threading import Thread
import re



def runLoop(rack):
    thread = Thread(target=gui, daemon=True, args=(rack,))
    thread.start()
    thread.join()
    raise KeyboardInterrupt("gui closed")

def LEDIndicator(key=None, radius=30):
    return sg.Graph(canvas_size=(radius, radius),
             graph_bottom_left=(-radius, -radius),
             graph_top_right=(radius, radius),
             pad=(0, 0), key=key, enable_events=True)

def SetLED(window, key, color):
    graph = window[key]
    graph.erase()
    graph.draw_circle((0, 0), 12, fill_color=color, line_color=color)

def SetCheckBox(window, key, value):
    check = window[key]
    check.Update(value = value)



def gui(rack : rc.RackController):
    layout = [[sg.Text('Port status indicators', size=(20,1))],
            [sg.Check(text = None, key='_C1_',enable_events=True), sg.Text('Port 1'), LEDIndicator('_A1_'), LEDIndicator('_LED1_')],
            [sg.Check(text = None, key='_C2_',enable_events=True), sg.Text('Port 2'), LEDIndicator('_A2_'), LEDIndicator('_LED2_')],
            [sg.Check(text = None, key='_C3_',enable_events=True), sg.Text('Port 3'), LEDIndicator('_A3_'), LEDIndicator('_LED3_')],
            [sg.Check(text = None, key='_C4_',enable_events=True), sg.Text('port 4'), LEDIndicator('_A4_'), LEDIndicator('_LED4_')],
            [sg.Check(text = None, key='_C5_',enable_events=True), sg.Text('port 5'), LEDIndicator('_A5_'), LEDIndicator('_LED5_')],
            [sg.Check(text = None, key='_C6_',enable_events=True), sg.Text('port 6'), LEDIndicator('_A6_'), LEDIndicator('_LED6_')],
            [sg.Button('Exit')]]

    window = sg.Window('My new window', layout, default_element_size=(12, 1), auto_size_text=False, finalize=True)

    while True:  # Event Loop
        event, value = window.read(timeout=100)
        if event == 'Exit' or event is None:
            break
        if value is None:
            break

        if '_A' in event:
            result = re.findall(r'\d+',event)
            port_number = int(result[0])
            rack.ports[port_number].make_activity()
        
        if '_C' in event:
            result = re.findall(r'\d+',event)
            port_number = int(result[0])
            if value[event]:
                rack.select_port(port_number)
            else:
                rack.deselect_port(port_number) 

        for port_number, port in rack.ports.items():
            SetLED(window, '_A{}_'.format(port_number), 'green' if port.activity else 'cyan')
            SetLED(window, '_LED{}_'.format(port_number), 'white' if port.get_light() else 'black')
            SetCheckBox(window, '_C{}_'.format(port_number),rack.ports_select_state[port_number].selected)

    window.close()