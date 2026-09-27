import tkinter as tk
from .models import Context
from math import cos, sin, sqrt, ceil
from .load_map import MapVisualizer


class DroneMoves:
    """Visualizes the movement of a drone fleet on a Tkinter canvas.

    Handles the resizing of drone images, calculation of coordinates for drones 
    at hubs and along connections, and the frame-by-frame animation of their 
    movements throughout the simulation.

    Attributes:
        circle_size (int): The radius size used to calculate
        spacing and image scaling.
        moves (list[str]): The chronological list of move strings representing
        the simulation.
        root (tk.Tk): The root Tkinter window.
        context (Context): The simulation context containing map data, hubs,
        and connections.
        nb_drone (int): The total number of drones in the simulation.
        img (tk.PhotoImage): The loaded and resized drone image asset.
        canvas (tk.Canvas): The Tkinter canvas where drones are drawn.
        load_map (MapVisualizer): The visualizer instance handling
        coordinate translations.
        drone_and_hub (dict[tuple[float, float], list[str]]):
        Mapping of real canvas coordinates to lists of drone IDs.
        label (tk.Label): The UI label displaying the current tick counter.
        drone_img_ids (dict[str, int]):
        Mapping of drone IDs to their Tkinter canvas image IDs.
        current_drone_pos (dict[str, str]):
        Mapping of drone IDs to their current logical target
        (hub or connection name).
        target_positions (dict[str, tuple[float, float]]):
        Mapping of drone IDs to their target (x, y) canvas coordinates.
    """
    def __init__(
        self, moves: list[str], context: Context, canvas: tk.Canvas,
            root: tk.Tk, my_visual: MapVisualizer, circle_size: int) -> None:
        """Initialize the DroneMoves visualizer.

        Args:
            moves (list[str]): The list of simulation steps.
            context (Context): The map and simulation context.
            canvas (tk.Canvas): The canvas to draw the drones on.
            root (tk.Tk): The root UI window.
            my_visual (MapVisualizer): The map visualization handler.
            circle_size (int): The base size for radius calculations.
        """
        self.circle_size: int = circle_size
        self.moves: list[str] = moves
        self.root = root
        self.context = context
        self.nb_drone = context.nb_drones
        self.img = tk.PhotoImage(file="drone.png").subsample(
            self.resize_drone_img())
        self.canvas = canvas
        self.load_map = my_visual
        self.drone_and_hub: dict[tuple[float, float], list[str]] = {}
        self.label = tk.Label(root, font=("Helvetica 40 bold"),
                              background="green", foreground="white")
        self.label.place(x=50, y=50)
        self.drone_img_ids: dict[str, int] = {}
        self.current_drone_pos: dict[str, str] = {}
        self.target_positions: dict[str, tuple[float, float]] = {}

    def get_simulation_turn(self, move: str) -> list[str]:
        """Split a turn string into individual drone move commands.

        Args:
            move (str): A space-separated string of
            drone moves for a single turn.

        Returns:
            list[str]: A list of individual drone move strings.
        """
        return move.split()

    def resize_drone_img(self) -> int:
        """Calculate the subsample factor needed to resize the drone image.

        Computes the scaling factor based on the original image dimensions 
        and the target circle size.

        Returns:
            int: The calculated subsample factor to apply to the image.
        """
        width = 2048
        height = 1148
        radius = self.circle_size
        diagonal = sqrt(width**2 + height**2)
        n = ceil(diagonal / (2 * radius))
        return n

    def process(self, simulation: list[str]) -> None:
        """Process a simulation turn to calculate target canvas coordinates.

        Updates the current logical positions of the drones, determines the real 
        canvas coordinates for those positions (whether at a hub or mid-connection), 
        and calculates distributed circular positions if multiple drones share the 
        same location. Creates canvas image items for new drones.

        Args:
            simulation (list[str]): A list of drone move strings (e.g., 'D1-HubA') for the current turn.
        """
        self.drone_and_hub = {}
        for drone in simulation:
            id, target_name = drone.split("-", 1)
            self.current_drone_pos[id] = target_name

        radius_drone = self.circle_size - 5
        self.drone_and_hub = {}
        for id, target_name in self.current_drone_pos.items():
            if target_name in self.context.hubs:
                x = self.load_map.get_x_real_coords(
                    self.context.hubs[target_name].x)
                y = self.load_map.get_y_real_coords(
                    self.context.hubs[target_name].y)
            else:
                conn_obj = next(
                    (
                        c
                        for c in self.context.connections
                        if f"{c.source}-{c.target}" == target_name
                        or f"{c.target}-{c.source}" == target_name
                    ),
                    None,
                )

                if conn_obj:
                    x1 = self.load_map.get_x_real_coords(
                        self.context.hubs[conn_obj.source].x
                    )
                    y1 = self.load_map.get_y_real_coords(
                        self.context.hubs[conn_obj.source].y
                    )
                    x2 = self.load_map.get_x_real_coords(
                        self.context.hubs[conn_obj.target].x
                    )
                    y2 = self.load_map.get_y_real_coords(
                        self.context.hubs[conn_obj.target].y
                    )

                    x = (x1 + x2) / 2
                    y = (y1 + y2) / 2
                else:
                    continue
            coords = (x, y)
            if coords not in self.drone_and_hub:
                self.drone_and_hub.update({coords: [id]})
            else:
                self.drone_and_hub[coords].append(id)

        for coords, drone_list in self.drone_and_hub.items():
            center_x, center_y = coords
            total_drone = len(drone_list)
            for index, ids in enumerate(drone_list):
                teta = index * ((2 * 3.14) / total_drone)
                if total_drone == 1:
                    x = center_x
                    y = center_y
                else:
                    x = center_x + (radius_drone * cos(teta))
                    y = center_y - (radius_drone * sin(teta))
                if ids not in self.drone_img_ids:
                    img_id = self.canvas.create_image(
                        x, y, anchor="center", image=self.img
                    )
                    self.drone_img_ids.update({ids: img_id})
                self.target_positions[ids] = (x, y)

    def animate_step(self, current_step: int,
                     max_steps: int, current_index: int) -> None:
        """Animate a single step of the drone movement between positions.

        Recursively calls itself using Tkinter's `after` method
        to smoothly interpolate
        drone images toward their target coordinates. Once the maximum steps
        are reached,
        it triggers the next tick function.

        Args:
            current_step (int): The current frame of the animation.
            max_steps (int): The total number of frames for
            the animation sequence.
            current_index (int): The index of the current simulation turn.
        """
        if current_step <= max_steps:
            for ids, target_coords in self.target_positions.items():
                if ids in self.drone_img_ids:
                    target_x, target_y = target_coords
                    current_x, current_y = self.canvas.coords(
                        self.drone_img_ids[ids])
                    frames_left = max_steps - current_step + 1
                    dx = (target_x - current_x) / frames_left
                    dy = (target_y - current_y) / frames_left
                    self.canvas.move(self.drone_img_ids[ids], dx, dy)
            self.root.after(30, self.animate_step,
                            current_step + 1, max_steps, current_index)
        else:
            self.root.after(300, self.tick_function, current_index + 1)

    def tick_function(self, current_index: int) -> None:
        """Process a single simulation turn and trigger its animation sequence.

        If the simulation is not yet complete, increments the tick counter,
        retrieves the current move set, processes the new target coordinates,
        and starts the animation step loop.

        Args:
            current_index (int): The index of the simulation turn to process.
        """
        if current_index == len(self.moves):
            return
        else:
            self.tick_counter(current_index + 1)
            simulation = self.get_simulation_turn(self.moves[current_index])

            self.target_positions = {}
            self.process(simulation)
            self.animate_step(1, 30, current_index)

    def tick_counter(self, current_index: int) -> None:
        """Update the on-screen label displaying the current tick.

        Args:
            current_index (int): The current tick/turn number to display.
        """
        self.label["text"] = f"Tick_counter {current_index}"

    def display_drones(self) -> None:
        """Initialize and start the drone visualization loop.

        Places all drones at the starting hub as a fake initial simulation
        step,
        updates the tick counter to 0, and begins the main tick function loop.
        """
        start_hub_name = next(
            hub for hub in self.context.hubs.values()
            if hub.role == "start_hub"
        ).name
        fake_initial_simulation = [
            f"D{i + 1}-{start_hub_name}" for i in range(self.nb_drone)
        ]
        self.process(fake_initial_simulation)
        self.tick_counter(0)
        self.tick_function(0)
        """display the drone in the line """
