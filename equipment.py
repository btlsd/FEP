from items import Item

class Equipment(Item):
    """Equipment that increases carrying capacity or grants bonuses."""

    def __init__(
        self,
        name,
        weight,
        capacity,
        can_enter_buildings=True,
        volume=1,
        stat_changes=None,
        flags=None,
    ):
        super().__init__(name, weight, volume)
        self.capacity = capacity
        self.can_enter_buildings = can_enter_buildings
        self.stat_changes = stat_changes or {}
        self.flags = flags or []


class BodyMod:
    """Cybernetic or biological enhancement."""

    def __init__(
        self,
        name,
        slot,
        stat_add=None,
        stat_mult=None,
        skills=None,
        flags=None,
        required_item=None,
        company=None,
        needs_brain=False,
    ):
        self.name = name
        self.slot = slot  # e.g. 'arm', 'eye'
        self.stat_add = stat_add or {}
        self.stat_mult = stat_mult or {}
        self.skills = skills or []
        self.flags = flags or []
        self.required_item = required_item
        self.company = company
        self.needs_brain = needs_brain


# Default equipment items
CLOTHES_WITH_POCKETS = Equipment("주머니 달린 옷", 1, 5, volume=1)
BASIC_UNIFORM = Equipment("경찰복", 3, 5, volume=2, flags=["police_look"])
BASIC_BADGE = Equipment("경찰 배지", 0.1, 0, volume=0.1, flags=["police"])
BASIC_BAG = Equipment("소형 가방", 2, 15, volume=2)
MEDIUM_BAG = Equipment("중형 가방", 3, 25, volume=3)
LARGE_BAG = Equipment("대형 가방", 4, 35, volume=4)
TRAVEL_SUITCASE = Equipment("여행용 캐리어", 5, 40, volume=5)
SMALL_CART = Equipment("소형 카트", 6, 50, volume=6)
MEDIUM_CART = Equipment("중형 카트", 8, 70, volume=8)
LARGE_CART = Equipment("대형 카트", 10, 100, can_enter_buildings=False, volume=10)

# Example body modifications
from items import (
    IR_EYE_LEFT_PART,
    IR_EYE_RIGHT_PART,
    PREC_EYE_LEFT_PART,
    PREC_EYE_RIGHT_PART,
    BRAIN_INTERFACE_CHIP,
)

BRAIN_INTERFACE = BodyMod(
    "신경 인터페이스",
    "brain",
    stat_add={},
    flags=["interface"],
    required_item=BRAIN_INTERFACE_CHIP,
)
IR_EYE_LEFT = BodyMod(
    "아이리움 적외선 눈(왼쪽)",
    "eye_left",
    stat_add={"perception": 2},
    skills=["적외선 감지"],
    required_item=IR_EYE_LEFT_PART,
    company="아이리움",
)
IR_EYE_RIGHT = BodyMod(
    "아이리움 적외선 눈(오른쪽)",
    "eye_right",
    stat_add={"perception": 2},
    skills=["적외선 감지"],
    required_item=IR_EYE_RIGHT_PART,
    company="아이리움",
)
PREC_EYE_LEFT = BodyMod(
    "정밀전자 분석 눈(왼쪽)",
    "eye_left",
    stat_add={"perception": 2},
    skills=["정밀 조준"],
    required_item=PREC_EYE_LEFT_PART,
    company="정밀전자",
    needs_brain=True,
)
PREC_EYE_RIGHT = BodyMod(
    "정밀전자 분석 눈(오른쪽)",
    "eye_right",
    stat_add={"perception": 2},
    skills=["정밀 조준"],
    required_item=PREC_EYE_RIGHT_PART,
    company="정밀전자",
    needs_brain=True,
)
POWER_ARM = BodyMod("강화 팔", "arm", stat_add={"strength": 3})
LIGHT_LEG = BodyMod("경량 다리", "leg", stat_add={"agility": 2})
MUSCLE_REPLACE = BodyMod(
    "근섬유 치환",
    "body",
    stat_add={"strength": 2, "agility": 1},
    stat_mult={"strength": 1.1, "agility": 1.1},
    flags=["muscle_replace"],
)

# Hidden weapon compartment allowing small weapons to be concealed
CONCEALED_SLOT = BodyMod(
    "은닉 무기 슬롯",
    "arm",
    flags=["conceal_slot"],
)

EXO_SUIT = Equipment(
    "엑소 슈트",
    8,
    20,
    can_enter_buildings=False,
    stat_changes={"strength": 2, "agility": 2},
    flags=["exosuit"],
    volume=5,
)

# Exo suit with jetpack allowing city travel
JETPACK_EXO_SUIT = Equipment(
    "제트팩 엑소 슈트",
    10,
    25,
    can_enter_buildings=False,
    stat_changes={"strength": 2, "agility": 3},
    flags=["exosuit", "jetpack"],
    volume=6,
)

BODY_MODS = [
    BRAIN_INTERFACE,
    IR_EYE_LEFT,
    IR_EYE_RIGHT,
    PREC_EYE_LEFT,
    PREC_EYE_RIGHT,
    POWER_ARM,
    LIGHT_LEG,
    MUSCLE_REPLACE,
    CONCEALED_SLOT,
]

# Lookup dictionaries for saving/loading
EQUIPMENT_BY_NAME = {
    eq.name: eq
    for eq in [
        CLOTHES_WITH_POCKETS,
        BASIC_UNIFORM,
        BASIC_BADGE,
        BASIC_BAG,
        MEDIUM_BAG,
        LARGE_BAG,
        TRAVEL_SUITCASE,
        SMALL_CART,
        MEDIUM_CART,
        LARGE_CART,
        EXO_SUIT,
        JETPACK_EXO_SUIT,
    ]
}

BODY_MODS_BY_NAME = {mod.name: mod for mod in BODY_MODS}
