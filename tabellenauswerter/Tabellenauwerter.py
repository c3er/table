#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Reads tables from HTML files'''

title = 'Tabellenauswerter'
default_addr = 'wm2010.html'

import subprocess

import tkinter
import tkinter.messagebox
import tkinter.ttk as ttk

import urllib.request

import table
from table import Curry

notebook = None
tables = None
asian_flag = None

def show_tables():
    global notebook
    if notebook is not None:
        notebook.destroy()
    notebook = ttk.Notebook()
    for t in tables:
        print (t)
        # print (repr (t))
        tw = table.TableWidget (notebook, t)
        notebook.add (tw.frame,
            text = 'Tabelle ' + str (tables.index (t) + 1))
    notebook.pack (expand = True, fill = 'both', anchor = 'n')

# Handler functions ############################################################
def mk_tabcols():
    if notebook is None:
        tkinter.messagebox.showerror ('Fehler',
            'Sie müssen zuerst eine gültige Adresse eingeben')
    else:
        # The current table index will be estimated by the text in the
        # notebook
        tabconf = notebook.tab ('current')
        index = int (tabconf ['text'].split() [1]) - 1
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
    if addr.startswith ('http://'):
        if asian_flag.get() == '1':
            try:
                page = subprocess.check_output (['asian', addr])
                page = page.decode ('utf_8', 'ignore').strip()
            except subprocess.CalledProcessError as msg:
                tkinter.messagebox.showerror ('Fehler',
                    'Asian-Modus gescheitert\n' + str (msg))
                return
            except OSError as msg:
                tkinter.messagebox.showerror ('Fehler',
                    'asian.exe konnte nicht aufgerufen werden\n' + str(msg))
                return
        else:
            try:
                f = urllib.request.urlopen (addr)
                page = f.read().decode ('utf_8', 'ignore').strip()
                f.close()
            except urllib.request.URLError as msg:
                tkinter.messagebox.showerror ('Fehler',
                    'Web-Seite konnte nicht gelesen werden\n' + str (msg))
                return
    elif addr.endswith ('.html') or addr.endswith ('.htm'):
        try:
            f = open (addr, 'rb')
            page = f.read().decode ('utf_8', 'ignore').strip()
            f.close()
        except IOError as msg:
            tkinter.messagebox.showerror ('Fehler',
                'Datei konnte nicht gelesen werden\n' + str (msg))
            return
    else:
        tkinter.messagebox.showerror ('Fehler', std_err_str)
        return

    tables = table.html2tables (page)
    table.filter_trash (tables)
    # print (tables)
    show_tables()
################################################################################

class Toolbar:
    def __init__ (self):
        global asian_flag
        self.frame = ttk.Frame()

        ttk.Button (self.frame,
            text = 'Erste Reihe zu Überschriften',
            command = mk_tabcols
        ).pack (side = 'left', padx = 2, pady = 2)

        asian_flag = tkinter.StringVar (self.frame)
        ttk.Checkbutton (self.frame,
            text = 'Asian-Modus',
            variable = asian_flag
        ).pack (side = 'left', padx = 2, pady = 2)

class CmdWidget:
    def __init__ (self, root):
        self.frame = ttk.Frame (root)
        self._setup_widgets()

    def _setup_widgets (self):
        Toolbar().frame.pack (anchor = 'n', fill = 'x')
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
    CmdWidget (root).frame.pack (fill = 'x', anchor = 'n')
    root.mainloop()
