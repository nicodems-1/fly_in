# objectif, utiliser djikstra pour calculer le chemin le plus efficace pour un seul drone
# trouver une table de correspondance facile coherente pour traiter ces donnees
#  type dict[hub, list[hub]]

# adjacency_list should be rebuilt every turn because of the different zones condition and capacity
import heapq
from .models import Context, Hub

class PathFinder():
    def __init__(self, context: Context):
        self.context = context
        self.came_from = {}
        self.cost_so_far = 0
        self.queue = []
        self.flight_plan = []
        self.adj = {}
        self.start_hub = next(iter(context.hubs.values())).name

    def get_cost(self, hub_name: str):
        metadata = self.context.hubs[hub_name].metadata
        print(metadata)
        if metadata == None:
            return(1)
        if metadata.zone is None or metadata.zone == 'normal':
            return(1)
        if metadata.zone == 'priority':
            return(1)
        if metadata.zone == 'blocked':
            return(float('inf'))
        if metadata.zone == 'restricted':
            return(2)

    def update_queue(self, hub_names):
        hub_content = self.context.hubs
        for hub in hub_names:
            print(f"cost of moving toward the node == {self.get_cost(hub)}")
            print(hub)
            heapq.heappush(self.queue, (self.get_cost(hub), hub))

    def build_adjacency_list(self):
        adjacency_list: dict[str, list[str]] = {}
        connections = self.context.connections
        hubs: dict[str, Hub] = self.context.hubs
        for hub in hubs.values():
            next_hubs = []
            for connection in connections:
                if hub.name in connection.source:
                    next_hubs.append(hubs[connection.target].name)
            adjacency_list.update({hub.name: next_hubs})
        self.adj = adjacency_list

    def engine_loop(self):
        heapq.heappush(self.queue, (0, self.start_hub))
        heapq.heapify(self.queue)
        while self.queue:
            popped = heapq.heappop(self.queue)
            self.update_queue(self.adj[popped[1]])
            # print(self.adj[popped[1]])
            # print(self.adj)
            # print(self.adj['start'])
            # print(popped)
    
    def run_djikstra(self):
        print()
        self.build_adjacency_list()
        self.engine_loop()
        # print(self.adj)
               