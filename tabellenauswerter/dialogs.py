﻿#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
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

PAGE_ONE_WEBSITE = 0
PAGE_ASIANBOOKIE = 1
PAGE_TEXTFILE = 2

Selection = enum(
    'UNKNOWN',
    'ONE_WEBSITE',
    'ONE_WEBSITE_HELPER',
    'LOCAL_FILE',
    'ASIANBOOKIE',
    'TEXTFILE',
)

# This stuff was originally from some demos ####################################
class _DialogBase(tkinter.Toplevel):
    def __init__(self, parent, title = None):
        'Must be called after initialization of inheriting classes.'
        
        super().__init__(parent)
        
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.canceled = False
        self.result = None
        
        body = ttk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx = 5, pady = 5)
        
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
            
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+{}+{}".format(
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50)
        )
        self.initial_focus.focus_set()
        self.wait_window(self)
        
    def close(self, event = None):
        '''Give focus back to the parent window and close the dialog.'''
        self.parent.focus_set()
        self.destroy()

    # Methods to overwrite #####################################################
    def body(self, master):
        '''Create dialog
        Returns a widget, which should have the focus immediatly. This method
        should be overwritten.
        '''
        pass

    def buttonbox(self):
        '''Add standard button box
        Overwrite, if there are no standard buttons wanted.
        '''
        box = ttk.Frame(self)
        
        ttk.Button(box,
            text = "Abbrechen",
            width = 10,
            command = self.cancel
        ).pack(side = 'right', padx = 5, pady = 5)
        
        ttk.Button(box,
            text = "OK",
            width = 10,
            command = self.ok,
            default = tkinter.ACTIVE
        ).pack(side = 'right', padx = 5, pady = 5)
        
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack(fill = 'x')

    # Standard button behavior ###
    def ok(self, event = None):
        '''Execute the validate function and if it returns False, it will just
        set the focus right and return.
        If validate returns True, then the apply function will be called and the
        dialog will be closed.
        '''
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.close()

    def cancel(self, event = None):
        '''Performs an Abortion of the dialog.'''
        self.canceled = True
        self.close(event)
    ###

    # Command hooks ###
    def validate(self):
        '''Overwrite.
        Validate the input. If the function returns false, the dialog will stay
        open.
        '''
        return True

    def apply(self):
        '''Overwrite.
        Process the input. This function will be called, after the dialog was
        closed.
        '''
        pass
    ###
    ############################################################################
################################################################################

