#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Reads tables from HTML files'''

title = 'Tabellenauswerter'
default_addr = 'wm2010.html'

import subprocess

import tkinter
import tkinter.messagebox
# import tkinter.filedialog
import tkinter.ttk as ttk

import urllib.request

import table
from table import Curry

notebook = None
tables = None
asian_flag = None
tabcols_button = None

def show_tables():
    global notebook
    if notebook is not None:
        notebook.destroy()
    notebook = ttk.Notebook()
    for i, t in enumerate (tables):
        # print (t)
        tw = table.TableWidget (notebook, t)
        notebook.add (tw.frame,
            text = 'Tabelle ' + str (i + 1))
    notebook.pack (expand = True, fill = 'both', anchor = 'n')

# Handler functions ############################################################
def mk_tabcols():
    index = notebook.index ('current')
    tables [index].make_header()
    show_tables()
    notebook.select (index)

def addr_button_click (addr_entry):
    global tables
    std_err_str = ('Die Adresse muss entweder auf eine lokale HTML-Datei ' +
        'verweisen oder eine vollständige Adresse zu einer Web-Seite enthalten')
    addr = addr_entry.get()

    if addr == '':
        tkinter.messagebox.showerror ('Fehler',
            'Bitte Adresse eingeben\n' + std_err_str)
        return
    elif addr.startswith ('http://'):
        if asian_flag.get():
            try:
                page = subprocess.check_output (['asian', addr])
            except subprocess.CalledProcessError as msg:
                tkinter.messagebox.showerror ('Fehler',
                    'Asian-Modus gescheitert\n' + str (msg))
                return
            except OSError as msg:
                tkinter.messagebox.showerror ('Fehler',
                    'asian.exe konnte nicht aufgerufen werden\n' + str (msg))
                return
        else:
            try:
                req = urllib.request.Request (addr)
                req.add_header ('User-agent', 'Mozilla/5.0')
                with urllib.request.urlopen (req) as f:
                    page = f.read()
            except urllib.request.URLError as msg:
                tkinter.messagebox.showerror ('Fehler',
                    'Web-Seite konnte nicht gelesen werden\n' + str (msg))
                return
    elif addr.endswith ('.html') or addr.endswith ('.htm'):
        try:
            with open (addr, 'rb') as f:
                page = f.read()
        except IOError as msg:
            tkinter.messagebox.showerror ('Fehler',
                'Datei konnte nicht gelesen werden\n' + str (msg))
            return
    else:
        tkinter.messagebox.showerror ('Fehler', std_err_str)
        return

    tables = table.html2tables (page)
    table.filter_trash (tables)
    show_tables()
    if len (tables) > 0:
        tabcols_button.config (state = tkinter.NORMAL)
    else:
        tabcols_button.config (state = tkinter.DISABLED)
################################################################################

def toolbar():
    global asian_flag
    global tabcols_button
    frame = ttk.Frame()

    tabcols_button = ttk.Button (frame,
        text = 'Erste Reihe zu Überschriften',
        command = mk_tabcols,
        state = tkinter.DISABLED
    )
    tabcols_button.pack (side = 'left')

    asian_flag = tkinter.BooleanVar (frame)
    ttk.Checkbutton (frame,
        text = 'Asian-Modus',
        variable = asian_flag
    ).pack (side = 'left')

    return frame

class CmdWidget:
    def __init__ (self, root):
        self.frame = ttk.Frame (root)
        self._setup_widgets()

    def _setup_widgets (self):
        toolbar().pack (anchor = 'n', fill = 'x', padx = 2, pady = 2)
        self.build_addr_bar().pack (fill = 'x', anchor = 's')

    def build_addr_bar (self):
        addr_frame = ttk.Frame (self.frame)
        label = ttk.Label (addr_frame, text = 'Adresse: ')
        tmp_frame = ttk.Frame (addr_frame)
        addr_entry = tkinter.Entry (tmp_frame, width = 40)
        addr_entry.insert (0, default_addr)
        addr_handler = Curry (addr_button_click, addr_entry)
        addr_entry.bind ('<Return>', lambda event: addr_handler())
        addr_button = ttk.Button (tmp_frame,
            text = 'Öffnen',
            command = addr_handler
        )

        label.pack (side = 'left', padx = 2, pady = 2)
        addr_entry.pack (side = 'left', expand = True, fill = 'x', pady = 2)
        addr_button.pack (side = 'right', pady = 2)
        tmp_frame.pack (side = 'right', expand = True, fill = 'x')
        return addr_frame

if __name__ == '__main__':
    root = tkinter.Tk()
    root.wm_title (title)
    CmdWidget (root).frame.pack (fill = 'x', anchor = 'n', padx = 2, pady = 2)
    root.mainloop()
