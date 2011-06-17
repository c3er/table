#!/usr/bin/env python
# -*- coding: utf-8 -*-

import table

class SessionError (Exception):
    pass

class Session:
    def __init__ (self):
        self._tables = None
        self._fname = None
        self.handlers = []
        self.state = None

    def get_tables (self):
        return self._tables

    def set_tables (self, tables):
        pass

    def get_filename (self):
        return self._fname

    def set_filename (self, fname):
        pass


    tables = property (get_tables, set_tables)
    filename = property (get_filename, set_filename)

    def _handle (self):
        for handler in self.handlers:
            handler (self)

    def save (self, fname = None):
        if self._fname is None and fname is None:
            raise SessionError ('Filename unknown')
        else:
            pass

    def add_handler (self, handler):
        if handler not in self.handlers:
            self.handlers.append (handler)

def new():
    pass

def load (fname):
    pass