class NewDialog(_DialogBase):
    TEXTBOX_WIDTH = 40
    
    def __init__(self, parent, title = None):
        self.notebook = None
        self.addr_entry = None
        self.base_addr_entry = None
        self.textfile_entry = None
        self.helper_flag = None
        self.selection = None
        self.addr = None

        super().__init__(parent, title)

    # Helper functions #########################################################
    @staticmethod
    def open_file(file_str, file_ext, entry):
        fname = tkinter.filedialog.askopenfilename (
            filetypes = [(file_str, file_ext)]
        )
        if fname:
            setentry(entry, fname)
    
    def open_html(self):
        self.open_file(res.HTML_FILE_STR, res.HTML_FILE_EXT, self.addr_entry)
            
    def open_textfile(self):
        self.open_file(
            res.TEXT_FILE_STR,
            res.TEXT_FILE_EXT,
            self.textfile_entry
        )
    ############################################################################

    # Definition of the appearence #############################################
    def frame_one_website(self, master):
        page = ttk.Frame(master)
        subpage = ttk.Frame(page)

        ########################################################################
        top_frame = ttk.Frame(subpage)
        ttk.Label(top_frame, text = res.ADDR_WEBSITE_LABEL).pack(side = 'left')
        top_frame.pack(side = 'top', fill = 'x')
        ########################################################################

        ########################################################################
        middle_frame = ttk.Frame(subpage)
        
        self.addr_entry = tkinter.Entry(middle_frame,
            width = self.TEXTBOX_WIDTH
        )
        self.addr_entry.insert(0, res.DEFAULT_ADDR)
        self.addr_entry.pack(side = 'left')
        
        self.helper_flag = tkinter.BooleanVar(master)
        ttk.Checkbutton(middle_frame,
            text = res.HELPER_LABEL,
            variable = self.helper_flag
        ).pack(side = 'left')
        
        middle_frame.pack(side = 'top', fill = 'x')
        ########################################################################

        ########################################################################
        bottom_frame = ttk.Frame(subpage)
        ttk.Button(bottom_frame,
            text = res.OPEN_HTML_LABEL,
            command = self.open_html,
        ).pack(side = 'left', pady = 5)
        bottom_frame.pack(side = 'top', fill = 'x')
        ########################################################################

        subpage.pack(padx = 5, pady = 5)
        return page

    def frame_asianbookie(self, master):
        page = ttk.Frame(master)
        subpage = ttk.Frame(page)

        top_frame = ttk.Frame(subpage)
        ttk.Label(top_frame, text = res.BASE_ADDR_LABEL).pack(side = 'left')
        top_frame.pack(side = 'top', fill = 'x')

        bottom_frame = ttk.Frame(subpage)
        self.base_addr_entry = tkinter.Entry(bottom_frame)
        self.base_addr_entry.insert(0, res.BASE_ADDR)
        self.base_addr_entry.pack(fill = 'x')
        bottom_frame.pack(side = 'top', fill = 'x')

        subpage.pack(padx = 5, pady = 5, fill = 'both')
        return page
    
    def frame_textfile(self, master):
        page = ttk.Frame(master)
        subpage = ttk.Frame(page)
        
        top_frame = ttk.Frame(subpage)
        ttk.Label(top_frame, text = res.FILEPATH_LABEL).pack(side = 'left')
        top_frame.pack(side = 'top', fill = 'x')
        
        middle_frame = ttk.Frame(subpage)
        self.textfile_entry = tkinter.Entry(middle_frame)
        self.textfile_entry.pack(fill = 'x')
        middle_frame.pack(side = 'top', fill = 'x')
        
        bottom_frame = ttk.Frame(subpage)
        ttk.Button(bottom_frame,
            text = res.BROWSE_LABEL,
            command = self.open_textfile,
        ).pack(side = 'left', pady = 5)
        bottom_frame.pack(side = 'top', fill = 'x')
        
        subpage.pack(padx = 5, pady = 5, fill = 'both')
        return page
    ############################################################################

    @log.logmethod
    def read_asianbookie(self):
        path = tkinter.filedialog.askdirectory()
        
        if path:
            # "self.addr" is the base address
            ad = AsianDialog(self.parent, self.addr, path, res.ASIAN_LABEL)
            self.result = [ad.result] if ad.result is not None else None
        else:
            self.cancel()
    ############################################################################

    # Inherited from _DialogBase ###############################################
    def body(self, master):
        self.notebook = ttk.Notebook(master)
        self.notebook.add(self.frame_one_website(master),
            text = res.NEW_SESSION_ONE_SITE_TITLE
        )
        self.notebook.add(self.frame_asianbookie(master),
            text = res.ASIAN_LABEL
        )
        self.notebook.add(self.frame_textfile(master),
            text = res.IMPORT_TEXTFILE_LABEL
        )
        self.notebook.pack(expand = True, fill = 'both', anchor = 'n')

        # Set focus to the address entry
        return self.addr_entry

    def validate(self):
        index = self.notebook.index('current')
        if index == PAGE_ONE_WEBSITE:
            self.addr = self.addr_entry.get()

            if not self.addr:
                error(res.ADDR_EMPTY_ERROR + res.STD_ERROR_MSG)
                return False
            elif self.addr.startswith('http://'):
                if self.helper_flag.get():
                    self.selection = Selection.ONE_WEBSITE_HELPER
                else:
                    self.selection = Selection.ONE_WEBSITE
            else:
                fname = self.addr.lower()
                if fname.endswith('.html') or fname.endswith('.htm'):
                    self.selection = Selection.LOCAL_FILE
                else:
                    error(res.STD_ERROR_MSG)
                    return False
            
            return True
        elif index == PAGE_ASIANBOOKIE:
            self.addr = self.base_addr_entry.get()
            self.selection = Selection.ASIANBOOKIE
            return True
        elif index == PAGE_TEXTFILE:
            # ...
            self.selection = Selection.TEXTFILE
            return True
        else:
            error(res.STD_ERROR_MSG)
            return False
        
    def apply(self):
        if self.selection == Selection.ONE_WEBSITE:
            try:
                req = urllib.request.Request(self.addr)
                req.add_header('User-agent', 'Mozilla/5.0')
                with urllib.request.urlopen(req) as f:
                    page = f.read()
            except urllib.request.URLError as msg:
                error(res.WEB_READ_ERROR + str(msg), msg)
                return
            
        elif self.selection == Selection.ONE_WEBSITE_HELPER:
            try:
                page = cmdcall(res.ASIAN_EXE, self.addr)
            except subprocess.CalledProcessError as msg:
                error(res.ASIAN_MODE_ERROR + str(msg), msg)
                return
            except OSError as msg:
                error(res.ASIAN_EXE_ERROR + str(msg), msg)
                return
            
        elif self.selection == Selection.LOCAL_FILE:
            try:
                with open(self.addr, 'rb') as f:
                    page = f.read()
            except IOError as msg:
                error(res.FILE_OPEN_ERROR + str(msg), msg)
                return
            
        elif self.selection == Selection.ASIANBOOKIE:
            self.read_asianbookie()
            return
        
        elif self.selection == Selection.TEXTFILE:
            # ...
            return
        
        else:
            error(res.STD_ERROR_MSG)
            return
        
        self.result = table.html2tables(page)
        self.result = table.filter_trash(self.result)
    ############################################################################

