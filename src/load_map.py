import tkinter as tk
from .models import Context, Hub

class MapVisualizer():
    def __init__(self):
        self.root = tk.Tk()
        self.screen_width= self.root.winfo_screenwidth()*0.7
        self.screen_height = self.root.winfo_screenheight()*0.7
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, borderwidth=0, highlightthickness=0,
                       bg="white")

    def _create_circle(self, x, y, r, **kwargs):
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def create_hubs(self, context: Context):
        hubs = context.hubs
        connections = context.connections
        x_max = max([hub.x for hub in hubs.values()])
        x_min = min([hub.x for hub in hubs.values()])
        y_max = max([hub.y for hub in hubs.values()])
        y_min = min([hub.y for hub in hubs.values()])
        print(f"screen height    {self.screen_height}")
        print(f"screen width    {self.screen_width}")

        dx = (x_max - x_min) or 1
        dy = (y_max - y_min) or 1
        scale_x = self.screen_width / dx
        scale_y = self.screen_height / dy

        scale = min(scale_x, scale_y) - (min(scale_x, scale_y)/3)
        print(scale)
        circle_size = scale/3
        offset_x = (self.screen_width - (dx*scale))/2
        offset_y = (self.screen_height - (dy*scale) + 2 * circle_size)/2
        for connection in connections:
            x0 = ((hubs[connection.source].x) - x_min)*scale + offset_x
            y0 = (y_max - (hubs[connection.source].y))*scale + offset_y
            x1 = ((hubs[connection.target].x) - x_min)*scale + offset_x
            y1 = (y_max - (hubs[connection.target].y))*scale + offset_y
            self.canvas.create_line(x0, y0, x1, y1)
        for hub in hubs.values():
            x = (hub.x - x_min)*scale + offset_x
            y = (y_max - hub.y)*scale + offset_y
            self._create_circle(x, y, circle_size, fill=hub.metadata.color)
            self.canvas.create_text(x,y,fill="white",font="Times 10 italic bold",
                            text=hub.name)

    def load_map(self, context):
        self.canvas.grid()
        self.create_hubs(context)
        self.root.title("FLY IN")
        self.root.mainloop()