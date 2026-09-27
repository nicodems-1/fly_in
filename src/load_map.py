import random
import tkinter as tk
from typing import Any

from .colors_available import colors
from .models import Context


class MapVisualizer:
    def __init__(self) -> None:
        self.root: tk.Tk = tk.Tk()
        self.screen_width: int = self.root.winfo_screenwidth()
        self.screen_height: int = self.root.winfo_screenheight()
        self.canvas: tk.Canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            borderwidth=0,
            highlightthickness=0,
            bg="white",
        )
        self.x_min: float = 0
        self.x_max: float = 0
        self.y_min: float = 0
        self.y_max: float = 0
        self.scale: float = 0.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.circle_radius_size: int = 0
        self.available_colors: list[str] = colors()

    def _create_circle(
        self, x: float, y: float, r: float, **kwargs: Any
    ) -> int:
        return self.canvas.create_oval(
            x - r, y - r, x + r, y + r, **kwargs
        )

    def setup_map_data(self, context: Context) -> None:
        hubs = context.hubs
        safe_margin: int = 100
        self.x_max = max(hub.x for hub in hubs.values())
        self.x_min = min(hub.x for hub in hubs.values())

        self.y_max = max(hub.y for hub in hubs.values())
        self.y_min = min(hub.y for hub in hubs.values())

        true_dx = self.x_max - self.x_min
        true_dy = self.y_max - self.y_min
        scale_dx = true_dx
        scale_dy = true_dy
        if true_dx == 0:
            scale_dx = 1
        if true_dy == 0:
            scale_dy = 1

        scale_x = (self.screen_width - (2 * safe_margin)) / scale_dx
        scale_y = (self.screen_height - (2 * safe_margin)) / scale_dy
        self.scale = min(scale_x, scale_y)
        ideal_size = self.scale / 4
        self.circle_radius_size = int(max(5, min(ideal_size, 40)))
        self.offset_x = (self.screen_width - (true_dx * self.scale)) / 2
        self.offset_y = ((self.screen_height) - (true_dy * self.scale)) / 2

    def get_x_real_coords(self, x_coords: float) -> float:
        return (x_coords - self.x_min) * self.scale + self.offset_x

    def get_y_real_coords(self, y_coords: float) -> float:
        return (self.y_max - y_coords) * self.scale + self.offset_y

    def create_hubs(self, context: Context) -> None:
        hubs = context.hubs
        connections = context.connections

        for connection in connections:
            x0 = self.get_x_real_coords(hubs[connection.source].x)
            y0 = self.get_y_real_coords(hubs[connection.source].y)
            x1 = self.get_x_real_coords(hubs[connection.target].x)
            y1 = self.get_y_real_coords(hubs[connection.target].y)
            self.canvas.create_line(x0, y0, x1, y1, width=3)

        for hub in hubs.values():
            x = self.get_x_real_coords(hub.x)
            y = self.get_y_real_coords(hub.y)

            if (hub.metadata is not None
                and hub.metadata.color is not None
                    and hub.metadata.color in self.available_colors):
                color = hub.metadata.color
            else:
                color = random.choice(self.available_colors)

            self._create_circle(x, y, self.circle_radius_size, fill=color)
            self.canvas.create_text(
                x,
                y - (self.circle_radius_size + 10),
                fill="black",
                font="Verdana 10 bold",
                text=hub.name,
            )

    def load_map(self, context: Context) -> tuple[tk.Canvas, tk.Tk, float]:
        self.setup_map_data(context)
        self.canvas.grid()
        self.create_hubs(context)
        self.root.title("FLY IN")
        return (self.canvas, self.root, self.circle_radius_size)
