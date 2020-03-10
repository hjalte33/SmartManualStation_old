from time import sleep

#################################################################

class Dummy:
    
    
    def __init__(self):
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setup(32, GPIO.OUT)
        self.s1 = 55
        self.s2 = "davdav"

    def wow(self):
        print(self.testvar2)


#i = Dummy()
#setattr(i,'something','goodday')
#print (i.something)

################################################################

s = Dummy()
l = Dummy()

a_list = {"one": s, "two": l}

b_list = []
b_list.append(a_list["two"])

b_list[0].s2 = "hejhej"

del a_list["two"]


print (a_list["one"].s2, b_list[0].s2)


sleep(1)




