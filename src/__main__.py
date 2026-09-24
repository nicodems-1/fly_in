from .parser import parsing
from .models import Context
from .load_map import MapVisualizer
from .path_finder import PathFinder
from .drone_fleet_handler import DronesFleetHandler
from .drone_visual import DroneMoves

print("Program initialization debug")
my_context = parsing("maps/medium/01_dead_end_trap.txt")
my_visual = MapVisualizer()
dfh = DronesFleetHandler(my_context)
canvas, root, circle_radius_size = my_visual.load_map(my_context)
moves = dfh.handle_drones(my_context.nb_drones)
drone_visual = DroneMoves(moves, my_context, canvas, root, my_visual, circle_radius_size)
drone_visual.display_drones()
root.mainloop()