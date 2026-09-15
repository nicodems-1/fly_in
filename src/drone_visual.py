import tkinter as tk
from .models import Context

class DroneMoves():
    def __init__(self, moves: list[str], context: Context, canvas, root, my_visual):
        self.moves: list[str] = moves
        self.root = root
        self.context = context
        self.nb_drone = context.nb_drones
        self.img = tk.PhotoImage(file="Rick.png").subsample(9)
        self.canvas = canvas
        self.load_map = my_visual
        self.lbl = tk.Label(self.root, text="1", font=('calibri', 40, 'bold'), background='purple',foreground='white')

    def get_simulation_turn(self, move):
        return(move.split())

    def init_drones(self):
        pass

    def process(self, simulation):
        for drone in simulation:
            _, next_hub = drone.split("-")
            x = self.load_map.get_x_real_coords(self.context.hubs[next_hub].x)
            y = self.load_map.get_y_real_coords(self.context.hubs[next_hub].y)
            image = self.canvas.create_image(x, y, anchor=tk.NW, image=self.img)
            # sleep(1)

    def tick_function(self, current_index):
        '''process one move from the moves list'''
        if current_index == len(self.moves):
            return
        else:
            simulation = self.get_simulation_turn(self.moves[current_index])
            self.process(simulation)
            self.tick_counter(current_index)
            self.root.after(700, self.tick_function, current_index + 1)

    def tick_counter(self, current_index):
        self.lbl.config(text=str(current_index))

    def display_drones(self):
        self.tick_function(0)
        self.root.mainloop()

        '''display the drone in the line '''
        