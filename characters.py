import json
import os
import random

from items import BROKEN_PART
from equipment import (
    Equipment,
    CLOTHES_WITH_POCKETS,
    BASIC_BAG,
)

from locations import (
    NATIONS,
    DEFAULT_LOCATION_BY_NATION,
    LOCATIONS,
)

LOCATIONS_BY_KEY = {getattr(loc, "key", loc.name): loc for loc in LOCATIONS}

TIME_OF_DAY = ["아침", "낮", "밤"]

class Character:
    def __init__(self, name, personality, affiliation, job, schedule, agility=5):
        self.name = name
        self.personality = personality
        self.affiliation = affiliation
        self.job = job
        self.schedule = schedule  # time index -> Location
        if schedule:
            self.location = schedule.get(0, next(iter(schedule.values())))
        else:
            self.location = DEFAULT_LOCATION_BY_NATION[NATIONS[0]]
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


def _load_npcs():
    path = os.path.join(os.path.dirname(__file__), "data", "characters.json")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    loc_map = LOCATIONS_BY_KEY
    npcs = []
    for entry in raw.get("npcs", []):
        schedule = {int(k): loc_map[v] for k, v in entry.get("schedule", {}).items()}
        npcs.append(
            Character(
                entry["name"],
                entry.get("personality", ""),
                entry.get("affiliation", ""),
                entry.get("job", ""),
                schedule,
                agility=entry.get("agility", 5),
            )
        )
    return npcs


NPCS = _load_npcs()

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
        # 테스트용으로 기본 개조 부품 하나를 지급
        from items import IR_EYE_LEFT_PART
        self.inventory.append(IR_EYE_LEFT_PART)
        self.equipment = {
            "clothing": CLOTHES_WITH_POCKETS,
            "bag": None,
        }
        # installed body modifications by slot
        self.mods = {}

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
        if self.mods:
            print("개조: " + ", ".join(m.name for m in self.mods.values()))
        est = self.estimated_weight()
        est_text = str(est) if self.perception >= 10 else f"약 {est}"
        print(f"소지 무게: {est_text}/{self.carrying_capacity()}\n")

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
        self.recalc_derived_stats()

    def recalc_derived_stats(self):
        self.max_health = 100 + self.endurance * 10
        self.max_stamina = 100 + self.endurance * 5
        self.max_satiety = 100 + self.endurance * 2
        self.max_cleanliness = 100 + self.charisma * 2
        self.health = min(self.health, self.max_health)
        self.stamina = min(self.stamina, self.max_stamina)
        self.satiety = min(self.satiety, self.max_satiety)
        self.cleanliness = min(self.cleanliness, self.max_cleanliness)

    # Inventory helpers
    def carrying_capacity(self):
        cap = self.base_capacity
        for eq in self.equipment.values():
            if eq:
                cap += eq.capacity
        return cap

    def current_weight(self):
        return sum(item.weight for item in self.inventory)

    def estimate_value(self, value):
        """Return an estimated measurement influenced by perception."""
        if self.perception >= 10:
            return value
        error_ratio = (10 - self.perception) / 10
        factor = random.uniform(-error_ratio, error_ratio)
        return max(0, round(value * (1 + factor), 1))

    def estimated_weight(self):
        return sum(self.estimate_value(it.weight) for it in self.inventory)

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
                est_w = self.estimate_value(it.weight)
                est_v = self.estimate_value(getattr(it, "volume", 0))
                w_text = str(est_w) if self.perception >= 10 else f"약 {est_w}"
                v_text = str(est_v) if self.perception >= 10 else f"약 {est_v}"
                print(f"- {it.name} (무게 {w_text}, 부피 {v_text})")
            total = self.estimated_weight()
            if self.perception < 10:
                total_text = f"약 {total}"
            else:
                total_text = str(total)
            print(f"총 무게 {total_text}/{self.carrying_capacity()}")

    # Body modification helpers
    def install_mod(self, mod):
        if mod.required_item and mod.required_item not in self.inventory:
            print(f"{mod.required_item.name}이(가) 없어 개조를 진행할 수 없습니다.")
            return
        if mod.required_item and mod.required_item in self.inventory:
            self.inventory.remove(mod.required_item)
        current = self.mods.get(mod.slot)
        if current:
            print(f"{current.name}을(를) 제거하고 {mod.name}을(를) 장착합니다.")
            self.remove_mod(current)
        else:
            print(f"{mod.name}을(를) 장착합니다.")
        self.mods[mod.slot] = mod
        for stat, value in mod.stat_changes.items():
            setattr(self, stat, getattr(self, stat) + value)
        self.recalc_derived_stats()
        if mod.needs_brain and "brain" not in self.mods:
            print("뇌 인터페이스가 없어 고성능 기능을 이용할 수 없습니다.")

    def remove_mod(self, mod):
        if self.mods.get(mod.slot) != mod:
            return
        del self.mods[mod.slot]
        for stat, value in mod.stat_changes.items():
            setattr(self, stat, getattr(self, stat) - value)
        self.recalc_derived_stats()

