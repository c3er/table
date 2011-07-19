#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

import threading
import queue

import urllib.request
import urllib.parse

import tkinter
import tkinter.ttk as ttk

import res
import log
import table

from misc import *

Selection = enum (
    'UNKNOWN',
    'ONE_WEBSITE',
    'ONE_WEBSITE_HELPER',
    'LOCAL_FILE',
    'ASIANBOOKIE'
)

# This stuff was originally from some demos ####################################
class _DialogBase (tkinter.Toplevel):
    def __init__ (self, parent, title = None):
        super().__init__ (parent)
        
        self.transient (parent)
        if title:
            self.title (title)
        self.parent = parent
        self.result = None
        
        body = ttk.Frame (self)
        self.initial_focus = self.body (body)
        body.pack (padx = 5, pady = 5)
        
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
            
        self.protocol ("WM_DELETE_WINDOW", self.cancel)
        self.geometry ("+{}+{}".format (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50)
        )
        self.initial_focus.focus_set()
        self.wait_window (self)

    # Methods to overwrite #####################################################
    def body (self, master):
        '''
        Create dialog
        Returns a widget, which should have the focus immediatly. This method
        should be overwritten.
        '''
        pass

    def buttonbox (self):
        '''
        Add standard button box
        Overwrite, if there are no standard buttons wanted.
        '''
        box = ttk.Frame (self)
        
        ttk.Button (box,
            text = "Abbrechen",
            width = 10,
            command = self.cancel
        ).pack (side = 'right', padx = 5, pady = 5)
        
        ttk.Button (box,
            text = "OK",
            width = 10,
            command = self.ok,
            default = tkinter.ACTIVE
        ).pack (side = 'right', padx = 5, pady = 5)
        
        self.bind ("<Return>", self.ok)
        self.bind ("<Escape>", self.cancel)
        box.pack (fill = 'x')

    # Standard button behavior ###
    def ok (self, event = None):
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()

    def cancel (self, event = None):
        # Give focus back to the parent window
        self.parent.focus_set()

        self.destroy()
    ###

    # Command hooks ###
    def validate (self):
        # Overwrite
        return True

    def apply (self):
        # Overwrite
        pass
    ###
    ############################################################################
################################################################################

