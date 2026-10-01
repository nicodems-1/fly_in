from typing import Optional

from models import Connection
from parser import Context
from path_finder import PathFinder as PF

# a detour is accepted if it costs at most this many extra turns
DETOUR_TOLERANCE = 2


class Drone:
    """Represents a single drone within the simulation.

    Attributes:
        drone_id (str): The unique identifier for the drone.
        flight_plan (list[str]): The last computed sequence of hubs.
        current_hub (Optional[str]): Hub where the drone is, None while it is
            on a connection (restricted zone crossing).
        previous_hub (Optional[str]): The previous hub the drone visited.
        turns_remaining (int): Turns left before arriving (0 = on the ground).
        reserved_destination (Optional[str]): Hub reserved while in transit.
        active_connection (Optional[Connection]): Connection used while in
            transit.
    """

    def __init__(self, drone_id: str) -> None:
        self.drone_id: str = drone_id
        self.flight_plan: list[str] = []
        self.current_hub: Optional[str] = None
        self.previous_hub: Optional[str] = None
        self.turns_remaining: int = 0
        self.reserved_destination: Optional[str] = None
        self.active_connection: Optional[Connection] = None

    def is_in_flight(self) -> bool:
        return self.turns_remaining > 0

    def decrement_transit_time(self) -> None:
        if self.turns_remaining > 0:
            self.turns_remaining -= 1


