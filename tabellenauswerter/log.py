#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''This is 'my_logger' module, which is imported into all the other modules of
my application.

Copied from "The Python Rag" - August 2009
'''

import logging
import logging.handlers
from functools import wraps

# Create a global logger
_vs_logger = None
_handler = None
_debug_on = None

def init(logfile, debug_on = False):
    '''Sets up the logger.
    Must be called, before any other function is called.
    '''
    global _vs_logger
    global _debug_on
    global _handler

    _vs_logger = logging.getLogger("my_logger")
    _debug_on = debug_on

    # Set the logger level
    if _debug_on:
        _vs_logger.setLevel(logging.DEBUG)
    else:
        _vs_logger.setLevel(logging.INFO)

    # Set the format
    form = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Add the log message handler to the logger
    _handler = logging.handlers.RotatingFileHandler(logfile,
        maxBytes = 1048576,  # 1 MB
        backupCount = 5
    )

    _handler.setFormatter(form)
    _vs_logger.addHandler(_handler)

def close():
    '''Closes the logger'''
    global _handler
    global _vs_logger
    _handler.close()
    _vs_logger = None

def isready():
    '''Returns the status of the logger.'''
    return _vs_logger is not None

def info(msg):
    '''Log message with level info.'''
    if _vs_logger:
        _vs_logger.info(str(msg))

def debug(msg):
    '''Log message with level debug.'''
    if _debug_on and _vs_logger:
        _vs_logger.debug(str(msg))

def error(msg):
    '''Log message with level error.'''
    if _vs_logger:
        _vs_logger.error(str(msg))

def exception(msg):
    '''Log message with level error plus exception traceback.'''
    if _vs_logger:
        _vs_logger.exception(str(msg))

def logfunction(f):
    '''Creates a decorator to log a function.'''
    @wraps(f)
    def wrapper(*args, **kw):
        debug("{} called".format(f.__name__))
        return f(*args, **kw)
    return wrapper

def logmethod(m):
    '''Creates a decorator to log a method.'''
    @wraps(m)
    def wrapper(self, *args, **kw):
        debug("{} in {} called".format(m.__name__, self.__class__.__name__))
        return m(self, *args, **kw)
    return wrapper
