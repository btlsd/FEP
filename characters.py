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
    SHELTER,
    APARTMENT,
)
from utils import choose_option

LOCATIONS_BY_KEY = {getattr(loc, "key", loc.name): loc for loc in LOCATIONS}

# 새벽, 아침, 오전, 오후, 저녁, 밤의 여섯 구간
TIME_OF_DAY = ["새벽", "아침", "오전", "오후", "저녁", "밤"]
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
MONTH_NAMES = [f"{m}월" for m in range(1, 13)]
SEASONS = ["봄", "여름", "가을", "겨울"]
WEATHER_BY_SEASON = {
    0: ["맑음", "비", "흐림"],
    1: ["맑음", "비", "무더위"],
    2: ["맑음", "비", "바람"],
    3: ["맑음", "눈", "눈보라"],
}

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
        blueprints=None,
        blueprint_drop=None,
        inventory=None,
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
        self.blueprints = blueprints or {}
        self.blueprint_drop = blueprint_drop
        self.inventory = inventory or []
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
        items = list(self.shop.items())
        bp_items = list(self.blueprints.items())
        choice = choose_option(["현금 거래", "물물 교환", "설계도 구매"])
        if choice is None:
            print("거래를 취소했습니다.")
            return
        if choice == 0:
            idx = choose_option([f"{it.name} - {price}{self.currency}" for it, price in items])
            if idx is None:
                print("거래를 취소했습니다.")
                return
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
        elif choice == 1:
            if not player.inventory:
                print("교환할 물건이 없습니다.")
                return
            give_idx = choose_option([it.name for it in player.inventory])
            if give_idx is None:
                print("거래를 취소했습니다.")
                return
            offered = player.inventory.pop(give_idx)
            recv_idx = choose_option([it.name for it, _ in items])
            if recv_idx is None:
                player.inventory.append(offered)
                print("거래를 취소했습니다.")
                return
            item = items[recv_idx][0]
            if not player.can_carry(item):
                print("무게 때문에 들 수 없습니다.")
                player.inventory.append(offered)
                return
            player.add_item(item)
            print("교환이 완료되었습니다.")
        else:
            if not bp_items:
                print("구매할 설계도가 없습니다.")
                return
            from items import _ITEMS
            idx = choose_option([f"{_ITEMS[key].name} 설계도 - {price}{self.currency}" for key, price in bp_items])
            if idx is None:
                print("거래를 취소했습니다.")
                return
            key, price = bp_items[idx]
            if not player.spend_money(price, self.currency):
                print("돈이 부족합니다.")
                return
            player.add_blueprint_progress(key, 100)

    def lend_money(self, player):
        if self.affinity >= 60:
            amount = 10
            currency = self.location.nation.currency
            player.add_money(amount, currency)
            self.affinity -= 5
            print(f"{self.name}은(는) {amount}{currency}을 빌려주었습니다.")
        else:
            print(f"{self.name}은(는) 돈을 빌려주지 않습니다.")

    def fight(self, player, ambush=None):
        from battle import start_battle
        if not getattr(self, "weapon", None):
            for it in self.inventory:
                if getattr(it, "damage", 0) > 0:
                    self.weapon = it
                    break
        return start_battle(player, self, ambush)


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
        blueprints = None
        if "blueprints" in entry:
            from items import _ITEMS
            blueprints = {key: price for key, price in entry["blueprints"].items() if key in _ITEMS}
        inventory = None
        if "inventory" in entry:
            from items import _ITEMS
            inventory = [_ITEMS[key] for key in entry["inventory"] if key in _ITEMS]
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
                blueprints=blueprints,
                blueprint_drop=entry.get("blueprint_drop"),
                inventory=inventory,
            )
        )
    return npcs


NPCS = _load_npcs()

