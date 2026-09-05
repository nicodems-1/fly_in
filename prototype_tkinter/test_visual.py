try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

root = tk.Tk()
screen_width= root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
canvas = tk.Canvas(root, width=screen_width*0.7, height=screen_height*0.7, borderwidth=0, highlightthickness=0,
                   bg="white")
canvas.grid()

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
tk.Canvas.create_circle = _create_circle

'''create a map with line as links and circle as hub'''
canvas.create_line(400, 400, 600, 400, width=3)
canvas.create_line(400, 400, 800, 400, width=3)
canvas.create_line(400, 400, 1000, 400, width=3)
canvas.create_line(400, 400, 1000, 100, width=3)
canvas.create_rectangle(120, 450, 450, 789)
circle_size = 70;
outline_with = circle_size/10;
canvas.create_circle(400, 400, circle_size, fill="green", outline="blue", width=outline_with)
canvas.create_circle(600, 400, circle_size, fill="blue", outline="blue")
canvas.create_circle(800, 400, circle_size, fill="blue", outline="blue")
canvas.create_circle(1000, 400, circle_size, fill="red", outline="blue")
canvas.create_circle(1000, 100, circle_size, fill="red", outline="blue")
root.title("TITRE")
root.mainloop()
