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

sess = None

# GUI elements, which are needed globally
save_button = None
save_as_button = None
tabcols_button = None

# Helper functions #############################################################
@log.logfunction
def adjust_state (sess):
    if not sess.isempty:
        save_as_button.config (state = 'enabled')
        
        curtab = sess.current_table
        
        if curtab.isheadered:
            tabcols_button.config (state = 'disabled')
        else:
            tabcols_button.config (state = 'enabled')
            
        if curtab.modified:
            save_button.config (state = 'enabled')
        else:
            save_button.config (state = 'disabled')
    else:
        tabcols_button.config (state = 'disabled')
        tabcols_button.config (state = 'disabled')
        tabcols_button.config (state = 'disabled')
################################################################################

# Button handlers ##############################################################
@log.logfunction
def new_session (root):
    nd = dialogs.NewDialog (root, res.NEW_SESSION_LABEL)
    if nd.result:
        sess.set_tablelist (nd.result)

@log.logfunction
def open_table():
    path = tkinter.filedialog.askopenfilename (
        filetypes = [(res.TAB_FILE_STR, res.TAB_FILE_EXT)]
    )
    if path:
        sess.open_tabfile (path)

@log.logfunction
def save_table_as (tab = None):
    path = tkinter.filedialog.asksaveasfilename (
        filetypes = [(res.TAB_FILE_STR, res.TAB_FILE_EXT)]
    )
    if path:
        if not path.endswith (res.TAB_FILE_EXT):
            path += res.TAB_FILE_EXT
        tab = sess.current_table if tab is None else tab
        tab.save (path)

@log.logfunction
def save_table (tab = None):
    try:
        tab = sess.current_table if tab is None else tab
        tab.save()
    except session.UnknownPathException:
        save_table_as()

@log.logfunction
def mk_tabcols():
    sess.current_table.mk_tabcols()
################################################################################

#def data

# Build the actual Interface ###################################################
def toolbar (root):
    global tabcols_button
    global save_button
    global save_as_button

    frame = ttk.Frame()

    ttk.Button (frame,
        text = res.NEW_LABEL,
        command = curry (new_session, root)
    ).pack (side = 'left')

    ttk.Button (frame,
        text = res.OPEN_LABEL,
        command = open_table
    ).pack (side = 'left')

    save_button = ttk.Button (frame,
        text = res.SAVE_LABEL,
        command = save_table,
        state = 'disabled'
    )
    save_button.pack (side = 'left')

    save_as_button = ttk.Button (frame,
        text = res.SAVE_AS_LABEL,
        command = save_table_as,
        state = 'disabled'
    )
    save_as_button.pack (side = 'left')

    ttk.Separator (frame, orient = 'vertical').pack (side = 'left', padx = 2)

    tabcols_button = ttk.Button (frame,
        text = res.MAKE_TABCOLS_LABEL,
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
    root.bind ('<Control-o>', lambda event: open_table())
    root.bind ('<Control-s>', lambda event: save_table())
    root.bind ('<Control-S>', lambda event: save_table_as())
################################################################################

if __name__ == '__main__':
    # Initializing
    log.init (res.LOGFILE, DEBUG_ON)
    log.info ('###### Anwendung gestartet ######')
    root = tkinter.Tk()
    sess = session.Session (root, adjust_state)
    root.wm_title (res.TITLE)
    cmdwidget (root).pack (fill = 'x', anchor = 'n', padx = 2, pady = 2)
    bind_events (root)

    root.mainloop()

    # Cleaning up
    log.info ('###### Anwendung beendet ########')
    log.close()
