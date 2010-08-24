#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tabellen aus HTML-Dateien einlesen

import sys
import html.parser

def catstrlist (l):
    string = ''
    for s in l: string += s
    return string

class TableRead (html.parser.HTMLParser):
    chrdict = {
        'auml': 'ä',
        'Auml': 'Ä',
        'ouml': 'ö',
        'Ouml': 'Ö',
        'uuml': 'ü',
        'Uuml': 'Ü',
        'szlig': 'ß',
        'quot': '"'
    }

    def __init__ (self):
        html.parser.HTMLParser.__init__ (self)
        self.table = None
        self.lasttable = None
        self.row = -1
        self.col = -1
        self.incell = False
        self.tmpdat = []

    def get_data (self):
        return self.lasttable
    data = property (get_data)

    def handle_starttag (self, tag, attrs):
        if tag == 'table': self.table = []
        elif self.table is not None:
            if tag == 'tr':
                self.table.append ([])
                self.row += 1
            elif tag == 'td' and self.row >= 0 and not self.incell:
                self.incell = True
                self.col += 1

    def handle_endtag (self, tag):
        if tag == 'table':
            self.lasttable = self.table
            self.table = None
        elif self.table is not None:
            if tag == 'td' and self.incell:
                self.table [self.row].append (catstrlist (self.tmpdat).strip())
                self.tmpdat = []
                self.incell = False

    def handle_data (self, data):
        if self.incell: self.tmpdat.append (data)

    def handle_charref (self, name):
        if self.incell: self.tmpdat.append (chr (int (name)))

    def handle_entityref (self, name):
        if self.incell: self.tmpdat.append (TableRead.chrdict [name])

f = open ('index.html', 'r')
page = f.read()
f.close()

parser = TableRead()
parser.feed (page)
table = parser.data
parser.close()

for row in table: print (row)
