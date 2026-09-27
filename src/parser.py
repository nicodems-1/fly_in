from .models import Hub, Connection, Context, HubRole
from .models import HubMetadata, ConnectionMetadata, ZoneType
import re
from typing import cast, TypedDict


class ParsedHubMeta(TypedDict, total=False):
    color: str | None
    max_drones: int
    zone: ZoneType


class MapParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.current_line: int = 0
        self.connections: list[Connection] = []
        self.start = False
        self.goal = False
        self.zone_names: list[str] = []
        self.skipped_line: int = 0
        self.nb_drones: int = 0
        self.hubs: dict[str, Hub] = {}
        self.nb_drone_declared: bool = False

    def _parsing_meta_hub(self, metadata: str) -> ParsedHubMeta:
        meta_dict: ParsedHubMeta = {}
        zone_type: set[str] = {"normal", "restricted", "blocked", "priority"}
        allowed_types: set[str] = {"zone", "color", "max_drones"}

        if not metadata.strip():
            return meta_dict

        for item in metadata.split():
            if "=" not in item:
                raise ValueError(f"Line {self.current_line}: "
                                 f"Invalide metadata syntax "
                                 f"<<{item}>>")
            key, val = item.split("=")
            if key in ["max_drones"]:
                meta_dict["max_drones"] = int(val)
            if key not in allowed_types:
                raise ValueError(
                    f"Line {self.current_line}\n"
                    f"KEY: <<{key}>> in metadata not correct\n"
                    f"Allowed key: {allowed_types}"
                )
            if key == "zone" and val not in zone_type:
                raise ValueError(
                    f"Line {self.current_line}\n"
                    f"zone type: {val} does not exist \n"
                    f"Allowed zones types: {zone_type}"
                )
                meta_dict["zone"] = cast(ZoneType, val)
            if key == "max_drones":
                if not val.isdigit():
                    raise ValueError(
                        f"Line {self.current_line}\n"
                        f"max_drones must be a positive integer\n"
                        f"current: <<{val}>>"
                    )
                    meta_dict["max_drones"] = int(val)
            elif key == "color":
                meta_dict["color"] = val
        return meta_dict

    def _parsing_meta_connection(self, metadata: str) -> ConnectionMetadata:
        if "=" not in metadata:
            raise ValueError(
                f"Line {self.current_line}\n"
                f"Metadata connection should be formated with "
                f"an equal sign in the middle "
                f"current: <<{metadata}>>"
            )
        splitted = metadata.split("=")
        if splitted[1].isdigit() is False:
            raise ValueError(
                f"Line {self.current_line}\n"
                f"Max_link_capacity must be a positive integer\n"
                f"Current: <<{splitted[1]}>>"
            )
        return ConnectionMetadata(max_link_capacity=int(splitted[1]))

    def _parse_nb_drone(self, line: str) -> None:
        variable_name = line.split()[0]
        if variable_name != "nb_drones:":
            raise ValueError(
                f"Line {self.current_line}: "
                f"Wrong format for nb_drones <<{variable_name}>>"
            )
        try:
            int(line.split()[1])
        except ValueError:
            print(f"Line {self.current_line}: nb_drone "
                  f"must be a positive integer")
        nb_drones = int(line.split()[1])
        if nb_drones < 1:
            raise ValueError(
                f"Line {self.current_line}: nb_drone "
                f"must be a positive integer > 1"
            )
        if self.skipped_line + 1 != self.current_line:
            raise ValueError(
                f"Line {self.current_line} nb_drones "
                f"should be on the first line"
            )
        self.nb_drone_declared = True
        self.nb_drones = nb_drones

    def _parse_hub(self, line: str) -> None:
        meta: ParsedHubMeta = {}
        if "[" in line or "]" in line:
            match = re.search(r"\[([^\[\]]+)\]\s*$", line)
            if not match:
                raise ValueError(
                    f"Line {self.current_line} : "
                    f"Invalid metaformat, brackets are "
                    f"not placed correctly"
                )
            meta_content = match.group(1)
            meta = self._parsing_meta_hub(meta_content)
            line = line[: match.start()].strip()
        splitted = line.split()
        if len(splitted) != 4:
            raise ValueError(
                f"Line {self.current_line} :"
                f"Too many or missing argument\n"
                f"Expected 4, got {len(splitted)}: {splitted}"
            )
        if splitted[0].strip(":") == splitted[0]:
            raise ValueError(
                f"Line {self.current_line} Wrong format, "
                f"missing the semi colon"
            )
        hub_type = ["start_hub", "end_hub", "hub"]
        if splitted[0].strip(":") not in hub_type:
            raise ValueError(
                f"Line {self.current_line} <<{splitted[0]}>> is "
                f"not a valid hub_type"
            )
        hub_name = splitted[1]
        if hub_name in self.zone_names:
            raise ValueError(
                f"Line {self.current_line} "
                f"Hub name: <<{hub_name}>> already in use"
                f"Each Hub can only have one single name"
            )
        if " " in hub_name:
            raise ValueError(
                f"Line {self.current_line} Space not allowed in Zone Names"
            )
        if "-" in hub_name:
            raise ValueError(
                f"Line {self.current_line} Dashes not allowed in Zone Names"
            )
        x_coord = splitted[2]
        if not x_coord.strip("-").isdigit():
            raise ValueError(
                f"Line {self.current_line} "
                f"x_coord = {splitted[2]} is not an integer"
                f"\nOnly integer are allowed"
            )
        y_coord = splitted[3]
        if not y_coord.strip("-").isdigit():
            raise ValueError(
                f"Line {self.current_line} "
                f"y_coord = {splitted[3]} is not an integer"
                f"\nOnly integer are allowed"
            )
        x_int = int(x_coord)
        y_int = int(y_coord)

        for existing_hub in self.hubs.values():
            if existing_hub.x == x_int and existing_hub.y == y_int:
                raise ValueError(
                    f"Line {self.current_line}\n"
                    f"Hub <<{existing_hub.name}>> already at this position\n"
                    f"Current hub: <<{hub_name}>> is overlaping"
                )
        if line.startswith("hub"):
            role = "hub"
        elif line.startswith("start_hub"):
            role = "start_hub"
        else:
            role = "end_hub"
        hub_role = cast(HubRole, role)
        if meta:
            meta_hub = HubMetadata(
                color=meta.get("color"),
                max_drones=meta.get("max_drones", 1),
                zone=meta.get('zone', 'normal'),
            )
        new_hub = Hub(
            x=int(x_coord), y=int(y_coord), name=hub_name,
            role=hub_role, metadata=meta_hub
        )
        self.zone_names.append(hub_name)
        self.hubs.update({hub_name: new_hub})

    def _parse_connection(self, line: str) -> None:
        meta_parsed = None
        if "[" in line or "]" in line:
            match = re.search(r"\[([^\[\]]+)\]\s*$", line)
            if not match:
                raise ValueError(
                    f"Line {self.current_line} : "
                    f"Invalid metaformat, brackets are "
                    f"not placed correctly"
                )
            else:
                connection_meta = match.group(1)
                meta_parsed = self._parsing_meta_connection(connection_meta)
                line = line[: match.start()].strip()
        splitted = line.split()
        if len(splitted) != 2:
            raise ValueError(
                f"Line {self.current_line} :"
                f"Too many or missing argument\n"
                f"Expected 2, got {len(splitted)}: {splitted}"
            )
        splitted = line.split()
        if splitted[0] != "connection:":
            raise ValueError(
                f"Line {self.current_line} "
                f"<<{splitted[0]}>> is "
                f"not a valid connection_type"
            )
        zones = splitted[1].split("-")
        if len(zones) != 2:
            raise ValueError(
                f"Line {self.current_line} Connection "
                f"format not respected\n {zones}"
            )
        conn_1, conn_2 = zones
        if conn_1 not in self.zone_names:
            raise ValueError(
                f"Line {self.current_line}\n"
                f"Invalid connection: {zones}\n"
                f"Zone <<{conn_1}>> does not exist"
            )
        if conn_2 not in self.zone_names:
            raise ValueError(
                f"Line {self.current_line}\n"
                f"Invalid connection: {zones}\n"
                f"Zone <<{conn_2}>> does not exist"
            )
        new_co = Connection(conn_1, conn_2)
        if meta_parsed:
            new_co.metadata = meta_parsed
        for connection in self.connections:
            if connection.source == new_co.target:
                if connection.target == new_co.source:
                    raise ValueError(
                        f"Line {self.current_line} "
                        f"Duplicate connection"
                        f"\n <<{splitted[1]}>>"
                    )
            if connection.source == new_co.source:
                if connection.target == new_co.target:
                    raise ValueError(
                        f"Line {self.current_line} "
                        f"Duplicate connection "
                        f"\n <<{splitted[1]}>>"
                    )
        self.connections.append(new_co)

    def parse(self) -> Context:
        with open(self.filepath) as f:
            for line in f:
                self.current_line += 1
                line = line.strip()
                if line.startswith("#") or not line:
                    self.skipped_line += 1
                    continue
                elif line.startswith("nb_drones:"):
                    self._parse_nb_drone(line)
                elif line.startswith("hub"):
                    self._parse_hub(line)
                elif line.startswith("conn"):
                    self._parse_connection(line)
                elif line.startswith("start_hub"):
                    if self.start is True:
                        raise ValueError(
                            f"Line {self.current_line} "
                            f"Only one start_hub should exist"
                        )
                    self.start = True
                    self._parse_hub(line)
                elif line.startswith("end_hub"):
                    if self.goal is True:
                        raise ValueError(
                            f"Line {self.current_line} "
                            f"Only one end_hub should exist"
                        )
                    self.goal = True
                    self._parse_hub(line)
                else:
                    raise ValueError(
                        f"Line {self.current_line} "
                        f"does not comply with authorized format "
                        f"\n <<{line}>> "
                    )
            if not self.goal:
                raise ValueError(f"Line {self.current_line}Missing end_hub")
            if not self.start:
                raise ValueError(f"Line {self.current_line}Missing start_hub")
            if not self.nb_drone_declared:
                raise ValueError("nb_drones is not declared")

        return Context(
            nb_drones=self.nb_drones, hubs=self.hubs,
            connections=self.connections
        )
