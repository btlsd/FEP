class Item:
    def __init__(self, name, weight, volume=1):
        self.name = name
        self.weight = weight
        self.volume = volume


# Example item players may find
BROKEN_PART = Item("부서진 부품", 2, 2)
