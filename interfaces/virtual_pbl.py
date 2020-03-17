#!/usr/bin/env python3
import PySimpleGUI as sg
from logic import rack_controller as rc
from threading import Thread
import re


def LEDIndicator(key=None, radius=30):
    return sg.Graph(canvas_size=(radius, radius),
             graph_bottom_left=(-radius, -radius),
             graph_top_right=(radius, radius),
             pad=(0, 0), key=key, enable_events=True)

class VirtualPBL(Thread):
    def __init__(self, rack: rc.RackController):
        super().__init__(daemon=True)
        self.rack = rack

    def _set_led(self, window, key, color):
        """Sets the LED indicator"""
        graph = self.window[key]
        graph.erase()
        graph.draw_circle((0, 0), 12, fill_color=color, line_color=color)

    def _set_checkbox(self, window, key, value):
        """Updates the value of the checkbox"""
        check = window[key]
        check.Update(value=value)

    def _create_layout(self):
        """Create a layout that matches the rack"""
        layout = [[sg.Text('Select, Port, Activity, Light', size=(20,1))]]

        for port_number in self.rack.ports:
            row = [sg.Check(text = None, key='_C{}_'.format(port_number), enable_events=True),
                   sg.Text('Port {}'.format(port_number)), 
                   LEDIndicator('_A{}_'.format(port_number)), 
                   LEDIndicator('_LED{}_'.format(port_number)),
                  ]
            layout.append(row)
        # Finally append the exit botton
        layout.append([sg.Button('Exit')])
        return layout
    
    def stop(self):
        self.window.close()

    def run(self):
        layout = self._create_layout()
        self.window = sg.Window('Virtual Pick By Light', layout, default_element_size=(12, 1), auto_size_text=False, finalize=True)
        while True:  # Event Loop
            event, value = self.window.read(timeout=100)
            if event == 'Exit' or event is None:
                break
            if value is None:
                break

            if '_A' in event:
                result = re.findall(r'\d+',event)
                port_number = int(result[0])
                self.rack.ports[port_number].make_activity()
            
            if '_C' in event:
                result = re.findall(r'\d+',event)
                port_number = int(result[0])
                if value[event]:
                    self.rack.select_port(port_number)
                else:
                    self.rack.deselect_port(port_number) 

            for port_number, port in self.rack.ports.items():
                self._set_led(self.window, '_A{}_'.format(port_number), 'green' if port.activity else 'cyan')
                self._set_led(self.window, '_LED{}_'.format(port_number), 'white' if port.get_light() else 'black')
                self._set_checkbox(self.window, '_C{}_'.format(port_number), self.rack.ports_select_state[port_number].selected)
        
        self.window.close()
        raise KeyboardInterrupt("gui closed")
 