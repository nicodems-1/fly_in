import heapq
from .models import Context, Hub


class PathFinder:
    """Computes optimal routes for drones through the map
    using Dijkstra's algorithm.

    Attributes:
        context (Context): The simulation context containing map data.
        came_from (dict[str, str | None]):
        Maps a hub to the hub that preceded it on the optimal path.
        cost_so_far (dict[str, float]): Tracks the minimum cumulative
        cost to reach each hub.
        queue (list[tuple[float, int, str]]): A priority queue used to explore
        the lowest-cost paths first.
        flight_plan (list[str]): The resulting computed path.
        adj (dict[str, list[str]]): The adjacency list
        representation of the map's graph.
        start_hub (str): The starting hub name.
        goal (str): The destination hub name.
    """

    def __init__(self, context: Context) -> None:
        """Initialize the PathFinder with the simulation context.

        Args:
            context (Context): The map context containing hubs and connections.
        """
        self.context = context
        self.came_from: dict[str, str | None] = {}
        self.cost_so_far: dict[str, float] = {}
        self.queue: list[tuple[float, int, str]] = []
        self.flight_plan: list[str] = []
        self.adj: dict[str, list[str]] = self.build_adjacency_list()
        self.start_hub = next(iter(context.hubs.values())).name
        self.goal = next(
            hub for hub in context.hubs.values() if hub.role == "end_hub"
        ).name

    def build_adjacency_list(self) -> dict[str, list[str]]:
        """Construct a graph adjacency list from the context's connections.

        Each hub includes itself in its list of neighbors to allow for
        waiting moves.

        Returns:
            dict[str, list[str]]: A dictionary mapping hub names to lists of
            accessible adjacent hub names.
        """
        adjacency_list: dict[str, list[str]] = {}
        connections = self.context.connections
        hubs: dict[str, Hub] = self.context.hubs
        for hub in hubs.values():
            next_hubs = []
            for connection in connections:
                if connection.source == hub.name:
                    next_hubs.append(connection.target)
                elif connection.target == hub.name:
                    next_hubs.append(connection.source)
            next_hubs.append(hub.name)
            adjacency_list.update({hub.name: next_hubs})
        return adjacency_list

    def get_cost(self, next_hub: str) -> float:
        """Determine the traversal cost for a specific hub based
        on its metadata.

        Args:
            next_hub (str): The name of the hub to evaluate.

        Returns:
            float: The cost to enter the hub (1.0 for normal, 2.0
            for restricted,
            infinity for blocked).
        """
        metadata = self.context.hubs[next_hub].metadata
        if metadata is None:
            return 1.0
        if metadata.zone == "blocked":
            return float("inf")
        if metadata.zone == "restricted":
            return 2.0
        return 1.0

    def update_queue(
        self, hub_neighboor: list[str], previous_node: str, base_node: str
    ) -> None:
        """Evaluate neighbor hubs and update the pathfinding priority queue.

        Calculates cumulative costs to reach neighboring hubs.
        If a cheaper path is found,
        updates the tracking dictionaries and pushes the new path to the
        priority queue.

        Args:
            hub_neighboor (list[str]): The list of neighboring hub names to
            evaluate.
            previous_node (str): The name of the hub currently being expanded.
            base_node (str): The initial starting node of the current path
            search.
        """
        for hub in hub_neighboor:
            meta = self.context.hubs[hub].metadata
            priority_score = 0 if (meta and meta.zone == "priority") else 1

            cost_current = self.get_cost(hub)
            if cost_current == float("inf"):
                continue

            cost_previous = self.cost_so_far[previous_node]
            challenger_cost = cost_current + cost_previous

            if (hub not in self.cost_so_far) or (
                challenger_cost < self.cost_so_far[hub]
            ):
                self.cost_so_far.update({hub: challenger_cost})
                self.came_from.update({hub: previous_node})
                heapq.heappush(self.queue,
                               (challenger_cost, priority_score, hub))

    def engine_loop(self, current_hub: str, ignored_nodes: list[str]) -> None:
        """Execute the core Dijkstra pathfinding loop.

        Explores the map graph from the current hub, evaluating paths based on
        cumulative cost until the goal is reached or the queue is exhausted.

        Args:
            current_hub (str): The starting hub for the current search.
            ignored_nodes (list[str]): A list of node names to skip during
            exploration.
        """
        if self.get_cost(current_hub) == float("inf"):
            return

        self.cost_so_far.update({current_hub: 0})

        meta = self.context.hubs[current_hub].metadata
        priority_score = 0 if (meta and meta.zone == "priority") else 1

        heapq.heappush(self.queue, (0, priority_score, current_hub))
        heapq.heapify(self.queue)

        self.came_from[current_hub] = None
        while self.queue:
            _, _, popped = heapq.heappop(self.queue)
            if popped == self.goal:
                break
            if popped in ignored_nodes:
                continue
            self.update_queue(self.adj[popped], popped, current_hub)

    def build_flight_plan(self, current_hub: str) -> list[str]:
        """Reconstruct the sequence of hubs from the computed path history.

        Backtracks from the goal node through the `came_from` dictionary to
        build a chronological sequence of steps from start to finish.

        Args:
            current_hub (str): The starting node of the path.

        Returns:
            list[str]: The ordered list of hub names comprising the
            flight plan.
                Returns a single waiting step `[current_hub, current_hub]`
                if no path exists.
        """
        zone: str | None = self.goal
        flight_plan: list[str] = []

        if self.goal not in self.came_from:
            return [current_hub, current_hub]

        while zone is not None and zone != current_hub:
            flight_plan.append(zone)
            zone = self.came_from[zone]

        if zone != current_hub:
            return [current_hub, current_hub]

        flight_plan.append(current_hub)
        return flight_plan[::-1]

    def run_djikstra(
        self, current_hub: str, ignored_nodes: list[str] | None = None
    ) -> list[str]:
        """Calculate and return the optimal flight plan to the goal.

        Resets pathfinding state, runs the exploration algorithm,
        and reconstructs
        the final path.

        Args:
            current_hub (str): The hub from which to begin pathfinding.
            ignored_nodes (list[str] | None, optional): Specific hubs to
            exclude from the search. Defaults to None.

        Returns:
            list[str]: The computed optimal flight plan as a list of hub names.
        """
        if ignored_nodes is None:
            ignored_nodes = []
        self.came_from = {}
        self.cost_so_far = {}
        self.queue = []
        self.engine_loop(current_hub, ignored_nodes)
        self.flight_plan = self.build_flight_plan(current_hub)
        return self.flight_plan
