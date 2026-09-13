import heapq
from .models import Context, Hub

class PathFinder():
    def __init__(self, context: Context):
        self.context = context
        self.came_from:dict[str, str|None] = {}
        self.cost_so_far: dict[str, int] = {} #cout jusqu'a maintenant --> dict["hub4"] = 156 equivalent visited
        self.queue = []
        self.flight_plan = []
        self.adj = {}
        self.start_hub = next(iter(context.hubs.values())).name
        self.goal = 'goal'

    def get_cost(self, hub_name: str)-> float|int:
        metadata = self.context.hubs[hub_name].metadata
        i = 0
        if(metadata.current_nb_drones > metadata.max_drones_capacity):
            i += 1
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
        return(1)

    def update_queue(self, hub_neighboor, previous_node):
        hub_content = self.context.hubs
        for hub in hub_neighboor:
            cost_current = self.get_cost(hub)
            cost_previous = self.cost_so_far[previous_node]
            challenger_cost = cost_current + cost_previous
            if (hub not in self.cost_so_far) or (challenger_cost < self.cost_so_far[hub]):
                self.cost_so_far.update({hub: challenger_cost})
                self.came_from.update({hub: previous_node})
                heapq.heappush(self.queue, (challenger_cost, hub))

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
        self.cost_so_far.update({self.start_hub: 0})
        heapq.heappush(self.queue, (0, self.start_hub))
        heapq.heapify(self.queue)
        self.came_from[self.start_hub] = None
        while self.queue:
            cost, popped = heapq.heappop(self.queue)
            if popped == 'goal':
                print("finished")
                break
            self.update_queue(self.adj[popped], popped)
            # print(popped)
    
    def build_flight_plan(self):
        zone = self.goal
        while(zone != self.start_hub):
            self.flight_plan.append(zone)
            zone = self.came_from[zone]
        self.flight_plan.append(self.start_hub)
        # self.flight_plan = self.flight_plan[:-1]
    
    def custom_flight_plan(self, current_hub: str):
        #this one could run the engine again probs
        zone = self.goal
        while(zone != current_hub):
            self.flight_plan.append(zone)
            zone = self.came_from[zone]
            
    def run_djikstra(self):
        self.build_adjacency_list()
        self.engine_loop()
        self.build_flight_plan()
        print(self.flight_plan)
        print(self.cost_so_far[self.goal])
        # print(self.came_from)