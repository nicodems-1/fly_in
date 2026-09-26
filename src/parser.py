from .models import Hub, Connection, Context, HubMetadata, ConnectionMetadata
import re


class MapParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.current_line: int = 0
        self.hub: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.start = False
        self.goal = False
        self.zone_names: list[str] = []
        self.skipped_line: int = 0
        self.nb_drones: int = 0
        self.hubs: dict[str, Hub] = {}

    def _parsing_meta_hub(self, metadata: str) -> dict[str, int] | None:
        meta_dict = {}
        zone_type = ["normal", "restricted", "blocked", "priority"]
        if not (metadata.endswith("]")):
            raise ValueError(f"Line {self.current_line}\n"
                             f"Metadata must be between brackets\n"
                             f"Current: {metadata}")
        splitted_meta = metadata.strip("[").strip("]").split()
        allowed_types = ["zone", "color", "max_drones"]
        for item in splitted_meta:
            key, val = item.split("=")
            if key in ["max_drones", "max_link_capacity"]:
                meta_dict[key] = int(val)
            if key not in allowed_types:
                raise ValueError(f"Line {self.current_line}\n"
                                 f"KEY: <<{key}>> in metadata not correct\n"
                                 f"Allowed key: {allowed_types}")
            if key == "zone" and val not in zone_type:
                raise ValueError(f"Line {self.current_line}\n"
                                 f"zone type: {val} does not exist \n"
                                 f"Allowed zones types: {zone_type}")
            else:
                meta_dict[key] = val
        return meta_dict

    def _parsing_meta_connection(self, metadata: str) -> None:
        clean_meta = metadata.strip("]")
        if "=" not in clean_meta:
            raise ValueError(f"Line {self.current_line}\n"
                             f"Metadata connection should be formated with "
                             f"an equal sign in the middle "
                             f"current: <<{clean_meta}>>")
        splitted = clean_meta.split("=")
        if splitted[1].isdigit() is False:
            raise ValueError(f"Line {self.current_line}\n"
                             f"Max_link_capacity must be a positive integer\n"
                             f"Current: <<{splitted[1]}>>")

    def _parse_nb_drone(self, line) -> None:
        nb_drones = int(line.split()[1])
        if nb_drones < 1:
            raise ValueError(f"Line {self.current_line}"
                             f"The number of drone should be more than 1")
        if self.skipped_line + 1 != self.current_line:
            raise ValueError(f"Line {self.current_line} "
                             f"nb_drone should be on the first line")
        self.nb_drones = nb_drones

    def _parse_hub(self, line: str):
        print("Entering the parsing of the hub")
        hub_type = ["start_hub", "end_hub", "hub"]
        splitted = line.split()
        if splitted[0].strip(":") == splitted[0]:
            raise ValueError(f"Line {self.current_line} "
                             f"Wrong format, missing the semi colon")
        if splitted[0].strip(":") not in hub_type:
            raise ValueError(f"Line {self.current_line} "
                             f"<<{splitted[0]}>> is not a valid hub_type")
        hub_name = splitted[1]
        if hub_name in self.zone_names:
            raise ValueError(f"Line {self.current_line} "
                             f"Hub name: <<{hub_name}>> already in use"
                             f"Each Hub can only have one single name")
        if " " in hub_name:
            raise ValueError(f"Line {self.current_line} "
                             f"Space are not allowed in Zone Names")
        if "-" in hub_name:
            raise ValueError(f"Line {self.current_line} "
                             f"Dashes are not allowed in Zone Names")
        x_coord = splitted[2]
        print(x_coord)
        if not x_coord.strip('-').isdigit():
            raise ValueError(f"Line {self.current_line} "
                             f"x_coord = {splitted[2]} is not an integer"
                             f"\nOnly integer are allowed")
        y_coord = splitted[3]
        if not y_coord.strip('-').isdigit():
            raise ValueError(f"Line {self.current_line} "
                             f"y_coord = {splitted[3]} is not an integer"
                             f"\nOnly integer are allowed")

        if len(splitted) > 3:
            self._parsing_meta_hub(metadata=line.split("[")[1])
        self.zone_names.append(hub_name)

    def _parse_connection(self, line: str):
        splitted = line.split()
        if splitted[0] != "connection:":
            raise ValueError(f"Line {self.current_line} "
                             f"<<{splitted[0]}>> is "
                             f"not a valid connection_type")
        zones = splitted[1].split("-")
        if len(zones) != 2:
            raise ValueError(f"Line {self.current_line} "
                             "Connection format not respected"
                             f"\n {zones}")
        conn_1, conn_2 = zones
        if conn_1 not in self.zone_names:
            raise ValueError(f"Line {self.current_line}\n"
                             f"Invalid connection: {zones}\n"
                             f"Zone <<{conn_1}>> does not exist")
        if conn_2 not in self.zone_names:
            raise ValueError(f"Line {self.current_line}\n"
                             f"Invalid connection: {zones}\n"
                             f"Zone <<{conn_2}>> does not exist")
        new_co = Connection(conn_1, conn_2)
        for connection in self.connections:
            if connection.source == new_co.target:
                if connection.target == new_co.source:
                    raise ValueError(f"Line {self.current_line} "
                                     f"Duplicate connection"
                                     f"\n <<{splitted[1]}>>")
            if connection.source == new_co.source:
                if connection.target == new_co.target:
                    raise ValueError(f"Line {self.current_line} "
                                     f"Duplicate connection"
                                     f"\n <<{splitted[1]}>>")
        if len(splitted) > 2:
            self._parsing_meta_connection(line.split("[")[1])

        self.connections.append(new_co)
        print(splitted[1])

    def parse(self) -> Context:
        with open(self.filepath) as f:
            for line in f:
                self.current_line += 1
                line = line.strip()
                if line.startswith("#") or not line:
                    self.skipped_line += 1
                    continue
                elif line.startswith("nb_drones"):
                    self._parse_nb_drone(line)
                elif line.startswith("hub"):
                    self._parse_hub(line)
                elif line.startswith("conn"):
                    self._parse_connection(line)
                elif line.startswith("start_hub"):
                    if self.start is True:
                        raise ValueError(f"Line {self.current_line} "
                                         f"Only one start_hub should exist")
                    self.start = True
                    self._parse_hub(line)
                elif line.startswith("end_hub"):
                    if self.goal is True:
                        raise ValueError(f"Line {self.current_line} "
                                         f"Only one end_hub should exist")
                    self.goal = True
                    self._parse_hub(line)
                else:
                    raise ValueError(f"Line {self.current_line} "
                                     f"does not comply with authorized format "
                                     f"\n <<{line}>> ")

        return Context(nb_drones=self.nb_drones, hubs=self.hubs, connections=self.connections)
