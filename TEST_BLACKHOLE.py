from tkinter import *
from random import randrange

SIDE=400
root = Tk()
cnv = Canvas(root, width=SIDE, height=SIDE)
cnv.pack()

logo = PhotoImage(file="python.gif")

def action(x, y):
    cnv.create_image((x, y), image=logo)

x, y= randrange(SIDE),randrange(SIDE)
cnv.after(1000, action, x, y)

x, y= randrange(SIDE),randrange(SIDE)
cnv.after(2000, action, x, y)

x, y= randrange(SIDE),randrange(SIDE)
cnv.after(3000, action, x, y)

x, y= randrange(SIDE),randrange(SIDE)
cnv.after(4000, action, x, y)

x, y= randrange(SIDE),randrange(SIDE)
cnv.after(5000, action, x, y)

x, y= randrange(SIDE),randrange(SIDE)
cnv.after(6000, action, x, y)

root.mainloop()