from time import sleep

#################################################################

class Dummy:
    
    
    def __init__(self):
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setup(32, GPIO.OUT)
        self.s1 = 55
        self.s2 = "davdav"

    def wow(self):
        print(self.s1)


#i = Dummy()
#setattr(i,'something','goodday')
#print (i.something)

################################################################

import curses
import time
import threading

def show_progress(win,X_line,sleeping_time):

    # This is to move the progress bar per iteration.
    pos = 10
    # Random number I chose for demonstration.
    for i in range(15):
        # Add '.' for each iteration.
        win.addstr(X_line,pos,".")
        # Refresh or we'll never see it.
        win.refresh()
        # Here is where you can customize for data/percentage.
        time.sleep(sleeping_time)
        # Need to move up or we'll just redraw the same cell!
        pos += 1
    # Current text: Progress ............... Done!
    win.addstr(X_line,26,"Done!")
    # Gotta show our changes.
    win.refresh()
    # Without this the bar fades too quickly for this example.
    time.sleep(0.5)

def show_progress_A(win):
    show_progress( win, 1, 0.1)

def show_progress_B(win):
    show_progress( win, 4 , 0.5)

if __name__ == '__main__':
    curses.initscr()


    win = curses.newwin(6,32,14,10)
    win.border(0)
    win.addstr(1,1,"Progress ")
    win.addstr(4,1,"Progress ")
    win.refresh()

    threading.Thread( target = show_progress_B, args = (win,) ).start()
    time.sleep(2.0)
    threading.Thread( target = show_progress_A, args = (win,)).start()




