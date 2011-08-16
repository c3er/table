#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Mediator between the GUI and the data.'''

import os

import tkinter
import tkinter.ttk as ttk

import table
import log
import res
from misc import *

class SessionError (Exception):
    pass

class UnknownPathException (Exception):
    pass

class TableContainer:
    def __init__ (self, tab, session, path = None):
        self.data = tab
        self.session = session
        self.tablewidget = None
        self.frame = None
        self.path = path
        
        # If there is a path then the table was loaded from a file and it is not
        # modified yet.
        self.modified = path is None
        
    # Properties ############################################################### 
    def get_filename (self):
        return os.path.basename (self.path) if self.path else res.UNKNOWN_FILE
    
    def get_isheadered (self):
        return self.data.isheadered
    
    filename = property (get_filename)
    isheadered = property (get_isheadered)
    ############################################################################
        
    def save (self, path = None):
        if path is not None:
            self.path = path

        if not self.path:
            raise UnknownPathException()
        else:
            self.data.dumb (self.path)
            self.modified = False
            self.session.update()
            
    def mk_tabcols (self):
        self.data.make_header()
        self.modified = True
        self.update()

    @log.logmethod
    def update (self, session_update = False):
        if not session_update:
            self.session.update()
        else:
            if self.frame:
                self.frame.destroy()
            self.tablewidget = table.TableWidget (
                self.session.notebook,
                self.data
            )
            self.frame = self.tablewidget.frame

class Session:
    def __init__ (self, root, state_handler):
        self.root = root
        self.notebook = None
        self.tables = []
        self.state_handler = state_handler
       
    # Properties ############################################################### 
    def get_modified (self):
        if self.isempty:
            return False
        for t in self.tables:
            if t.modified:
                return True
        return False
    
    def get_current_table (self):
        if self.notebook:
            index = self.notebook.index ('current')
            return self.tables [index]
        else:
            raise SessionError (res.SESSION_NOTEBOOK_ERROR)
        
    def get_isempty (self):
        return self.tables is None or len (self.tables) == 0
    
    modified = property (get_modified)
    current_table = property (get_current_table)
    isempty = property (get_isempty)
    ############################################################################
    
    def add_table (self, tab):
        self.tables.append (TableContainer (tab, self))
    
    def set_tablelist (self, tables):
        if len (tables) > 0:
            self.tables = []
            for t in tables:
                self.add_table (t)
            self.update (True)
            
    def get_table (self, index):
        return self.tables [index]
    
    def get_table_index (self, path):
        for t in self.tables:
            if t.path == path:
                return self.tables.index (t)
        return -1
    
    def open_tabfile (self, path):
        tindex = self.get_table_index (path)
        if tindex == -1:
            tab = table.load (path)
            tc = TableContainer (tab, self, path)
            self.tables.append (tc)
            self.update()
            self.notebook.select (len (self.tables) - 1)
        else:
            self.notebook.select (tindex)
    
    @log.logmethod
    def update (self, isnew = False):
        log.debug ('Anzahl der Tabellen: ' + str (len (self.tables)))
        index = 0
        
        if self.notebook is not None:
            if not isnew:
                index = self.notebook.index ('current')
            self.notebook.destroy()
        self.notebook = ttk.Notebook()
        
        counter = 1
        for t in self.tables:
            t.update (True)
            title = t.filename
            
            if title == res.UNKNOWN_FILE:
                title += ' ' + str (counter)
                counter += 1
                
            if t.modified:
                title += '*'
                
            self.notebook.add (t.frame, text = title)
            
        self.notebook.pack (expand = True, fill = 'both', anchor = 'n')
        self.notebook.select (index)
        self.notebook.bind (
            '<<NotebookTabChanged>>',
            lambda event: self.state_handler (self)
        )
        
        self.state_handler (self)
