#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tabellen aus HTML-Dateien einlesen

import tkinter
import tkinter.font
from tkinter import ttk

import html.parser
import html.entities

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
            if self._data.index (row) < limit: string += ', '
        return string + ']'

    def __str__ (self):
        string = ''
        for row in self._data: string += str (row) + '\n'
        return string

    def _make_header (self):
        if self._header is None and self.headered:
            self._header = self._data [0]
            self._data = self._data [1:]

    def get_data (self):
        self._make_header()
        return self._data

    def get_header (self):
        self._make_header()
        return self._header

    data = property (get_data)
    header = property (get_header)

    def add_row (self):
        self._data.append ([])
        self.row += 1

    def add_data (self, data):
        if self.row >= 0: self._data [self.row].append (data)

    def add_header_data (self, data):
        if not self.headered: self.headered = True
        self.add_data (data)

class TableRead (html.parser.HTMLParser):
    def __init__ (self):
        super().__init__()
        self.table = None
        self.tablelist = []
        self.tmptable = []
        self.incell = False
        self.nested = False
        self.tmpdat = ''

    def __enter__ (self):
        return TableRead()

    def __exit__ (self, exc_type, exc_value, traceback):
        self.close()

    def get_tables (self):
        return self.tablelist

    tables = property (get_tables)

    def handle_starttag (self, tag, attrs):
        if tag == 'table':
            if self.table is None: self.table = Table()
            else:
                self.tmptable.append (self.table)
                self.table = Table()
                self.incell = False
                self.nested = True
        elif tag == 'img' and self.incell: self.tmpdat += '_img_'
        elif self.table is not None:
            if tag == 'tr': self.table.add_row()
            elif tag in ('td', 'th') and not self.incell: self.incell = True

    def handle_endtag (self, tag):
        if tag == 'table':
            if self.nested:
                self.tmpdat = self.table
                self.table = self.tmptable.pop()
                self.nested = False
                self.incell = True
            else:
                self.tablelist.append (self.table)
                self.table = None
        elif self.table is not None:
            if tag in ('td', 'th') and self.incell:
                if type (self.tmpdat) == str: self.tmpdat = self.tmpdat.strip()
                if tag == 'td': self.table.add_data (self.tmpdat)
                else: self.table.add_header_data (self.tmpdat)
                self.tmpdat = ''
                self.incell = False

    def handle_data (self, data):
        if self.incell and type (self.tmpdat) != Table: self.tmpdat += data

    def handle_charref (self, name):
        if self.incell and type (self.tmpdat) != Table:
            self.tmpdat += chr (int (name))

    def handle_entityref (self, name):
        if self.incell and type (self.tmpdat) != Table:
            self.tmpdat += html.entities.entitydefs [name]

################################################################################
# Dieses Zeug ist ursprünglich aus einem Demo in der Python-Distribution #######
def sortby (tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set (child, col), child) for child in tree.get_children ('')]

    # reorder data
    data.sort (reverse = descending)
    for indx, item in enumerate (data): tree.move (item [1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading (col,
        command = lambda c = col: sortby (tree, c, int (not descending)))

class TableWidget:
    def __init__ (self, frame, table):
        self.tree = None
        self.tabcols = table.header
        self.tabdata = table.data
        if self.tabcols is None:
            maxlen = max ((len (line) for line in self.tabdata))
            self.tabcols = ['Spalte ' + str (i + 1) for i in range (maxlen)]
        self._setup_widgets (frame)
        self._build_tree()

    def _setup_widgets (self, frame):
        # container = ttk.Frame()
        container = frame
        container.pack (fill = 'both', expand = True)

        # XXX Sounds like a good support class would be one for constructing
        #     a treeview with scrollbars.
        self.tree = ttk.Treeview (columns = self.tabcols, show = "headings")
        vsb = ttk.Scrollbar (orient = "vertical", command = self.tree.yview)
        hsb = ttk.Scrollbar (orient = "horizontal", command = self.tree.xview)
        self.tree.configure (yscrollcommand = vsb.set, xscrollcommand = hsb.set)
        self.tree.grid (column = 0, row = 0, sticky = 'nsew', in_ = container)
        vsb.grid (column = 1, row = 0, sticky = 'ns', in_ = container)
        hsb.grid (column = 0, row = 1, sticky = 'ew', in_ = container)

        container.grid_columnconfigure (0, weight = 1)
        container.grid_rowconfigure (0, weight = 1)

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

with open ('nested.html', 'r') as f: page = f.read()
with TableRead() as parser:
    parser.feed (page)
    tables = parser.tables

root = tkinter.Tk()
root.wm_title ('Wettprogramm')
nb = ttk.Notebook()
i = 0
for table in tables:
    i += 1
    f = tkinter.Frame (nb)
    TableWidget (f, table)
    nb.add (f, text = 'Tabelle ' + str (i))
    print (table)
nb.pack (expand = 1, fill = 'both')
root.mainloop()
