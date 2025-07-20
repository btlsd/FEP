from items import Item

class Equipment(Item):
    """Equipment that increases carrying capacity or grants bonuses."""

    def __init__(self, name, weight, capacity, can_enter_buildings=True, volume=1):
        super().__init__(name, weight, volume)
        self.capacity = capacity
        self.can_enter_buildings = can_enter_buildings


class BodyMod:
    """Cybernetic or biological enhancement."""

    def __init__(self, name, slot, stat_changes=None, skills=None, flags=None):
        self.name = name
        self.slot = slot  # e.g. 'arm', 'eye'
        self.stat_changes = stat_changes or {}
        self.skills = skills or []
        self.flags = flags or []


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
CYBER_EYE = BodyMod("강화 시야", "eye", {"perception": 2}, skills=["야간시"])
POWER_ARM = BodyMod("강화 팔", "arm", {"strength": 3})
LIGHT_LEG = BodyMod("경량 다리", "leg", {"agility": 2})

BODY_MODS = [CYBER_EYE, POWER_ARM, LIGHT_LEG]