class DronesFleetHandler:
    """Turn-based simulation of a drone fleet.

    Each turn:
      1. link usage is recomputed (only drones still crossing a connection
         occupy it),
      2. every drone is processed (possibly several passes so that a drone
         can take the place freed by another one in the same turn),
      3. the moves are logged on one line.

    Movement rules:
      - normal / priority zone: the drone arrives during the same turn
        (log "D1-B"),
      - restricted zone: turn 1 the drone is on the connection (log "D1-A-B"),
        turn 2 it arrives (log "D1-B").
    """

    def __init__(self, context: Context) -> None:
        self.context = context
        self.hubs = context.hubs
        self.connections: list[Connection] = list(context.connections)
        self.path_finder = PF(context)

        self.drones: list[Drone] = []
        self.nb_drones: int = 0
        # number of drones using each link during the current turn
        self.link_load: dict[frozenset[str], int] = {}

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
        return self.path_finder.get_connection(zone1, zone2)

    @staticmethod
    def link_key(conn: Connection) -> frozenset[str]:
        return frozenset((conn.source, conn.target))

    def is_zone_restricted(self, zone_name: str) -> bool:
        hub = self.hubs[zone_name]
        return (
            hub.metadata is not None
            and getattr(hub.metadata, "zone", "") == "restricted"
        )

    def has_hub_capacity(self, zone_name: str) -> bool:
        """True if one more drone can be in (or heading to) this hub."""
        hub = self.hubs[zone_name]
        if hub.role in ["start_hub", "end_hub"]:
            return True
        max_cap = getattr(hub.metadata, "max_drones", 1)
        count = sum(
            1
            for d in self.drones
            if d.current_hub == hub.name or d.reserved_destination == hub.name
        )
        return count < max_cap

    def has_connection_capacity(self, conn: Connection) -> bool:
        max_cap = getattr(conn.metadata, "max_link_capacity", 1)
        return self.link_load.get(self.link_key(conn), 0) < max_cap

    def reserve_connection(self, conn: Connection, increment: int) -> None:
        key = self.link_key(conn)
        self.link_load[key] = self.link_load.get(key, 0) + increment

    def begin_turn(self) -> None:
        """Recompute link usage: only drones still in transit hold a link
        (including those arriving this turn, they cross it one last turn)."""
        self.link_load = {}
        for drone in self.drones:
            if drone.is_in_flight() and drone.active_connection is not None:
                self.reserve_connection(drone.active_connection, 1)

    def process_drone(self, drone: Drone) -> Optional[str]:
        """Entry point of a drone for one turn."""
        if drone.is_in_flight():
            return self._process_in_flight(drone)
        return self._process_on_ground(drone)

    def _process_in_flight(self, drone: Drone) -> Optional[str]:
        drone.decrement_transit_time()
        if drone.is_in_flight():
            return None
        # arrival (the link stays counted until the next begin_turn)
        drone.current_hub = drone.reserved_destination
        drone.reserved_destination = None
        drone.active_connection = None
        return f"{drone.drone_id}-{drone.current_hub}"

    def _can_step(self, origin: str, nxt: str) -> bool:
        """True if a drone can start moving origin -> nxt this turn."""
        conn = self.get_connection(origin, nxt)
        return (
            conn is not None
            and self.has_connection_capacity(conn)
            and self.has_hub_capacity(nxt)
        )

    def _plan_cost(self, plan: list[str]) -> float:
        return sum(self.path_finder.get_cost(h) for h in plan[1:])

    @staticmethod
    def _back_hubs(drone: Drone) -> list[str]:
        prev = drone.previous_hub
        return [prev] if prev and prev != drone.current_hub else []

    def _detour_or_wait(self, drone: Drone, plan: list[str]) -> list[str]:
        """Look for another route whose first step is free. Return it only
        if it is not much longer than the blocked shortest path, otherwise
        return [] (the drone waits)."""
        origin = str(drone.current_hub)
        neighbours = self.path_finder.adj[origin]
        ignored_hub = [
            n for n in neighbours if not self.has_hub_capacity(n)
        ] + self._back_hubs(drone)
        ignored_connection: list[Connection] = []
        for n in neighbours:
            conn = self.get_connection(origin, n)
            if conn is not None and not self.has_connection_capacity(conn):
                ignored_connection.append(conn)
        alt = self.path_finder.run_djikstra(
            origin, ignored_connection, ignored_hub
        )
        if len(alt) < 2 or alt[1] == origin:
            return []
        if self._plan_cost(alt) > self._plan_cost(plan) + DETOUR_TOLERANCE:
            return []
        return alt

    def _process_on_ground(self, drone: Drone) -> Optional[str]:
        if drone.current_hub is None:
            return None
        if self.hubs[drone.current_hub].role == "end_hub":
            return None

        origin = drone.current_hub
        # 1) shortest path ignoring current occupancy
        # (never step back to the previous hub, unless it is the only way)
        back = self._back_hubs(drone)
        flight_plan = self.path_finder.run_djikstra(origin, [], back)
        if len(flight_plan) < 2 or flight_plan[1] == origin:
            flight_plan = self.path_finder.run_djikstra(origin)
        if len(flight_plan) < 2 or flight_plan[1] == origin:
            return None  # goal unreachable

        # 2) only the FIRST step needs free capacity right now
        if not self._can_step(origin, flight_plan[1]):
            flight_plan = self._detour_or_wait(drone, flight_plan)
            if not flight_plan:
                return None  # waiting is better than a long detour

        next_hub = flight_plan[1]
        conn = self.get_connection(origin, next_hub)
        if conn is None:
            return None
        self.reserve_connection(conn, 1)

        drone.flight_plan = flight_plan
        drone.previous_hub = origin

        if self.is_zone_restricted(next_hub):
            # turn 1 on the connection, arrival on the next turn
            drone.reserved_destination = next_hub
            drone.active_connection = conn
            drone.turns_remaining = 1
            drone.current_hub = None
            return f"{drone.drone_id}-{origin}-{next_hub}"

        # normal / priority: arrives this very turn
        drone.current_hub = next_hub
        return f"{drone.drone_id}-{next_hub}"

    def handle_drones(self, nb_drones: int) -> list[str]:
        """Simulate the fleet turn by turn until everyone is at the goal.

        Returns:
            list[str]: one line per turn.

        Raises:
            ValueError: if the map cannot be solved or drones deadlock.
        """
        self.nb_drones = nb_drones
        self.initialize_drones()

        logs_list: list[str] = []
        finished_drones: set[str] = set()
        max_turns = 2000
        turn = 0

        while len(finished_drones) < nb_drones and turn < max_turns:
            self.begin_turn()
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
                    was_in_flight = drone.is_in_flight()
                    log = self.process_drone(drone)

                    if was_in_flight or log:
                        has_moved_this_turn.add(drone.drone_id)
                    if log:
                        turn_logs.append(log)
                        moved_in_pass = True
                    if drone.current_hub == self.goal:
                        finished_drones.add(drone.drone_id)

            if not turn_logs:
                break  # nobody can move and nobody is in transit: deadlock
            logs_list.append(" ".join(turn_logs))
            turn += 1

        if len(finished_drones) < nb_drones:
            raise ValueError(
                "Map impossible to solve (blocked or deadlocked drones)"
            )
        for line in logs_list:
            print(line)
        return logs_list