# Stuff to read in the whole table from Asianbookie ############################
class DataToken:
    def __init__(self, result = None, phase = 0, count = 0):
        self.result = result
        self.phase = phase
        self.count = count

class Event:
    def __init__(self, data = None, stop = False, exc = None):
        self.data = data
        self.stop = stop
        self.exc = exc

class AsianWorker(threading.Thread):
    def __init__(self, workdir, baseaddr):
        super().__init__()
        self._running = True
        self.running_mutex = threading.Lock()
        self.workdir = workdir
        self.baseaddr = baseaddr
        self.outqueue = queue.Queue()
        
    # Properties ###############################################################
    def get_event(self):
        return self.get_elem(self.outqueue)
    
    def get_running(self):
        self.running_mutex.acquire()
        val = self._running
        self.running_mutex.release()
        return val
    
    def set_running(self, val):
        self.running_mutex.acquire()
        self._running = val
        self.running_mutex.release()
    
    event = property(get_event)
    running = property(get_running, set_running)
    ############################################################################
    
    # For internal use #########################################################
    def get_elem(self, q):
        try:
            elem = q.get_nowait()
        except queue.Empty:
            elem = None
        return elem
    
    def send_event(self, data = None, stop = False, exc = None):
        self.outqueue.put(Event(data, stop, exc))
        
    def request_tables(self, addr):
        page = cmdcall(res.ASIAN_EXE, '"' + addr + '"')
        return table.filter_trash(table.html2tables(page))
        
    def do_work(self):
        # XXX VERY UGLY!!!
        
        i = 0
        phase = 0
        addr = self.baseaddr
        tab = None
        lasttab = None
        firstloop = True
        row_offset = 1
        
        while self.running:
            if phase == 0:
                if firstloop:
                    firstloop = False
                    tables = self.request_tables(addr)
                    tab = tables[1]
                    tab.make_header()
                    
                    # XXX In der fertigen Version muss die erste (richtige)
                    # Reihe genommen werden...
                    entry = tab.data[0][1]
                    #entry = tab.lastrow[1]
                    
                    print('Phase 0')
                    print(entry.data, entry.link)
                    
                    addr = urllib.parse.urljoin(addr, entry.link)
                else:
                    i += 1
                    
                    print('Requesting tables')
                    tables = self.request_tables(addr)
                    print('Tables requested')
                    
                    if len(tables) > 1 and len(tables[1].data[0]) > 2:
                        row_offset = 1
                        
                        for tab in tables:
                            print(tab, end = '\n\n')
                        
                        lasttab = tab
                        
                        # XXX Even more ugly!!!
                        # The usage of the (self written) helper program
                        # must be reworked!!!
                        succeeded = False
                        counter = 0
                        while not succeeded:
                            succeeded = False
                            try:
                                #if len(tables[1].data[0]) > 2:
                                tab = tables[1]
                                succeeded = True
                                counter = 0
                            except IndexError:
                                succeeded = False
                                print(
                                    'XXXX IndexError',
                                    counter,
                                    file = sys.stderr
                                )
                            if not succeeded:
                                counter += 1
                                tables = self.request_tables(addr)
                    
                        tab.make_header()
                    else:
                        row_offset += 1
                        
                    entry = tab.data[len(tab.data) - row_offset][1]
                    
                    '''try:
                        lasttab = tab
                        tab = tables[1]
                        tab.make_header()
                        #print(tab)
                        entry = tab.data[0][1]
                    except IndexError:
                        tab = lasttab'''
                    
                    print(entry.data, entry.link)
                    
                    if tab != lasttab and entry.link:
                        tab.dumb(os.path.join(
                            self.workdir, 
                            str(i) + res.TAB_FILE_EXT)
                        )
                        addr = urllib.parse.urljoin(addr, entry.link)
                        print(addr)
                        self.send_event(
                            data = DataToken(phase = phase, count = i)
                        )
                    else:
                        print(tab != lasttab, bool(entry.link))
                        phase = 1
                        print(phase)
            elif phase == 1:
                tab = None
                nexttab = None
                filelist = os.listdir(self.workdir)
                for f in filelist:
                    path = os.path.join(self.workdir, f)
                    if tab is None:
                        tab = table.load(path)
                    else:
                        nexttab = table.load(path)
                        tab.concat(nexttab)
                phase = 2
                self.send_event(data = DataToken(result = tab, phase = phase))
            else:
                self.stopworker()
    
    def run(self):
        try:
            self.do_work()
        except Exception as exc:
            self.send_event(stop = True, exc = exc)
            raise exc
    ############################################################################
    
    def stopworker(self):
        self.running = False
        self.send_event(stop = True)

