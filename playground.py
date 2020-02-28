from time import sleep

#################################################################

class Dummy:
    
    
    def __init__(self):
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setup(32, GPIO.OUT)
        self.testvar1 = 55
        self.testvar2 = "davdav"

    def wow(self):
        print(self.testvar2)

class WithSlots:
    __slots__ = ['s1', 's2']

#i = Dummy()
#setattr(i,'something','goodday')
#print (i.something)

################################################################

s = WithSlots()
s.s1 = "foo"
setattr(s,"ns1","bar")

print (s.ns1)

i = Dummy()

print(s.s1)

sleep(1)




