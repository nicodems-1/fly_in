# Source - https://stackoverflow.com/a/34029360
# Posted by furas
# Retrieved 2026-09-16, License - CC BY-SA 3.0

import tkinter as tk

def countdown(count):
    # change text in label        
    label['text'] = count

    if count > 0:
        # call countdown again after 1000ms (1s)
        root.after(1000, countdown, count-1)

root = tk.Tk()

label = tk.Label(root)
label.place(x=35, y=15)

# call countdown first time    
countdown(5)
# root.after(0, countdown, 5)

root.mainloop()
