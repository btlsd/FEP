import json
import os


class Nation:
    def __init__(self, name, description, currency="화폐", transport="도보"):
        self.name = name
        self.description = description
        self.currency = currency
        self.transport = transport


class Location:
    def __init__(
        self,
        name,
        description,
        nation,
        zone=None,
        indoors=False,
        descriptions=None,
        open_times=None,
        mod_shop=None,
        station=False,
        international=False,
        job_office=False,
        printer=False,
    ):
        self.name = name
        self.description = description
        self.nation = nation
        self.zone = zone or name
        self.indoors = indoors
        self.connections = []
        self.hidden_connections = {}
        # optional dict of time_index -> description
        self.descriptions = descriptions or {}
        # list of allowed time indexes (0~5)
        self.open_times = open_times if open_times is not None else list(range(6))
        self.mod_shop = mod_shop  # "legal" or "illegal"
        self.station = station
        self.international = international
        self.job_office = job_office
        self.printer = printer

    def get_description(self, time_idx):
        # descriptions keys might be strings in JSON
        return self.descriptions.get(time_idx) or self.descriptions.get(str(time_idx)) or self.description

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
NATIONS = [
    Nation(
        n["name"],
        n["description"],
        n.get("currency", "화폐"),
        n.get("transport", "도보"),
    )
    for n in data["nations"]
]
NATION_BY_NAME = {n.name: n for n in NATIONS}

# Locations
_locations = {}
for entry in data["locations"]:
    nation = NATIONS[entry["nation"]]
    loc = Location(
        entry["name"],
        entry.get("description", ""),
        nation,
        entry.get("zone"),
        entry.get("indoors", False),
        entry.get("descriptions"),
        entry.get("open_times"),
        entry.get("mod_shop"),
        entry.get("station", False),
        entry.get("international", False),
        entry.get("job_office", False),
        entry.get("printer", False),
    )
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
    "NATION_BY_NAME",
    "DEFAULT_LOCATION_BY_NATION",
    "LOCATIONS",
] + list(_locations.keys())
