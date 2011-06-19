#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter.messagebox

import res
import log

def _print_log (msg, exc = None):
    if exc is None:
        log.error (msg)
    else:
        log.error (msg)
        log.exception (exc)

def error (msg, exc = None):
    '''The function, which has always be called, if there a foreseen error
    occures. It shows the user an error message box and makes a note in the
    log file.
    "msg" shall be string object, which contains the message, which will be
    showen to the user and be noted in the log file.'''
    tkinter.messagebox.showerror (res.std_error_title, msg)

    if log.isready():
        _print_log (msg, exc)
    else:
        log.init (res.logfile)
        _print_log (msg, exc)
        log.close()

def setentry (entry, text):
    entry.delete (0, 'end')
    entry.insert (0, text)

# This stuff was originally from some demos ####################################
class curry:
    """Handles arguments for callback functions"""
    def __init__ (self, callback, *args, **kw):
        self.callback = callback
        self.args = args
        self.kw = kw

    def __call__ (self):
        return self.callback (*self.args, **self.kw)
################################################################################