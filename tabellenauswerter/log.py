#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''This is 'my_logger' module, which is imported into all
the other modules of my application.

Copied from "The Python Rag" - August 2009'''

import logging
import logging.handlers
from functools import wraps

# Create a global logger
_vs_logger = None
_handler = None
_debug_on = None

def init (logfile, debug_on = False):
    '''Sets up the logger.
    Must be called, before any other function is called.'''
    global _vs_logger
    global _debug_on
    global _handler

    _vs_logger = logging.getLogger ("my_logger")
    _debug_on = debug_on

    # Set the logger level
    if _debug_on:
        _vs_logger.setLevel (logging.DEBUG)
    else:
        _vs_logger.setLevel (logging.INFO)

    # Set the format
    form = logging.Formatter ("%(asctime)s - %(levelname)s - %(message)s")

    # Add the log message handler to the logger
    _handler = logging.handlers.RotatingFileHandler (logfile,
        maxBytes = 1048576,  # 1 MB
        backupCount = 5
    )

    _handler.setFormatter (form)
    _vs_logger.addHandler (_handler)

def close():
    '''Closes the logger'''
    global _handler
    _handler.close()

def info (msg):
    '''Log message with level info'''
    if _vs_logger:
        _vs_logger.info (str (msg))

def debug (msg):
    '''Log message with level debug'''
    if _debug_on and _vs_logger:
        _vs_logger.debug (str (msg))

def logfunction (func):
    '''Creates a decorator to log a function'''
    @wraps (func)
    def wrapper (*args, **kw):
        debug ("{} called".format (func.__name__))
        return func (*args, **kw)
    return wrapper

def logmethod (method):
    "Creates a decorator to log a method"
    @wraps (method)
    def wrapper (self, *args, **kw):
        debug ("{} in {} called".format (
            method.__name__,
            self.__class__.__name__)
        )
        return method (self, *args, **kw)
    return wrapper

def exception (msg):
    '''Log message with level error plus exception traceback'''
    if _vs_logger:
        _vs_logger.exception (str (msg))
