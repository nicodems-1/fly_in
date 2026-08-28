from models import Hub, Connection, Context, HubMetadata, ConnectionMetadata

def extract_line(raw_line: str) ->tuple[str, str | None]:
    if "[" in raw_line:
        splitted = raw_line.split("[", 1)
        return (splitted[0], splitted[1].strip().strip("]"))
    else:
        return(raw_line.strip(), None)
    
def parsing_meta(metadata: str)->dict[str, str] or None:
    meta_dict = {}
    splitted_meta = metadata.split()
    for item in splitted_meta:
        key, val = item.split("=")
        meta_dict[key] = val
    return(meta_dict)


def parsing(path: str) -> Context:
    '''Parse separately connections and hubs in two differents classes, parse metadata for
    connection and for hubs'''
    nb_drones = 0
    hubs: dict[str, Hub] = {}
    connections: list[Connection] = []
    with open(path) as f:
        for x in f:
            if x.startswith("#"):
                continue

            if x.startswith("nb_drones"):
                nb_drones = int(x.split(":")[1].strip())

            if(x.startswith(("start_hub", "hub", "end_hub"))):
                hub_data, metadata = extract_line(x)
                my_meta = None
                if(metadata != None):
                    meta_dict = parsing_meta(metadata)
                    my_meta = HubMetadata(**meta_dict)

                tokens = hub_data.split()
                role, name, x, y = tokens
                my_hub = Hub(x=x, y=y, name=name, role=role.strip(":"), metadata=my_meta)
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
        

