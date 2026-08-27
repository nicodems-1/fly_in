from pydantic import BaseModel, Field
from typing import Optional, Literal


class Hub(BaseModel):
    '''class hub which contains info for each hub such as color position, name and role'''
    x: int
    y: int
    color: Optional[str] = None
    name: str
    role: Literal["start_hub", "end_hub", "hub"]

class Connection(BaseModel):
    '''class that contains the links between the differents hubs'''
    source: str
    target: str

class Context(BaseModel):
    '''context contain all the infos from class hub and class connection, we'll use context
    for the calculations and the display'''
    nb_of_drones: int
    hubs: dict[str, Hub]
    connections: list[Connection]

class Metadata(BaseModel):
    '''class containing different options for base model such as:
     max_link_capacity, max_drone capacity, zone, color '''
    color: Optional[str] = None
    max_drones: Optional[int] = None
    max_link_capacity: Optional[int] = None
    zone: Optional[Literal["normal", "restricted", "priority", "blocked"]] = None
    