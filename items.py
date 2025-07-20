import json
import os


class Item:
    def __init__(self, name, weight, volume=1, valid_nations=None, universal=False):
        self.name = name
        self.weight = weight
        self.volume = volume
        self.valid_nations = valid_nations
        self.universal = universal


def _load_items():
    path = os.path.join(os.path.dirname(__file__), "data", "items.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    items = {}
    for key, val in raw.items():
        items[key] = Item(
            val["name"],
            val["weight"],
            val.get("volume", 1),
            val.get("valid_nations"),
            val.get("universal", False),
        )
    return items


_ITEMS = _load_items()
_KEY_BY_ITEM = {v: k for k, v in _ITEMS.items()}

def item_key(item):
    """Return the key string for a given item object."""
    return _KEY_BY_ITEM.get(item)

globals().update(_ITEMS)

__all__ = ["Item", "item_key"] + list(_ITEMS.keys())
