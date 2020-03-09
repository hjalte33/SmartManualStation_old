from time import sleep
from threading import Thread, Event
from simple_pick_by_light import simple_pbl as pbl
from simple_pick_by_light.simple_pbl import Box
import socket
from opcua import ua, Client

client = Client("opc.tcp://172.20.8.1:4840")

class FestoServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        # setup tcpip server that the festo line can connect to. 
        self.TCP_IP = '0.0.0.0'
        self.TCP_PORT = 5005
        self.BUFFER_SIZE = 3  # Normally 1024, but we want fast response

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.TCP_IP, self.TCP_PORT))
        self.s.listen(1)
    
        client = Client(url)

        client.connect()
        print("Client Connected")
        flag = client.get_node("ns=2;s=|var|CECC-LK.Application.g_ctrl_modules.man_1.com") 
        

    def run(self):


        while True:
            print('listening for tcp-ip')
            conn, addr = self.s.accept()
            print ('Connection address:', addr)
            while True:
                try:
                    print("waiting for data")
                    data = conn.recv(self.BUFFER_SIZE)
                    print(data)
                    print ("received data:", data.decode())
                    if data.decode():
                        conn.send("1".encode())
                    else:
                        break
                    response = operation_number_handler(data.decode())
                    print("sending ", response)
                    conn.send(response.encode())  # echo
                
                except KeyboardInterrupt:
                    print('interrupted!')
                    conn.close()
                except Exception as e:
                    print("error on tcp connection: clossing connection ", e)
                    conn.close()
                    break


def init():
    # start Festo Server 
    server = FestoServer()
    server.start()


def draw_pic(color):
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
    return "2"


