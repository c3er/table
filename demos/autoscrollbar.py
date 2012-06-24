import tkinter
import tkinter.ttk as ttk

class AutoScrollbar(ttk.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError("cannot use pack with this widget")
    def place(self, **kw):
        raise TclError("cannot use place with this widget")
        
# Usage
#
# create scrolled canvas

root = tkinter.Tk()

vscrollbar = AutoScrollbar(root)
vscrollbar.grid(row = 0, column = 1, sticky = 'n' + 's')
hscrollbar = AutoScrollbar(root, orient = tkinter.HORIZONTAL)
hscrollbar.grid(row = 1, column = 0, sticky = 'e' + 'w')

canvas = tkinter.Canvas(root,
    yscrollcommand = vscrollbar.set,
    xscrollcommand = hscrollbar.set
)
canvas.grid(row = 0, column = 0, sticky = 'news')

vscrollbar.config(command = canvas.yview)
hscrollbar.config(command = canvas.xview)

# make the canvas expandable
root.grid_rowconfigure(0, weight = 1)
root.grid_columnconfigure(0, weight = 1)

#
# create canvas contents

frame = ttk.Frame(canvas)
frame.rowconfigure(1, weight = 1)
frame.columnconfigure(1, weight = 1)

rows = 10
for i in range(1, rows):
    for j in range(1, 10):
        button = tkinter.Button(frame,
            padx = 7,
            pady = 7,
            text = "[%d,%d]" % (i,j)
        )
        button.grid(row = i, column = j, sticky = 'news')

canvas.create_window(0, 0, anchor = 'nw', window = frame)

frame.update_idletasks()

canvas.config(scrollregion = canvas.bbox("all"))

root.mainloop()