#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import tkinter.messagebox

import res
import log

# Normally, this constant should be defined in subprocess.
# Needed to hide the console window, which would appear under Windows by calling
# an external command line program.
STARTF_USESHOWWINDOW = 1

def _print_log (msg, exc = None):
    '''Used by the error function.'''
    if exc is None:
        log.error (msg)
    else:
        log.error (msg)
        log.exception (exc)

def error (msg, exc = None):
    '''
    The function, which will be always called, if there a foreseen error
    occures. It shows the user an error message box and makes a note in the
    log file.
    "msg" shall be string object, which contains the message, which will be
    showen to the user and be noted in the log file.
    '''
    tkinter.messagebox.showerror (res.STD_ERROR_TITLE, msg)

    if log.isready():
        _print_log (msg, exc)
    else:
        log.init (res.LOGFILE)
        _print_log (msg, exc)
        log.close()

def setentry (entry, text):
    entry.delete (0, 'end')
    entry.insert (0, text)
    
def cmdcall (cmd, *args):
    # Hide the console window, which would appear under Windows
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW
    
    # Build the command
    calllist = [cmd]
    calllist.append (args)
    
    # Do the actual call
    return subprocess.check_output (calllist, startupinfo = startupinfo)

# This stuff was originally from some demos ####################################
class curry:
    '''Handles arguments for callback functions'''
    def __init__ (self, callback, *args, **kw):
        self.callback = callback
        self.args = args
        self.kw = kw

    def __call__ (self):
        return self.callback (*self.args, **self.kw)
    
def enum (*sequential, **named):
    enums = dict (zip (sequential, range (len (sequential))), **named)
    return type ('Enum', (), enums)
################################################################################