import tkinter as tk
from .models import Context
from tkinter import font

class DroneMoves():
    def __init__(self, moves: list[str], context: Context, canvas, root, my_visual):
        self.moves: list[str] = moves
        self.root = root
        self.context = context
        self.nb_drone = context.nb_drones
        self.img = tk.PhotoImage(file="drone.png").subsample(30)
        self.canvas = canvas
        self.load_map = my_visual
        self.droneid_png: dict[id, png_id] = {}
        self.label = tk.Label(root, font=('Helvetica 40 bold'), background='green', foreground='white')
        self.label.place(x=50, y=50)
    def get_simulation_turn(self, move):
        return(move.split())

    def init_drones(self):
        pass

    def process(self, simulation):
        '''Need to know the last img pos to calculate the lenght of movment needeed'''
        for drone in simulation:
            id, next_hub = drone.split("-")
            x_target = self.load_map.get_x_real_coords(self.context.hubs[next_hub].x)
            y_target = self.load_map.get_y_real_coords(self.context.hubs[next_hub].y)
            if id not in self.droneid_png:
                img_id = self.canvas.create_image(x_target, y_target, anchor='center', image=self.img)
                self.droneid_png.update({id: img_id})
            else:
                img_id = self.droneid_png[id]
                current_x, current_y = self.canvas.coords(img_id)
                dx = x_target - current_x
                dy = y_target - current_y
                self.canvas.move(img_id, dx, dy)

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
        