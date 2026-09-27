from dataclasses import dataclass, field
from typing import Literal, Dict, List, TypedDict


@dataclass
class HubMetadata:
    color: str | None = None
    max_drones: int = 1
    zone: Literal["normal", "restricted", "priority", "blocked"] = "normal"


ZoneType = Literal["normal", "restricted", "priority", "blocked"]


class ParsedHubMeta(TypedDict, total=False):
    color: str | None
    max_drones: int
    zone: ZoneType


@dataclass
class ConnectionMetadata:
    max_link_capacity: int = 1


@dataclass
class Hub:
    """class hub which contains info for each
    hub such as color position, name and role"""

    x: int
    y: int
    name: str
    role: Literal["start_hub", "end_hub", "hub"]
    metadata: HubMetadata = field(default_factory=HubMetadata)
    current_nb_drones: int = 0


@dataclass
class Connection:
    """class that contains the links between the differents hubs"""

    source: str
    target: str
    metadata: ConnectionMetadata = field(default_factory=ConnectionMetadata)
    current_link_capacity: int = 0


@dataclass
class Context:
    """context contain all the infos from
    class hub and class connection, we'll use context
    for the calculations and the display"""

    hubs: Dict[str, Hub]
    connections: List[Connection]
    nb_drones: int = 0
