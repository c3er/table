#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This file consists of the definition of the main window and is supposed to be
executed by the user.
'''

DEBUG_ON = True

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import tkinter.ttk as ttk

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
merge_table_button = None

# Helper functions #############################################################
def disable(button):
    button.config(state = 'disabled')

def enable(button):
    button.config(state = 'enabled')

def avoid_tableloss():
    '''Ask the user for every table, which is modified, if he wants to save it.
    If the user only clicks on "Yes" or "No", the function returns True.
    If the user clicks on any dialog on "Cancel", the function returns False.
    '''
    if not sess.modified:
        return True
    else:
        for t in sess.tables:
            if t.modified:
                result = tkinter.messagebox.askyesnocancel(
                    res.SAVE_TABLE_TITLE,
                    res.SAVE_TABLE_QUESTION.format(t.filename)
                )
                if result:
                    # User clicked on "Yes"
                    save_table(t)
                elif result is None:
                    # User clicked on "Cancel"
                    return False
                # Do nothing, if the user clicked on "No"
        return True
    
def create_button(frame, label, command):
    button = ttk.Button(frame, text = label, command = command)
    button.pack(side = 'left')
    return button
################################################################################

# Handler functions ############################################################
@log.logfunction
def adjust_state(sess):
    if not sess.isempty:
        enable(save_as_button)
        enable(merge_table_button)
        
        curtab = sess.current_table
        
        if curtab.isheadered:
            disable(tabcols_button)
        else:
            enable(tabcols_button)
            
        if curtab.modified:
            enable(save_button)
        else:
            disable(save_button)
    else:
        # No table loaded yet.
        disable(save_button)
        disable(save_as_button)
        disable(tabcols_button)
        disable(merge_table_button)

@log.logfunction
def new_session(root):
    if avoid_tableloss():
        nd = dialogs.NewDialog(root, res.NEW_SESSION_LABEL)
        if nd.result:
            sess.set_tablelist(nd.result)
        elif not nd.canceled:
            tkinter.messagebox.showwarning(res.TITLE, res.NO_TABLE_ERROR)

@log.logfunction
def open_table():
    path = tkinter.filedialog.askopenfilename(
        filetypes = [(res.TAB_FILE_STR, res.TAB_FILE_EXT)]
    )
    if path:
        sess.open_tabfile(path)

@log.logfunction
def save_table_as(tab = None):
    path = tkinter.filedialog.asksaveasfilename(
        filetypes = [(res.TAB_FILE_STR, res.TAB_FILE_EXT)]
    )
    if path:
        if not path.endswith(res.TAB_FILE_EXT):
            path += res.TAB_FILE_EXT
        if tab is None:
            tab = sess.current_table
        tab.save(path)

@log.logfunction
def save_table(tab = None):
    try:
        if tab is None:
            tab = sess.current_table
        tab.save()
    except session.UnknownPathException:
        save_table_as(tab)

@log.logfunction
def mk_tabcols():
    sess.current_table.mk_tabcols()

@log.logfunction
def merge_tables():
    path = tkinter.filedialog.askopenfilename(
        filetypes = [(res.TAB_FILE_STR, res.TAB_FILE_EXT)]
    )
    if path:
        sess.merge_tables(path)

@log.logfunction
def appclose_callback(root):
    if avoid_tableloss():
        root.destroy()
################################################################################

# Build the actual interface ###################################################
def toolbar(root):
    '''Build the toolbar, which consists of an horicontal row of buttons.'''
    global tabcols_button
    global save_button
    global save_as_button
    global merge_table_button

    frame = ttk.Frame()

    create_button(frame, res.NEW_LABEL, curry(new_session, root))
    create_button(frame, res.OPEN_LABEL, open_table)
    save_button = create_button(frame, res.SAVE_LABEL, save_table)
    save_as_button = create_button(frame, res.SAVE_AS_LABEL, save_table_as)

    ttk.Separator(frame, orient = 'vertical').pack(side = 'left', padx = 2)

    tabcols_button = create_button(frame, res.MAKE_TABCOLS_LABEL, mk_tabcols)
    merge_table_button = create_button(frame,
        res.MERGE_TABLES_LABEL,
        merge_tables
    )
    
    return frame

def cmdwidget(root):
    '''Container for the elements, which appear at application start.'''
    frame = ttk.Frame(root)
    toolbar(root).pack(anchor = 'n', fill = 'x', padx = 2, pady = 2)
    return frame

def bind_events(root):
    root.bind('<Control-n>', lambda event: new_session(root))
    root.bind('<Control-o>', lambda event: open_table())
    root.bind('<Control-s>', lambda event: save_table())
    root.bind('<Control-S>', lambda event: save_table_as())
    root.protocol('WM_DELETE_WINDOW', curry(appclose_callback, root))
################################################################################

if __name__ == '__main__':
    # Initializing
    log.init(res.LOGFILE, DEBUG_ON)
    log.info('###### Anwendung gestartet ######')
    root = tkinter.Tk()
    root.wm_title(res.TITLE)
    cmdwidget(root).pack(fill = 'x', anchor = 'n', padx = 2, pady = 2)
    bind_events(root)
    sess = session.Session(root, adjust_state)

    root.mainloop()

    # Cleaning up
    log.info('###### Anwendung beendet ########')
    log.close()
