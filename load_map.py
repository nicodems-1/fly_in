import random
import tkinter as tk
from typing import Any

from colors_available import colors
from models import Context


class MapVisualizer:
    """Handles the graphical visualization of the map, hubs, and connections.

    Initializes a Tkinter window and canvas,
    calculates coordinate scaling to fit
    the screen, and draws the static map elements.

    Attributes:
        root (tk.Tk): The main Tkinter window.
        screen_width (int): The width of the user's screen.
        screen_height (int): The height of the user's screen.
        canvas (tk.Canvas): The drawing canvas for the map.
        x_min (float): The minimum logical X coordinate among all hubs.
        x_max (float): The maximum logical X coordinate among all hubs.
        y_min (float): The minimum logical Y coordinate among all hubs.
        y_max (float): The maximum logical Y coordinate among all hubs.
        scale (float): The scaling factor to fit the map onto the screen.
        offset_x (float): The horizontal offset to center the map.
        offset_y (float): The vertical offset to center the map.
        circle_radius_size (int):
        The calculated radius for drawing hub circles.
        available_colors (list[str]): A list of valid Tkinter color names.
    """

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

    def _create_circle(self, x: float, y: float,
                       r: float, **kwargs: Any) -> int:
        """Draw a circle on the canvas.

        Args:
            x (float): The X coordinate of the circle's center.
            y (float): The Y coordinate of the circle's center.
            r (float): The radius of the circle.
            **kwargs (Any): Additional keyword arguments for the Tkinter
            create_oval method (e.g., fill color).

        Returns:
            int: The integer ID of the created canvas item.
        """
        return self.canvas.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def setup_map_data(self, context: Context) -> None:
        """Calculate and set the scaling and offset values for the map.

        Determines the bounding box of all hubs and calculates the necessary
        scaling factor (`self.scale`) and offsets
        (`self.offset_x`, `self.offset_y`)
        to fit and center the map on the screen with a safe margin.
        Also calculates
        an appropriate radius for the hub circles.

        Args:
            context (Context): The map context containing the hubs.
        """
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
        self.root.resizable(False, False)

    def get_x_real_coords(self, x_coords: float) -> float:
        """Convert a logical map X coordinate to a physical
        canvas X coordinate.

        Args:
            x_coords (float): The logical X coordinate from the map data.

        Returns:
            float: The scaled and offset X coordinate for the canvas.
        """
        return (x_coords - self.x_min) * self.scale + self.offset_x

    def get_y_real_coords(self, y_coords: float) -> float:
        """Convert a logical map Y coordinate to a physical
        canvas Y coordinate.

        Note that the Y-axis is inverted during conversion so
        that higher logical
        Y values appear higher on the screen (standard Cartesian coordinates),
        unlike Tkinter's default top-left origin.

        Args:
            y_coords (float): The logical Y coordinate from the map data.

        Returns:
            float: The scaled and offset Y coordinate for the canvas.
        """
        return (self.y_max - y_coords) * self.scale + self.offset_y

    def create_hubs(self, context: Context) -> None:
        """Draw the connections and hubs on the canvas.

        Iterates through the context to draw lines representing connections,
        followed by circles and labels representing the hubs. Assigns colors
        based on hub metadata or picks a random color if metadata is invalid
        or missing.

        Args:
            context (Context): The map context containing hubs and connections.
        """
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

            if (
                hub.metadata is not None
                and hub.metadata.color is not None
                and hub.metadata.color in self.available_colors
            ):
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
        """Orchestrate the setup and drawing of the map visualization.

        Calls the necessary setup functions to process map data, render the
        components on the canvas, and set the window title.

        Args:
            context (Context): The parsed map context.

        Returns:
            tuple[tk.Canvas, tk.Tk, float]:
            A tuple containing the canvas object,
                the root window, and the calculated circle radius size.
        """
        self.setup_map_data(context)
        self.canvas.grid()
        self.create_hubs(context)
        self.root.title("FLY IN")
        return (self.canvas, self.root, self.circle_radius_size)
