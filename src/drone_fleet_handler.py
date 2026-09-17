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
        self.goal = next(hub for hub in context.hubs.values() if hub.role == "end_hub").name
        self.path_finder = PF(context)
        self.hubs = context.hubs

    def initalized_drone_array(self) -> None:
        for i in range(self.nb_drones):
            self.drones.append(Drone(drone_id="D"+str(i+1)))

        
    def update_djikstra_path(self, drone: Drone):
         return (self.path_finder.run_djikstra(drone.current_hub))

    def update_drone_pos(self, drone: Drone):
        if len(drone.flight_plan) > 1:
            if(drone.current_hub != drone.flight_plan[1]):
                self.hubs[drone.current_hub].current_nb_drones -= 1
                self.hubs[drone.flight_plan[1]].current_nb_drones += 1
            drone.current_hub = drone.flight_plan[1]
        else:
            if(drone.current_hub != drone.flight_plan[0]):
                self.hubs[drone.current_hub].current_nb_drones -= 1
                self.hubs[drone.flight_plan[0]].current_nb_drones += 1
            drone.current_hub = drone.flight_plan[0]

    def get_logs(self, drone: Drone):
        return(f"{drone.drone_id}-{drone.current_hub} ")

    def handle_drones(self, nb_drones: int):
        self.nb_drones = nb_drones
        self.initalized_drone_array()
        count = 0
        logs_list: list[str] = []
        while(count <= nb_drones):
            tick_log = ""
            count = 1
            for drone in self.drones:
                if drone.current_hub == self.goal:
                    count += 1
                drone.flight_plan = self.update_djikstra_path(drone)
                tick_log += self.get_logs(drone)
                self.update_drone_pos(drone)
            logs_list.append(tick_log)
        print(logs_list)
        return(logs_list)