'''
Small threaded GUI application for calculating Fibonacci numbers

WARNING: You must use the "Quit" button; other methods of exiting are not
hooked to App.quit() -- they don't close down the calc thread.
'''

import tkinter
import threading
import queue

class Token:
    '''Data class. Kinda ugly and primitive.'''
    def __init__(self):
        self.cancel = None
        self.done = False
        self.halt = False
        self.percent = None
        self.quit = None
        self.start = None
        self.total = None
        self.value = None

class Fib(threading.Thread):
    def __init__(self):
        super().__init__()
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue(1)
        self.curr_calc = None
        self.calc_stack = []
        self.haswork = False

    def run(self):
        while True:
            if self.calc_stack:
                self.curr_calc = self.calc_stack.pop(0)
            else:
                self.haswork = None
                
                # Block until the first value comes in.
                self.curr_calc = self.in_queue.get()
                
                self.haswork = True
                
            if self.curr_calc.quit:
                return
            if self.curr_calc.value:
                self.calc()

    def calc(self):
        curr_calc = self.curr_calc
        value = curr_calc.value
        token = Token()
        token.start = 1
        token.value = value
        self.queueUpdate (token, True)
        fib = {0: 1, 1: 1}
        for i in range(2, value + 1):
            try:
                token = self.in_queue.get_nowait()
                if token.halt:
                    self.calc_stack = []
                    self.queueUpdate(token, 1)
                    return
                self.calc_stack.append(token)
            except queue.Empty:
                pass
            fib[i] = fib[i - 1] + fib[i - 2]
            curr_calc.percent = 1.0 * i / value
            self.queueUpdate(curr_calc)
        curr_calc.total = fib[value]
        curr_calc.done = True
        self.queueUpdate(curr_calc, 1)
    
    def put(self, value):
        self.in_queue.put (value)

    def queueUpdate(self, token, blocking = False):
        if blocking:
            self.out_queue.put(token)
        else:
            try:
                self.out_queue.put_nowait(token)
            except queue.Full:
                pass
    
    def getStatus (self):
        try:
            token = self.out_queue.get_nowait()
        except queue.Empty:
            token = None
        return token

    # This is technically not completely thread-safe
    def outputPending(self):
        return self.haswork or (not self.out_queue.empty())

class App:
    def __init__(self, master):
        self.master = master
        self.setupWindow(self.master)
        
        # Create and start thread. Thread will waiting for value.
        self.calcThread = Fib()
        self.calcThread.start()

    def setupWindow(self, master):
        bigFont = ('Helvetica', 34)
        smallFont = ('Times', 26)
        
        frame = tkinter.Frame(master)
        frame.pack()
        tmpFrame = tkinter.Frame(frame)
        tmpFrame.pack()
        
        calc = tkinter.Button(tmpFrame,
            text = 'Fibonacci',
            command = self.startCalc,
            font=bigFont
        )
        calc.pack (side = tkinter.LEFT)
        
        stop = tkinter.Button(tmpFrame,
            text = 'Stop',
            command = self.stopCalc,
            font = bigFont
        )
        stop.pack(side = tkinter.LEFT)
        
        quit = tkinter.Button(tmpFrame,
            text = 'Quit',
            command = self.quit,
            font = bigFont
        )
        quit.pack()
        
        self.entry = tkinter.Entry(frame, font = bigFont)
        self.entry.pack()
        
        self.progressWidth = 400
        self.progressHeight = 25
        self.canvas = tkinter.Canvas(frame,
            width = self.progressWidth, 
            height = self.progressHeight,
            borderwidth = 1,
            relief = tkinter.RIDGE
        )
        self.canvas.pack()
        self.progressBar = self.canvas.create_rectangle(0, 0, 0, 0,
            fill = 'black'
        )
        
        self.output = tkinter.Text(frame,
            font = smallFont,
            height = 12,
            width = 55,
            state = tkinter.DISABLED
        )
        self.output.pack()

    def startCalc(self):
        value = self.entry.get()
        try:
            self.updateBar(0.0)
            value = int(value)
            assert value >= 0
            token = Token()
            token.value = value
            
            # Put the value in the thread.
            # The thread will now start the calculation.
            self.calcThread.put(token)
            
            self.setCheck()
        except (ValueError, AssertionError):
            self.display("Illegal value: " + str(value))

    def setCheck(self):
        # In a real application, use 100ms instead of 1ms
        self.master.after (1, self.checkCalc)

    def checkCalc(self):
        token = self.calcThread.getStatus()
        if not token:
            pass
        elif token.start:
            self.updateBar(0.0)
            self.display('Calculating Fibonacci number %s' % token.value)
        elif token.halt:
            self.updateBar(1.0)
            self.display("Calculation halted")
        elif token.done:
            self.updateBar(1.0)
            self.display(token.total)
        elif token.percent:
            self.updateBar(token.percent)
        else:
            raise Exception("What am I doing here?")
        if self.calcThread.outputPending():
            self.setCheck()

    def stopCalc(self):
        token = Token()
        token.halt = 1
        self.calcThread.put(token)

    def quit (self):
        token = Token()
        token.halt = 1
        self.calcThread.put(token)
        token = Token()
        token.quit = 1
        self.calcThread.put(token)
        self.checkCalc()
        self.calcThread.join()
        self.master.destroy()

    def display (self, value):
        self.output.configure(state = tkinter.NORMAL)
        self.output.delete(1.0, tkinter.END)
        self.output.insert(tkinter.END, value)
        self.output.configure(state = tkinter.DISABLED)
        self.master.update_idletasks()

    def updateBar(self, percent):
        width = self.progressWidth * percent
        height = self.progressHeight
        self.canvas.coords(self.progressBar, 0, 0, width, height)
        self.master.update_idletasks()

root = tkinter.Tk()
app = App(root)
root.mainloop()
