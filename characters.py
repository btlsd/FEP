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
    NATION_BY_NAME,
    DEFAULT_LOCATION_BY_NATION,
    LOCATIONS,
)

LOCATIONS_BY_KEY = {getattr(loc, "key", loc.name): loc for loc in LOCATIONS}

# 새벽, 아침, 오전, 오후, 저녁, 밤의 여섯 구간
TIME_OF_DAY = ["새벽", "아침", "오전", "오후", "저녁", "밤"]

class Character:
    def __init__(
        self,
        name,
        personality,
        affiliation,
        job,
        schedule,
        agility=5,
        age=None,
        gender=None,
        origin=None,
        status=None,
        shop=None,
    ):
        self.name = name
        self.personality = personality or {}
        self.affiliation = affiliation
        self.job = job
        self.age = age
        self.gender = gender
        self.origin = origin
        self.status = status
        self.schedule = schedule  # time index -> Location
        if schedule:
            self.location = schedule.get(0, next(iter(schedule.values())))
        else:
            self.location = DEFAULT_LOCATION_BY_NATION[NATIONS[0]]
        if origin and origin in NATION_BY_NAME:
            self.currency = NATION_BY_NAME[origin].currency
        else:
            self.currency = self.location.nation.currency
        self.affinity = 50
        self.shop = shop or {}
        self.health = 50
        self.agility = agility

    def update_location(self, time_idx):
        self.location = self.schedule.get(time_idx, self.location)

    def talk(self, player):
        from dialogues import greeting

        print(greeting(self, player))
        gain = max(1, player.charisma // 2)
        self.affinity = min(100, self.affinity + gain)

    def trade(self, player):
        if self.job != "상인" or not self.shop:
            price = 5
            currency = self.currency
            if not player.spend_money(price, currency):
                print("돈이 부족합니다.")
                return
            player.satiety = min(player.max_satiety, player.satiety + 20 + player.endurance)
            player.stamina = min(player.max_stamina, player.stamina + 10 + player.strength // 2)
            print(f"{self.name}에게서 음식을 구입했습니다.")
            return

        from dialogues import merchant_intro

        print(merchant_intro(self, player))
        print("1. 현금 거래")
        print("2. 물물 교환")
        choice = input("> ").strip()
        items = list(self.shop.items())
        if choice == "1":
            print("구입할 물건을 선택하세요:")
            for i, (item, price) in enumerate(items, start=1):
                print(f"{i}. {item.name} - {price}{self.currency}")
            sel = input("> ").strip()
            if sel.isdigit():
                idx = int(sel) - 1
                if 0 <= idx < len(items):
                    item, price = items[idx]
                    pay_price = price
                    pay_currency = self.currency
                    if not player.has_money(price, pay_currency):
                        pay_price = int(price * 1.2)
                        for cur in player.money:
                            if cur != pay_currency and player.has_money(pay_price, cur):
                                pay_currency = cur
                                break
                        else:
                            print("돈이 부족합니다.")
                            return
                    if not player.can_carry(item):
                        print("무게 때문에 들 수 없습니다.")
                        return
                    player.spend_money(pay_price, pay_currency)
                    player.add_item(item)
                    print(f"{pay_currency}로 {pay_price} 지불했습니다.")
                else:
                    print("잘못된 선택입니다.")
            else:
                print("거래를 취소했습니다.")
        elif choice == "2":
            if not player.inventory:
                print("교환할 물건이 없습니다.")
                return
            print("제시할 물건을 선택하세요:")
            for i, it in enumerate(player.inventory, start=1):
                print(f"{i}. {it.name}")
            sel = input("> ").strip()
            if not sel.isdigit():
                print("거래를 취소했습니다.")
                return
            give_idx = int(sel) - 1
            if not (0 <= give_idx < len(player.inventory)):
                print("잘못된 선택입니다.")
                return
            offered = player.inventory.pop(give_idx)
            print("받을 물건을 선택하세요:")
            for i, (item, _) in enumerate(items, start=1):
                print(f"{i}. {item.name}")
            sel = input("> ").strip()
            if sel.isdigit():
                idx = int(sel) - 1
                if 0 <= idx < len(items):
                    item = items[idx][0]
                    if not player.can_carry(item):
                        print("무게 때문에 들 수 없습니다.")
                        player.inventory.append(offered)
                    else:
                        player.add_item(item)
                        print("교환이 완료되었습니다.")
                else:
                    player.inventory.append(offered)
                    print("잘못된 선택입니다.")
            else:
                player.inventory.append(offered)
                print("거래를 취소했습니다.")
        else:
            print("거래를 취소했습니다.")

    def lend_money(self, player):
        if self.affinity >= 60:
            amount = 10
            currency = self.location.nation.currency
            player.add_money(amount, currency)
            self.affinity -= 5
            print(f"{self.name}은(는) {amount}{currency}을 빌려주었습니다.")
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
        shop = None
        if "shop" in entry:
            shop = {}
            from items import _ITEMS
            for key, price in entry["shop"].items():
                if key in _ITEMS:
                    shop[_ITEMS[key]] = price
        npcs.append(
            Character(
                entry["name"],
                entry.get("personality", {}),
                entry.get("affiliation", ""),
                entry.get("job", ""),
                schedule,
                agility=entry.get("agility", 5),
                age=entry.get("age"),
                gender=entry.get("gender"),
                origin=entry.get("origin"),
                status=entry.get("status"),
                shop=shop,
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
        # 각 국가별 화폐를 기록한다
        self.money = {NATIONS[0].currency: 20}
        self.experience = 0
        self.day = 1
        self.location = DEFAULT_LOCATION_BY_NATION[NATIONS[0]]
        # 시간은 0~5까지의 4시간 간격 구간으로 취급한다
        self.time = 0  # 0=새벽,1=아침,2=오전,3=오후,4=저녁,5=밤

        # Inventory and equipment
        self.base_capacity = 5
        self.inventory = []
        # 테스트용으로 기본 개조 부품 하나를 지급
        from items import IR_EYE_LEFT_PART, BOARDING_PASS
        self.inventory.append(IR_EYE_LEFT_PART)
        self.inventory.append(BOARDING_PASS)
        self.equipment = {
            "clothing": CLOTHES_WITH_POCKETS,
            "bag": None,
        }
        # installed body modifications by slot
        self.mods = {}
        self.flags = set()

    # Flag helpers
    def has_flag(self, flag):
        return flag in self.flags

    def add_flag(self, flag):
        self.flags.add(flag)

    # Money helpers
    def add_money(self, amount, currency):
        self.money[currency] = self.money.get(currency, 0) + amount

    def spend_money(self, amount, currency):
        if self.money.get(currency, 0) >= amount:
            self.money[currency] -= amount
            return True
        return False

    def has_money(self, amount, currency):
        return self.money.get(currency, 0) >= amount

    def status(self):
        print(f"\n{self.day}일차 {TIME_OF_DAY[self.time]}")
        print(f"{self.name}의 상태:")
        print(f"건강: {self.health}/{self.max_health}")
        print(f"포만감: {self.satiety}/{self.max_satiety}")
        print(f"기력: {self.stamina}/{self.max_stamina}")
        print(f"청결도: {self.cleanliness}/{self.max_cleanliness}")
        money_str = ", ".join(f"{amt}{cur}" for cur, amt in self.money.items())
        print(f"보유 화폐: {money_str}")
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
        loc = self.location
        if not getattr(loc, "mod_shop", None):
            print("이곳에서는 개조 시술을 받을 수 없습니다.")
            return
        if mod.required_item and mod.required_item not in self.inventory:
            print(f"{mod.required_item.name}이(가) 없어 개조를 진행할 수 없습니다.")
            return
        if mod.required_item and mod.required_item in self.inventory:
            self.inventory.remove(mod.required_item)
        if loc.mod_shop == "illegal":
            roll = random.random()
            if roll < 0.2:
                print("시술이 실패해 부상을 입었습니다!")
                self.health -= 10
                return
            elif roll < 0.4:
                print("가품 부품이 사용되어 효과가 없습니다.")
                return
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

