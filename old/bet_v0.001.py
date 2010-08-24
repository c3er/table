#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Gibt den eigenen Quellcode aus

import sys
import html.parser

class TableRead (html.parser.HTMLParser):
    def handle_starttag (self, tag, attrs):
        print ('Start-Tag: ' + tag, attrs, sep = '\t')

    def handle_endtag (self, tag):
        print ('End-Tag:   ' + tag)

    def handle_data (self, data):
        print ('Daten:     ' + data, type (data), sep = '\t')

    def handle_charref(self, name):
        print ('Zeichen:   ' + name, type (name), sep = '\t')

    def handle_entityref (self, name):
        print ('Zeichen:   ' + name, type (name), sep = '\t')

f = open ('../nested.html', 'r')
page = f.read()
f.close()
parser = TableRead()
parser.feed (page)
