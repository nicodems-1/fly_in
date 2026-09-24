import tkinter as tk
from .models import Context
from tkinter import font
from math import cos, sin, sqrt, ceil

class DroneMoves():
    def __init__(self, moves: list[str], context: Context, canvas, root, my_visual, circle_size):
        self.circle_size = circle_size
        self.moves: list[str] = moves
        self.root = root
        self.context = context
        self.nb_drone = context.nb_drones
        self.img = tk.PhotoImage(file="drone.png").subsample(self.resize_drone_img())
        self.canvas = canvas
        self.load_map = my_visual
        self.drone_and_hub: dict[tuple(float, float): str] = {} 
        self.label = tk.Label(root, font=('Helvetica 40 bold'), background='green', foreground='white')
        self.label.place(x=50, y=50)
        self.drone_img_ids = {}
        self.current_drone_pos = {}
        self.target_positions = {}

    def get_simulation_turn(self, move):
        return(move.split())

    def resize_drone_img(self)->int:
        width = 2048
        height = 1148
        radius = self.circle_size
        diagonal = sqrt(width**2 + height**2)
        n = ceil(diagonal/(2*radius))
        return n

    def process(self, simulation):
        '''Need to create a dict of type dict[position: list[Drone_id]]'''
        self.drone_and_hub = {}
        for drone in simulation:
            id, target_name = drone.split("-", 1)
            self.current_drone_pos[id] = target_name

        radius_drone = self.circle_size - 5
        self.drone_and_hub = {}
        for id, target_name in self.current_drone_pos.items():
            if target_name in self.context.hubs:
                x = self.load_map.get_x_real_coords(self.context.hubs[target_name].x)
                y = self.load_map.get_y_real_coords(self.context.hubs[target_name].y)
            else:
                conn_obj = next((c for c in self.context.connections if f"{c.source}-{c.target}" == target_name or f"{c.target}-{c.source}" == target_name), None)

                if conn_obj:
                    print("restricted found")
                    x1 = self.load_map.get_x_real_coords(self.context.hubs[conn_obj.source].x)
                    y1 = self.load_map.get_y_real_coords(self.context.hubs[conn_obj.source].y)
                    x2 = self.load_map.get_x_real_coords(self.context.hubs[conn_obj.target].x)
                    y2 = self.load_map.get_y_real_coords(self.context.hubs[conn_obj.target].y)

                    x = (x1 + x2)/2
                    y = (y1 + y2)/2
                else:
                    continue

            if ((x, y) not in self.drone_and_hub):
                self.drone_and_hub.update({(x, y):[id]})
            else:
                self.drone_and_hub[(x, y)].append(id)

        for coords, drone_list in self.drone_and_hub.items():
            center_x, center_y = coords
            total_drone = len(drone_list)
            for index, ids in enumerate(drone_list):
                teta = index * ((2*3.14)/total_drone)
                x = center_x + (radius_drone * cos(teta))
                y = center_y - (radius_drone * sin(teta))
                if ids not in self.drone_img_ids:
                    img_id = self.canvas.create_image(x, y, anchor='center', image=self.img)
                    self.drone_img_ids.update({ids: img_id})
                self.target_positions[ids] = (x, y)

    def animate_step(self, current_step, max_steps, current_index):
        if current_step <= max_steps:
            for ids, target_coords in self.target_positions.items():
                if ids in self.drone_img_ids:
                    target_x, target_y = target_coords
                    current_x, current_y = self.canvas.coords(self.drone_img_ids[ids])
                    frames_left = max_steps - current_step + 1
                    dx = (target_x - current_x) / frames_left
                    dy = (target_y - current_y) / frames_left
                    self.canvas.move(self.drone_img_ids[ids], dx, dy) 
            self.root.after(30, self.animate_step, current_step + 1, max_steps, current_index)
        else:
            self.root.after(300, self.tick_function, current_index + 1)

    def tick_function(self, current_index):
        '''process one move from the moves list'''
        if current_index == len(self.moves):
            return
        else:
            simulation = self.get_simulation_turn(self.moves[current_index])
            self.tick_counter(current_index)
            
            self.target_positions =  {}
            self.process(simulation)
            self.animate_step(1, 30, current_index)

    def tick_counter(self, current_index):
        self.label['text'] = f"Tick_counter {current_index}"

    def display_drones(self):
        start_hub_name = next(hub for hub in self.context.hubs.values() if hub.role == "start_hub").name
        fake_initial_simulation = [f"D{i+1}-{start_hub_name}" for i in range(self.nb_drone)]
        self.process(fake_initial_simulation)
        self.tick_function(0)
        '''display the drone in the line '''
        