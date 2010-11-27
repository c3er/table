#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Reads tables from HTML files'''

import tkinter
import tkinter.font
import tkinter.messagebox
import tkinter.ttk as ttk

import html.parser
import html.entities

class TableError (Exception):
    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr (self.value)

class Entry:
    def __init__ (self, data = '', image = None, link = None):
        self.data = data
        self.image = image
        self.link = link

    def __str__ (self):
        return self.data

    def __repr__ (self):
        return "'" + self.data + "'"

    def isempty (self):
        return self.data in ('', None)

class Table:
    def __init__ (self):
        '''Initiate a new empty table object'''
        self._data = []
        self.row = -1
        self.headered = False
        self._header = None

    def __str__ (self):
        if self._header is not None:
            string = str (self._header) + '\n'
        else:
            string = ''
        for row in self._data:
            string += str (row) + '\n'
        return string

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

    def _mk_header (self):
        '''Internal function to prepare the header'''
        if self.headered and self._header is None and self._data != []:
            self._header = self._data [0]
            if len (self._data) > 0:
                self._data = self._data [1:]
            self.row -= 1

            # This handles some special conditions, which occurre while working
            # with Tk
            if self._data is not None and len (self._data) > 0:
                headerlen = len (self._header)
                datalen = len (self._data [0])
                if headerlen < datalen:
                    for i in range (headerlen, datalen):
                        self._header.append (Entry ('Spalte ' + str (i + 1)))
            for i in range (len (self._header)):
                if self._header [i].data == '':
                    self._header [i] = Entry ('Spalte ' + str (i + 1))

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
            if len (row) > index:
                col.append (row [index])
            else:
                row.append (Entry())
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
        '''Adds new data to the current row.
        The table must contain at least one row. The data will be appended to
        the current row. This is also true for list or tuples'''
        if self.row >= 0:
            if type (data) in (list, tuple):
                # A tuple will be transformed automatically to a list if the row
                # is already a list
                self._data [self.row] += data
            elif type (data) == Entry:
                self._data [self.row].append (data)
            else:
                self._data [self.row].append (Entry (data))
        else:
            raise TableError (
                'Table contains no row where the data could be added')

    def add_header_data (self, data):
        '''Adds new data to the header. This function have to be called, before
        normal data was added.'''
        if not self.headered:
            self.headered = True
        self.add_data (data)

    def del_last_row (self):
        '''Deletes the last row of the table.'''
        if self.row >= 0:
            self._data.pop()
            self.row -= 1
        else:
            raise TableError ('Table contains no row to delete')

    def del_col (self, index):
        '''Deletes a column of the table'''
        if self._header is not None:
            self._header.remove (self._header [index])
        if self._data is not None and self._data != []:
            for row in self._data:
                row.remove (row [index])
        else:
            raise TableError ('Error by deleting column')

    def make_header (self):
        '''Transforms the first line of the table to the header line'''
        self.headered = True
        self._mk_header()

class TableRead (html.parser.HTMLParser):
    def __init__ (self):
        super().__init__()
        self.stack = []
        self._reset (True)
        self.row = None
        self.tablelist = []
        self.nested = False
        self.tmpdat = ''
        self.starttags = {
            'table': self.table_start,
            'tr': self.tr_start,
            'td': self.td_start,
            'th': self.th_start,
            'a': self.a_start,
            'img': self.img
        }
        self.endtags = {
            'table': self.table_end,
            'tr': self.tr_end,
            'td': self.td_end,
            'th': self.th_end,
            'a': self.a_end
        }

    def __enter__ (self):
        return TableRead()

    def __exit__ (self, exc_type, exc_value, traceback):
        self.close()

    def _reset (self, isinit):
        if isinit:
            self.table = None
        else:
            self.table = Table()
        self.nested = not isinit
        self.entry = None
        self.incell = False
        self.colspaned = False

    def get_tables (self):
        return self.tablelist

    tables = property (get_tables)

    def push (self):
        self.stack.append ((
            self.table,
            self.entry,
            self.incell,
            self.colspaned,
            self.nested
        ))

    def pop (self):
        (
            self.table,
            self.entry,
            self.incell,
            self.colspaned,
            self.nested
        ) = self.stack.pop()

    # Handler for the HTML-Tags (registered in self.starttags and self.endtags)
    def table_start (self, attrs):
        if self.table is None:
            self.table = Table()
        else:
            self.push()
            self._reset (False)

    def table_end (self):
        if self.nested:
            self.tablelist.append (self.table)
            self.pop()
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
            for param, val in attrs:
                if param == 'colspan':
                    self.colspaned = int (val)
            self.incell = True
            self.entry = Entry()

    def th_end (self):
        if self.table is not None:
            if type (self.colspaned) == int:
                self.tmpdat = self.tmpdat.strip()
                self.entry.data = self.tmpdat
                self.table.add_header_data (
                    [self.entry if i == 0 else Entry ('Spalte ' + str (i + 1))
                    for i in range (self.colspaned)]
                )
                self.colspaned = False
                self.tmpdat = ''
                self.incell = False
                self.entry = None
            else:
                self.add_cell_data (self.table.add_header_data)

    def td_start (self, attrs):
        if self.table is not None and not self.incell:
            for param, val in attrs:
                if param == 'colspan':
                    self.colspaned = True
            if not self.colspaned:
                self.incell = True
                self.entry = Entry()

    def td_end (self):
        if self.table is not None:
            self.add_cell_data (self.table.add_data)

    def img (self, attrs):
        if self.incell:
            # Todo: Download the actuall image from the web page
            self.tmpdat += '<Bild>'

    def a_start (self, attrs):
        pass

    def a_end (self):
        pass
    ############################################################################

    # Helper functions #########################################################
    def add_cell_data (self, func):
        if self.incell and not self.colspaned:
            if type (self.tmpdat) == str:
                # Keep just one space character between the words
                tmplist = self.tmpdat.split()
                self.tmpdat = ''
                for word in tmplist:
                    self.tmpdat += word + ' '
                self.tmpdat = self.tmpdat.strip()
            self.entry.data = self.tmpdat
            func (self.entry)
            self.tmpdat = ''
            self.incell = False
            self.entry = None
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
    ############################################################################

