#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Beispiel für tkinter - Destroy Events behandeln

import tkinter
import tkinter.messagebox

def callback():
    if tkinter.messagebox.askokcancel ("Beenden",
            "Wollen Sie wirklich das Programm beenden?"):
        root.destroy()

root = tkinter.Tk()
root.protocol ("WM_DELETE_WINDOW", callback)
root.mainloop()
