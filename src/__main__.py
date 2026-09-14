from .parser import parsing
from .models import Context
from .load_map import MapVisualizer
from .path_finder import PathFinder
from .drone_fleet_handler import DronesFleetHandler

my_context = parsing("maps/easy/01_linear_path.txt")
my_visual = MapVisualizer()
dfh = DronesFleetHandler(my_context)
my_visual.load_map(my_context)
dfh.handle_drones(5)