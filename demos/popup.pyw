from tkinter import *
import tkinter.messagebox

###########################
def senden():
    tkinter.messagebox.showinfo('Senden','May be later!')

def verbinde():
    tkinter.messagebox.showinfo('Verbinde','May be later!')

def info():
    import sys
    py_ver = sys.version    ## Python-Version testen . . .
    python_version = py_ver[0:3]
    major = python_version[0]
    minor = python_version[2]
    tkinter.messagebox.showinfo('Info','Popup-Men\xfc-Demo!')
    

def ende():
    root.destroy()

###########################
def popupMenu(event):     
    popup.post(event.x_root, event.y_root) 
    
############################
## MAIN - Hauptprogramm
############################
root = Tk()
root.title('Popup-Menue-Demo')

foben = Frame(root,width=500) 
foben.pack(expand=YES, fill=BOTH) 

textfenster = Text(foben,width=90)
textfenster.pack(fill=BOTH,expand=YES)

popup = Menu(foben,tearoff=0)
popup.add_command(label='Info', command=info)
popup.add_separator()
popup.add_command(label='Beenden', command=ende)    

funten = Frame(root,width=500) 
funten.pack(side=BOTTOM,expand=YES, fill=BOTH) 


eingabe = Entry(funten,width=60)
eingabe.pack(side=LEFT,fill=BOTH,expand=YES)

but1 = Button(funten,text='Senden', command = senden)
but1.pack(side = LEFT,expand=NO)

but2 = Button(funten,text='Verbinden', command = verbinde)
but2.pack(side = LEFT,expand=NO)

but3 = Button(funten,text='Info', command = info)
but3.pack(side = LEFT,expand=NO)

but4 = Button(funten,text='Beenden', command = ende)
but4.pack(side = LEFT,expand=NO)

textfenster.bind('<Button-3>',popupMenu)

textfenster.insert(END,'Versuche die rechte Maustaste im Textfenster!\n')

root.mainloop()
