#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Reads tables from HTML files
XXX This comment is not up to date anymore'''

import sys
import collections
import gc

import tkinter
import tkinter.font
import tkinter.messagebox
import tkinter.ttk as ttk

import html.parser
import html.entities

import res
import log
from misc import *

import objgraph

# Version of the table file.
CURRENT_FILE_VERSION = '0.2'

class TableError(Exception):
    pass

class EntryError(TableError):
    pass

class TableFileError(TableError):
    pass

class MarkupReaderBase(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.tmpdat = ''
        self._read_data_flag = False
        self.starttags = self._fill_tagdict('starttag')
        self.endtags = self._fill_tagdict('endtag')

    def __enter__(self):
        return self.__class__()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    # Properties ###############################################################
    @property
    def read_data_flag(self):
        return self._read_data_flag
    
    @read_data_flag.setter
    def read_data_flag(self, val):
        self._read_data_flag = val
        self.tmpdat = ''
    ############################################################################
    
    def _fill_tagdict(self, tag_marker):
        tagdict = {}
        attrs = dir(self)
        for attr in attrs:
            if attr.startswith(tag_marker):
                tag_name = attr.split('_')[1]
                tagdict[tag_name] = getattr(self, attr)
        return tagdict
    
    # Inherited from html.parser.HTMLParser ####################################
    def handle_starttag(self, tag, attrs):
        try:
            self.starttags[tag](attrs)
        except KeyError:
            pass

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        try:
            self.endtags[tag]()
        except KeyError:
            pass

    def handle_data(self, data):
        if self.read_data_flag:
            self.tmpdat += data

    def handle_charref(self, name):
        if self.read_data_flag:
            try:
                self.tmpdat += chr(int(name))
            except ValueError:
                self.tmpdat += '&' + str(int(name)) + ';'

    def handle_entityref(self, name):
        if self.read_data_flag:
            self.tmpdat += html.entities.entitydefs[name]
    ############################################################################

class TableHTMLReader(MarkupReaderBase):
    '''Internal used parser class to parse the tables from the given HTML.'''

    def __init__(self):
        super().__init__()
        self.stack = []
        self._reset(True)
        self.tablelist = []

    # Properties ###############################################################
    def get_tables(self):
        return self.tablelist

    tables = property(get_tables)
    ############################################################################

    def _reset(self, isinit = False):
        if isinit:
            self.table = None
        else:
            self.table = Table()
        self.nested = not isinit
        self.entry = None
        self.read_data_flag = False
        self.colspaned = False

    def push(self):
        self.stack.append((
            self.table,
            self.entry,
            self.read_data_flag,
            self.colspaned,
            self.nested
        ))

    def pop(self):
        (
            self.table,
            self.entry,
            self.read_data_flag,
            self.colspaned,
            self.nested
        ) = self.stack.pop()

    # Handler for the HTML-Tags (registered in self.starttags and self.endtags)
    def starttag_table(self, attrs):
        if self.table is None:
            self.table = Table()
        else:
            self.push()
            self._reset()

    def endtag_table(self):
        if self.nested:
            self.tablelist.append(self.table)
            self.pop()
        elif self.table is not None:
            self.tablelist.append(self.table)
            self.table = None

    def starttag_tr(self, attrs):
        if self.table is not None:
            self.table.add_row()

    def endtag_tr(self):
        if self.table is not None and self.colspaned:
            self.table.del_last_row()
            self.colspaned = False

    def starttag_th(self, attrs):
        if self.table is not None and not self.read_data_flag:
            val = find_attr(attrs, 'colspan')
            if val is not None:
                self.colspaned = int(val)
            self.read_data_flag = True
            self.entry = Entry()

    def endtag_th(self):
        if self.table is not None:
            if type(self.colspaned) == int:
                self.tmpdat = self.tmpdat.strip()
                self.entry.data = self.tmpdat + ' 1'
                self.table.add_header_data([
                    self.entry
                    if i == 0 else
                    Entry(self.tmpdat + ' ' + str(i + 1))
                    for i in range(self.colspaned)
                ])
                self.colspaned = False
                self.read_data_flag = False
                self.entry = None
            else:
                self.add_cell_data(self.table.add_header_data)

    def starttag_td(self, attrs):
        if self.table is not None and not self.read_data_flag:
            self.colspaned = find_attr(attrs, 'colspan') is not None
            if not self.colspaned:
                self.read_data_flag = True
                self.entry = Entry()

    def endtag_td(self):
        if self.table is not None:
            self.add_cell_data(self.table.add_data)

    def starttag_img(self, attrs):
        if self.read_data_flag:
            # Todo: Download the actual image from the web page
            # self.tmpdat += res.IMAGE_DUMMY
            pass

    def starttag_a(self, attrs):
        if self.read_data_flag:
            self.entry.link = find_attr(attrs, 'href')

    def endtag_a(self):
        pass
    ############################################################################

    # Helper functions #########################################################
    def add_cell_data(self, func):
        if self.read_data_flag and not self.colspaned:
            if type(self.tmpdat) == str:
                # Keep just one space character between the words
                tmplist = self.tmpdat.split()
                self.tmpdat = ''
                for word in tmplist:
                    self.tmpdat += word + ' '
                self.tmpdat = self.tmpdat.strip()
            self.entry.data = self.tmpdat
            func(self.entry)
            self.read_data_flag = False
            self.entry = None
    ############################################################################

class TableFileReader(MarkupReaderBase):
    def __init__(self):
        super().__init__()
        self.table = None
        self.entry = None
        self.entrydata = None
        self.headerflag = False
        self.isolddata = False
        self.add_data_func = None
        
    # Handler for the tags #####################################################
    def starttag_tablefile(self, attrs):
        if not attrs:
            raise TableFileError('No file version found.')

        version = find_attr(attrs, 'version')
        if version is None:
            raise TableFileError('No file version found.')
        elif version not in ('0.0', CURRENT_FILE_VERSION):
            raise TableFileError(
                'Wrong file version. The found version is {}.'.format(version)
            )
    
    def endtag_tablefile(self):
        pass
    
    def starttag_table(self, attrs):
        self.table = Table()
    
    def endtag_table(self):
        pass
    
    def starttag_headerrow(self, attrs):
        self.headerflag = True
        self.table.add_row()
        self.add_data_func = self.table.add_header_data
    
    def endtag_headerrow(self):
        self.headerflag = False
    
    def starttag_row(self, attrs):
        self.table.add_row()
        self.add_data_func = self.table.add_data
    
    def endtag_row(self):
        pass
    
    def starttag_entry(self, attrs):
        self.entry = Entry()
    
    def endtag_entry(self):
        pass
    
    def starttag_data(self, attrs):
        pass
    
    def endtag_data(self):
        self.add_data_func(self.entry)
        #print(self.table)
    
    def starttag_current(self, attrs):
        self.isolddata = False
        self.entrydata = EntryData()
    
    def endtag_current(self):
        self.entry.data = self.entrydata
    
    def starttag_old(self, attrs):
        self.isolddata = True
    
    def endtag_old(self):
        self.isolddata = False
    
    def starttag_olddata(self, attrs):
        self.entrydata = EntryData()
    
    def endtag_olddata(self):
        self.entry.add_olddata(self.entrydata)
    
    def starttag_number(self, attrs):
        self.read_data_flag = True
    
    def endtag_number(self):
        tmpdat = self.tmpdat.strip()
        
        try:
            self.entrydata.number = str2num(tmpdat)
        except ValueError:
            tb = sys.exc_info()[2]
            raise TableFileError(
                'Number could not be recognized.'
            ).with_traceback(tb)

        self.read_data_flag = False
    
    def starttag_string(self, attrs):
        print(dir(self))
        self.read_data_flag = True
    
    def endtag_string(self):
        # In previous versions of the program was a bug, which caused it to
        # actually break the file. To handle this broken file a workaraound is
        # needed.
        number, string = split_data(self.tmpdat.strip())
        if number is not None:
            self.entrydata.number = number
        if string:
            self.entrydata.string = string
            
        self.read_data_flag = False
    
    def starttag_link(self, attrs):
        addr = find_attr(attrs, 'addr')
        if addr is not None:
            self.entry.link = addr
        else:
            raise TableFileError('Link element does not contain an address.')
    ############################################################################
    
class EntryData:
    def __init__(self, val = None):
        self.number = None
        self.string = ''
        if val is not None:
            self.set(val)
            
    def __str__(self):
        #print('EntryData.__str__:', self.string)
        if self.string is None:
            self.string = ''
        numstr = str(self.number) if self.number is not None else ''
        return numstr + self.string
    
    def __eq__(self, other):
        if other is not None and isinstance(other, EntryData):
            return self.number == other.number and self.string == other.string
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def set(self, val):
        #print('EntryData.set:', val)
        if isinstance(val, str):
            self.number, self.string = split_data(val)
        elif isinstance(val, EntryData):
            self.number = val.number
            self.string = val.string
        elif isinstance(val, int) or isinstance(val, float):
            self.number = val
        else:
            raise EntryError(
                "The value must be either of type " +
                "'EntryData', 'str', 'int' or 'float'."
            )
    
    def dumb(self):
        output = ''
        if self.number is not None:
            output += write_tag('number', content = self.number)
        if self.string:
            output += write_tag('string', content = encode_string(self.string))
        return output

class Entry:
    def __init__(self, data = '', link = None):
        self._data = EntryData(data)
        self.link = link
        self.olddata = []

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return "'" + self.data + "'"
    
    def __eq__(self, other):
        # "self.olddata" will be ignored...
        if other is not None and isinstance(other, Entry):
            return self._data == other._data and self.link == other.link
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    # Properties ###############################################################
    def get_data(self):
        return str(self._data)
    
    def set_data(self, val):
        self._data.set(val)
        
    def get_number(self):
        return self._data.number
    
    def set_number(self, val):
        self._data.number = val
    
    def get_string(self):
        return self._data.string
    
    def set_string(self, val):
        self._data.string = val
        
    data = property(get_data, set_data)
    number = property(get_number, set_number)
    string = property(get_string, set_string)
    ############################################################################

    def isempty(self):
        return self.data in ('', None)
    
    def add_olddata(self, val):
        self.olddata.append(EntryData(val))
    
    def dumb(self):
        '''Returns a string, containing an entry, which can be used to append it
        to a file.
        '''
        curdatastr = write_tag('current', content = self._data.dumb())
        
        olddatastr = ''
        if self.olddata:
            olddata_content = ''
            for od in self.olddata:
                olddata_content += write_tag('olddata', content = od.dumb())
            olddatastr = write_tag('old', content = olddata_content)
            
        datastr = write_tag('data', content = curdatastr + olddatastr)
        
        linkstr = ''
        if self.link:
            linkstr = write_tag('link', attrs = [('addr', self.link)])
        
        return write_tag('entry', content = datastr + linkstr)
    
class TableRow(collections.UserList):
    def __init__(self, table, initlist = None):
        super().__init__(initlist)
        self.table = table
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]
        elif isinstance(key, str):
            for i, entry in enumerate(self.table.header):
                if entry.data == key:
                    return self.data[i]
            raise KeyError('Key "{}" not found.'.format(key))
        else:
            raise TypeError('The key must be of type "int" or "str"')
    
    def __setitem__(self, key, val):
        if isinstance(key, int):
            self.data[key] = val
        elif isinstance(key, str):
            for i, entry in enumerate(self.table.header):
                if entry.data == key:
                    self.data[i] = val
                    return
            raise KeyError('Key "{}" not found.'.format(key))
        else:
            raise TypeError('The key must be of type "int" or "str"')
        
    def __str__(self):
        return str(self.data)
    
    def dumb(self):
        content = ''
        for entry in self.data:
            content += entry.dumb()
        return content

class Table:
    # Magic methods ############################################################
    def __init__(self):
        '''Initiate a new empty table object'''
        self._data = []
        self.row = -1
        self.isheadered = False
        self._header = None

    def __str__(self):
        if self._header is not None:
            string = str(self._header) + '\n'
        else:
            string = ''
        for row in self._data:
            string += str(row) + '\n'
        return string

    def __repr__(self):
        string = '['
        if self._header is not None:
            string += str(self._header) + ','
        limit = len(self._data) - 1
        for row in self._data:
            string += str(row)
            if self._data.index(row) < limit:
                string += ', '
        return string + ']'
    
    def __eq__(self, other):
        if other is not None and isinstance(other, Table):
            if len(self._data) != len(other._data):
                return False
            for i in range(len(self._data)):
                # Are the rows different?
                if len(self._data[i]) != len(other._data[i]):
                    return False
                for j in range(len(self._data[i])):
                    # Are the entries different?
                    if self._data[i][j] != other._data[i][j]:
                        return False
            return True
        else:
            return False
        
    def __ne__(self, other):
        return not self.__eq__(other)
    ############################################################################

    def _mk_header(self):
        '''Internal function for adding a header to the table.'''
        if self.isheadered and self._header is None and self._data != []:
            self._header = self._data[0]
            if len(self._data) > 0:
                self._data = self._data[1:]
            self.row -= 1

            ####################################################################
            # This handles some special conditions, which occure while working
            # with Tk
            
            # The header is shorter then the data
            # -> Append additional header entries to make it fit to the data
            if self._data is not None and len(self._data) > 0:
                headerlen = len(self._header)
                datalen = len(self._data[0])
                if headerlen < datalen:
                    for i in range(headerlen, datalen):
                        self._header.append(
                            Entry(res.STD_COL_LABEL + str(i + 1))
                        )
                        
            # There are empty entries in the header
            for i in range(len(self._header)):
                if self._header[i].data == '':
                    self._header[i] = Entry(res.STD_COL_LABEL + str(i + 1))
                    
            # Delete empty columns
            j = 0
            for i in range(len(self._header)):
                col = self.get_col(j)
                if col is not None:
                    col = [str(entry) for entry in col]
                    collen = len(col) - 1
                    if col[1:] == ['' for k in range(collen)]:
                        self.del_col(j)
                    else:
                        j += 1
            ####################################################################

    # Properties ###############################################################
    def get_data(self):
        self._mk_header()
        return self._data

    def get_header(self):
        self._mk_header()
        return self._header
    
    def get_lastrow(self):
        return self._data[len(self._data) - 1]

    data = property(get_data)
    header = property(get_header)
    lastrow = property(get_lastrow)
    ############################################################################

    def get_col(self, index):
        col = []
        if self._header is not None:
            col.append(self._header[index])
        for row in self._data:
            if len(row) > index:
                col.append(row[index])
            else:
                row.append(Entry())
                col.append(row[index])
        return col

    def dumb(self, path):
        '''Saves the table object to a file.
        The parameter "path" contains the location to the file.
        '''
        headerstr = ''
        if self.isheadered:
            header_content = ''
            for entry in self._header:
                header_content += entry.dumb()
            headerstr = write_tag('headerrow', content = header_content)
            
        table_content = headerstr
        for row in self._data:
            row_content = ''
            for entry in row:
                row_content += entry.dumb()
            table_content += write_tag('row', content = row_content)
            
        tablestr = write_tag('table', content = table_content)
        
        output = write_tag('tablefile',
            attrs = [('version', CURRENT_FILE_VERSION)],
            content = tablestr
        )
        
        # Do the fucking write.
        with open(path, 'w') as f:
            f.write(output)

    def add_row(self, row = None):
        '''Appends a row to the table.
        The optional parameter row must be a TableRow, list or tuple.
        '''
        if islistlike(row):
            self._data.append(TableRow(self, row))
        elif row is not None:
            raise TypeError('"row" is neither list nor tuple')
        else:
            self._data.append(TableRow(self))
        self.row += 1

    def add_data(self, data):
        '''Adds new data to the current row.
        The table must contain at least one row. The data will be appended to
        the current row. This is also true for list or tuples.
        '''
        if self.row >= 0:
            if islistlike(self.row):
                self._data[self.row] += data
            elif isinstance(data, Entry):
                self._data[self.row].append(data)
            else:
                self._data[self.row].append(Entry(data))
        else:
            raise TableError(
                'Table contains no row where the data could be added'
            )

    def add_header_data(self, data):
        '''Adds new data to the header.
        This function has to be called, before normal data has been added.
        '''
        if self.row > 1:
            raise TableError('Table contains already data.')
        
        if not self.isheadered:
            self.isheadered = True
        self.add_data(data)

    def del_last_row(self):
        '''Deletes the last row of the table.'''
        if self.row >= 0:
            self._data.pop()
            self.row -= 1
        else:
            raise TableError('Table contains no row to delete')

    def del_col(self, index):
        '''Deletes a column of the table.'''
        if self._header is not None:
            self._header.remove(self._header[index])
        if self._data is not None and self._data != []:
            for row in self._data:
                row.remove(row[index])
        else:
            raise TableError('Error by deleting column')

    def make_header(self):
        '''Transforms the first line of the table to the header line.'''
        self.isheadered = True
        self._mk_header()
        
    def concat(self, other):
        for row in other.data:
            if row not in self.data:
                self.add_row(row)
                
    def merge(self, other):
        # XXX Ugly: Specific for Asianbookie!
        merged_rows = []
        for row1 in self.data:
            for i, row2 in enumerate(other.data):
                try:
                    if row1['Tipster'].data == row2['Tipster'].data:
                        if row2['Balance'].data != 'Bankrupt':
                            print('Row to merge:', row1['Tipster'].data)
                            
                            row1['Balance'].add_olddata(row1['Balance'].number)
                            row1['W'].add_olddata(row1['W'].number)
                            row1['D'].add_olddata(row1['D'].number)
                            row1['L'].add_olddata(row1['L'].number)
                            
                            row1['Balance'].number += row2['Balance'].number
                            row1['W'].number += row2['W'].number
                            row1['D'].number += row2['D'].number
                            row1['L'].number += row2['L'].number
                        
                        merged_rows.append(i)
                        
                except Exception as exc:
                    print(row1)
                    print(row2)
                    raise exc
        
        print('Adding new rows.')
        for i in range(len(other.data)):
            row = other.data[i]
            if i not in merged_rows and row['Balance'].data != 'Bankrupt':
                self.data.append(row)
                
        print('Finished')
                        
# This stuff was originally from some demos ####################################
def sortby(tree, col, descending):
    '''Sort tree contents when a column is clicked on.'''

    # Grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # The numeric values should not be sorted alphabetical
    converted = True
    tmpdat = []
    string = ''
    for val, foo in data:
        number, string = split_data(val)
        if number is not None:
            tmpdat.append((number, foo))
        else:
            converted = False
            break

    # Reorder data
    if converted:
        tmpdat.sort(reverse = not descending)
        data = [(str(val) + string, foo) for val, foo in tmpdat]
    else:
        data.sort(reverse = descending)
    for i, val in enumerate(data):
        tree.move(val[1], '', i)

    # Switch the heading so that it will sort in the opposite direction
    tree.heading(col, command = curry(sortby, tree, col, not descending))

class TableWidget:
    def __init__(self, root, table):
        self.tree = None
        self.tabcols = table.header
        self.tabdata = table.data
        
        if self.tabcols is None:
            # The table does not have a header. Make one.
            try:
                maxlen = max(len(line) for line in self.tabdata)
                self.tabcols = [
                    res.STD_COL_LABEL + str(i + 1) for i in range(maxlen)
                ]
            except ValueError:
                self.tabcols = [res.STD_ILLEGAL_LABEL]
        else:
            self.tabcols = self._build_row(self.tabcols)
            
        if self.tabdata is not None:
            tmp = []
            for row in self.tabdata:
                tmp.append(self._build_row(row))
            self.tabdata = tmp

        self.frame = ttk.Frame(root)
        self._setup_widgets(self.frame)
        self._build_tree()

    def _build_row(self, row):
        '''Replace empty entries with entries, which consist of a space
        character.
        Needed for representing the header of the table.
        '''
        tmp = []
        for entry in row:
            entry = ' ' if entry.isempty() else str(entry)
            tmp.append(entry)
        return tmp

    def _setup_widgets(self, frame):
        self.tree = ttk.Treeview(columns = self.tabcols, show = "headings")
        self.tree.bind("<MouseWheel>", self.wheelscroll)

        # Setup the scrollbars
        vsb = AutoScrollbar(frame,
            orient = "vertical",
            command = self.tree.yview
        )
        hsb = AutoScrollbar(frame,
            orient = "horizontal",
            command = self.tree.xview
        )
        self.tree.configure(yscrollcommand = vsb.set, xscrollcommand = hsb.set)
        self.tree.grid(column = 0, row = 0, sticky = 'nsew', in_ = frame)
        vsb.grid(column = 1, row = 0, sticky = 'ns')
        hsb.grid(column = 0, row = 1, sticky = 'ew')
        
        #ttk.Sizegrip(frame).grid(column = 1, row = 1, sticky = ('s', 'e'))

        frame.grid_columnconfigure(0, weight = 1)
        frame.grid_rowconfigure(0, weight = 1)
        frame.pack(fill = 'both', expand = True)

    def _build_tree(self):
        for col in self.tabcols:
            self.tree.heading(str(col),
                text = str(col),
                command = curry(sortby, self.tree, col, False)
            )

            # XXX tkinter.font.Font().measure expected args are incorrect
            # according to the Tk docs
            self.tree.column(col, width = tkinter.font.Font().measure(str(col)))

        for line in self.tabdata:
            # XXX Link this ID to the appropriate row in the appropriate table
            id_ = self.tree.insert('', 'end', values = line)

            # Adjust columns lenghts if necessary
            for i, val in enumerate(line):
                ilen = tkinter.font.Font().measure(val)
                if self.tree.column(self.tabcols[i], width = None) < ilen:
                    self.tree.column(self.tabcols[i], width = ilen)

    def wheelscroll(self, event):
        if event.delta > 0:
            self.tree.yview('scroll', -2, 'units')
        else:
            self.tree.yview('scroll', 2, 'units')
################################################################################

# Helper functions #############################################################
def filter_trash(tables):
    '''Filter the tables, which seem to contain nothing of interest.'''
    result = []
    for t in tables:
        if len(t.data) > 3 and t not in result:
            result.append(t)
    return result
        
def str2num(string):
    fval = float(string)
    ival = int(fval)
    return ival if fval - ival == 0 else fval

def find_attr(attrs, name):
    for attr, val in attrs:
        if attr == name:
            return val
    return None

def write_tag(tag, *args, attrs = None, content = None):
    '''Writes a tag, following the XML syntax.
    
    Parameters:
        "tag" contains the name of the tag.
        "attrs" shall be a list, containing tuples in the form "(attr, val)".
        The first element is the name of the attribute and the second is its
        value.
        "content" contains the whole content between start and end tag. If its
        value is None, the resulting tag will be a start/end tag.
    '''
    output = '<' + tag
    
    if attrs is not None:
        for attr, val in attrs:
            output += ' ' + attr + '="' + val + '"'

    if content is not None:
        output += '>\n' + str(content) + '\n</' + tag + '>\n'
    else:
        output += '/>\n'
    
    return output

def encode_string(string):
    whitelist = [chr(i) for i in range(39, 127)]
    whitelist.remove('<')
    whitelist.remove('>')
    
    output = ''
    for s in string:
        if s in whitelist:
            output += s
        else:
            output += '&#' + str(ord(s)) + ';'
    
    return output
            
def split_data(data):
    '''Splits the given data (which shall be a str object) and returns a tupel,
    containig the number as first element and the rest as second element.
    If the data does not begin with a number, the first element of the tuple
    will be None.
    '''
    number = None
    string = data

    tmpstr = ''
    if data is not None:
        #print ('1:', data)
        data = data.strip()
        if data != '' and (data[0].isdigit() or data[0] == '-'):
            
            # Extract the number from the data string
            numstr = ''
            for i, char in enumerate(data):
                if char.isdigit() or char in ('.', '-'):
                    numstr += char
                elif char == ',':
                    numstr += '.'
                elif char == ' ':
                    # Suppress space characters
                    continue
                else:
                    # "tmpstr" contains the non numeric rest.
                    tmpstr = data[i:]
                    break
            
            # The number string may end with dots, which must be deleted.
            while numstr.endswith('.'):
                numstr = numstr[: -1]
            
            #print ('2:', numstr)
            
            # The resulting numstr can still contain an illegal value...
            try:
                number = str2num(numstr)
                string = tmpstr
            except ValueError:
                string = data
    else:
        string = ''

    #print('split_data:', 'n:', number, 's:', string)
    return number, string

def islistlike(list_):
    return isinstance(list_, (list, tuple, collections.UserList))
################################################################################

# "Public" functions ###########################################################
def load(path):
    '''Loads a table file from the given path.
    It returns a Table object.
    '''
    with open(path, 'rb') as f:
        page = f.read().decode('utf_8', 'ignore').strip()
        with TableFileReader() as parser:
            try:
                parser.feed(page)
            except (html.parser.HTMLParseError, TableFileError) as exc:
                error(res.FILE_READ_ERROR, exc)
                return None
            return parser.table

def html2tables(page):
    '''Transforms a HTML page, containing tables, to a list of Table objects.
    The parameter "page" has to be a bytes object.
    '''
    page = page.decode('utf_8', 'ignore').strip()
    linecount = len(page.splitlines())
    with TableHTMLReader() as parser:
        parerr = False
        while parser.getpos()[0] < linecount:
            try:
                parser.feed(page)
                if not parerr:
                    break
            except html.parser.HTMLParseError:
                parerr = True
        return parser.tables
################################################################################

if __name__ == '__main__':
    error(res.WRONG_FILE_STARTED)