def html2tables (page):
    '''Transforms a HTML page, containing tables, to a list of Table objects
    The parameter "page" has to be a bytes object'''
    page = page.decode ('utf_8', 'ignore').strip()
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

def filter_trash (tables):
    listlen = len (tables)
    j = 0
    for i in range (listlen):
        if (tables [j].data in ([], [['']], [''], [['', '', 'No.']]) or
                len (tables [j].data) <= 3):
            tables.remove (tables [j])
            listlen -= 1
        else:
            j += 1

# This stuff was originally from some demos ####################################
class Curry:
    """handles arguments for callback functions"""
    def __init__ (self, callback, *args, **kw):
        self.callback = callback
        self.args = args
        self.kw = kw

    def __call__ (self):
        return self.callback (*self.args, **self.kw)

def sortby (tree, col, descending):
    """Sort tree contents when a column is clicked on."""

    # grab values to sort
    data = [(tree.set (child, col), child) for child in tree.get_children ('')]

    # The numeric values should not be sorted alphabetical
    tmpstr = ''
    converted = False
    tmpdat = []
    try:
        # XXX Erkennung für Zahlenwerte überarbeiten
        for val, foo in data:
            if val.endswith ('.'):
                val = val [0: -1]
                tmpstr = '.'
            elif val.endswith ('%'):
                val = val [0: -1]
                tmpstr = '%'
            fval = float (val)
            ival = int (fval)
            tmpdat.append ((ival if fval - ival == 0 else fval, foo))
        converted = True
    except ValueError:
        pass

    # reorder data
    if converted:
        tmpdat.sort (reverse = not descending)
        data = [(str (val) + tmpstr, foo) for val, foo in tmpdat]
    else:
        data.sort (reverse = descending)
    for i, val in enumerate (data):
        tree.move (val [1], '', i)

    # switch the heading so that it will sort in the opposite direction
    tree.heading (col,
        command = Curry (sortby, tree, col, int (not descending)))

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
            self.tabcols = self._build_row (self.tabcols)
        if self.tabdata is not None:
            tmp = []
            for row in self.tabdata:
                tmp.append (self._build_row (row))
            self.tabdata = tmp
            j = 0
            for i in range (len (self.tabcols)):
                col = table.get_col (j)
                if col is not None:
                    col = [str (entry) for entry in col]
                    collen = len (col) - 1
                    if col [1:] == ['' for k in range (collen)]:
                        table.del_col (j)
                    else:
                        j += 1
        self.frame = ttk.Frame (root)
        self._setup_widgets (self.frame)
        self._build_tree()

    def _build_row (self, row):
        tmp = []
        for entry in row:
            entry = ' ' if entry.isempty() else str (entry)
            tmp.append (entry)
        return tmp

    def _setup_widgets (self, frame):
        frame.pack (fill = 'both', expand = True)
        self.tree = ttk.Treeview (columns = self.tabcols, show = "headings")
        self.tree.bind ("<MouseWheel>", self.wheelscroll)

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
            self.tree.heading (str (col),
                text = str (col),
                command = Curry (sortby, self.tree, col, False)
            )

            # XXX tkinter.font.Font().measure expected args are incorrect
            # according to the Tk docs
            self.tree.column (col,
                width = tkinter.font.Font().measure (str (col)))

        for line in self.tabdata:
            # XXX Link this ID to the appropriate row in the appropriate table
            id_ = self.tree.insert ('', 'end', values = line)

            # adjust columns lenghts if necessary
            for i, val in enumerate (line):
                ilen = tkinter.font.Font().measure (val)
                if self.tree.column (self.tabcols [i], width = None) < ilen:
                    self.tree.column (self.tabcols [i], width = ilen)

    def wheelscroll (self, event):
        if event.delta > 0:
            self.tree.yview ('scroll', -2, 'units')
        else:
            self.tree.yview ('scroll', 2, 'units')
################################################################################

if __name__ == '__main__':
    root = ttk.Frame()
    tkinter.messagebox.showerror ('Fehler',
        'Sie müssen "Tabellenauswerter.py" starten')
    root.destroy()
