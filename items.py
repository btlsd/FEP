class Item:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


class Equipment(Item):
    """Equipment that increases carrying capacity."""
    def __init__(self, name, weight, capacity):
        super().__init__(name, weight)
        self.capacity = capacity


# Default equipment
CLOTHES_WITH_POCKETS = Equipment("주머니 달린 옷", 1, 5)
BASIC_BAG = Equipment("소형 가방", 2, 15)

# Example item players may find
BROKEN_PART = Item("부서진 부품", 2)
