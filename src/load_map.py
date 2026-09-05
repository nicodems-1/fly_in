import tkinter as tk
from .models import Context, Hub

class MapVisualizer():
    def __init__(self):
        self.root = tk.Tk()
        self.screen_width= self.root.winfo_screenwidth()*0.7
        self.screen_height = self.root.winfo_screenheight()*0.7
        self.img = tk.PhotoImage(file="drone.png").subsample(35)
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, borderwidth=0, highlightthickness=0,
                       bg="white")
        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0
        self.scale = 0

    def spawn_png(self):
        image = self.canvas.create_image(100, 100, anchor=tk.NW, image=self.img)

    def _create_circle(self, x, y, r, **kwargs):
        return self.canvas.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def setup_map_data(self, context: Context):
        hubs = context.hubs
        connections = context.connections

        self.x_max = max([hub.x for hub in hubs.values()])
        self.x_min = min([hub.x for hub in hubs.values()])

        self.y_max = max([hub.y for hub in hubs.values()])
        self.y_min = min([hub.y for hub in hubs.values()])

        dx = (self.x_max - self.x_min) or 1
        dy = (self.y_max - self.y_min) or 1

        scale_x = self.screen_width / dx
        scale_y = self.screen_height / dy
        full_scale = min(scale_x, scale_y)
        padding = (min(scale_x, scale_y)/3)
        final_scale = full_scale - padding
        self.scale = final_scale

    def get_x_real_coords(self, x_coords):
        offset_x = (self.screen_width - ((self.x_max-self.x_min)*self.scale))/2
        return((x_coords - self.x_min)*self.scale + offset_x)

    def get_y_real_coords(self, y_coords):
        offset_y = (self.screen_height - ((self.y_max - self.y_min)*self.scale) + 2 * (self.scale/3))/2
        return((self.y_max - y_coords)*self.scale + offset_y)

    def create_hubs(self, context: Context):
        hubs = context.hubs
        connections = context.connections
        circle_size = self.scale/3
        for connection in connections:
            x0 = self.get_x_real_coords(hubs[connection.source].x)
            y0 = self.get_y_real_coords(hubs[connection.source].y)
            x1 = self.get_x_real_coords(hubs[connection.target].x)
            y1 = self.get_y_real_coords(hubs[connection.target].y)
            self.canvas.create_line(x0, y0, x1, y1)
        for hub in hubs.values():
            x = self.get_x_real_coords(hub.x)
            y = self.get_y_real_coords(hub.y)
            self._create_circle(x, y, circle_size, fill=hub.metadata.color)
            self.canvas.create_text(x,y,fill="white",font="Times 10 italic bold",
                            text=hub.name)

    def load_map(self, context):
        self.setup_map_data(context)
        self.canvas.grid()
        self.spawn_png()
        self.create_hubs(context)
        self.root.title("FLY IN")
        self.root.mainloop()