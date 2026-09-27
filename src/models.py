from dataclasses import dataclass
from typing import Literal

HubRole = Literal["start_hub", "end_hub", "hub"]
ZoneType = Literal["normal", "restricted", "blocked", "priority"]


@dataclass
class HubMetadata:
    """Represents additional configuration and constraints for a hub.

    Attributes:
        color (str | None): The display color of the hub for visualization.
        max_drones (int): The maximum number of drones the hub
        can hold simultaneously.
        zone (ZoneType): The classification of the zone
        (e.g., normal, restricted).
    """

    color: str | None = None
    max_drones: int = 1
    zone: ZoneType = "normal"


@dataclass
class ConnectionMetadata:
    """Represents additional configuration and constraints for a connection.

    Attributes:
        max_link_capacity (int): The maximum number of drones that can travel
        on this connection simultaneously.
    """

    max_link_capacity: int = 1


@dataclass
class Hub:
    """Represents a location or node within the drone network map.

    Attributes:
        x (int): The X coordinate of the hub on the map.
        y (int): The Y coordinate of the hub on the map.
        name (str): The unique identifier/name of the hub.
        role (HubRole): The operational role of the hub (start_hub, end_hub,
        or standard hub).
        metadata (HubMetadata | None): Additional properties and constraints
        for the hub.
        current_nb_drones (int): The current number of drones occupying or
        reserved for this hub.
    """

    x: int
    y: int
    name: str
    role: HubRole
    metadata: HubMetadata | None = None
    current_nb_drones: int = 0


@dataclass
class Connection:
    """Represents a navigable path linking two hubs together.

    Attributes:
        source (str): The name of the starting hub for this connection.
        target (str): The name of the destination hub for this connection.
        current_link_capacity (int): The current number of drones traveling
        on or reserved for this connection.
        metadata (ConnectionMetadata | None): Additional properties and
        constraints for the connection.
    """

    source: str
    target: str
    current_link_capacity: int = 0
    metadata: ConnectionMetadata | None = None


@dataclass
class Context:
    """Holds the overall parsed state and configuration of the simulation map.

    Attributes:
        nb_drones (int): The total number of drones participating
        in the simulation.
        hubs (dict[str, Hub]): A dictionary mapping hub names to their
        respective Hub objects.
        connections (list[Connection]): A list of all valid connections
        between hubs on the map.
    """

    nb_drones: int
    hubs: dict[str, Hub]
    connections: list[Connection]
