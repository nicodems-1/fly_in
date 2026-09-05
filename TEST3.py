from tkinter import Tk, Canvas

root = Tk()
cnv = Canvas(root, width=180, height=100)
cnv.pack()

cnv.create_rectangle(20, 20, 80, 80, fill='red', outline='')

def dessiner(c):
    cnv.create_rectangle(100, 20, 100+c, 20+c, fill='blue', outline='')

cnv.after(1000, dessiner, 42)

root.mainloop()