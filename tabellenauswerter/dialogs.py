#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import urllib.request

import tkinter
import tkinter.ttk as ttk

import res
import log
import table

from misc import *

# Normally, this constant should be defined in subprocess.
# Needed to hide the console window, which would appear under Windows by calling
# an external command line program.
STARTF_USESHOWWINDOW = 1

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
        '''Create dialog
        Returns a widget, which should have the focus immediatly. This method
        should be overwritten.'''
        pass

    def buttonbox (self):
        '''Add standard bottun box
        Overwrite, if there are no standard buttons wanted.'''
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

    # Standard button behavior
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

    # Command hooks
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
            text = res.addr_website_label
        ).pack (side = 'left')
        top_frame.pack (side = 'top', fill = 'x')

        middle_frame = ttk.Frame (subpage)
        self.addr_entry = tkinter.Entry (middle_frame, width = 40)
        self.addr_entry.insert (0, res.default_addr)
        self.addr_entry.pack (side = 'left')
        self.helper_flag = tkinter.BooleanVar (master)
        ttk.Checkbutton (middle_frame,
            text = res.helper_label,
            variable = self.helper_flag
        ).pack (side = 'left')
        middle_frame.pack (side = 'top', fill = 'x')

        bottom_frame = ttk.Frame (subpage)
        ttk.Button (bottom_frame,
            text = res.open_html_label,
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
            text = res.base_addr_label
        ).pack (side = 'left')
        top_frame.pack (side = 'top', fill = 'x')

        bottom_frame = ttk.Frame (subpage)
        self.base_addr_entry = tkinter.Entry (bottom_frame)
        self.base_addr_entry.insert (0, res.base_addr)
        self.base_addr_entry.pack (fill = 'x')
        bottom_frame.pack (side = 'top', fill = 'x')

        subpage.pack (padx = 5, pady = 5, fill = 'both')
        return page

    @log.logmethod
    def read_one_website (self):
        addr = self.addr_entry.get()

        if not addr:
            error (res.addr_empty_error + res.std_error_msg)
            return False
        elif addr.startswith ('http://'):
            if self.helper_flag.get():
                try:
                    # Hide the console window, which would appear under Windows
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= STARTF_USESHOWWINDOW
                    
                    # Do the actual call
                    page = subprocess.check_output ([res.asian_exe, addr],
                        startupinfo = startupinfo
                    )
                except subprocess.CalledProcessError as msg:
                    error (res.asian_mode_error + str (msg), msg)
                    return False
                except OSError as msg:
                    error (res.asian_exe_error + str (msg), msg)
                    return False
            else:
                try:
                    req = urllib.request.Request (addr)
                    req.add_header ('User-agent', 'Mozilla/5.0')
                    with urllib.request.urlopen (req) as f:
                        page = f.read()
                except urllib.request.URLError as msg:
                    error (res.web_read_error + str (msg), msg)
                    return False
        elif addr.endswith ('.html') or addr.endswith ('.htm'):
            try:
                with open (addr, 'rb') as f:
                    page = f.read()
            except IOError as msg:
                error (res.file_open_error + str (msg), msg)
                return False
        else:
            error (res.std_error_msg)
            return False

        self.result = table.html2tables (page)
        table.filter_trash (self.result)
        return True

    @log.logmethod
    def read_asianbookie (self):
        tkinter.messagebox.showinfo ('Hallo', res.asian_label)
        return True
    ############################################################################

    # Inherited from smpldlg.Dialog ############################################
    def body (self, master):
        self.notebook = ttk.Notebook (master)
        self.notebook.add (self.frame_one_website (master),
            text = res.new_session_one_site_title
        )
        self.notebook.add (self.frame_asianbookie (master),
            text = res.asian_label
        )
        self.notebook.pack (expand = True, fill = 'both', anchor = 'n')

        # Set focus to the address entry
        return self.addr_entry

    def validate (self):
        index = self.notebook.index ('current')
        if index == 0:
            return self.read_one_website()
        else:
            return self.read_asianbookie()
    ############################################################################

if __name__ == '__main__':
    error (res.wrong_file_started)
