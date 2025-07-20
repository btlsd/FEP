import random

from items import (
    CLOTHES_WITH_POCKETS,
    BASIC_BAG,
    BROKEN_PART,
    Item,
    Equipment,
)

from locations import (
    NATIONS,
    DEFAULT_LOCATION_BY_NATION,
    SEWER,
    STATION,
    MARKET,
    RESIDENTIAL,
)

TIME_OF_DAY = ["아침", "낮", "밤"]

class Character:
    def __init__(self, name, personality, affiliation, job, schedule, agility=5):
        self.name = name
        self.personality = personality
        self.affiliation = affiliation
        self.job = job
        self.schedule = schedule  # time index -> Location
        self.location = schedule.get(0, SEWER)
        self.affinity = 50
        self.health = 50
        self.agility = agility

    def update_location(self, time_idx):
        self.location = self.schedule.get(time_idx, self.location)

    def talk(self, player):
        if self.affinity >= 70:
            print(f"{self.name}은(는) 반갑게 당신을 맞이합니다.")
        elif self.affinity >= 30:
            print(f"{self.name}은(는) 무난하게 대화에 응합니다.")
        else:
            print(f"{self.name}은(는) 시큰둥한 반응을 보입니다.")
        gain = max(1, player.charisma // 2)
        self.affinity = min(100, self.affinity + gain)

    def trade(self, player):
        price = 5
        if player.money < price:
            print("돈이 부족합니다.")
            return
        player.money -= price
        player.satiety = min(player.max_satiety, player.satiety + 20 + player.endurance)
        player.stamina = min(player.max_stamina, player.stamina + 10 + player.strength // 2)
        print(f"{self.name}에게서 음식을 구입했습니다.")

    def lend_money(self, player):
        if self.affinity >= 60:
            amount = 10
            player.money += amount
            self.affinity -= 5
            print(f"{self.name}은(는) {amount}원을 빌려주었습니다.")
        else:
            print(f"{self.name}은(는) 돈을 빌려주지 않습니다.")

    def fight(self, player):
        from battle import start_battle

        start_battle(player, self)


NPCS = [
    Character(
        "상인 정",
        "친절한",
        "인류연합국 상인조합",
        "상인",
        {0: MARKET, 1: MARKET, 2: RESIDENTIAL},
    ),
    Character(
        "로봇 42",
        "차가운",
        "전계국",
        "경비",
        {0: STATION, 1: STATION, 2: STATION},
    ),
]

class Player:
    def __init__(self, name):
        self.name = name
        # 기본 능력치
        self.strength = 5
        self.perception = 5
        self.endurance = 5
        self.charisma = 5
        self.intelligence = 5
        self.agility = 5

        self.max_health = 100 + self.endurance * 10
        self.max_stamina = 100 + self.endurance * 5
        self.max_satiety = 100 + self.endurance * 2
        self.max_cleanliness = 100 + self.charisma * 2

        self.health = self.max_health
        self.stamina = self.max_stamina
        self.satiety = self.max_satiety
        self.cleanliness = self.max_cleanliness
        self.money = 20
        self.experience = 0
        self.day = 1
        self.location = DEFAULT_LOCATION_BY_NATION[NATIONS[0]]
        self.time = 0  # 0=아침,1=낮,2=밤

        # Inventory and equipment
        self.base_capacity = 5
        self.inventory = []
        self.equipment = {
            "clothing": CLOTHES_WITH_POCKETS,
            "bag": None,
        }

    def status(self):
        print(f"\n{self.day}일차 {TIME_OF_DAY[self.time]}")
        print(f"{self.name}의 상태:")
        print(f"건강: {self.health}/{self.max_health}")
        print(f"포만감: {self.satiety}/{self.max_satiety}")
        print(f"기력: {self.stamina}/{self.max_stamina}")
        print(f"청결도: {self.cleanliness}/{self.max_cleanliness}")
        print(f"돈: {self.money}원")
        print(f"경험치: {self.experience}")
        print(f"현재 위치: {self.location.name} ({self.location.nation.name})")
        nearby = [c.name for c in NPCS if c.location == self.location]
        if nearby:
            print("주변 인물: " + ", ".join(nearby))
        print()
        print(f"힘: {self.strength}")
        print(f"지각: {self.perception}")
        print(f"인내심: {self.endurance}")
        print(f"매력: {self.charisma}")
        print(f"지능: {self.intelligence}")
        print(f"민첩: {self.agility}")
        print(
            f"소지 무게: {self.current_weight()}/{self.carrying_capacity()}\n"
        )

    def is_alive(self):
        return self.health > 0

    def end_day(self):
        self.day += 1
        self.satiety -= 5
        self.cleanliness -= 10
        if self.satiety <= 0:
            self.health += self.satiety
            self.satiety = 0
        if self.stamina <= 0:
            self.health += self.stamina
            self.stamina = 0
        if self.health > self.max_health:
            self.health = self.max_health
        if self.cleanliness < 0:
            self.cleanliness = 0

    # Inventory helpers
    def carrying_capacity(self):
        cap = self.base_capacity
        for eq in self.equipment.values():
            if eq:
                cap += eq.capacity
        return cap

    def current_weight(self):
        return sum(item.weight for item in self.inventory)

    def can_carry(self, item):
        return self.current_weight() + item.weight <= self.carrying_capacity()

    def add_item(self, item):
        if self.can_carry(item):
            self.inventory.append(item)
            print(f"{item.name}을(를) 획득했습니다.")
        else:
            print(f"{item.name}은(는) 너무 무거워서 들 수 없습니다.")

    def show_inventory(self):
        if not self.inventory:
            print("소지품이 없습니다.")
        else:
            print("소지품:")
            for it in self.inventory:
                print(f"- {it.name} (무게 {it.weight})")
            print(f"총 무게 {self.current_weight()}/{self.carrying_capacity()}")

