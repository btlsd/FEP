from items import Item

class Equipment(Item):
    """Equipment that increases carrying capacity or grants bonuses."""

    def __init__(self, name, weight, capacity, can_enter_buildings=True, volume=1):
        super().__init__(name, weight, volume)
        self.capacity = capacity
        self.can_enter_buildings = can_enter_buildings


class BodyMod:
    """Cybernetic or biological enhancement."""

    def __init__(
        self,
        name,
        slot,
        stat_changes=None,
        skills=None,
        flags=None,
        required_item=None,
        company=None,
        needs_brain=False,
    ):
        self.name = name
        self.slot = slot  # e.g. 'arm', 'eye'
        self.stat_changes = stat_changes or {}
        self.skills = skills or []
        self.flags = flags or []
        self.required_item = required_item
        self.company = company
        self.needs_brain = needs_brain


# Default equipment items
CLOTHES_WITH_POCKETS = Equipment("주머니 달린 옷", 1, 5, volume=1)
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
    {},
    flags=["interface"],
    required_item=BRAIN_INTERFACE_CHIP,
)
IR_EYE_LEFT = BodyMod(
    "아이리움 적외선 눈(왼쪽)",
    "eye_left",
    {"perception": 2},
    skills=["적외선 감지"],
    required_item=IR_EYE_LEFT_PART,
    company="아이리움",
)
IR_EYE_RIGHT = BodyMod(
    "아이리움 적외선 눈(오른쪽)",
    "eye_right",
    {"perception": 2},
    skills=["적외선 감지"],
    required_item=IR_EYE_RIGHT_PART,
    company="아이리움",
)
PREC_EYE_LEFT = BodyMod(
    "정밀전자 분석 눈(왼쪽)",
    "eye_left",
    {"perception": 2},
    skills=["정밀 조준"],
    required_item=PREC_EYE_LEFT_PART,
    company="정밀전자",
    needs_brain=True,
)
PREC_EYE_RIGHT = BodyMod(
    "정밀전자 분석 눈(오른쪽)",
    "eye_right",
    {"perception": 2},
    skills=["정밀 조준"],
    required_item=PREC_EYE_RIGHT_PART,
    company="정밀전자",
    needs_brain=True,
)
POWER_ARM = BodyMod("강화 팔", "arm", {"strength": 3})
LIGHT_LEG = BodyMod("경량 다리", "leg", {"agility": 2})

BODY_MODS = [
    BRAIN_INTERFACE,
    IR_EYE_LEFT,
    IR_EYE_RIGHT,
    PREC_EYE_LEFT,
    PREC_EYE_RIGHT,
    POWER_ARM,
    LIGHT_LEG,
]
