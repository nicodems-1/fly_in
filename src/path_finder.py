# objectif, utiliser djikstra pour calculer le chemin le plus efficace pour un seul drone
# trouver une table de correspondance facile coherente pour traiter ces donnees
#  type dict[hub, list[hub]]

# adjacency_list should be rebuilt every turn because of the different zones condition and capacity
import heapq
from .models import Context, Hub
from time import sleep 

class PathFinder():
    def __init__(self, context: Context):
        self.context = context
        self.came_from:dict[str, str|None] = {}
        self.cost_so_far: dict[str, int] = {} #cout jusqu'a maintenant --> dict["hub4"] = 156 equivalent visited
        self.queue = []
        self.flight_plan = []
        self.adj = self.build_adjacency_list()
        self.start_hub = next(iter(context.hubs.values())).name
        self.goal = next(hub for hub in context.hubs.values() if hub.role == "end_hub").name

    def build_adjacency_list(self) -> dict[str, list[str]]:
        adjacency_list: dict[str, list[str]] = {}
        connections = self.context.connections
        hubs: dict[str, Hub] = self.context.hubs
        for hub in hubs.values():
            next_hubs = []
            for connection in connections:
                if hub.name in connection.source:
                    next_hubs.append(hubs[connection.target].name)
            next_hubs.append(hub.name)
            adjacency_list.update({hub.name: next_hubs})
        return(adjacency_list)

    def get_connection_metadata(self, next_hub, start_hub) -> tuple[int, int]:
        connections = self.context.connections
        for connection in connections:
            if connection.source == start_hub and connection.target == next_hub and connection.metadata != None:
                # print("found connection 1")
                # sleep(1)
                # Fixed: Returning both current and max to match the tuple[int, int] signature
                return (connection.current_link_capacity, connection.metadata.max_link_capacity)

            if connection.source == next_hub and connection.target == start_hub and connection.metadata != None:
                # print("found connection 2")
                # sleep(1)
                # Fixed: Changed 'connections.metadata' (the list) to 'connection.metadata' (the item)
                return (connection.current_link_capacity, connection.metadata.max_link_capacity)

        # Fixed: Moved outside the for-loop so it only triggers if the entire list is checked
        # print(f"No connections capacity found source == {start_hub}, target == {next_hub}")
        return (0, 110)

    def get_cost(self, next_hub: str, start_hub:str)-> float|int:
        metadata = self.context.hubs[next_hub].metadata
        hubs = self.context.hubs
        current_link_capacity, max_link_capacity = self.get_connection_metadata(next_hub, start_hub)
        # print(current_link_capacity, max_link_capacity)
        if next_hub == start_hub:
            return(1)
        if metadata == None:
            return(1)
        if(current_link_capacity >= max_link_capacity):
            return(float('inf'))
        if metadata.max_drones is not None and metadata.max_drones != 0:
            if (hubs[next_hub].current_nb_drones) >= metadata.max_drones:
                return(float('inf'))
        if metadata.zone is None or metadata.zone == 'normal':
            return(1)
        if metadata.zone == 'priority':
            return(1)
        if metadata.zone == 'blocked':
            return(float('inf'))
        if metadata.zone == 'restricted':
            return(2)
        return(1)

    def update_queue(self, hub_neighboor, previous_node, base_node):
        hub_content = self.context.hubs
        for hub in hub_neighboor:
            cost_current = self.get_cost(hub, base_node)
            if cost_current == float('inf'):
                continue
            cost_previous = self.cost_so_far[previous_node]
            challenger_cost = cost_current + cost_previous
            if (hub not in self.cost_so_far) or (challenger_cost < self.cost_so_far[hub]):
                self.cost_so_far.update({hub: challenger_cost})
                self.came_from.update({hub: previous_node})
                heapq.heappush(self.queue, (challenger_cost, hub))


    def engine_loop(self, current_hub):
        self.cost_so_far.update({current_hub: 0})
        heapq.heappush(self.queue, (0, current_hub))
        heapq.heapify(self.queue)
        self.came_from[current_hub] = None
        while self.queue:
            cost, popped = heapq.heappop(self.queue)
            if popped == self.goal:
                break
            self.update_queue(self.adj[popped], popped, current_hub)
    
    def build_flight_plan(self, current_hub) -> list[str]:
        zone = self.goal
        flight_plan = []
        while(zone != current_hub):
            if self.goal not in self.came_from:
                return [current_hub, current_hub]
            flight_plan.append(zone)
            zone = self.came_from[zone]
        flight_plan.append(current_hub)
        return(flight_plan[::-1])

    def run_djikstra(self, current_hub) -> list[str]:
        self.came_from = {}
        self.cost_so_far = {}
        self.queue = []
        self.engine_loop(current_hub)
        self.flight_plan = self.build_flight_plan(current_hub)
        return(self.flight_plan)