class Player:
    def __init__(self, name, gender="none", stats=None):
        self.name = name
        self.gender = gender
        stats = stats or {}
        self.age = stats.get("age", 20)
        self.age_days = 0
        # 기본 능력치
        self.strength = stats.get("strength", 5)
        self.perception = stats.get("perception", 5)
        self.endurance = stats.get("endurance", 5)
        self.charisma = stats.get("charisma", 5)
        self.intelligence = stats.get("intelligence", 5)
        self.agility = stats.get("agility", 5)
        self.intuition = stats.get("intuition", 5)

        self.base_stats = {
            "strength": self.strength,
            "perception": self.perception,
            "endurance": self.endurance,
            "charisma": self.charisma,
            "intelligence": self.intelligence,
            "agility": self.agility,
            "intuition": self.intuition,
        }

        self.max_health = 100 + self.endurance * 10
        self.max_stamina = 100 + self.endurance * 5
        self.max_satiety = 100 + self.endurance * 2
        self.max_cleanliness = 100 + self.charisma * 2
        self.max_satisfaction = 100 + (self.charisma + self.intelligence) * 2

        self.health = self.max_health
        self.stamina = self.max_stamina
        self.satiety = self.max_satiety
        self.cleanliness = self.max_cleanliness
        self.satisfaction = self.max_satisfaction
        # 각 국가별 화폐를 기록한다
        self.money = {NATIONS[0].currency: 20}
        self.bank = {n.currency: 0 for n in NATIONS}
        self.experience = 0
        self.day = 1
        self.weekday = 0  # 0=월,1=화,2=수,3=목,4=금,5=토,6=일
        self.location = DEFAULT_LOCATION_BY_NATION[NATIONS[0]]
        self.home = SHELTER
        self.loan_balance = 0
        self.monthly_rent = 0
        self.arrears = 0
        self.kidnap_due = False
        self.home_ambush = False
        self.month_day = 1
        self.month = 1
        self.season = 0
        self.weather = random.choice(WEATHER_BY_SEASON[self.season])
        self.shower_count = 0
        self.appliance_usage = 0
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
            "accessory": None,
        }
        self.weapon = None
        # installed body modifications by slot
        self.mods = {}
        self.flags = set()
        self.job = None
        # blueprint progress by item key
        self.blueprints = {}
        self.skills = set()
        self.max_skills = 3 + self.intelligence // 2

        self.flags.update(self.equipment["clothing"].flags)
        self.recalculate_stats()
        self.update_memory_capacity()
        self.update_smell()

    # Flag helpers
    def has_flag(self, flag):
        return flag in self.flags

    def add_flag(self, flag):
        self.flags.add(flag)

    # Money helpers
    def add_money(self, amount, currency):
        self.money[currency] = self.money.get(currency, 0) + amount

    def deposit(self, amount, currency):
        if self.spend_money(amount, currency):
            self.bank[currency] = self.bank.get(currency, 0) + amount
            return True
        return False

    def withdraw(self, amount, currency):
        if self.bank.get(currency, 0) >= amount and amount > 0:
            self.bank[currency] -= amount
            self.add_money(amount, currency)
            return True
        return False

    def spend_money(self, amount, currency):
        if self.money.get(currency, 0) >= amount:
            self.money[currency] -= amount
            return True
        return False

    def has_money(self, amount, currency):
        return self.money.get(currency, 0) >= amount

    def describe_stat(self, value):
        if value >= 20:
            return "초인적이다"
        if value >= 16:
            return "매우 뛰어난 편이다"
        if value >= 13:
            return "준수한 편이다"
        if value >= 8:
            return "평범한 수준이다"
        if value >= 5:
            return "다소 부족한 편이다"
        return "매우 낮은 편이다"

    def update_memory_capacity(self):
        base = 3 + self.intelligence // 2
        bonus = sum(getattr(m, "memory_bonus", 0) for m in self.mods.values())
        self.max_skills = base + bonus

    def status(self):
        print(f"\n{self.day}일차 {WEEKDAYS[self.weekday]}요일 {TIME_OF_DAY[self.time]}")
        print(f"{self.name}의 상태:")
        print(f"건강: {self.health}/{self.max_health}")
        print(f"포만감: {self.satiety}/{self.max_satiety}")
        print(f"기력: {self.stamina}/{self.max_stamina}")
        print(f"청결도: {self.cleanliness}/{self.max_cleanliness}")
        print(f"만족감: {self.satisfaction}/{self.max_satisfaction}")
        money_str = ", ".join(f"{amt}{cur}" for cur, amt in self.money.items())
        print(f"보유 화폐: {money_str}")
        bank_str = ", ".join(f"{amt}{cur}" for cur, amt in self.bank.items() if amt)
        if bank_str:
            print(f"은행 예금: {bank_str}")
        print(f"경험치: {self.experience}")
        print(f"현재 위치: {self.location.name} ({self.location.nation.name})")
        print(f"거주지: {self.home.name}")
        if self.loan_balance:
            print(f"대출 잔액: {self.loan_balance}{self.home.nation.currency}")
        print(f"직업: {self.job or '없음'}")
        print(f"성별: {self.gender}")
        print(f"나이: {self.age}")
        if self.skills:
            print("습득 기술: " + ", ".join(sorted(self.skills)))
        nearby = [c.name for c in NPCS if c.location == self.location]
        if nearby:
            print("주변 인물: " + ", ".join(nearby))
        print()
        for key, label in [
            ("strength", "근력"),
            ("perception", "지각"),
            ("endurance", "인내심"),
            ("charisma", "매력"),
            ("intelligence", "지능"),
            ("agility", "민첩"),
            ("intuition", "직감"),
        ]:
            val = getattr(self, key)
            if "brain" in self.mods:
                print(f"{label}: {val}")
            else:
                print(f"{label}: {self.describe_stat(val)}")
        if self.mods:
            print("개조: " + ", ".join(m.name for m in self.mods.values()))
        eq_list = [f"{slot}:{eq.name}" for slot, eq in self.equipment.items() if eq]
        if eq_list:
            print("장비: " + ", ".join(eq_list))
        if self.weapon:
            print(f"무기: {self.weapon.name}")
        est = self.estimated_weight()
        est_text = str(est) if self.perception >= 10 else f"약 {est}"
        print(f"소지 무게: {est_text}/{self.carrying_capacity()}")
        print()

    def is_alive(self):
        return self.health > 0

    def pass_time(self):
        """Reduce basic needs each time segment."""
        self.satiety -= 2
        self.stamina -= 1
        self.cleanliness -= 1
        self.satisfaction -= 1
        if self.satiety < 0:
            self.health += self.satiety
            self.satiety = 0
        if self.stamina < 0:
            self.health += self.stamina
            self.stamina = 0
        if self.cleanliness < 0:
            self.cleanliness = 0
        if self.satisfaction < 0:
            self.health -= 1
            self.satisfaction = 0
        self.update_smell()

    def update_smell(self):
        """Adjust charisma if the player smells bad from low cleanliness."""
        if self.cleanliness < 20:
            if "smelly" not in self.flags:
                self.flags.add("smelly")
                self.charisma -= 2
        else:
            if "smelly" in self.flags:
                self.flags.remove("smelly")
                self.charisma += 2

    def end_day(self):
        self.day += 1
        self.weekday = (self.weekday + 1) % 7
        self.month_day += 1
        self.age_days += 1
        if self.age_days >= 365:
            self.age += 1
            self.age_days -= 365
        self.satiety -= 5
        self.cleanliness -= 10
        self.satisfaction -= 5
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
        if self.satisfaction < 0:
            self.satisfaction = 0
        self.recalc_derived_stats()
        if self.month_day > 30:
            self.month_day = 1
            self.month += 1
            if self.month % 3 == 1:
                self.season = (self.season + 1) % 4
            if self.month > 12:
                self.month = 1
            self.process_monthly_costs()
        self.weather = random.choice(WEATHER_BY_SEASON[self.season])
        self.update_smell()

    def recalc_derived_stats(self):
        self.max_health = 100 + self.endurance * 10
        self.max_stamina = 100 + self.endurance * 5
        self.max_satiety = 100 + self.endurance * 2
        self.max_cleanliness = 100 + self.charisma * 2
        self.max_satisfaction = 100 + (self.charisma + self.intelligence) * 2
        self.health = min(self.health, self.max_health)
        self.stamina = min(self.stamina, self.max_stamina)
        self.satiety = min(self.satiety, self.max_satiety)
        self.cleanliness = min(self.cleanliness, self.max_cleanliness)
        self.satisfaction = min(self.satisfaction, self.max_satisfaction)

    def recalculate_stats(self):
        for key, val in self.base_stats.items():
            setattr(self, key, val)
        for eq in self.equipment.values():
            if eq:
                for stat, add in getattr(eq, "stat_changes", {}).items():
                    setattr(self, stat, getattr(self, stat) + add)
        for mod in self.mods.values():
            for stat, add in mod.stat_add.items():
                setattr(self, stat, getattr(self, stat) + add)
        for eq in self.equipment.values():
            if eq:
                for stat, mul in getattr(eq, "stat_mult", {}).items():
                    setattr(self, stat, int(getattr(self, stat) * mul))
        for mod in self.mods.values():
            for stat, mul in mod.stat_mult.items():
                setattr(self, stat, int(getattr(self, stat) * mul))
        self.recalc_derived_stats()
        self.update_memory_capacity()
        self.update_smell()

    def start_job(self, job):
        self.job = job
        if self.home == SHELTER:
            cur = self.location.nation.currency
            self.loan_balance = 50
            self.monthly_rent = 5
            self.add_money(50, cur)
            self.home = APARTMENT
            self.location = APARTMENT
            print(f"정부 지원으로 50{cur}을 빌리고 임대 아파트에 입주했습니다.")

    def process_monthly_costs(self):
        currency = self.home.nation.currency
        # 월급 입금 (월급제 직업)
        from game import JOB_PAY
        info = JOB_PAY.get(self.job)
        if info and info.get("type") == "monthly":
            amount = info.get("rate", 0)
            self.bank[currency] = self.bank.get(currency, 0) + amount
            print(f"월급 {amount}{currency}이 은행에 입금되었습니다.")
        loan_payment = min(10, self.loan_balance)
        self.loan_balance -= loan_payment
        utilities = self.shower_count * 0.5 + self.appliance_usage * 0.5
        if self.season in (1, 3):
            utilities += 5
        total = loan_payment + self.monthly_rent + utilities
        if total > 0:
            if not self.spend_money(total, currency):
                print(f"생활비 {total}{currency}를 지불할 돈이 부족합니다.")
                self.arrears += 1
                if self.arrears >= 3:
                    self.kidnap_due = True
            else:
                print(f"생활비 {total}{currency}를 납부했습니다.")
                self.arrears = 0
        self.shower_count = 0
        self.appliance_usage = 0
        # 이자 지급
        for cur, bal in self.bank.items():
            interest = int(bal * 0.01)
            if interest:
                self.bank[cur] += interest
                print(f"{cur} 예금 이자로 {interest}{cur}이 추가되었습니다.")

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

    def learn_skill(self, skill):
        if skill in self.skills:
            print(f"이미 {skill}을(를) 알고 있습니다.")
            return
        if len(self.skills) >= self.max_skills:
            print("더 이상 새로운 지식을 기억하기 어렵습니다.")
            return
        self.skills.add(skill)
        print(f"{skill}을(를) 습득했습니다.")

    # Blueprint helpers
    def add_blueprint_progress(self, item_key, amount):
        from items import _ITEMS

        item = _ITEMS[item_key]
        progress = self.blueprints.get(item_key, 0) + amount
        if progress > 100:
            progress = 100
        self.blueprints[item_key] = progress
        if progress >= 100:
            print(f"{item.name} 설계도가 완성되었습니다!")
        else:
            print(f"{item.name} 설계도 진행률 {progress}%")

    def has_blueprint(self, item_key):
        return self.blueprints.get(item_key, 0) >= 100

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
                line = f"- {it.name} (무게 {w_text}, 부피 {v_text})"
                if getattr(it, "weapon_type", None) in ["둔기", "냉병기"]:
                    mat = getattr(it, "material", "-")
                    qual = getattr(it, "quality", 1.0)
                    line += f" [재질: {mat}, 제련도: {qual}]"
                print(line)
            total = self.estimated_weight()
            if self.perception < 10:
                total_text = f"약 {total}"
            else:
                total_text = str(total)
            print(f"총 무게 {total_text}/{self.carrying_capacity()}")
        if self.weapon:
            print(f"장착 무기: {self.weapon.name}")

    def equip(self, item, slot):
        from equipment import Equipment

        if not isinstance(item, Equipment):
            print("장비할 수 없는 아이템입니다.")
            return
        current = self.equipment.get(slot)
        if current is item:
            print("이미 장착 중입니다.")
            return
        if current:
            self.unequip(slot)
        if item in self.inventory:
            self.inventory.remove(item)
        self.equipment[slot] = item
        self.flags.update(item.flags)
        self.recalculate_stats()
        print(f"{item.name}을(를) 장착했습니다.")

    def unequip(self, slot):
        item = self.equipment.get(slot)
        if not item:
            return
        self.inventory.append(item)
        for flag in getattr(item, "flags", []):
            self.flags.discard(flag)
        self.equipment[slot] = None
        self.recalculate_stats()

    def equip_weapon(self, item):
        if getattr(item, "damage", 0) <= 0:
            print("무기로 사용할 수 없습니다.")
            return
        if self.weapon is item:
            print("이미 장착한 무기입니다.")
            return
        if self.weapon:
            self.inventory.append(self.weapon)
        if item in self.inventory:
            self.inventory.remove(item)
        self.weapon = item
        print(f"{item.name}을(를) 무기로 장착했습니다.")

    def unequip_weapon(self):
        if self.weapon:
            self.inventory.append(self.weapon)
            print(f"{self.weapon.name}을(를) 해제했습니다.")
            self.weapon = None

    def show_data(self):
        if not self.blueprints:
            print("획득한 데이터가 없습니다.")
            return
        from items import _ITEMS
        print("설계도 진행도:")
        for key, prog in self.blueprints.items():
            name = _ITEMS[key].name
            print(f"- {name} {prog}%")

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
        self.flags.update(mod.flags)
        self.recalculate_stats()
        if mod.needs_brain and "brain" not in self.mods:
            print("뇌 인터페이스가 없어 고성능 기능을 이용할 수 없습니다.")

    def remove_mod(self, mod):
        if self.mods.get(mod.slot) != mod:
            return
        del self.mods[mod.slot]
        for flag in mod.flags:
            self.flags.discard(flag)
        self.recalculate_stats()

    # Saving and loading
    def to_dict(self):
        from items import item_key

        return {
            "name": self.name,
            "gender": self.gender,
            "stats": self.base_stats,
            "age": self.age,
            "age_days": self.age_days,
            "health": self.health,
            "stamina": self.stamina,
            "satiety": self.satiety,
            "cleanliness": self.cleanliness,
            "satisfaction": self.satisfaction,
            "money": self.money,
            "bank": self.bank,
            "experience": self.experience,
            "day": self.day,
            "weekday": self.weekday,
            "time": self.time,
            "location": getattr(self.location, "key", self.location.name),
            "home": getattr(self.home, "key", self.home.name),
            "loan": self.loan_balance,
            "rent": self.monthly_rent,
            "arrears": self.arrears,
            "kidnap_due": self.kidnap_due,
            "home_ambush": self.home_ambush,
            "month_day": self.month_day,
            "month": self.month,
            "season": self.season,
            "weather": self.weather,
            "inventory": [item_key(it) for it in self.inventory],
            "equipment": {slot: eq.name if eq else None for slot, eq in self.equipment.items()},
            "weapon": item_key(self.weapon) if self.weapon else None,
            "mods": {slot: mod.name for slot, mod in self.mods.items()},
            "flags": list(self.flags),
            "job": self.job,
            "blueprints": self.blueprints,
            "skills": list(self.skills),
        }

    @classmethod
    def from_dict(cls, data):
        from items import _ITEMS
        from equipment import EQUIPMENT_BY_NAME, BODY_MODS_BY_NAME

        player = cls(data["name"], data.get("gender", "none"), data.get("stats"))
        player.age = data.get("age", 20)
        player.age_days = data.get("age_days", 0)
        player.health = data.get("health", player.max_health)
        player.stamina = data.get("stamina", player.max_stamina)
        player.satiety = data.get("satiety", player.max_satiety)
        player.cleanliness = data.get("cleanliness", player.max_cleanliness)
        player.satisfaction = data.get("satisfaction", player.max_satisfaction)
        player.money = data.get("money", {})
        player.bank = {n.currency: 0 for n in NATIONS}
        player.bank.update(data.get("bank", {}))
        player.experience = data.get("experience", 0)
        player.day = data.get("day", 1)
        player.weekday = data.get("weekday", 0)
        player.time = data.get("time", 0)
        player.location = LOCATIONS_BY_KEY.get(data.get("location"), player.location)
        player.home = LOCATIONS_BY_KEY.get(data.get("home"), SHELTER)
        player.loan_balance = data.get("loan", 0)
        player.monthly_rent = data.get("rent", 0)
        player.arrears = data.get("arrears", 0)
        player.kidnap_due = data.get("kidnap_due", False)
        player.home_ambush = data.get("home_ambush", False)
        player.month_day = data.get("month_day", 1)
        player.month = data.get("month", 1)
        player.season = data.get("season", 0)
        player.weather = data.get("weather", random.choice(WEATHER_BY_SEASON[player.season]))
        player.inventory = [_ITEMS[key] for key in data.get("inventory", []) if key in _ITEMS]
        player.equipment = {
            slot: EQUIPMENT_BY_NAME.get(name) if name else None
            for slot, name in data.get("equipment", {}).items()
        }
        weapon_key = data.get("weapon")
        player.weapon = _ITEMS.get(weapon_key)
        player.mods = {}
        for slot, name in data.get("mods", {}).items():
            mod = BODY_MODS_BY_NAME.get(name)
            if mod:
                player.mods[slot] = mod
                player.flags.update(mod.flags)
        for eq in player.equipment.values():
            if eq:
                player.flags.update(eq.flags)
        player.recalculate_stats()
        player.flags.update(data.get("flags", []))
        player.job = data.get("job")
        player.blueprints = data.get("blueprints", {})
        player.skills = set(data.get("skills", []))
        return player

