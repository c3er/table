#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Reads tables from HTML files'''

DEBUG_ON = True

import pickle

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import tkinter.ttk as ttk

import table
import log
import res
import session
import dialogs
from misc import *

tables = None
filename = None

# GUI elements, which are needed globally
save_button = None
save_as_button = None
tabcols_button = None
notebook = None

# Helper functions #############################################################
def adjust_state():
    if tables is not None and len (tables) > 0:
        tabcols_button.config (state = 'normal')
        save_button.config (state = 'normal')
        save_as_button.config (state = 'normal')
    else:
        tabcols_button.config (state = 'disabled')
        save_button.config (state = 'disabled')
        save_as_button.config (state = 'disabled')

@log.logfunction
def show_tables():
    global notebook
    log.debug ('Anzahl der Tabellen: ' + str (len (tables)))
    if notebook is not None:
        notebook.destroy()
    notebook = ttk.Notebook()
    for i, t in enumerate (tables):
        tw = table.TableWidget (notebook, t)
        notebook.add (tw.frame, text = res.tab_title + str (i + 1))
    notebook.pack (expand = True, fill = 'both', anchor = 'n')
    adjust_state()

def setfilename (fname):
    global filename
    if fname is not None:
        filename = fname

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
def new_session (root):
    global tables
    nd = dialogs.NewDialog (root, res.new_session_label)
    if nd.result:
        tables = nd.result
        show_tables()

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
################################################################################

# Build the actual Interface ###################################################
def toolbar (root):
    global tabcols_button
    global save_button
    global save_as_button
    frame = ttk.Frame()

    ttk.Button (frame,
        text = res.new_label,
        command = curry (new_session, root)
    ).pack (side = 'left')

    ttk.Button (frame,
        text = res.open_label,
        command = open_session
    ).pack (side = 'left')

    save_button = ttk.Button (frame,
        text = res.save_label,
        command = save_session,
        state = 'disabled'
    )
    save_button.pack (side = 'left')

    save_as_button = ttk.Button (frame,
        text = res.save_as_label,
        command = save_session_as,
        state = 'disabled'
    )
    save_as_button.pack (side = 'left')

    ttk.Separator (frame, orient = 'vertical').pack (side = 'left', padx = 2)

    tabcols_button = ttk.Button (frame,
        text = res.make_tabcols_label,
        command = mk_tabcols,
        state = 'disabled'
    )
    tabcols_button.pack (side = 'left')

    return frame

def cmdwidget (root):
    frame = ttk.Frame (root)
    toolbar (root).pack (anchor = 'n', fill = 'x', padx = 2, pady = 2)
    return frame

def bind_events (root):
    root.bind ('<Control-n>', lambda event: new_session (root))
    root.bind ('<Control-o>', lambda event: open_session())
    root.bind ('<Control-s>', lambda event: save_session())
    root.bind ('<Control-S>', lambda event: save_session_as())
################################################################################

if __name__ == '__main__':
    # Initializing
    log.init (res.logfile, DEBUG_ON)
    log.info ('###### Anwendung gestartet ######')
    root = tkinter.Tk()
    root.wm_title (res.title)
    cmdwidget (root).pack (fill = 'x', anchor = 'n', padx = 2, pady = 2)
    bind_events (root)

    root.mainloop()

    # Cleaning up
    log.info ('###### Anwendung beendet ########')
    log.close()
