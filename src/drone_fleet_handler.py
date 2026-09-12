class Drone():
    def __init__(self, drone_id):
        self.drone_id = drone_id
        self.flight_plan = []
        self.current_hub = 'start'

class Drones_fleet_handler():
    def __init__(self, nb_drones: int) -> None:
        self.drones: list[Drone] = []
        self.nb_drones = nb_drones
        self.final_hub = 'goal'

    def initalized_drone_array(self) -> None:
        for i in range(1, self.nb_drones):
            self.drones.append(Drone(drone_id="D"+str(i)))

        
    def update_djikstra_path(self, drone: Drone):
        pass

    def check_hub_availability(self):
        #check the current drone flight plan, if the next_hub is available (need to check link capacity and hub capacity) we move to the next hub and update the infos
        return (True)

    def print_drone_logs(self, drone: Drone):
        #print_drone movment depending of the djikstra algorithm
        print(f"{drone.drone_id}-{drone.current_hub}")

    def handle_drones(self):
        self.initalized_drone_array()
        for drone in self.drones:
            if self.check_hub_availability() is False:
                self.update_djikstra_path(drone)
            self.print_drone_logs(drone)

dfh = Drones_fleet_handler(5)

dfh.handle_drones()