*This project has been created as part of the 42 curriculum by <your_login_here>.*

# FLY IN: Drone Fleet Simulator

## Description
**FLY IN** is a drone fleet simulation and routing project. Its primary goal is to calculate and visualize the optimal flight paths for a fleet of drones traveling through a constrained network of hubs and connections. 

The project parses custom map files to build a network of nodes (hubs) and edges (connections). It then simulates the movement of multiple drones from a designated start hub to an end hub while strictly respecting link capacities, hub capacities, and specific zone restrictions (e.g., restricted, blocked, or priority zones). A built-in graphical interface renders the network and animates the drones' movements in real time.

## Instructions
**Prerequisites:** 
* Python 3.13+
* `tkinter` (usually bundled with Python, but may require a separate package install on some Linux distributions, e.g., `sudo apt-get install python3-tk`).

**Execution:**
1. Clone the repository and navigate to the root directory.
2. Run the application as a Python module:
   ```bash
   uv run main.py "example_map.txt"
   ```
3. The program will prompt you for a map file if you run the program without specifying a map. Provide the path to one of the text files in the `maps/` directory (e.g., `maps/easy/01_linear_path.txt`).
   ```text
   Enter the path of the map of your choice: maps/easy/01_linear_path.txt
   ```

## Algorithm Choices and Implementation Strategy
The core routing engine relies on **Dijkstra's Algorithm**, implemented using Python's `heapq` module to maintain a priority queue for efficient pathfinding.

* **Dynamic Cost Evaluation:** Graph edges/nodes do not have fixed weights. Instead, costs are dynamically calculated based on hub metadata. Standard hubs have a cost of `1.0`, `restricted` zones cost `2.0`, and `blocked` zones carry an infinite cost. `priority` zones do not alter the cost but manipulate the priority queue tie-breaker to favor them.
* **Collision and Capacity Management:** The `DronesFleetHandler` tracks real-time capacity constraints. Before a drone commits to its next step, the handler verifies if the target hub and connection have available capacity. 
* **Dynamic Rerouting:** If a bottleneck is detected (a hub or link is full), the drone temporarily ignores the congested node and re-runs Dijkstra's algorithm to find an alternative route. If no alternative exists, the drone waits in place.

## Visual Representation Features
The project features a 2D Graphical User Interface built with **Tkinter**, designed to make the routing logic transparent and visually intuitive.

* **Dynamic Scaling:** The `MapVisualizer` calculates the minimum and maximum coordinates of the provided map and automatically scales/offsets the network to comfortably fit the user's screen dimensions while maintaining a safe margin.
* **Hub and Connection Mapping:** Hubs are drawn as colored circles (customizable via the map file metadata) and connected by lines representing valid flight paths.
* **Circular Drone Distribution:** To prevent visual clutter when multiple drones occupy the same hub simultaneously, the visualizer calculates an angular offset (using sine and cosine) to distribute the drone icons evenly around the hub's center.
* **Smooth Animation:** Drone movements are interpolated frame-by-frame over a set tick rate, providing fluid motion across the connections rather than instant teleportation. A live tick counter tracks the simulation's progress on screen.

## Example Input and Expected Output

**Example Map Input (`example_map.txt`):**
```text
nb_drones: 2
start_hub: Start 0 0 [max_drones=5]
hub: Middle 50 50 [zone=normal max_drones=1]
end_hub: End 100 100 [max_drones=5]
connection: Start-Middle [max_link_capacity=1]
connection: Middle-End [max_link_capacity=1]
```

**Expected Console Output:**
When executing the simulation, the console prints the log of drone movements per turn, mapping Drone IDs to their target hubs or connections:
```text
D1-Start D2-Start
D1-Middle
D1-End D2-Middle
D2-End
```
*Simultaneously, the Tkinter window will open, drawing the three hubs and animating Drone 1 moving to the Middle hub, followed by Drone 2 once the capacity at the Middle hub frees up.*

## Resources
* **Tkinter Documentation:** [Python Official Tkinter Docs](https://docs.python.org/3/library/tkinter.html) - Used for building the graphical canvas and handling animation loops.
* **Dijkstra's Algorithm:** [Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) / Pathfinding Tutorials - Used as the mathematical foundation for the `PathFinder` class.
* **AI Usage:** Large Language Models (LLMs) were utilized during the development of this project to generate PEP-257 compliant docstrings (Google/NumPy style) for all primary classes and functions (e.g., `MapParser`, `DronesFleetHandler`, `DroneMoves`, `PathFinder`) to ensure standardized, highly readable code documentation.