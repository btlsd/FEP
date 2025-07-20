class Item:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


class Equipment(Item):
    """Equipment that increases carrying capacity."""

    def __init__(self, name, weight, capacity, can_enter_buildings=True):
        super().__init__(name, weight)
        self.capacity = capacity
        self.can_enter_buildings = can_enter_buildings


# Default equipment
CLOTHES_WITH_POCKETS = Equipment("주머니 달린 옷", 1, 5)
BASIC_BAG = Equipment("소형 가방", 2, 15)
MEDIUM_BAG = Equipment("중형 가방", 3, 25)
LARGE_BAG = Equipment("대형 가방", 4, 35)
TRAVEL_SUITCASE = Equipment("여행용 캐리어", 5, 40)
SMALL_CART = Equipment("소형 카트", 6, 50)
MEDIUM_CART = Equipment("중형 카트", 8, 70)
LARGE_CART = Equipment("대형 카트", 10, 100, can_enter_buildings=False)

# Example item players may find
BROKEN_PART = Item("부서진 부품", 2)
