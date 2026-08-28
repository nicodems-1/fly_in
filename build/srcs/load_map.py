import tkinter as tk
from models import Context, Hub

class MapVisualizer():
    def __init__(self):
        self.root = tk.Tk()
        screen_width= self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.canvas = tk.Canvas(self.root, width=screen_width*0.7, height=screen_height*0.7, borderwidth=0, highlightthickness=0,
                       bg="white")

    def _create_circle(self, x, y, r, **kwargs):
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def create_hubs(self, context: Context):
        hubs = context.hubs
        for hub in hubs.values():
            self._create_circle(hub.x*100 + 100, hub.y*100 + 300, 30)

    def load_map(self, context):
        self.canvas.grid()
        self.create_hubs(context)
        self.root.title("FLY IN")
        self.root.mainloop()