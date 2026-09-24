from .models import Hub, Connection, Context, HubMetadata, ConnectionMetadata

def extract_line(raw_line: str) ->tuple[str, str | None]:
    if "[" in raw_line:
        splitted = raw_line.split("[", 1)
        # check_valid_name(splitted[0])
        # print(splitted)
        return (splitted[0], splitted[1].strip().strip("]"))
    else:
        return(raw_line.strip(), None)
    
def parsing_meta(metadata: str)->dict[str, str] | None:
    meta_dict = {}
    splitted_meta = metadata.split()
    for item in splitted_meta:
        key, val = item.split("=")
        if key in ["max_drones", "max_link_capacity"]:
            meta_dict[key] = int(val)
        else:
            meta_dict[key] = val
    return(meta_dict)

def check_matching_hub_type(hub_type: str, line: int)-> None:
    accepted_hubs = ["start_hub", "hub", "end_hub"]
    for hub in accepted_hubs:
        if(hub == hub_type):
            return
    raise ValueError(f"Line {line}: The type {hub_type} does not exist, please specify a valid type")


def parsing(path: str) -> Context:
    '''Parse separately connections and hubs in two differents classes, parse metadata for
    connection and for hubs'''
    nb_drones = 0
    hubs: dict[str, Hub] = {}
    connections: list[Connection] = []
    nb_of_start_hub = 0
    nb_of_end_hub = 0
    comments_len = 0
    with open(path) as f:
        for i, x in enumerate(f):
            if x.startswith("#") or x == "\n":
                comments_len += 1
                continue
            if x.startswith("nb_drones") and i != comments_len:
                raise ValueError(f" Line {i} The nb Drones should be on the first line")
            elif x.startswith("nb_drones"):
                if x.split(":")[0] != "nb_drones":
                    raise ValueError(f"Line {i}: {x.split(':')[0]} is not a valid key")
                nb_drones = int(x.split(":")[1].strip())
            if(x.startswith(("start_hub", "hub", "end_hub"))):
                check_matching_hub_type(x.split(":")[0], i)
                hub_data, metadata = extract_line(x)
                my_meta = None
                if(metadata != None):
                    meta_dict = parsing_meta(metadata)
                    my_meta = HubMetadata(**meta_dict)
                tokens = hub_data.split()
                role, name, x, y = tokens
                my_hub = Hub(x=int(x), y=int(y), name=name, role=role.strip(":"), metadata=my_meta)
                hubs.update({name: my_hub})

            if(x.startswith("connection")):
                co_data, metadata = extract_line(x)
                my_meta = None

                if (metadata != None):
                    meta_dict = parsing_meta(metadata)
                    my_meta = ConnectionMetadata(**meta_dict)

                tokens = co_data.split(":")
                tokens = tokens[1].strip().split("-")
                source, target = tokens
                my_connection = Connection(source=source, target=target, metadata=my_meta)
                connections.append(my_connection)

        return(Context(nb_drones=nb_drones, hubs=hubs, connections=connections))
        

