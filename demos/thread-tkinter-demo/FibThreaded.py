'''
Small threaded GUI application for calculating Fibonacci numbers

WARNING: You must use the "Quit" button; other methods of exiting are not
hooked to App.quit() -- they don't close down the calc thread.
'''

from tkinter import Tk, Frame, Button, Entry, Canvas, Text
from tkinter import LEFT, DISABLED, NORMAL, RIDGE, END
import threading
import queue

class Token:
    '''Data class'''
    def __init__(self):
        self.cancel = None
        self.done = None
        self.halt = None
        self.percent = None
        self.quit = None
        self.start = None
        self.total = None
        self.value = None

class Fib(threading.Thread):
    def __init__ (self):
        threading.Thread.__init__ (self)
        self.inputQueue = queue.Queue()
        self.outputQueue = queue.Queue (1)
        self.currCalc = None
        self.calcQueue = []
        self.hasWork = None

    def run (self):
        while 1:
            if self.calcQueue:
                self.currCalc = self.calcQueue.pop (0)
            else:
                self.hasWork = None
                
                # Block until the first value comes in.
                self.currCalc = self.inputQueue.get()
                
                self.hasWork = 1
                
            if self.currCalc.quit:
                return
            if self.currCalc.value:
                self.calc()

    def calc (self):
        currCalc = self.currCalc
        value = currCalc.value
        token = Token()
        token.start = 1
        token.value = value
        self.queueUpdate (token, 1)
        fib = {0: 1, 1: 1}
        for i in range (2, value + 1):
            try:
                token = self.inputQueue.get_nowait()
                if token.halt:
                    self.calcQueue = []
                    self.queueUpdate (token, 1)
                    return
                self.calcQueue.append (token)
            except queue.Empty:
                pass
            fib [i] = fib [i - 1] + fib [i - 2]
            currCalc.percent = 1.0 * i / value
            self.queueUpdate (currCalc)
        currCalc.total = fib [value]
        currCalc.done = 1
        self.queueUpdate (currCalc, 1)
    
    def put (self, value):
        self.inputQueue.put (value)

    def queueUpdate (self, token, blocking = 0):
        if blocking:
            self.outputQueue.put (token)
        else:
            try:
                self.outputQueue.put_nowait (token)
            except queue.Full:
                pass
    
    def getStatus (self):
        try:
            token = self.outputQueue.get_nowait()
        except queue.Empty:
            token = None
        return token

    # This is technically not completely thread-safe
    def outputPending (self):
        return self.hasWork or (not self.outputQueue.empty())

class App:
    def __init__ (self, master):
        self.master = master
        self.setupWindow (self.master)
        
        # Create and start thread. Thread will waiting for value.
        self.calcThread = Fib()
        self.calcThread.start()

    def setupWindow (self, master):
        bigFont = ('Helvetica', 34)
        smallFont = ('Times', 26)
        
        frame = Frame(master)
        frame.pack()
        tmpFrame = Frame(frame)
        tmpFrame.pack()
        
        calc = Button (tmpFrame,
            text = 'Fibonacci',
            command = self.startCalc,
            font=bigFont
        )
        calc.pack (side = LEFT)
        
        stop = Button (tmpFrame,
            text = 'Stop',
            command = self.stopCalc,
            font = bigFont
        )
        stop.pack (side = LEFT)
        
        quit = Button (tmpFrame,
            text = 'Quit',
            command = self.quit,
            font = bigFont
        )
        quit.pack()
        
        self.entry = Entry (frame, font = bigFont)
        self.entry.pack()
        
        self.progressWidth = 400
        self.progressHeight = 25
        self.canvas = Canvas (frame,
            width = self.progressWidth, 
            height = self.progressHeight,
            borderwidth = 1,
            relief = RIDGE
        )
        self.canvas.pack()
        self.progressBar = self.canvas.create_rectangle (0, 0, 0, 0,
            fill = 'black'
        )
        
        self.output = Text (frame,
            font = smallFont,
            height = 12,
            width = 55,
            state = DISABLED)
        self.output.pack()

    def startCalc (self):
        value = self.entry.get()
        try:
            self.updateBar (0.0)
            value = int (value)
            assert value >= 0
            token = Token()
            token.value = value
            
            # Put the value in the thread.
            # The thread will now start the calculation.
            self.calcThread.put (token)
            
            self.setCheck()
        except (ValueError, AssertionError):
            self.display ("Illegal value: " + str (value))

    def setCheck (self):
        # In a real application, use 100ms instead of 1ms
        self.master.after (1, self.checkCalc)

    def checkCalc (self):
        token = self.calcThread.getStatus()
        if not token:
            pass
        elif token.start:
            self.updateBar (0.0)
            self.display ('Calculating Fibonacci number %s' % token.value)
        elif token.halt:
            self.updateBar (1.0)
            self.display ("Calculation halted")
        elif token.done:
            self.updateBar (1.0)
            self.display (token.total)
        elif token.percent:
            self.updateBar (token.percent)
        else:
            raise Exception ("What am I doing here?")
        if self.calcThread.outputPending():
            self.setCheck()

    def stopCalc (self):
        token = Token()
        token.halt = 1
        self.calcThread.put (token)

    def quit (self):
        token = Token()
        token.halt = 1
        self.calcThread.put (token)
        token = Token()
        token.quit = 1
        self.calcThread.put(token)
        self.checkCalc()
        self.calcThread.join()
        self.master.quit()

    def display (self, value):
        self.output.configure (state = NORMAL)
        self.output.delete (1.0, END)
        self.output.insert (END, value)
        self.output.configure (state = DISABLED)
        self.master.update_idletasks()

    def updateBar (self, percent):
        width = self.progressWidth * percent
        height = self.progressHeight
        self.canvas.coords (self.progressBar, 0, 0, width, height)
        self.master.update_idletasks()

root = Tk()
app = App (root)
root.mainloop()
