import json
import os


class Item:
    def __init__(self, name, weight, volume=1):
        self.name = name
        self.weight = weight
        self.volume = volume


def _load_items():
    path = os.path.join(os.path.dirname(__file__), "data", "items.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    items = {}
    for key, val in raw.items():
        items[key] = Item(val["name"], val["weight"], val.get("volume", 1))
    return items


_ITEMS = _load_items()
globals().update(_ITEMS)

__all__ = ["Item"] + list(_ITEMS.keys())