class NewDialog (_DialogBase):
    def __init__ (self, parent, title = None):
        self.notebook = None
        self.addr_entry = None
        self.base_addr_entry = None
        self.helper_flag = None
        self.selection = None
        self.addr = None

        super().__init__ (parent, title)

    # Helper functions #########################################################
    def open_html (self):
        fname = tkinter.filedialog.askopenfilename (
            filetypes = [('HTML-Dateien', '*.htm;*.html')]
        )
        if fname:
            setentry (self.addr_entry, fname)

    def frame_one_website (self, master):
        page = ttk.Frame (master)
        subpage = ttk.Frame (page)

        top_frame = ttk.Frame (subpage)
        ttk.Label (top_frame,
            text = res.ADDR_WEBSITE_LABEL
        ).pack (side = 'left')
        top_frame.pack (side = 'top', fill = 'x')

        middle_frame = ttk.Frame (subpage)
        self.addr_entry = tkinter.Entry (middle_frame, width = 40)
        self.addr_entry.insert (0, res.DEFAULT_ADDR)
        self.addr_entry.pack (side = 'left')
        self.helper_flag = tkinter.BooleanVar (master)
        ttk.Checkbutton (middle_frame,
            text = res.HELPER_LABEL,
            variable = self.helper_flag
        ).pack (side = 'left')
        middle_frame.pack (side = 'top', fill = 'x')

        bottom_frame = ttk.Frame (subpage)
        ttk.Button (bottom_frame,
            text = res.OPEN_HTML_LABEL,
            command = self.open_html,
        ).pack (side = 'left', pady = 5)
        bottom_frame.pack (side = 'top', fill = 'x')

        subpage.pack (padx = 5, pady = 5)
        return page

    def frame_asianbookie (self, master):
        page = ttk.Frame (master)
        subpage = ttk.Frame (page)

        top_frame = ttk.Frame (subpage)
        ttk.Label (top_frame,
            text = res.BASE_ADDR_LABEL
        ).pack (side = 'left')
        top_frame.pack (side = 'top', fill = 'x')

        bottom_frame = ttk.Frame (subpage)
        self.base_addr_entry = tkinter.Entry (bottom_frame)
        self.base_addr_entry.insert (0, res.BASE_ADDR)
        self.base_addr_entry.pack (fill = 'x')
        bottom_frame.pack (side = 'top', fill = 'x')

        subpage.pack (padx = 5, pady = 5, fill = 'both')
        return page

    @log.logmethod
    def read_asianbookie (self):
        dir = tkinter.filedialog.askdirectory()
        #dir = 'bla'
        
        if dir:
            # self.addr is the base address
            ad = AsianDialog (self.parent, self.addr, dir, res.ASIAN_LABEL)
            self.result = [ad.result]
        else:
            self.cancel()
    ############################################################################

    # Inherited from smpldlg.Dialog ############################################
    def body (self, master):
        self.notebook = ttk.Notebook (master)
        self.notebook.add (self.frame_one_website (master),
            text = res.NEW_SESSION_ONE_SITE_TITLE
        )
        self.notebook.add (self.frame_asianbookie (master),
            text = res.ASIAN_LABEL
        )
        self.notebook.pack (expand = True, fill = 'both', anchor = 'n')

        # Set focus to the address entry
        return self.addr_entry

    def validate (self):
        index = self.notebook.index ('current')
        if index == 0:
            self.addr = self.addr_entry.get()

            if not self.addr:
                error (res.ADDR_EMPTY_ERROR + res.STD_ERROR_MSG)
                return False
            elif self.addr.startswith ('http://'):
                if self.helper_flag.get():
                    self.selection = Selection.ONE_WEBSITE_HELPER
                else:
                    self.selection = Selection.ONE_WEBSITE
            elif self.addr.endswith ('.html') or self.addr.endswith ('.htm'):
                self.selection = Selection.LOCAL_FILE
            else:
                error (res.STD_ERROR_MSG)
                return False
            
            return True
        else:
            self.addr = self.base_addr_entry.get()
            self.selection = Selection.ASIANBOOKIE
            return self.addr == res.BASE_ADDR
        
    def apply (self):
        if self.selection == Selection.ONE_WEBSITE:
            try:
                req = urllib.request.Request (self.addr)
                req.add_header ('User-agent', 'Mozilla/5.0')
                with urllib.request.urlopen (req) as f:
                    page = f.read()
            except urllib.request.URLError as msg:
                error (res.WEB_READ_ERROR + str (msg), msg)
                return
            
        elif self.selection == Selection.ONE_WEBSITE_HELPER:
            try:
                page = cmdcall (res.ASIAN_EXE, self.addr)
            except subprocess.CalledProcessError as msg:
                error (res.ASIAN_MODE_ERROR + str (msg), msg)
                return
            except OSError as msg:
                error (res.ASIAN_EXE_ERROR + str (msg), msg)
                return
            
        elif self.selection == Selection.LOCAL_FILE:
            try:
                with open (self.addr, 'rb') as f:
                    page = f.read()
            except IOError as msg:
                error (res.FILE_OPEN_ERROR + str (msg), msg)
                return False
            
        elif self.selection == Selection.ASIANBOOKIE:
            self.read_asianbookie()
            return
        
        else:
            error (res.STD_ERROR_MSG)
            return
        
        self.result = table.html2tables (page)
        self.result = table.filter_trash (self.result)
    ############################################################################

# Stuff to read in the whole table from Asianbookie ############################
class Event:
    def __init__ (self, stop = False, phase = 0, count = 0, result = None):
        self.stop = stop
        self.phase = phase
        self.count = count
        self.result = result

