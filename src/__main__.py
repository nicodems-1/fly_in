from .parser import parsing
from .models import Context
from .load_map import MapVisualizer

my_context = parsing("maps/easy/02_simple_fork.txt")
my_visual = MapVisualizer()
my_visual.load_map(my_context)

# la modification test