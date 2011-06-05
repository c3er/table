import tkinter

root = tkinter.Tk()

tkinter.Button (root, text = 'Bla').pack()

tkinter.Label (root,
    text = 'Right-click to display menu',
    width = 40,
    height = 20
).pack()

# create a menu
popup = tkinter.Menu (root, tearoff = 0)
popup.add_command (label = 'Next') # , command=next) etc...
popup.add_command (label = 'Previous')
popup.add_separator()
popup.add_command (label = 'Home')

def do_popup (event):
    # display the popup menu
    try:
        popup.post (event.x_root, event.y_root)
    finally:
        # make sure to release the grab (Tk 8.0a1 only)
        popup.grab_release()
    print (event.__dict__)

root.bind ('<Button-3>', do_popup)

tkinter.Button (root, text = 'Quit', command = root.destroy).pack()

root.mainloop()
