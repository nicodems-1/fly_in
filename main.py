import argparse
import sys

from parser import MapParser
from load_map import MapVisualizer
from drone_fleet_handler import DronesFleetHandler
from drone_visual import DroneMoves


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Drone Fleet Simulation (Fly-In)")
    parser.add_argument(
        "map_file", nargs="?", help="Path of the file to simulate")
    return parser.parse_args()


def main() -> None:
    """Execute the main workflow for the drone simulation application.

    This function prompts the user for a map file path, parses the map data,
    initializes the graphical user interface, calculates the drone movements
    via the fleet handler, and begins the visualization main loop.

    Raises:
        SystemExit: If the user provides an empty string for the file path.
    """
    args = parse_args()
    file_path = args.map_file
    if not file_path:
        file_path = input("Enter the path of the map of your choice: ").strip()
    if not file_path:
        print("Error: No Path given")
        raise SystemExit(1)

    mp: MapParser = MapParser(file_path)
    my_context = mp.parse()
    my_visual: MapVisualizer = MapVisualizer()
    dfh: DronesFleetHandler = DronesFleetHandler(my_context)
    canvas, root, circle_radius_size = my_visual.load_map(my_context)
    moves = dfh.handle_drones(my_context.nb_drones)
    drone_visual: DroneMoves = DroneMoves(
        moves,
        my_context,
        canvas,
        root,
        my_visual,
        int(circle_radius_size),
    )
    drone_visual.display_drones()
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError,
            PermissionError, IsADirectoryError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
