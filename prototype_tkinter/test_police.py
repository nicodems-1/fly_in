import tkinter as tk

root = tk.Tk()

label = tk.Label(
    root,
    text="TEST",
    font=("Arial", 100, "bold"),
    bg="green",
    fg="white"
)

label.pack()

root.mainloop()
