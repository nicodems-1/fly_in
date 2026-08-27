from models import Hub, Connection, Context

def parsing():
    nb_of_drones = 0
    hubs: dict[str, Hub] = {}
    connnection: Connection = []
    with open("maps/easy/01_linear_path.txt") as f:
        for x in f:
            if x.startswith("#"):
                pass
            if x.startswith("nb_drones"):
                nb_of_drones = int(x.split(":")[1].strip())
            if(x.startswith("start_hub") or x.startswith("hub") or x.startswith("end_hub")):
                splitted = x.strip().split()
                print("splitted", splitted)
                role = splitted[0].strip(":")
                name = splitted[1]
                x_coor = splitted[2]
                y_coor = splitted[3]
                if(len(splitted) == 5):
                    metadata = splitted[4].strip("\n")
                print (f"{role}\n{name}\n{x_coor}\n{y_coor}\n{metadata}\n")

parsing()

def parsing_metadata(metadata: str):
    ...