class AsianDialog(_DialogBase):
    def __init__(self, parent, addr, workdir, title = None):
        self.parent = parent
        self.addr = addr
        self.workdir = workdir
        self.labelvar = tkinter.StringVar()
        self.labelvar.set('')
        
        self.asianworker = AsianWorker(workdir, addr)
        self.asianworker.start()
        
        parent.after(100, self.worker_handler)
        
        super().__init__(parent, title)

    def buttonbox(self):
        box = ttk.Frame(self)
        
        ttk.Button(box,
            text = "Abbrechen",
            width = 10,
            command = self.stopwork
        ).pack(padx = 5, pady = 5)
        
        self.bind("<Escape>", self.stopwork)
        box.pack(fill = 'x')
        
    def body(self, master):
        ttk.Label(master, text = res.ASIAN_READING_MSG).pack(side = 'top')
        ttk.Label(master, textvariable = self.labelvar).pack(side = 'top')
        
    def stopwork(self):
        self.asianworker.stopworker()
        self.cancel()
        
    def update(self, data):
        print(data.count, data.phase)

        explenation = res.ASIAN_PHASE_EXPLANATION[data.phase]
        if data.phase == 0:
            explenation = explenation.format(data.count + 1)

        phase_str = res.ASIAN_PHASE.format(data.phase + 1)
        self.labelvar.set(phase_str + explenation)
        
        if data.result is not None:
            self.result = data.result
        
    def worker_handler(self):
        event = self.asianworker.event
        
        if event is not None:
            if event.data is not None:
                self.update(event.data)
            if event.exc is not None:
                tkinter.messagebox.showerror(
                    res.TITLE,
                    res.ASIANBOOKIE_ERROR + str(event.exc)
                )
                self.stopwork()
            if event.stop:
                self.stopwork()
        
        if event is None or not event.stop:
            self.parent.after(100, self.worker_handler)
################################################################################

if __name__ == '__main__':
    error(res.WRONG_FILE_STARTED)
