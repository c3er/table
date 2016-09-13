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


class SessionError(Exception):
    pass


class UnknownPathException(Exception):
    pass


class TableContainer:
    def __init__(self, tab, session, path = None):
        self.data = tab
        self.session = session
        self.tablewidget = None
        self.frame = None
        self.path = path
        
        # If there is a path then the table was loaded
        # from a file and it is not modified yet.
        self.modified = path is None
        
    # Properties ############################################################### 
    def get_filename(self):
        if self.path:
            return os.path.basename(self.path)
        else:
            return res.UNKNOWN_FILE + ' ' + str(self.session.tables.index(self))
    
    def get_isheadered(self):
        return self.data.isheadered
    
    filename = property(get_filename)
    isheadered = property(get_isheadered)
    ############################################################################
    
    def _basic_wrapper(self, func):
        func()
        self.modified = True
        self.update()
        
    def save(self, path = None):
        if path is not None:
            self.path = path

        if not self.path:
            raise UnknownPathException()
        else:
            self.data.dumb(self.path)
            self.modified = False
            self.session.update()
            
    def mk_tabcols(self):
        self._basic_wrapper(self.data.make_header)
                
    def merge(self, other):
        self._basic_wrapper(curry(self.data.merge, other))

    @log.logmethod
    def update(self, session_update = False):
        '''Regenerates the view of the table.
        The parameter "session_update" will be set to "True", if this function
        is called in the update method of a "Session" object.
        '''
        if not session_update:
            self.session.update()
        else:
            if self.frame:
                self.frame.destroy()
            if self.data is not None:
                self.tablewidget = table.TableWidget(
                    self.session.notebook,
                    self.data
                )
                self.frame = self.tablewidget.frame


class Session:
    def __init__(self, root, state_handler):
        self.root = root
        self.notebook = None
        self.tables = []
        self.state_handler = state_handler
        self.update(True)
       
    # Properties ############################################################### 
    def get_modified(self):
        if self.isempty:
            return False
        for t in self.tables:
            if t.modified:
                return True
        return False
    
    def get_current_table(self):
        if self.notebook:
            return self.tables[self.notebook.index('current')]
        else:
            raise SessionError(res.SESSION_NOTEBOOK_ERROR)
        
    def get_isempty(self):
        return not self.tables
    
    modified = property(get_modified)
    current_table = property(get_current_table)
    isempty = property(get_isempty)
    ############################################################################
    
    def add_table(self, tab):
        self.tables.append(TableContainer(tab, self))
    
    def set_tablelist(self, tables):
        if len(tables) > 0:
            self.tables = []
            for t in tables:
                self.add_table(t)
            self.update(True)
            
    def get_table(self, index):
        return self.tables[index]
    
    def get_table_index(self, path):
        for t in self.tables:
            if t.path == path:
                return self.tables.index(t)
            
        # No table found, which has the given path.
        return -1
    
    def open_tabfile(self, path):
        tindex = self.get_table_index(path)
        if tindex == -1:
            tab = table.load(path)
            if tab is not None:
                tc = TableContainer(tab, self, path)
                self.tables.append(tc)
                self.update()
                self.notebook.select(len(self.tables) - 1)
        else:
            self.notebook.select(tindex)
            
    def merge_tables(self, path):
        tab = table.load(path)
        tc = self.current_table
        tc.merge(tab)
    
    @log.logmethod
    def update(self, isnew = False):
        log.debug('Anzahl der Tabellen: ' + str(len(self.tables)))
        index = 0
        
        if self.notebook is not None:
            # Save the current index, if some tables are open.
            tablen = len(self.notebook.tabs())
            if not isnew and tablen > 0:
                index = self.notebook.index('current')
                #print('index: "{}"'.format(index), type(index))
                
            self.notebook.destroy()
        self.notebook = ttk.Notebook()
        
        for t in self.tables:
            t.update(True)
            if t.data is not None:
                title = t.filename
                    
                if t.modified:
                    title += '*'
                    
                self.notebook.add(t.frame, text = title)
        
        if len(self.tables) > 0:
            self.notebook.pack(expand = True, fill = 'both', anchor = 'n')
            self.notebook.select(index)
            self.notebook.bind(
                '<<NotebookTabChanged>>',
                lambda event: self.state_handler(self)
            )
        
        self.state_handler(self)