class AsianWorker (threading.Thread):
    def __init__ (self, workdir, baseaddr):
        super().__init__()
        self.running = True
        self.workdir = workdir
        self.baseaddr = baseaddr
        self.url = None
        self.outqueue = queue.Queue()
        
    def get_event (self):
        try:
            event = self.outqueue.get_nowait()
        except queue.Empty:
            event = None
        return event
    
    event = property (get_event)
    
    def send_event (self, val):
        self.outqueue.put (val)
        
    def request_tables (self, addr):
        page = cmdcall (res.ASIAN_EXE, addr)
        return table.filter_trash (table.html2tables (page))

    def run (self):
        # XXX VERY UGLY
        
        i = 0
        phase = 0
        addr = self.baseaddr
        tab = None
        lasttab = None
        firstloop = True
        
        while self.running:
            if phase == 0:
                if firstloop:
                    firstloop = False
                    tables = self.request_tables (addr)
                    tab = tables [0]
                    tab.make_header()
                    
                    # XXX In der fertigen Version muss die erste (richtige)
                    # Reihe genommen werden...
                    #entry = tab.data [0] [2]
                    entry = tab.lastrow [2]
                    
                    print (entry.data, entry.link)
                    
                    addr = urllib.parse.urljoin (addr, entry.link)
                else:
                    i += 1
                    
                    tables = self.request_tables (addr)
                    tab = tables [1]
                    tab.make_header()
                    
                    entry = tab.data [0] [2]
                    #entry = tab.lastrow [2]
                    
                    print (entry.data, entry.link)
                    
                    if tab != lasttab:
                        tab.dumb (os.path.join (self.workdir, 
                            str (i) + res.TAB_FILE_EXT)
                        )
                        addr = urllib.parse.urljoin (addr, entry.link)
                        self.send_event (Event (phase = phase, count = i))
                    else:
                        phase = 1
                    
                    lasttab = tab
            elif phase == 1:
                tab = None
                nexttab = None
                filelist = os.listdir (self.workdir)
                for f in filelist:
                    if tab is None:
                        tab = table.load (os.path.join (self.workdir, f))
                    else:
                        nexttab = table.load (os.path.join (self.workdir, f))
                        tab.concat (nexttab)
                phase = 2
                self.send_event (Event (result = tab, phase = phase))
                #self.stopworker()
            else:
                self.stopworker()
    
    def stopworker (self):
        self.running = False
        self.send_event (Event (stop = True))

class AsianDialog (_DialogBase):
    def __init__  (self, parent, addr, workdir, title = None):
        self.parent = parent
        self.addr = addr
        self.workdir = workdir
        self.labelvar = tkinter.StringVar()
        self.labelvar.set ('')
        
        self.asianworker = AsianWorker (workdir, addr)
        self.asianworker.start()
        
        parent.after (100, self.update)
        
        super().__init__ (parent, title)

    def buttonbox (self):
        box = ttk.Frame (self)
        
        ttk.Button (box,
            text = "Abbrechen",
            width = 10,
            command = self.stopwork
        ).pack (padx = 5, pady = 5)
        
        self.bind ("<Escape>", self.stopwork)
        box.pack (fill = 'x')
        
    def body (self, master):
        ttk.Label (master, text = res.ASIAN_READING_MSG).pack (side = 'top')
        ttk.Label (master, textvariable = self.labelvar).pack (side = 'top')
        
    def stopwork (self):
        self.asianworker.stopworker()
        self.cancel()
        
    def update (self):
        event = self.asianworker.event
        
        if event is not None:
            print (event.count, event.phase)

            explenation = res.ASIAN_PHASE_EXPLANATION [event.phase]
            if event.phase == 0:
                explenation = explenation.format (event.count + 1)

            phase_str = res.ASIAN_PHASE.format (event.phase + 1)
            self.labelvar.set (phase_str + explenation)
            
            if event.result is not None:
                self.result = event.result
            
            if event.stop:
                self.stopwork()
        
        if event is None or not event.stop:
            self.parent.after (250, self.update)
################################################################################

if __name__ == '__main__':
    error (res.WRONG_FILE_STARTED)
