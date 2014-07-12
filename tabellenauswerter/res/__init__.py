#!/usr/bin/env python
# -*- coding: utf-8 -*-

TITLE = 'Tabellenauswerter'
DEFAULT_ADDR = 'test-data/test.html'
BASE_ADDR = 'http://fun2.asianbookie.com/index.cfm?top20=1'

LOGFILE = 'logfile.txt'
ASIAN_EXE = 'asian'

TAB_FILE_STR = 'Tabellen Dateien'
TAB_FILE_EXT = '.table'

HTML_FILE_STR = 'HTML-Dateien'
HTML_FILE_EXT = '*.htm;*.html'

UNKNOWN_FILE = 'Unbekannt'

STD_ERROR_TITLE = 'Fehler'
STD_ERROR_MSG = (
    'Die Adresse muss entweder auf eine lokale HTML- oder Tabellen-Datei ' +
    'verweisen oder eine vollständige Adresse zu einer Web-Seite enthalten'
)
FILE_OPEN_ERROR = 'Datei konnte nicht geöffnet werden\n'
FILE_SAVE_ERROR = 'Datei konnte nicht gespeichert werden\n'
FILE_READ_ERROR = 'Konnte Datei nicht lesen'
ADDR_EMPTY_ERROR = 'Bitte Adresse eingeben\n'
ASIAN_MODE_ERROR = 'Asian-Modus gescheitert\n'
ASIAN_EXE_ERROR = ASIAN_EXE + '.exe konnte nicht aufgerufen werden\n'
WEB_READ_ERROR = 'Web-Seite konnte nicht gelesen werden\n'
WRONG_FILE_STARTED = 'Sie müssen "Tabellenauswerter.py" starten'
SESSION_NOTEBOOK_ERROR = (
    'There is no Notebook element, where a table could be selected'
)
NO_TABLE_ERROR = 'Es konnte keine Tabelle erkannt werden'
ASIANBOOKIE_ERROR = 'Asianbookie konnte nicht eingelesen werden.\n'

SAVE_TABLE_TITLE = 'Tabelle speichern'
SAVE_TABLE_QUESTION = 'Soll die Tabelle "{}" gespeichert werden?'

NEW_LABEL = 'Neu'
OPEN_LABEL = 'Öffnen'
SAVE_LABEL = 'Speichern'
SAVE_AS_LABEL = 'Speichern unter'
MAKE_TABCOLS_LABEL = 'Erste Reihe zu Überschriften'
MERGE_TABLES_LABEL = 'Mit weiterer Tabelle verschmelzen'
ASIAN_LABEL = 'Asianbookie einlesen'
ADDR_LABEL = 'Adresse: '
GOTO_LABEL = 'Gehe zu'

TAB_TITLE = 'Tabelle '
STD_COL_LABEL = 'Spalte '
STD_ILLEGAL_LABEL = 'Ungültig'
IMAGE_DUMMY = '<Bild>'

NEW_SESSION_LABEL = 'Neue Session'
NEW_SESSION_ONE_SITE_TITLE = 'Einzelne Webseite einlesen'
ADDR_WEBSITE_LABEL = 'Adresse der Webseite'
BASE_ADDR_LABEL = 'Basisadresse'
HELPER_LABEL = 'Hilfsprogramm benutzen'
OPEN_HTML_LABEL = 'HTML-Datei öffnen'

# Asianbookie specific #########################################################
ASIAN_READING_MSG = '''Asianbookie wird eingelesen.

Diese Operation kann eine Weile dauern. Wenn es abgebrochen wird,
muss es wieder von vorne angefangen werden!'''

ASIAN_PHASE = 'Phase {} von 2:\n'
ASIAN_PHASE_EXPLANATION = (
    'Seite {} wird eingelesen',
    'Tabelle wird zusammengefügt',
    'Ende'
)
################################################################################