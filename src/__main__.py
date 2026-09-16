from .parser import parsing
from .models import Context
from .load_map import MapVisualizer
from .path_finder import PathFinder
from .drone_fleet_handler import DronesFleetHandler
from .drone_visual import DroneMoves

my_context = parsing("maps/easy/02_simple_fork.txt")
my_visual = MapVisualizer()
dfh = DronesFleetHandler(my_context)
canvas, root = my_visual.load_map(my_context)
moves = dfh.handle_drones(15)
drone_visual = DroneMoves(moves, my_context, canvas, root, my_visual)
drone_visual.display_drones()
root.mainloop()