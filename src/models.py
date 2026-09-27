from dataclasses import dataclass
from typing import Literal

HubRole = Literal["start_hub", "end_hub", "hub"]
ZoneType = Literal["normal", "restricted", "blocked", "priority"]


@dataclass
class HubMetadata:
    color: str | None = None
    max_drones: int = 1
    zone: ZoneType = "normal"


@dataclass
class ConnectionMetadata:
    max_link_capacity: int = 1


@dataclass
class Hub:
    x: int
    y: int
    name: str
    role: HubRole
    metadata: HubMetadata | None = None
    current_nb_drones: int = 0


@dataclass
class Connection:
    source: str
    target: str
    current_link_capacity: int = 0
    metadata: ConnectionMetadata | None = None


@dataclass
class Context:
    nb_drones: int
    hubs: dict[str, Hub]
    connections: list[Connection]
