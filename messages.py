import json
import os
import random


def _load_messages():
    """Return a mapping of message lists keyed by category from ``messages.json``."""
    path = os.path.join(os.path.dirname(__file__), 'data', 'messages.json')
    try:
        with open(path, encoding='utf-8') as f:
            raw = json.load(f)
    except FileNotFoundError:
        return {}
    return raw.get('messages', raw)


_MESSAGES = _load_messages()


def get_message(key: str) -> str:
    """Return a random message for ``key`` or an empty string if none exist."""
    options = _MESSAGES.get(key, [])
    return random.choice(options) if options else ''


__all__ = ['get_message']
