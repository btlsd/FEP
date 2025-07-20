class Item:
    def __init__(self, name, weight, volume=1):
        self.name = name
        self.weight = weight
        self.volume = volume


# Parts used for body modifications
IR_EYE_LEFT_PART = Item("아이리움 사이버 눈(좌)", 1)
IR_EYE_RIGHT_PART = Item("아이리움 사이버 눈(우)", 1)
PREC_EYE_LEFT_PART = Item("정밀전자 사이버 눈(좌)", 1)
PREC_EYE_RIGHT_PART = Item("정밀전자 사이버 눈(우)", 1)
BRAIN_INTERFACE_CHIP = Item("뇌 인터페이스 칩", 1)


# Example item players may find
BROKEN_PART = Item("부서진 부품", 2, 2)
