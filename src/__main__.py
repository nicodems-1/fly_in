from .parser import parsing
from .models import Context
from .load_map import MapVisualizer
from .path_finder import PathFinder

my_context = parsing("maps/hard/03_ultimate_challenge.txt")
my_visual = MapVisualizer()
my_p_f = PathFinder(my_context)
my_p_f.run_djikstra()
my_visual.load_map(my_context)

# la modification test