from typing import Optional

from .models import Connection
from .parser import Context
from .path_finder import PathFinder as PF


class Drone:
    """Represents a single drone within the simulation.

    Attributes:
        drone_id (str): The unique identifier for the drone.
        flight_plan (list[str]): The planned sequence of hubs to reach the goal.
        current_hub (str): The name of the hub the drone is currently located at.
        previous_hub (str): The name of the previous hub the drone visited.
        turns_remaining (int): The number of turns the drone must wait in transit.
        reserved_destination (Optional[str]): The target hub reserved for the drone while in transit.
    """
    def __init__(self, drone_id: str) -> None:
        """Initialize a new Drone instance.

        Args:
            drone_id (str): The unique identifier for this drone.
        """
        self.drone_id: str = drone_id
        self.flight_plan: list[str] = []
        self.current_hub: str = ""
        self.previous_hub: str = ""
        self.turns_remaining: int = 0
        self.reserved_destination: Optional[str] = None


class DronesFleetHandler:
    """Manages a fleet of drones, coordinating their movement and resource
    constraints.

    Handles capacity limits on hubs and connections, dynamically reroutes
    drones,
    and manages the overall simulation loop for drone traversal.

    Attributes:
        context (Context): The parsed map context containing hubs and
        connections.
        hubs (dict): A dictionary of all available hubs in the map.
        connections (list[Connection]): A list of all valid connections
        between hubs.
        path_finder (PF): The pathfinding utility used to route drones.
        drones (list[Drone]): The fleet of drones being managed.
        nb_drones (int): The total number of drones in the fleet.
        start (str): The name of the starting hub.
        goal (str): The name of the destination hub.
    """
    def __init__(self, context: Context) -> None:
        """Initialize the DronesFleetHandler with a specific map context.

        Args:
            context (Context): The parsed context containing map constraints, hubs, and connections.
        """
        self.context = context
        self.hubs = context.hubs
        self.connections: list[Connection] = list(context.connections)
        self.path_finder = PF(context)

        self.drones: list[Drone] = []
        self.nb_drones: int = 0

        self.start = next(
            hub for hub in self.hubs.values() if hub.role == "start_hub"
        ).name
        self.goal = next(
            hub for hub in self.hubs.values() if hub.role == "end_hub"
        ).name

    def initialize_drones(self) -> None:
        """Instantiate the drone fleet and place them at the start hub."""
        self.drones = [Drone(f"D{i + 1}") for i in range(self.nb_drones)]
        for drone in self.drones:
            drone.current_hub = self.start
            drone.previous_hub = self.start

    def get_connection(self, zone1: str, zone2: str) -> Optional[Connection]:
        """Retrieve the bidirectional connection between two specific zones.

        Args:
            zone1 (str): The name of the first zone.
            zone2 (str): The name of the second zone.

        Returns:
            Optional[Connection]: The connection object linking the two zones,
            or None if it does not exist.
        """
        for conn in self.connections:
            if (conn.source == zone1 and conn.target == zone2) or (
                conn.source == zone2 and conn.target == zone1
            ):
                return conn
        return None

    def is_zone_restricted(self, zone_name: str) -> bool:
        """Check if a specific hub is marked as a restricted zone.

        Args:
            zone_name (str): The name of the hub to check.

        Returns:
            bool: True if the zone is restricted, False otherwise.
        """
        hub = self.hubs[zone_name]
        return (
            hub.metadata is not None
            and getattr(hub.metadata, "zone", "") == "restricted"
        )

    def has_hub_capacity(self, zone_name: str) -> bool:
        """Determine if a hub can accommodate an additional drone.

        Start and end hubs are assumed to have infinite capacity.

        Args:
            zone_name (str): The name of the hub to check.

        Returns:
            bool: True if the hub has available capacity, False otherwise.
        """
        hub = self.hubs[zone_name]
        if hub.role in ["start_hub", "end_hub"]:
            return True
        max_cap = getattr(hub.metadata, "max_drones", 1)
        return getattr(hub, "current_nb_drones", 0) < max_cap

    def has_connection_capacity(self, conn: Connection) -> bool:
        """Determine if a connection can accommodate an additional drone in transit.

        Args:
            conn (Connection): The connection to check.

        Returns:
            bool: True if the connection has available capacity, False otherwise.
        """
        max_cap = getattr(conn.metadata, "max_link_capacity", 1)
        return getattr(conn, "current_drones", 0) < max_cap

    def reserve_hub(self, zone_name: str, increment: int) -> None:
        """Modify the current drone count of a specific hub.

        Args:
            zone_name (str): The name of the hub to reserve or free up.
            increment (int): The amount to change the capacity by (positive to reserve, negative to free).
        """
        hub = self.hubs[zone_name]
        if hub.role not in ["start_hub", "end_hub"]:
            current = getattr(hub, "current_nb_drones", 0)
            setattr(hub, "current_nb_drones", current + increment)

    def reserve_connection(self, conn: Connection, increment: int) -> None:
        """Modify the current drone count of a specific connection.

        Args:
            conn (Connection): The connection to reserve or free up.
            increment (int): The amount to change the capacity by
            (positive to reserve, negative to free).
        """
        current = getattr(conn, "current_drones", 0)
        setattr(conn, "current_drones", current + increment)

    def process_drone(self, drone: Drone) -> Optional[str]:
        """Process a single simulation turn for an individual drone.

        Handles countdowns for drones in transit, calculates optimal paths,
        checks
        capacity constraints, attempts rerouting if blocked,
        and updates capacities.

        Args:
            drone (Drone): The drone to process.

        Returns:
            Optional[str]: A log string describing the drone's
            movement (e.g., 'D1-HubA'),
                or None if the drone did not move.
        """
        if drone.turns_remaining > 0:
            drone.turns_remaining -= 1
            if drone.turns_remaining == 0:
                if drone.reserved_destination is None:
                    return None

                conn = self.get_connection(
                    drone.previous_hub, drone.reserved_destination
                )
                if conn is None:
                    return None

                self.reserve_connection(conn, -1)

                drone.current_hub = drone.reserved_destination
                drone.reserved_destination = None

                return f"{drone.drone_id}-{drone.current_hub}"

            return None

        drone.flight_plan = self.path_finder.run_djikstra(drone.current_hub)

        if not drone.flight_plan:
            return None

        next_hub_name: Optional[str] = None
        for step in drone.flight_plan:
            if step != drone.current_hub:
                next_hub_name = step
                break

        if next_hub_name is None:
            return None

        conn = self.get_connection(drone.current_hub, next_hub_name)
        if conn is None:
            return None

        if (
            not self.has_hub_capacity(next_hub_name)
            or not self.has_connection_capacity(conn)
        ):
            alt_plan = self.path_finder.run_djikstra(
                drone.current_hub, ignored_nodes=[next_hub_name]
            )

            if alt_plan and len(alt_plan) > 1:
                alt_next_hub = alt_plan[1]
                alt_conn = self.get_connection(drone.current_hub, alt_next_hub)

                if (
                    alt_conn is not None
                    and self.has_hub_capacity(alt_next_hub)
                    and self.has_connection_capacity(alt_conn)
                ):
                    drone.flight_plan = alt_plan
                    next_hub_name = alt_next_hub
                    conn = alt_conn
                else:
                    return None
            else:
                return None

        self.reserve_hub(drone.current_hub, -1)

        if self.is_zone_restricted(next_hub_name):
            self.reserve_hub(next_hub_name, 1)
            self.reserve_connection(conn, 1)

            drone.previous_hub = drone.current_hub
            drone.reserved_destination = next_hub_name
            drone.turns_remaining = 1

            conn_name = getattr(conn, "name", f"{conn.source}-{conn.target}")
            return f"{drone.drone_id}-{conn_name}"

        self.reserve_hub(next_hub_name, 1)
        drone.previous_hub = drone.current_hub
        drone.current_hub = next_hub_name

        return f"{drone.drone_id}-{drone.current_hub}"

    def handle_drones(self, nb_drones: int) -> list[str]:
        """Simulate the movement of the entire drone fleet from start to goal.

        Iterates through turns, processing each drone's movement
        until all drones
        have reached the end hub or a maximum turn limit is reached.

        Args:
            nb_drones (int): The total number of drones to simulate.

        Returns:
            list[str]: A list of space-separated log strings detailing
            drone movements per turn.

        Raises:
            ValueError: If the map cannot be solved or drones are permanently
            deadlocked.
        """
        self.nb_drones = nb_drones
        self.initialize_drones()

        logs_list: list[str] = []
        finished_drones: set[str] = set()

        max_turns = 2000
        turn = 0

        while len(finished_drones) < nb_drones and turn < max_turns:
            turn_logs: list[str] = []

            has_moved_this_turn: set[str] = set()
            moved_in_pass = True
            while moved_in_pass:
                moved_in_pass = False

                for drone in self.drones:
                    if (
                        drone.drone_id in finished_drones
                        or drone.drone_id in has_moved_this_turn
                    ):
                        continue

                    log = self.process_drone(drone)

                    if log:
                        turn_logs.append(log)
                        has_moved_this_turn.add(drone.drone_id)
                        moved_in_pass = True

                    if (
                        drone.current_hub == self.goal
                        and drone.turns_remaining == 0
                    ):
                        finished_drones.add(drone.drone_id)

            if turn_logs:
                logs_list.append(" ".join(turn_logs))
            else:
                if len(finished_drones) < nb_drones:
                    break

            turn += 1

        if not logs_list:
            raise ValueError("Map impossible to solve provide another map!")

        return logs_list
