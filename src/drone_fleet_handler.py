from typing import List, Optional
from .path_finder import PathFinder as PF
from .parser import Context

class Drone:
    def __init__(self, drone_id: str):
        self.drone_id: str = drone_id
        self.flight_plan: List[str] = []
        self.current_hub: str = "" 
        self.previous_hub: str = ""
        self.turns_remaining: int = 0
        self.reserved_destination: Optional[str] = None


class DronesFleetHandler:
    def __init__(self, context: Context) -> None:
        self.context = context
        self.hubs = context.hubs
        self.connections = context.connections
        self.path_finder = PF(context)
        
        self.drones: List[Drone] = []
        self.nb_drones: int = 0
        
        self.start = next(hub for hub in self.hubs.values() if hub.role == "start_hub").name
        self.goal = next(hub for hub in self.hubs.values() if hub.role == "end_hub").name

    def initialize_drones(self) -> None:
        self.drones = [Drone(f"D{i+1}") for i in range(self.nb_drones)]
        for drone in self.drones:
            drone.current_hub = self.start
            drone.previous_hub = self.start

    def get_connection(self, zone1: str, zone2: str):
        for conn in self.connections:
            if (conn.source == zone1 and conn.target == zone2) or \
               (conn.source == zone2 and conn.target == zone1):
                return conn
        return None

    def is_zone_restricted(self, zone_name: str) -> bool:
        hub = self.hubs[zone_name]
        return hub.metadata is not None and getattr(hub.metadata, 'zone', '') == "restricted"

    def has_hub_capacity(self, zone_name: str) -> bool:
        hub = self.hubs[zone_name]
        if hub.role in ["start_hub", "end_hub"]:
            return True
        max_cap = hub.metadata.max_drones if (hub.metadata and hasattr(hub.metadata, 'max_drones')) else 1
        return getattr(hub, 'current_nb_drones', 0) < max_cap

    def has_connection_capacity(self, conn) -> bool:
        max_cap = conn.metadata.max_link_capacity if (conn.metadata and hasattr(conn.metadata, 'max_link_capacity')) else 1
        return getattr(conn, 'current_drones', 0) < max_cap

    def reserve_hub(self, zone_name: str, increment: int):
        hub = self.hubs[zone_name]
        if hub.role not in ["start_hub", "end_hub"]:
            if not hasattr(hub, 'current_nb_drones'):
                hub.current_nb_drones = 0
            hub.current_nb_drones += increment

    def reserve_connection(self, conn, increment: int):
        if not hasattr(conn, 'current_drones'):
            conn.current_drones = 0
        conn.current_drones += increment

    def process_drone(self, drone: Drone) -> Optional[str]:
        if drone.turns_remaining > 0:
            drone.turns_remaining -= 1
            if drone.turns_remaining == 0:
                conn = self.get_connection(drone.previous_hub, drone.reserved_destination)
                self.reserve_connection(conn, -1) 
                
                drone.current_hub = drone.reserved_destination
                drone.reserved_destination = None
                
                return f"{drone.drone_id}-{drone.current_hub}"
            else:
                return None
        
        drone.flight_plan = self.path_finder.run_djikstra(drone.current_hub)
        
        if not drone.flight_plan:
            return None
            
        # Cherche la première étape du plan qui n'est pas la position actuelle
        next_hub_name = None
        for step in drone.flight_plan:
            if step != drone.current_hub:
                next_hub_name = step
                break
                
        # S'il n'y a pas de prochaine étape, le drone est arrivé ou bloqué
        if not next_hub_name:
            return None
            
        conn = self.get_connection(drone.current_hub, next_hub_name)
        
        if conn is None:
            print(f"ERREUR FATALE: Aucune connexion trouvée entre '{drone.current_hub}' et '{next_hub_name}'. Vérifie les .strip() dans ton parseur !", flush=True)
            return None

        if not self.has_hub_capacity(next_hub_name) or not self.has_connection_capacity(conn):
            return None

        self.reserve_hub(drone.current_hub, -1)
        
        if self.is_zone_restricted(next_hub_name):
            self.reserve_hub(next_hub_name, 1)
            self.reserve_connection(conn, 1)
            
            drone.previous_hub = drone.current_hub
            drone.reserved_destination = next_hub_name
            drone.turns_remaining = 1
            
            conn_name = getattr(conn, 'name', f"{conn.source}-{conn.target}")
            return f"{drone.drone_id}-{conn_name}"
            
        else:
            self.reserve_hub(next_hub_name, 1)
            drone.previous_hub = drone.current_hub
            drone.current_hub = next_hub_name
            
            return f"{drone.drone_id}-{drone.current_hub}"

    def handle_drones(self, nb_drones: int) -> List[str]:
        self.nb_drones = nb_drones
        self.initialize_drones()
        
        logs_list: List[str] = []
        finished_drones = set()

        max_turns = 2000  
        turn = 0

        while len(finished_drones) < nb_drones and turn < max_turns:
            turn_logs = []
            
            for drone in self.drones:
                if drone.drone_id in finished_drones:
                    continue
                    
                log = self.process_drone(drone)
                
                if log:
                    turn_logs.append(log)
                    
                if drone.current_hub == self.goal and drone.turns_remaining == 0:
                    finished_drones.add(drone.drone_id)

            if turn_logs:
                logs_list.append(" ".join(turn_logs))
            else:
                if len(finished_drones) < nb_drones:
                    break
                    
            turn += 1
        print(logs_list)
        return logs_list