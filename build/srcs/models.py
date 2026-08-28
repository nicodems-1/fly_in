from pydantic import BaseModel, Field, PositiveInt
from typing import Optional, Literal

class HubMetadata(BaseModel):
    model_config = {"extra": "forbid"}
    color: Optional[str] = None
    max_drones: Optional[PositiveInt] = None
    zone: Optional[Literal["normal", "restricted", "priority", "blocked"]] = (None)


class ConnectionMetadata(BaseModel):
    model_config = {"extra": "forbid"}
    max_link_capacity: Optional[PositiveInt] = None


class Hub(BaseModel):
    '''class hub which contains info for each hub such as color position, name and role'''
    x: int
    y: int
    name: str
    role: Literal["start_hub", "end_hub", "hub"]
    metadata: Optional[HubMetadata] = None

class Connection(BaseModel):
    '''class that contains the links between the differents hubs'''
    source: str
    target: str
    metadata: Optional[HubMetadata] = None

class Context(BaseModel):
    '''context contain all the infos from class hub and class connection, we'll use context
    for the calculations and the display'''
    nb_drones: PositiveInt
    hubs: dict[str, Hub]
    connections: list[Connection]
    