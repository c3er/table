#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Beispiel für tkinter - Dialog-Fenster

import tkinter

class MyDialog:
    def __init__ (self, parent):
        self.top = tkinter.Toplevel (parent)
        tkinter.Label (self.top, text = "Wert").pack()
        self.e = tkinter.Entry (self.top)
        self.e.pack (padx = 5)
        tkinter.Button (self.top, text = "OK", command = self.ok).pack (pady = 5)

    def ok (self):
        print ("Der Wert ist", self.e.get())
        self.top.destroy()

root = tkinter.Tk()
tkinter.Button (root, text = "Hallo").pack()
d = MyDialog (root)
root.wait_window()
