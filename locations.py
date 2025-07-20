import json
import os


class Nation:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Location:
    def __init__(self, name, description, nation, indoors=False):
        self.name = name
        self.description = description
        self.nation = nation
        self.indoors = indoors
        self.connections = []
        self.hidden_connections = {}

    def connect(self, other, required_perception=None):
        if required_perception is None:
            if other not in self.connections:
                self.connections.append(other)
            if self not in other.connections:
                other.connections.append(self)
        else:
            self.hidden_connections[other] = required_perception
            other.hidden_connections[self] = required_perception


def _load_data():
    path = os.path.join(os.path.dirname(__file__), "data", "locations.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


data = _load_data()

# Nations
NATIONS = [Nation(n["name"], n["description"]) for n in data["nations"]]

# Locations
_locations = {}
for entry in data["locations"]:
    nation = NATIONS[entry["nation"]]
    loc = Location(entry["name"], entry["description"], nation, entry.get("indoors", False))
    loc.key = entry["key"]
    _locations[entry["key"]] = loc

# Connections
for conn in data["connections"]:
    if isinstance(conn, list):
        a, b = _locations[conn[0]], _locations[conn[1]]
        a.connect(b)
    else:
        a = _locations[conn["from"]]
        b = _locations[conn["to"]]
        a.connect(b, required_perception=conn["perception"])

# Default locations
DEFAULT_LOCATION_BY_NATION = {NATIONS[int(k)]: _locations[v] for k, v in data["default_locations"].items()}

# Export location variables for convenience
globals().update(_locations)

LOCATIONS = list(_locations.values()) + list({loc for loc in DEFAULT_LOCATION_BY_NATION.values() if loc not in _locations.values()})

__all__ = [
    "Nation",
    "Location",
    "NATIONS",
    "DEFAULT_LOCATION_BY_NATION",
    "LOCATIONS",
] + list(_locations.keys())
