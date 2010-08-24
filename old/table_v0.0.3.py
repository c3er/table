#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Read tables from HTML files

import sys

import tkinter
import tkinter.font
from tkinter import ttk
from tkinter import tix

import html.parser
import html.entities

import urllib.request

class TableError (Exception):
    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr (self.value)

class Table:
    def __init__ (self):
        self._data = []
        self.row = -1
        self.headered = False
        self._header = None

    def __repr__ (self):
        string = '['
        limit = len (self._data) - 1
        for row in self._data:
            string += str (row)
            if self._data.index (row) < limit:
                string += ', '
        return string + ']'

    def __str__ (self):
        string = ''
        for row in self._data:
            string += str (row) + '\n'
        return string

    def _make_header (self):
        if self._header is None and self.headered:
            self._header = self._data [0]
            self._data = self._data [1:]
            self.row -= 1

    def get_data (self):
        self._make_header()
        return self._data

    def get_header (self):
        self._make_header()
        return self._header

    data = property (get_data)
    header = property (get_header)

    def add_row (self, row = None):
        '''Appends a row to the table. The optional parameter row must be a
        list or a tuple'''
        if type (row) == list:
            self._data.append (row)
        elif type (row) == tuple:
            self._data.append (list (row))
        elif row is not None:
            raise ValueError ('row is neither list nor tuple')
        else:
            self._data.append ([])
        self.row += 1

    def add_data (self, data):
        if self.row >= 0:
            if type (data) in (list, tuple):
                self._data [self.row] += data
            else:
                self._data [self.row].append (data)
        else:
            raise TableError ('Table contains no row')

    def add_header_data (self, data):
        if not self.headered:
            self.headered = True
        self.add_data (data)

    def del_last_row (self):
        if self.row >= 0:
            self._data.pop()
            self.row -= 1
        else:
            raise TableError ('Table containts no row to delete')

class TableRead (html.parser.HTMLParser):
    def __init__ (self):
        super().__init__()
        self.table = None
        self.row = None
        self.tablelist = []
        self.tmptable = []
        self.incell = False
        self.nested = False
        self.colspaned = False
        self.collist = []
        self.tmpdat = ''
        self.starttags = {
            'table': self.table_start,
            'tr': self.tr_start,
            'td': self.td_start,
            'th': self.th_start,
            'img': self.img
        }
        self.endtags = {
            'table': self.table_end,
            'tr': self.tr_end,
            'td': self.td_end,
            'th': self.th_end
        }

    def __enter__ (self):
        return TableRead()

    def __exit__ (self, exc_type, exc_value, traceback):
        self.close()

    def get_tables (self):
        return self.tablelist

    tables = property (get_tables)

    # Handler for the HTML-Tags (registered in self.starttags and self.endtags)
    def table_start (self, attrs):
        if self.table is None:
            self.table = Table()
        else:
            self.tmptable.append (self.table)
            self.table = Table()
            self.incell = False
            self.nested = True
            self.collist.append (self.colspaned)
            self.colspaned = False

    def table_end (self):
        if self.nested:
            self.tablelist.append (self.table)
            self.table = self.tmptable.pop()
            self.nested = False
            self.incell = True
            self.colspaned = self.collist.pop()
        elif self.table is not None:
            self.tablelist.append (self.table)
            self.table = None

    def tr_start (self, attrs):
        if self.table is not None:
            self.table.add_row()

    def tr_end (self):
        if self.table is not None and self.colspaned:
            self.table.del_last_row()
            self.colspaned = False

    def th_start (self, attrs):
        if self.table is not None and not self.incell:
            for attr in attrs:
                if attr [0] == 'colspan':
                    self.colspaned = int (attr [1])
            self.incell = True

    def th_end (self):
        if self.table is not None:
            if type (self.colspaned) == int:
                self.tmpdat = self.tmpdat.strip()
                self.table.add_header_data (
                    [self.tmpdat if i == 0 else 'Spalte ' + str (i + 1)
                    for i in range (self.colspaned)]
                )
                self.colspaned = False
                self.tmpdat = ''
                self.incell = False
            else:
                self.add_cell_data (self.table.add_header_data)

    def td_start (self, attrs):
        if self.table is not None and not self.incell:
            for attr in attrs:
                if attr [0] == 'colspan':
                    self.colspaned = True
            if not self.colspaned:
                self.incell = True

    def td_end (self):
        if self.table is not None:
            self.add_cell_data (self.table.add_data)

    def img (self, attrs):
        if self.incell:
            self.tmpdat += '_img_'
    ############################################################################

    # Helperfunctions ##########################################################
    def add_cell_data (self, func):
        if self.incell and not self.colspaned:
            if type (self.tmpdat) == str:
                tmplist = self.tmpdat.split()
                self.tmpdat = ''
                for word in tmplist:
                    self.tmpdat += word + ' '
                self.tmpdat = self.tmpdat.strip()
            func (self.tmpdat)
            self.tmpdat = ''
            self.incell = False
    ############################################################################

    # Inherited from HTMLParser ################################################
    def handle_starttag (self, tag, attrs):
        if tag in self.starttags.keys():
            self.starttags [tag] (attrs)

    def handle_startendtag (self, tag, attrs):
        self.handle_starttag (tag, attrs)

    def handle_endtag (self, tag):
        if tag in self.endtags.keys():
            self.endtags [tag]()

    def handle_data (self, data):
        if self.incell:
            self.tmpdat += data

    def handle_charref (self, name):
        if self.incell:
            try:
                self.tmpdat += chr (int (name))
            except ValueError:
                self.tmpdat += '?'

    def handle_entityref (self, name):
        if self.incell:
            self.tmpdat += html.entities.entitydefs [name]

