from time import sleep
from threading import Thread, Event
from simple_pick_by_light import simple_pbl as pbl
from simple_pick_by_light.simple_pbl import Box
import socket



class FestoServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        # setup tcpip server that the festo line can connect to. 
        self.TCP_IP = '127.0.0.1'
        self.TCP_PORT = 5005
        self.BUFFER_SIZE = 20  # Normally 1024, but we want fast response

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.TCP_IP, self.TCP_PORT))
        self.s.listen(1)

    def run(self):
        while True:
            conn, addr = self.s.accept()
            print ('Connection address:', addr)
            data = conn.recv(self.BUFFER_SIZE)
            if not data: 
                break
            print ("received data:", data)
            response = operation_number_handler(data)
            conn.send(response)  # echo
            conn.close()


def init():
    # start Festo Server 
    server = FestoServer()
    server.start()



def operation_number_handler(op_number):
    if op_number == 801:
        # select something
        pbl.select_box(1)
        pbl.wait_for_pick(1)
        pbl.select_box(2)
        pbl.select_box(3)
        pbl.wait_for_pick(2)
        pbl.wait_for_pick(3)

    elif op_number == 802:
        ... # do something else

    return "hej"


