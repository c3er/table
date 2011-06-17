#!/usr/bin/env python
# -*- coding: utf-8 -*-

title = 'Tabellenauswerter'
default_addr = 'test.html'
base_addr = 'http://fun2.asianbookie.com/index.cfm?top20=1'

logfile = 'logfile.txt'
asian_exe = 'asian'

tab_file_str = 'Tabellen Dateien'
tab_file_ext = '.tab'

std_error_title = 'Fehler'
std_error_msg = (
    'Die Adresse muss entweder auf eine lokale HTML- oder Tabellen-Datei ' +
    'verweisen oder eine vollständige Adresse zu einer Web-Seite enthalten'
)
file_open_error = 'Datei konnte nicht geöffnet werden\n'
file_save_error = 'Datei konnte nicht gespeichert werden\n'
addr_empty_error = 'Bitte Adresse eingeben\n'
asian_mode_error = 'Asian-Modus gescheitert\n'
asian_exe_error = asian_exe + '.exe konnte nicht aufgerufen werden\n'
web_read_error = 'Web-Seite konnte nicht gelesen werden\n'
wrong_file_started = 'Sie müssen "Tabellenauswerter.py" starten'

new_label = 'Neu'
open_label = 'Öffnen'
save_label = 'Speichern'
save_as_label = 'Speichern unter'
make_tabcols_label = 'Erste Reihe zu Überschriften'
asian_label = 'Asianbookie einlesen'
asian_mode_label = 'Asian-Modus'
addr_label = 'Adresse: '
goto_label = 'Gehe zu'

tab_title = 'Tabelle '
std_col_label = 'Spalte '
std_illegal_label = 'Ungültig'
image_dummy = '<Bild>'

new_session_label = 'Neue Session'
new_session_one_site_title = 'Einzelne Webseite einlesen'
addr_website_label = 'Adresse der Webseite'
base_addr_label = 'Basisadresse'
helper_label = 'Hilfsprogramm benutzen'
open_html_label = 'HTML-Datei öffnen'