'''
Tiny unthreaded GUI application for calculating Fibonacci numbers
'''

from tkinter import Tk, Frame, Button, Entry, Canvas, Text
from tkinter import LEFT, DISABLED, NORMAL, RIDGE, END

class App:
    def __init__(self, master):
        bigFont = ('Helvetica', 34)
        smallFont = ('Times', 26)
        self.master = master
        frame = Frame(master)
        frame.pack()
        tmpFrame = Frame(frame)
        tmpFrame.pack()
        calc = Button(tmpFrame, text='Fibonacci', command = self.calc, font=bigFont)
        calc.pack(side=LEFT)
        stop = Button(tmpFrame, text='Stop', font=bigFont)
        stop.pack(side=LEFT)
        quit = Button(tmpFrame, text='Quit', command=frame.quit, font=bigFont)
        quit.pack()
        self.entry = Entry(frame, font=bigFont)
        self.entry.pack()
        self.progressWidth = 400
        self.progressHeight = 25
        self.canvas = Canvas(frame, width=self.progressWidth, 
            height=self.progressHeight, borderwidth=1, relief=RIDGE)
        self.canvas.pack()
        self.progressBar = self.canvas.create_rectangle(0,0,0,0, fill='black')
        self.output = Text(frame, font=smallFont, height=12, width=55, state=DISABLED)
        self.output.pack()

    def calc(self):
        value = self.entry.get()
        try:
            self.updateBar(0.0)
            value = int(value)
            assert value >= 0
            self.display('Calculating Fibonacci number %s' % value)
            fib = {0:1, 1:1}
            for i in range(2, value+1):
                fib[i] = fib[i-1] + fib[i-2]
                self.updateBar(1.0 * i / value)
            self.display(fib[value])
        except (ValueError, AssertionError):
            self.display("Illegal value: " + str(value) )

    def display(self, value):
        self.output.configure(state=NORMAL)
        self.output.delete(1.0, END)
        self.output.insert(END, value)
        self.output.configure(state=DISABLED)

    def updateBar(self, percent):
        width = self.progressWidth * percent
        height = self.progressHeight
        self.canvas.coords(self.progressBar, 0, 0, width, height)
        self.master.update_idletasks()

root = Tk()

app = App(root)

root.mainloop()
