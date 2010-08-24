#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Beispiel für tkinter - Menü

import tkinter
import tkinter.messagebox

WIDTH = 800
HEIGHT = 600

class StatusBar (tkinter.Frame):
    def __init__ (self, master):
        tkinter.Frame.__init__ (self, master)
        self._label = tkinter.Label (self,
            bd = 1,
            relief = tkinter.SUNKEN,
            anchor = tkinter.W)
        self._label.pack (fill = tkinter.X)
        self._ltext = ""

    def get_label (self):
        return self._ltext

    def set_label (self, msg):
        self._ltext = msg
        self._label.config (text = msg)
        self._label.update_idletasks()

    text = property (get_label, set_label)

    def clear (self):
        self._label.config (text = "")
        self._label.update_idletasks()


def callback (status, cnt):
    status.text = "Callback aufgerufen: {}".format (cnt [0])
    cnt [0] += 1

def print_pos (event):
    print ("Klick bei", event.x, event.y)

def end_app():
    if tkinter.messagebox.askokcancel ("Beenden",
            "Wollen Sie wirklich das Programm beenden?"):
        root.destroy()

cnt = [0]
root = tkinter.Tk()
root.protocol ("WM_DELETE_WINDOW", end_app)

# Statusleiste erzeugen
status = StatusBar (root)
status.pack (side = tkinter.BOTTOM, fill = tkinter.X)

# Menü erzeugen
menu = tkinter.Menu (root)
root.config (menu = menu)

filemenu = tkinter.Menu (menu)
menu.add_cascade (label = "Datei", menu = filemenu)
filemenu.add_command (label = "Neu",
    command = lambda s = status, c = cnt: callback (s, c))
filemenu.add_command (label = "Öffnen",
    command = lambda s = status, c = cnt: callback (s, c))
filemenu.add_separator()
filemenu.add_command (label = "Beenden", command = end_app)

helpmenu = tkinter.Menu (menu)
menu.add_cascade (label = "Hilfe", menu = helpmenu)
helpmenu.add_command (label = "Über",
    command = lambda s = status, c = cnt: callback (s, c))

# Werkzeugleiste erzeugen
toolbar = tkinter.Frame (root)
tkinter.Button (toolbar, text = "Neu",
    width = 6,
    command = lambda s = status, c = cnt: callback (s, c)
).pack (side = tkinter.LEFT, padx = 2, pady = 2)
tkinter.Button (toolbar, text = "Öffnen",
    width = 6,
    command = lambda s = status, c = cnt: callback (s, c)
).pack (side = tkinter.LEFT, padx = 2, pady = 2)
toolbar.pack (side = tkinter.TOP, fill = tkinter.X)

# Die Fläche dazwischen ausfüllen
frame = tkinter.Frame (root, width = WIDTH, height = HEIGHT)
frame.bind ("<Button-1>", print_pos)
frame.pack()

tkinter.mainloop()
