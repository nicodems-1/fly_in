from models import Hub, Connection, Context, HubMetadata, ConnectionMetadata

def parsing_meta(metadata: str)->dict[str, str] or None:
    meta_dict = {}
    if(metadata.endswith("]")):
        clean_meta = metadata.strip("]")
        splitted_meta = clean_meta.split()
        for item in splitted_meta:
            key, val = item.split("=")
            meta_dict[key] = val
        print(f"{meta_dict} metadict_connection")
        return(meta_dict)
    else:
        raise ValueError("Error line 33, metadata format does not correspond")

def parsing() -> Context:
    nb_drones = 0
    hubs: dict[str, Hub] = {}
    connections: list[Connection] = []
    with open("maps/easy/01_linear_path.txt") as f:
        for x in f:
            if x.startswith("#"):
                continue
            if x.startswith("nb_drones"):
                nb_drones = int(x.split(":")[1].strip())
            if(x.startswith("start_hub") or x.startswith("hub") or x.startswith("end_hub")):
                hub_split = x.strip().split()
                if("[" in x):
                    split_meta = x.split("[")
                    hub_data = split_meta[0]
                    metadata = split_meta[1].strip()
                    parsing_meta(metadata)
                    hub_split = hub_data.strip().split()
                x_coor = hub_split[2]
                y_coor = hub_split[3]
                name = hub_split[1]
                role = hub_split[0].strip(":")
                my_hub = Hub(x=x_coor, y=y_coor, name=name, role=role)
                hubs.update({name: my_hub})
            if(x.startswith("connection")):
                co_data = x.split(":")[1]
                if("[" in x):
                    split_meta = x.split("[")
                    co_data = split_meta[0]
                    metadata = split_meta[1].strip()
                    parsing_meta(metadata)
                co_split = co_data.strip().split("-")
                source = co_split[0]
                target = co_split[1]
                my_connection = Connection(source=source, target=target)
                connections.append(my_connection)
        print(connections, hubs)
        return(Context(nb_drones=nb_drones, hubs=hubs, connections=connections))

parsing()


        

