class Dummy:
    def __getattr__(self, name):
        print ('iran')
        return "heyy"

i = Dummy()

#setattr(i,'something','goodday')
print (i.something)