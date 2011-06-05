#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter.messagebox

import res
import log

def error (msg, exc = None):
    '''The function, which has always be called, if there a foreseen error
    occures. It shows the user an error message box and makes a note in the
    log file.
    "msg" shall be string object, which contains the message, which will be
    showen to the user and be noted in the log file.'''
    # XXX Behandlung von Exception überarbeiten
    tkinter.messagebox.showerror (res.std_error_title, msg)
    logfunc = log.error if exc is None else log.exception
    if log.isready():
        logfunc (msg)
    else:
        log.init (res.logfile)
        logfunc (msg)
        log.close()

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