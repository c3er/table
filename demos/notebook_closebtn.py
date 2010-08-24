"""A Ttk Notebook with close buttons.

Based on an example by patthoyts, http://paste.tclers.tk/896
"""
import tkinter
from tkinter import ttk

root = tkinter.Tk()

# create a ttk notebook with our custom style, and add some tabs to it
nb = ttk.Notebook(width=200, height=200)
f1 = tkinter.Frame(nb, background="red")
f2 = tkinter.Frame(nb, background="green")
f3 = tkinter.Frame(nb, background="blue")
nb.add(f1, text='Red', padding=3)
nb.add(f2, text='Green', padding=3)
nb.add(f3, text='Blue', padding=3)
nb.pack(expand=1, fill='both')

root.mainloop()
