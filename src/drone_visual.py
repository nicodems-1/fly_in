import tkinter as tk
from .models import Context
from tkinter import font
from math import cos, sin

class DroneMoves():
    def __init__(self, moves: list[str], context: Context, canvas, root, my_visual):
        self.moves: list[str] = moves
        self.root = root
        self.context = context
        self.nb_drone = context.nb_drones
        self.img = tk.PhotoImage(file="drone.png").subsample(22)
        self.canvas = canvas
        self.load_map = my_visual
        self.drone_and_hub: dict[tuple(float, float): str] = {} 
        self.label = tk.Label(root, font=('Helvetica 40 bold'), background='green', foreground='white')
        self.label.place(x=50, y=50)
        self.drone_img_ids = {}
    def get_simulation_turn(self, move):
        return(move.split())

    def init_drones(self):
        pass

    def process(self, simulation):
        '''Need to create a dict of type dict[position: list[Drone_id]]'''
        self.drone_and_hub = {}
        radius_drone = 10
        for drone in simulation:
            id, next_hub = drone.split("-")
            x = self.load_map.get_x_real_coords(self.context.hubs[next_hub].x)
            y = self.load_map.get_y_real_coords(self.context.hubs[next_hub].y)
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
                    img_id = self.drone_img_ids[ids]
                else:
                    current_x, current_y = self.canvas.coords(self.drone_img_ids[ids])
                    dx = x - current_x
                    dy = y - current_y
                    self.canvas.move(self.drone_img_ids[ids], dx, dy)

    def tick_function(self, current_index):
        '''process one move from the moves list'''
        if current_index == len(self.moves):
            return
        else:
            simulation = self.get_simulation_turn(self.moves[current_index])
            self.tick_counter(current_index)
            self.process(simulation)
            self.root.after(1000, self.tick_function, current_index + 1)

    def tick_counter(self, current_index):
        self.label['text'] = f"Tick_counter {current_index}"

    def display_drones(self):
        self.tick_function(0)
        '''display the drone in the line '''
        