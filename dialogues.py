import json
import os
from messages import get_message


def _load_dialogues():
    path = os.path.join(os.path.dirname(__file__), "data", "dialogues.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_DIALOGUES = _load_dialogues()

AGE_BRACKETS = [
    ("아기", 0, 3),
    ("미취학 아동", 3, 7),
    ("저학년", 7, 10),
    ("고학년", 10, 13),
    ("청소년", 13, 19),
    ("청년", 19, 30),
    ("성년", 30, 50),
    ("중년", 50, 65),
    ("노년", 65, 200),
]


def _age_group(age):
    for name, start, end in AGE_BRACKETS:
        if start <= age < end:
            return name
    return "노년"


def _personality_code(p):
    if not p:
        return None
    code = ""
    for key in "OCEAN":
        code += "H" if p.get(key, 50) >= 50 else "L"
    return code


def greeting(npc, player):
    d = _DIALOGUES.get("greetings", {})

    # 전계국 소속은 통일된 기계적 인사를 사용
    if (
        (npc.origin and "전계국" in npc.origin)
        or (npc.affiliation and "전계국" in npc.affiliation)
        or (npc.groups and "전계국" in npc.groups)
    ):
        line = d.get("origin", {}).get("전계국", "전계국 시스템이 당신을 인식했습니다, {player}.")
        return line.format(player=player.name, npc=npc.name)

    # 호감도가 낮으면 불친절한 인사말 사용
    if getattr(npc, "affinity", 50) < 30:
        bad = get_message("greeting_bad_mood")
        if bad:
            return bad.format(player=player.name, npc=npc.name)

    parts = []
    if player.fame >= 50 and "famous" in d.get("fame", {}):
        parts.append(d["fame"]["famous"])
    if npc.gender and npc.gender in d.get("gender", {}):
        parts.append(d["gender"][npc.gender])

    if npc.age is not None:
        group = _age_group(npc.age)
        if group in d.get("age", {}):
            parts.append(d["age"][group])

    if npc.job and npc.job in d.get("job", {}):
        parts.append(d["job"][npc.job])

    if npc.origin and npc.origin in d.get("origin", {}):
        parts.append(d["origin"][npc.origin])

    if npc.status and npc.status in d.get("status", {}):
        parts.append(d["status"][npc.status])

    code = _personality_code(npc.personality)
    if code and code in d.get("personality", {}):
        parts.append(d["personality"][code])

    if not parts:
        parts.append(d.get("default", "안녕하세요."))

    text = " ".join(parts)
    extra = get_message("greeting_simple")
    if extra:
        text += " " + extra
    return text.format(player=player.name, npc=npc.name)


def merchant_intro(npc, player):
    d = _DIALOGUES.get("merchant_trade", {})
    line = d.get("intro", "무엇을 찾으십니까?")
    return line.format(player=player.name, npc=npc.name)
