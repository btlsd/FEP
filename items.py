import json
import os


class Item:
    def __init__(
        self,
        name,
        weight,
        volume=1,
        valid_nations=None,
        universal=False,
        printable=False,
        damage=0,
        weapon_type=None,
        concealable=False,
        material=None,
        quality=1.0,
        durability=None,
        weapon_range=None,
    ):
        self.name = name
        self.weight = weight
        self.volume = volume
        self.valid_nations = valid_nations
        self.universal = universal
        self.printable = printable
        self.damage = damage
        self.weapon_type = weapon_type
        self.concealable = concealable
        self.material = material
        self.quality = quality
        base_dur = {"나무": 40, "철": 70, "강철": 90, "합금": 110}
        if durability is None:
            durability = int(base_dur.get(material, 50) * quality)
        self.durability = durability
        if weapon_type and damage:
            self.damage = int(damage * quality)
        else:
            self.damage = damage
        self.weapon_range = weapon_range


def _load_items():
    """Load item definitions from ``data/items.json``.

    The JSON file may either be a simple mapping of ID to item info or contain
    an ``items`` object with that mapping. Additional keys such as comments are
    ignored so anyone can annotate the file freely.
    """
    path = os.path.join(os.path.dirname(__file__), "data", "items.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    data = raw.get("items", raw)
    items = {}
    for key, val in data.items():
        if key.startswith("_"):
            continue
        items[key] = Item(
            val["name"],
            val["weight"],
            val.get("volume", 1),
            val.get("valid_nations"),
            val.get("universal", False),
            val.get("printable", False),
            val.get("damage", 0),
            val.get("weapon_type"),
            val.get("concealable", False),
            val.get("material"),
            val.get("quality", 1.0),
            val.get("durability"),
            val.get("range"),
        )
    return items


_ITEMS = _load_items()
_KEY_BY_ITEM = {v: k for k, v in _ITEMS.items()}

def item_key(item):
    """Return the key string for a given item object."""
    return _KEY_BY_ITEM.get(item)

globals().update(_ITEMS)

__all__ = ["Item", "item_key"] + list(_ITEMS.keys())
