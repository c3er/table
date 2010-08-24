#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tabellen aus HTML-Dateien einlesen

import sys
import html.parser

class TableRead (html.parser.HTMLParser):
    chrdict = {
        'auml': 'ä',
        'Auml': 'Ä',
        'ouml': 'ö',
        'Ouml': 'Ö',
        'uuml': 'ü',
        'Uuml': 'Ü',
        'szlig': 'ß',
        'quot': '"',
        'amp': '&',
        'nbsp': ' ',
        'copy': '(C)',
        'eacute': 'é',
        'euro': '€',
        'lt': '<',
        'gt': '>',
        'iexcl': '¡',
        'cent': '¢',
        'Agrave': 'À',
        'Aacute': 'Á'
        # Muss noch erweitert werden
    }

    def __init__ (self):
        super().__init__()
        self.table = None
        self.tablelist = []
        self.tmptable = []
        self.row = -1
        self.tmprow = []
        self.incell = False
        self.nested = False
        self.tmpdat = ''

    def get_tables (self):
        return self.tablelist

    tables = property (get_tables)

    def handle_starttag (self, tag, attrs):
        if tag == 'table':
            if self.table is None: self.table = []
            else:
                self.tmptable.append (self.table)
                self.table = []
                self.tmprow.append (self.row)
                self.row = -1
                self.incell = False
                self.nested = True
        elif tag == 'img' and self.incell: self.tmpdat += '_Bild_'
        elif self.table is not None:
            if tag == 'tr':
                self.table.append ([])
                self.row += 1
            elif tag == 'td' and self.row >= 0 and not self.incell:
                self.incell = True

    def handle_endtag (self, tag):
        if tag == 'table':
            if self.nested:
                self.tmpdat = self.table
                self.table = self.tmptable.pop()
                self.row = self.tmprow.pop()
                self.nested = False
                self.incell = True
            else:
                self.tablelist.append (self.table)
                self.table = None
                self.row = -1
        elif self.table is not None:
            if tag == 'td' and self.incell:
                if type (self.tmpdat) == str: self.tmpdat = self.tmpdat.strip()
                elif type (self.tmpdat) == list:
                    index = 0
                    for i in self.tmpdat:
                        if type (i) != list:
                            index = self.tmpdat.index (i)
                            break
                    del self.tmpdat [index:]
                self.table [self.row].append (self.tmpdat)
                self.tmpdat = ''
                self.incell = False

    def handle_data (self, data):
        if self.incell: self.tmpdat += data

    def handle_charref (self, name):
        if self.incell: self.tmpdat += chr (int (name))

    def handle_entityref (self, name):
        if self.incell: self.tmpdat += TableRead.chrdict [name]

f = open ('nested.html', 'r')
page = f.read()
f.close()

parser = TableRead()
parser.feed (page)
tables = parser.tables
parser.close()

for table in tables:
    print()
    for row in table: print (row)
