import json
import os
import random


def _load_dialogues():
    path = os.path.join(os.path.dirname(__file__), "data", "dialogues.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_DIALOGUES = _load_dialogues()

def greeting(npc, player):
    d = _DIALOGUES.get("greetings", {})
    candidates = []
    # job-specific
    if npc.job and npc.job in d.get("job", {}):
        candidates.append(d["job"][npc.job])
    # gender-specific
    if npc.gender and npc.gender in d.get("gender", {}):
        candidates.append(d["gender"][npc.gender])
    # origin-specific
    if npc.origin and npc.origin in d.get("origin", {}):
        candidates.append(d["origin"][npc.origin])
    # age-related
    if hasattr(npc, "age") and npc.age is not None and npc.age >= 60 and "age_old" in d:
        candidates.append(d["age_old"])
    # personality based on extraversion
    extr = 50
    if npc.personality and isinstance(npc.personality, dict):
        extr = npc.personality.get("E", 50)
    if extr >= 60 and "high_E" in d.get("personality", {}):
        candidates.append(d["personality"]["high_E"])
    elif extr <= 40 and "low_E" in d.get("personality", {}):
        candidates.append(d["personality"]["low_E"])
    # default
    candidates.append(d.get("default", "안녕하세요."))
    text = random.choice(candidates)
    return text.format(player=player.name)
