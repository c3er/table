#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Reads tables from HTML files'''

title = 'Tabellenauswerter'

import sys

import tkinter
import tkinter.font
import tkinter.messagebox
from tkinter import ttk

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
        if self._header is not None:
            string += str (self._header) + ','
        limit = len (self._data) - 1
        for row in self._data:
            string += str (row)
            if self._data.index (row) < limit:
                string += ', '
        return string + ']'

    def __str__ (self):
        if self._header is not None:
            string = str (self._header) + '\n'
        else:
            string = ''
        for row in self._data:
            string += str (row) + '\n'
        return string

    def _mk_header (self):
        if self._header is None and self.headered and self._data != []:
            print (self._data)
            self._header = self._data [0]
            self._data = self._data [1:]
            self.row -= 1

    def get_data (self):
        self._mk_header()
        return self._data

    def get_header (self):
        self._mk_header()
        return self._header

    def get_col (self, index):
        col = []
        if self._header is not None:
            col.append (self._header [index])
        for row in self._data:
            col.append (row [index])
        return col

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
                # A tuple will be transformed automatically to a list if the row
                # is already a list
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

    def del_col (self, index):
        if self._header is not None:
            self._header.remove (self._header [index])
        if self._data is not None and self._data != []:
            for row in self._data:
                row.remove (row [index])

    def make_header (self):
        '''Transforms the first line of the table to the header line'''
        self.headered = True
        self._mk_header()

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
            self.tmpdat += '<Bild>'
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
    for index, item in enumerate (data):
        tree.move (item [1], '', index)

    # switch the heading so that it will sort in the opposite direction
    tree.heading (col,
        command = lambda c = col: sortby (tree, c, int (not descending)))

class TableWidget:
    def __init__ (self, root, table):
        self.tree = None
        self.tabcols = table.header
        self.tabdata = table.data
        if self.tabcols is None:
            try:
                maxlen = max (len (line) for line in self.tabdata)
                self.tabcols = ['Spalte ' + str (i + 1) for i in range (maxlen)]
            except ValueError:
                self.tabcols = ['Ungültig']
        else:
            j = 0
            for i in range (len (self.tabcols)):
                col = table.get_col (j)
                if (col is not None and
                        col [1:] == ['' for k in range (len (col) - 1)]):
                    table.del_col (j)
                else:
                    j += 1
        self.frame = ttk.Frame (root)
        self._setup_widgets (self.frame)
        self._build_tree()

    def _setup_widgets (self, frame):
        frame.pack (fill = 'both', expand = True)

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
            self.tree.heading (col, text = str (col),
                command = lambda c = col: sortby (self.tree, c, 0))

            # XXX tkinter.font.Font().measure expected args are incorrect
            # according to the Tk docs
            self.tree.column (col,
                width = tkinter.font.Font().measure (str (col)))

        for item in self.tabdata:
            self.tree.insert ('', 'end', values = item)

            # adjust columns lenghts if necessary
            for index, val in enumerate (item):
                ilen = tkinter.font.Font().measure (val)
                if self.tree.column (self.tabcols [index], width = None) < ilen:
                    self.tree.column (self.tabcols [index], width = ilen)
################################################################################

def html2tables (page):
    linecount = len (page.splitlines())
    with TableRead() as parser:
        parerr = False
        while parser.getpos() [0] < linecount:
            try:
                parser.feed (page)
                if not parerr:
                    break
            except html.parser.HTMLParseError as msg:
                # print (msg)
                parerr = True
        return parser.tables

class CmdWidget:
    def __init__ (self, root):
        self.frame = ttk.Frame (root)
        self.notebook = None
        self.tables = None
        self._setup_widgets()

    def _setup_widgets (self):
        ttk.Button (self.frame,
            text = 'Erste Reihe zu Überschriften',
            command = self.mk_tabcols
        ).pack (anchor = 'n')
        self.build_addr_bar().pack (fill = 'x', anchor = 's')

    def build_addr_bar (self):
        addr_frame = ttk.Frame (self.frame)
        label = ttk.Label (addr_frame, text = 'Adresse: ')
        tmp_frame = ttk.Frame (addr_frame)
        addr_entry = tkinter.Entry (tmp_frame, width = 40)
        addr_entry.insert (0, 'test.html')
        addr_handler = lambda s = self, a = addr_entry: s.addr_button_click (a)
        addr_entry.bind ('<Return>', lambda event: addr_handler())
        addr_button = ttk.Button (tmp_frame,
            text = 'Öffnen',
            command = addr_handler
        )

        label.pack (side = 'left')
        addr_entry.pack (side = 'left', expand = True, fill = 'x')
        addr_button.pack (side = 'right')
        tmp_frame.pack (side = 'right', expand = True, fill = 'x')
        return addr_frame

    # Handler functions ########################################################
    def mk_tabcols (self):
        if self.notebook is None:
            tkinter.messagebox.showerror (title,
                'Sie müssen zuerst eine gültige Adresse eingeben')
        else:
            tabconf = self.notebook.tab ('current')
            index = int (tabconf ['text'].split() [1]) - 1
            self.tables [index].make_header()
            self.show_tables()
            self.notebook.select (index)

    def addr_button_click (self, addr_entry):
        std_err_str = ('Die Adresse muss entweder auf eine lokale HTML-Datei ' +
            'verweisen oder eine vollständige Adresse zu einer Web-Seite ' +
            'enthalten')
        addr = addr_entry.get()

        if addr == '':
            tkinter.messagebox.showerror (title,
                'Bitte Adresse eingeben\n' + std_err_str)
            return
        if addr.startswith ('http://'):
            try:
                f = urllib.request.urlopen (addr)
                page = f.read().decode ('utf_8', 'ignore').strip()
                f.close()
            except urllib.request.URLError as msg:
                tkinter.messagebox.showerror (title,
                    'Web-Seite konnte nicht gelesent werden\n' + str (msg))
                return
        elif addr.endswith ('.html') or addr.endswith ('.htm'):
            try:
                f = open (addr, 'r')
                page = f.read()
                f.close()
            except IOError as msg:
                tkinter.messagebox.showerror (title,
                    'Datei konnte nicht gelesen werden\n' + str (msg))
                return
        else:
            tkinter.messagebox.showerror (title, std_err_str)
            return

        self.tables = html2tables (page)
        # print (self.tables)
        self.show_tables()
    ############################################################################

    # Helper functions #########################################################
    def show_tables (self):
        if self.notebook is not None:
            self.notebook.destroy()
        self.notebook = ttk.Notebook()
        for table in self.tables:
            print (table)
            # print (repr (table))
            tw = TableWidget (self.notebook, table)
            self.notebook.add (tw.frame,
                text = 'Tabelle ' + str (self.tables.index (table) + 1))
        self.notebook.pack (expand = True, fill = 'both', anchor = 'n')
    ############################################################################

if __name__ == '__main__':
    root = tkinter.Tk()
    root.wm_title (title)
    CmdWidget (root).frame.pack (fill = 'x', anchor = 'n')
    root.mainloop()
