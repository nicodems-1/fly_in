import tkinter as tk
from .models import Context, Hub

class MapVisualizer():
    def __init__(self):
        self.root = tk.Tk()
        self.screen_width= self.root.winfo_screenwidth()*0.97
        self.screen_height = self.root.winfo_screenheight()*0.97
        self.img = tk.PhotoImage(file="drone.png").subsample(35)
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, borderwidth=0, highlightthickness=0,
                       bg="white")
        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0
        self.scale = 0
        self.offset_x = 0
        self.offset_y = 0
        self.circle_size = 0

    def spawn_png(self):
        image = self.canvas.create_image(100, 100, anchor=tk.NW, image=self.img)

    def _create_circle(self, x, y, r, **kwargs):
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def setup_map_data(self, context: Context):
        hubs = context.hubs

        self.x_max = max(hub.x for hub in hubs.values())
        self.x_min = min(hub.x for hub in hubs.values())

        self.y_max = max(hub.y for hub in hubs.values())
        self.y_min = min(hub.y for hub in hubs.values())

        dx = (self.x_max - self.x_min) or 1
        dy = (self.y_max - self.y_min) or 1

        scale_x = (self.screen_width / dx)
        scale_y = (self.screen_height / dy)
        full_scale = min(scale_x, scale_y)
        final_scale = full_scale * 0.80
        self.scale = final_scale
        self.circle_size = self.scale/4

        self.offset_x = (self.screen_width - (dx*self.scale))/2
        self.offset_y = (self.screen_height - (dy*self.scale))/2

    def get_x_real_coords(self, x_coords):
        return((x_coords - self.x_min)*self.scale + self.offset_x)

    def get_y_real_coords(self, y_coords):
        return((self.y_max - y_coords)*self.scale + self.offset_y)

    def create_hubs(self, context: Context):
        hubs = context.hubs
        connections = context.connections
        for connection in connections:
            x0 = self.get_x_real_coords(hubs[connection.source].x)
            y0 = self.get_y_real_coords(hubs[connection.source].y)
            x1 = self.get_x_real_coords(hubs[connection.target].x)
            y1 = self.get_y_real_coords(hubs[connection.target].y)
            self.canvas.create_line(x0, y0, x1, y1)
        for hub in hubs.values():
            x = self.get_x_real_coords(hub.x)
            y = self.get_y_real_coords(hub.y)
            self._create_circle(x, y, self.circle_size, fill=hub.metadata.color)
            self.canvas.create_text(x,y - (self.circle_size+10),fill="black",font="Verdana 10 bold",
                            text=hub.name)

    def load_map(self, context):
        self.setup_map_data(context)
        self.canvas.grid()
        self.spawn_png()
        self.create_hubs(context)
        self.root.title("FLY IN")
        self.root.mainloop()