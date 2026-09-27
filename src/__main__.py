from .parser import MapParser
# from .models import Context
from .load_map import MapVisualizer
# from .path_finder import PathFinder
from .drone_fleet_handler import DronesFleetHandler
from .drone_visual import DroneMoves
import sys


def main() -> None:
    file_path = input("Enter the path of the map of your choice:").strip()
    if not file_path:
        print("Error: No Path given")
        sys.exit(1)
    mp = MapParser(file_path)
    my_context = mp.parse()
    my_visual: MapVisualizer = MapVisualizer()
    dfh = DronesFleetHandler(my_context)
    canvas, root, circle_radius_size = my_visual.load_map(my_context)
    moves = dfh.handle_drones(my_context.nb_drones)
    drone_visual = DroneMoves(
        moves, my_context, canvas, root, my_visual, circle_radius_size
    )
    drone_visual.display_drones()
    root.mainloop()


# try:
#     if __name__ == "__main__":
main()
# except ValueError as e:
#     print(e)
# except FileNotFoundError as e:
#     print("The path is wrong or the file does not exist", e)
# except PermissionError as e:
#     print("Cannot open the map \n", e)
