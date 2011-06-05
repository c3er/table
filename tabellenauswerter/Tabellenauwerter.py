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
import session
from misc import *

tables = None
filename = None

# GUI elements, which are needed globally
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

def adjust_state():
    if len (tables) > 0:
        tabcols_button.config (state = tkinter.NORMAL)
        save_button.config (state = tkinter.NORMAL)
        save_as_button.config (state = tkinter.NORMAL)
    else:
        tabcols_button.config (state = tkinter.DISABLED)
        save_button.config (state = tkinter.DISABLED)
        save_as_button.config (state = tkinter.DISABLED)

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
    adjust_state()

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
        error (res.file_open_error + str (msg), msg)
################################################################################

# Handler functions ############################################################
@log.logfunction
def new_session():
    tkinter.messagebox.showinfo ('Hallo', res.new_label)

@log.logfunction
def open_session():
    fname = tkinter.filedialog.askopenfilename (
        filetypes = [(res.tab_file_str, res.tab_file_ext)]
    )
    if fname:
        open_tabfile (fname)

@log.logfunction
def save_session_as():
    fname = tkinter.filedialog.asksaveasfilename (
        filetypes = [(res.tab_file_str, res.tab_file_ext)]
    )
    if fname:
        if not fname.endswith (res.tab_file_ext):
            fname += res.tab_file_ext
        setfilename (fname)
        save_session()

@log.logfunction
def save_session():
    if not filename:
        save_session_as()
    else:
        try:
            with open (filename, 'wb') as f:
                pickle.dump (tables, f)
        except IOError as msg:
            error (res.file_save_error + str (msg), msg)

@log.logfunction
def mk_tabcols():
    index = notebook.index ('current')
    tables [index].make_header()
    show_tables()
    notebook.select (index)

@log.logfunction
def read_asian():
    tkinter.messagebox.showinfo ('Hallo', res.asian_label)

@log.logfunction
def addr_button_click():
    global tables
    global addr_entry
    addr = addr_entry.get()

    if not addr:
        error (res.addr_empty_error + res.std_error_msg)
        return
    elif addr.startswith ('http://'):
        if asian_flag.get():
            try:
                page = subprocess.check_output ([res.asian_exe, addr])
            except subprocess.CalledProcessError as msg:
                error (res.asian_mode_error + str (msg), msg)
                return
            except OSError as msg:
                error (res.asian_exe_error + str (msg), msg)
                return
        else:
            try:
                req = urllib.request.Request (addr)
                req.add_header ('User-agent', 'Mozilla/5.0')
                with urllib.request.urlopen (req) as f:
                    page = f.read()
            except urllib.request.URLError as msg:
                error (res.web_read_error + str (msg), msg)
                return
    elif addr.endswith ('.html') or addr.endswith ('.htm'):
        try:
            with open (addr, 'rb') as f:
                page = f.read()
        except IOError as msg:
            error (res.file_open_error + str (msg), msg)
            return
    elif addr.endswith (res.tab_file_ext):
        open_tabfile (addr)
        return
    else:
        error (res.std_error_msg)
        return

    tables = table.html2tables (page)
    table.filter_trash (tables)
    show_tables()
################################################################################

# Build the actual Interface ###################################################
def toolbar():
    global asian_flag
    global tabcols_button
    global save_button
    global save_as_button
    frame = ttk.Frame()

    ttk.Button (frame,
        text = res.new_label,
        command = new_session
    ).pack (side = 'left')

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

    ttk.Separator (frame, orient = 'vertical').pack (side = 'left', padx = 2)

    tabcols_button = ttk.Button (frame,
        text = res.make_tabcols_label,
        command = mk_tabcols,
        state = tkinter.DISABLED
    )
    tabcols_button.pack (side = 'left')

    ttk.Separator (frame, orient = 'vertical').pack (side = 'left', padx = 2)

    ttk.Button (frame,
        text = res.asian_label,
        command = read_asian
    ).pack (side = 'left')

    asian_flag = tkinter.BooleanVar (frame)
    ttk.Checkbutton (frame,
        text = res.asian_mode_label,
        variable = asian_flag
    ).pack (side = 'left')

    return frame

def addrbar (frame):
    global addr_entry

    addr_frame = ttk.Frame (frame)
    label = ttk.Label (addr_frame, text = res.addr_label)
    tmp_frame = ttk.Frame (addr_frame)
    addr_entry = tkinter.Entry (tmp_frame, width = 40)
    addr_entry.insert (0, res.default_addr)
    addr_handler = addr_button_click
    addr_entry.bind ('<Return>', lambda event: addr_handler())
    addr_entry.focus()
    addr_button = ttk.Button (tmp_frame,
        text = res.goto_label,
        command = addr_handler,
    )

    label.pack (side = 'left', padx = 2, pady = 2)
    addr_entry.pack (side = 'left', expand = True, fill = 'x', pady = 2)
    addr_button.pack (side = 'right', pady = 2)
    tmp_frame.pack (side = 'right', expand = True, fill = 'x')
    return addr_frame

def cmdwidget (root):
    frame = ttk.Frame (root)
    toolbar().pack (anchor = 'n', fill = 'x', padx = 2, pady = 2)
    addrbar (frame).pack (fill = 'x', anchor = 's')
    return frame

def bind_events (root):
    root.bind ('<Control-n>', lambda event: new_session())
    root.bind ('<Control-o>', lambda event: open_session())
    root.bind ('<Control-s>', lambda event: save_session())
    root.bind ('<Control-S>', lambda event: save_session_as())
################################################################################

if __name__ == '__main__':
    # Initializing
    log.init (res.logfile, DEBUG_ON)
    log.info ('Anwendung gestartet')
    root = tkinter.Tk()
    root.wm_title (res.title)
    cmdwidget (root).pack (fill = 'x', anchor = 'n', padx = 2, pady = 2)
    bind_events (root)

    root.mainloop()

    # Cleaning up
    log.info ('Anwendung beendet')
    log.close()
