from parser import parsing
from models import Context
from load_map import MapVisualizer

my_context = parsing("maps/hard/03_ultimate_challenge.txt")
my_visual = MapVisualizer()
my_visual.load_map(my_context)

# la modification test