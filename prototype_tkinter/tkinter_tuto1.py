

from tkinter import *
from tkinter import ttk

my_img = PhotoImage(file='drone.png').subsample(35)
ttk.canvas.create_image(10, 10, image=my_img, anchor='nw')


def move(event):
    """Move the sprite image with a d w and s when click them"""
    if event.char == "a":
        canvas.move(my_img, -10, 0)
    elif event.char == "d":
        canvas.move(my_img, 10, 0)
    elif event.char == "w":
        canvas.move(my_img, 0, -10)
    elif event.char == "s":
        canvas.move(my_img, 0, 10)

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

canvas = Canvas(root)
canvas.grid(column=0, row=0, sticky=(N, W, E, S))

root.bind("<Key>", move)
root.mainloop()