################################################################################
# This stuff was originally from some demos in the Python-distribution #########

def sortby (tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set (child, col), child) for child in tree.get_children ('')]

    # reorder data
    data.sort (reverse = descending)
    for indx, item in enumerate (data):
        tree.move (item [1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading (col,
        command = lambda c = col: sortby (tree, c, int (not descending)))

class TableWidget:
    def __init__ (self, frame, table):
        self.tree = None
        self.tabcols = table.header
        self.tabdata = table.data
        if self.tabcols is None:
            maxlen = max (len (line) for line in self.tabdata)
            self.tabcols = ['Spalte ' + str (i + 1) for i in range (maxlen)]
        self._setup_widgets (frame)
        self._build_tree()

    def _setup_widgets (self, frame):
        frame.pack (fill = 'both', expand = True)

        # XXX Sounds like a good support class would be one for constructing
        #     a treeview with scrollbars.
        self.tree = ttk.Treeview (columns = self.tabcols, show = "headings")
        vsb = ttk.Scrollbar (orient = "vertical", command = self.tree.yview)
        hsb = ttk.Scrollbar (orient = "horizontal", command = self.tree.xview)
        self.tree.configure (yscrollcommand = vsb.set, xscrollcommand = hsb.set)
        self.tree.grid (column = 0, row = 0, sticky = 'nsew', in_ = frame)
        vsb.grid (column = 1, row = 0, sticky = 'ns', in_ = frame)
        hsb.grid (column = 0, row = 1, sticky = 'ew', in_ = frame)

        frame.grid_columnconfigure (0, weight = 1)
        frame.grid_rowconfigure (0, weight = 1)

    def _build_tree (self):
        for col in self.tabcols:
            self.tree.heading (col, text = col.title(),
                command = lambda c = col: sortby (self.tree, c, 0))
            # XXX tkFont.Font().measure expected args are incorrect according
            #     to the Tk docs
            self.tree.column (col,
                width = tkinter.font.Font().measure (col.title()))

        for item in self.tabdata:
            self.tree.insert ('', 'end', values = item)

            # adjust columns lenghts if necessary
            for indx, val in enumerate (item):
                ilen = tkinter.font.Font().measure (val)
                if self.tree.column (self.tabcols [indx], width = None) < ilen:
                    self.tree.column (self.tabcols [indx], width = ilen)
################################################################################

class CmdWidget:
    def __init__ (self, frame):
        self._setup_widgets (frame)

    def _setup_widgets (self, frame):
        entry = tkinter.Entry()
        entry.pack (expand = 1, fill = 'both')

def html2tables (page):
    linecount = len (page.splitlines())
    with TableRead() as parser:
        parerr = False
        while parser.getpos() [0] < linecount:
            try:
                parser.feed (page)
                if not parerr:
                    break
            except html.parser.HTMLParseError:
                parerr = True
        return parser.tables

if __name__ == '__main__':
    with open ('nested.html', 'r') as f:
        page = f.read()
    ''' url = 'http://blog-fussball.de/wm-2010-in-sudafrika/die-wm-2010-spielplan-im-fernsehen-live-ubertragungen-der-ard-zdf-und-rtl'
    with urllib.request.urlopen (url) as f:
        page = f.read().decode ('utf_8', 'ignore').strip() '''

    tables = html2tables (page)
    # for table in tables: print (table)

    root = tkinter.Tk()
    root.wm_title ('Tabellenauswerter')

    f = tkinter.Frame (root)
    CmdWidget (f)
    f.pack (expand = 1, fill = 'both', anchor = 'n')

    nb = ttk.Notebook()
    i = 0
    for table in tables:
        print (table)
        i += 1
        f = tkinter.Frame (nb)
        TableWidget (f, table)
        nb.add (f, text = 'Tabelle ' + str (i))
    nb.pack (expand = 1, fill = 'both', anchor = 's')
    root.mainloop()
