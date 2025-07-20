class Item:
    def __init__(self, name, weight, volume=1):
        self.name = name
        self.weight = weight
        self.volume = volume


class Equipment(Item):
    """Equipment that increases carrying capacity."""

    def __init__(self, name, weight, capacity, can_enter_buildings=True, volume=1):
        super().__init__(name, weight, volume)
        self.capacity = capacity
        self.can_enter_buildings = can_enter_buildings


# Default equipment
CLOTHES_WITH_POCKETS = Equipment("주머니 달린 옷", 1, 5, volume=1)
BASIC_BAG = Equipment("소형 가방", 2, 15, volume=2)
MEDIUM_BAG = Equipment("중형 가방", 3, 25, volume=3)
LARGE_BAG = Equipment("대형 가방", 4, 35, volume=4)
TRAVEL_SUITCASE = Equipment("여행용 캐리어", 5, 40, volume=5)
SMALL_CART = Equipment("소형 카트", 6, 50, volume=6)
MEDIUM_CART = Equipment("중형 카트", 8, 70, volume=8)
LARGE_CART = Equipment("대형 카트", 10, 100, can_enter_buildings=False, volume=10)

# Example item players may find
BROKEN_PART = Item("부서진 부품", 2, 2)
