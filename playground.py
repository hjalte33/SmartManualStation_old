from time import sleep

#################################################################

class Dummy:
    def __getattr__(self, name):
        print ('iran')
        return "heyy"
    
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(32, GPIO.OUT)

#i = Dummy()
#setattr(i,'something','goodday')
#print (i.something)

################################################################
import RPi.GPIO as GPIO





##################################################################3
#!/usr/bin/env python

import socket


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = "803"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE.encode())
data = s.recv(BUFFER_SIZE)
s.close()

print ("received data:", data)



