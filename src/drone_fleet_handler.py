from .path_finder import PathFinder as PF
from .parser import Context

class Drone():
    def __init__(self, drone_id):
        self.drone_id = drone_id
        self.flight_plan: list[str] = []
        self.current_hub = 'start'

class DronesFleetHandler():
    def __init__(self, context: Context) -> None:
        self.drones: list[Drone] = []
        self.nb_drones = 0
        self.goal = 'goal'
        self.path_finder = PF(context)

    def initalized_drone_array(self) -> None:
        for i in range(self.nb_drones):
            self.drones.append(Drone(drone_id="D"+str(i+1)))

        
    def update_djikstra_path(self, drone: Drone):
         return (self.path_finder.run_djikstra(drone.current_hub))

    def update_drone_pos(self, drone: Drone):
        if len(drone.flight_plan) > 1:
            drone.current_hub = drone.flight_plan[1]
        else:
            drone.current_hub = drone.flight_plan[0]

    def print_drone_logs(self, drone: Drone):
        print(f"{drone.drone_id}-{drone.current_hub}", end = " ")

    def handle_drones(self, nb_drones: int):
        self.nb_drones = nb_drones
        self.initalized_drone_array()
        tick_simulation = 0
        count = 0
        while(count <= nb_drones):
            tick_simulation += 1
            print()
            for drone in self.drones:
                if drone.current_hub == self.goal:
                    count += 1
                drone.flight_plan = self.update_djikstra_path(drone)
                # print(drone.flight_plan)
                self.print_drone_logs(drone)
                self.update_drone_pos(drone)