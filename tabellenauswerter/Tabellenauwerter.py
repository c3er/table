#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Reads tables from HTML files'''

DEBUG_ON = True

import subprocess
import pickle

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import tkinter.ttk as ttk

import urllib.request

import table
import log
import res
from table import curry

tables = None
filename = None

save_button = None
save_as_button = None
tabcols_button = None
asian_flag = None
addr_entry = None
notebook = None

# Helper functions #############################################################
def setentry (entry, text):
    entry.delete (0, 'end')
    entry.insert (0, text)

@log.logfunction
def show_tables():
    global notebook
    if notebook is not None:
        notebook.destroy()
    notebook = ttk.Notebook()
    for i, t in enumerate (tables):
        log.debug (t)
        tw = table.TableWidget (notebook, t)
        notebook.add (tw.frame,
            text = res.tab_title + str (i + 1))
    notebook.pack (expand = True, fill = 'both', anchor = 'n')
    if len (tables) > 0:
        tabcols_button.config (state = tkinter.NORMAL)
        save_button.config (state = tkinter.NORMAL)
        save_as_button.config (state = tkinter.NORMAL)
    else:
        tabcols_button.config (state = tkinter.DISABLED)
        save_button.config (state = tkinter.DISABLED)
        save_as_button.config (state = tkinter.DISABLED)

def setfilename (fname):
    global filename
    if fname is not None:
        filename = fname
        setentry (addr_entry, fname)

def open_tabfile (fname):
    global tables
    try:
        with open (fname, 'rb') as f:
            tables = pickle.load (f)
        setfilename (fname)
        show_tables()
    except IOError as msg:
        tkinter.messagebox.showerror (res.std_error_title,
            res.file_open_error + msg)
################################################################################

# Handler functions ############################################################
@log.logfunction
def open_session():
    fname = tkinter.filedialog.askopenfilename (
        filetypes = [(res.tab_file_str, res.tab_file_ext)]
    )
    if fname is not None:
        open_tabfile (fname)

@log.logfunction
def save_session_as():
    fname = tkinter.filedialog.asksaveasfilename (
        filetypes = [(res.tab_file_str, res.tab_file_ext)]
    )
    if fname is not None:
        if not fname.endswith (res.tab_file_ext):
            fname += res.tab_file_ext
        setfilename (fname)
        save_session()

@log.logfunction
def save_session():
    if filename is None:
        save_session_as()
    else:
        try:
            with open (filename, 'wb') as f:
                pickle.dump (tables, f)
        except IOError as msg:
            tkinter.messagebox.showerror (res.std_error_title,
                res.file_save_error + msg)

@log.logfunction
def mk_tabcols():
    index = notebook.index ('current')
    tables [index].make_header()
    show_tables()
    notebook.select (index)

@log.logfunction
def addr_button_click():
    global tables
    global addr_entry
    addr = addr_entry.get()

    if addr == '':
        tkinter.messagebox.showerror (res.std_error_title,
            res.addr_empty_error + res.std_error_msg)
        return
    elif addr.startswith ('http://'):
        if asian_flag.get():
            try:
                page = subprocess.check_output ([res.asian_exe, addr])
            except subprocess.CalledProcessError as msg:
                tkinter.messagebox.showerror (res.std_error_title,
                    res.asian_mode_error + str (msg))
                return
            except OSError as msg:
                tkinter.messagebox.showerror (res.std_error_title,
                    res.asian_exe_error + str (msg))
                return
        else:
            try:
                req = urllib.request.Request (addr)
                req.add_header ('User-agent', 'Mozilla/5.0')
                with urllib.request.urlopen (req) as f:
                    page = f.read()
            except urllib.request.URLError as msg:
                tkinter.messagebox.showerror (res.std_error_title,
                    res.web_read_error + str (msg))
                return
    elif addr.endswith ('.html') or addr.endswith ('.htm'):
        try:
            with open (addr, 'rb') as f:
                page = f.read()
        except IOError as msg:
            tkinter.messagebox.showerror (res.std_error_title,
                res.file_open_error + str (msg))
            return
    elif addr.endswith (res.tab_file_ext):
        open_tabfile (addr)
        return
    else:
        tkinter.messagebox.showerror (res.std_error_title, res.std_error_msg)
        return

    tables = table.html2tables (page)
    table.filter_trash (tables)
    show_tables()
################################################################################

def toolbar():
    global asian_flag
    global tabcols_button
    global save_button
    global save_as_button
    frame = ttk.Frame()

    ttk.Button (frame,
        text = res.open_label,
        command = open_session
    ).pack (side = 'left')

    save_button = ttk.Button (frame,
        text = res.save_label,
        command = save_session,
        state = tkinter.DISABLED
    )
    save_button.pack (side = 'left')

    save_as_button = ttk.Button (frame,
        text = res.save_as_label,
        command = save_session_as,
        state = tkinter.DISABLED
    )
    save_as_button.pack (side = 'left')

    tabcols_button = ttk.Button (frame,
        text = res.make_tabcols_label,
        command = mk_tabcols,
        state = tkinter.DISABLED
    )
    tabcols_button.pack (side = 'left')

    asian_flag = tkinter.BooleanVar (frame)
    ttk.Checkbutton (frame,
        text = res.asian_mode_label,
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
        global addr_entry
        addr_frame = ttk.Frame (self.frame)
        label = ttk.Label (addr_frame, text = res.addr_label)
        tmp_frame = ttk.Frame (addr_frame)
        addr_entry = tkinter.Entry (tmp_frame, width = 40)
        addr_entry.insert (0, res.default_addr)
        addr_handler = addr_button_click
        addr_entry.bind ('<Return>', lambda event: addr_handler())
        addr_button = ttk.Button (tmp_frame,
            text = res.goto_label,
            command = addr_handler
        )

        label.pack (side = 'left', padx = 2, pady = 2)
        addr_entry.pack (side = 'left', expand = True, fill = 'x', pady = 2)
        addr_button.pack (side = 'right', pady = 2)
        tmp_frame.pack (side = 'right', expand = True, fill = 'x')
        return addr_frame

if __name__ == '__main__':
    log.init (res.logfile, DEBUG_ON)
    log.info ('Anwendung gestartet')
    root = tkinter.Tk()
    root.wm_title (res.title)
    CmdWidget (root).frame.pack (fill = 'x', anchor = 'n', padx = 2, pady = 2)
    root.mainloop()
    log.info ('Anwendung beendet')
    log.close()
