#!/usr/bin/env python
# -*- coding: utf-8 -*-

import table

class SessionError (Exception):
    pass

class TableContainer:
    def __init__ (self, tab):
        self.table = tab
        self.tablewidget = None
        self.frame = None
        self.filename = None
        self.modified = True

class Session:
    def __init__ (self):
        self.notebook = None
        self.tables = None
        
    def new (self):
        pass
    
    def save_table (self):
        pass
    
    def save_table_as (self):
        pass
