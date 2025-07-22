import random

from locations import (
    NATIONS,
    DEFAULT_LOCATION_BY_NATION,
    LOCATIONS,
    SHELTER,
    HOSPITAL,
)

from characters import NPCS, Player, Character
from items import (
    BROKEN_PART,
    CITY_PLANNER_CERT,
    MILITARY_CERT,
    LAND_SURVEY_CERT,
    ROBOT_MANAGER_CERT,
    CREATOR_CERT,
    SOCIAL_WORK_CERT,
    DETECTIVE_CERT,
    SECURITY_CERT,
    IRON_PIPE,
)
from equipment import BODY_MODS
from gui import draw_screen
from utils import choose_option, roll_check
import json
import os

_act_path = os.path.join(os.path.dirname(__file__), "data", "actions.json")
with open(_act_path, encoding="utf-8") as f:
    _ACTION_DATA = json.load(f).get("actions", [])
ACTIONS = {a["key"]: a["name"] for a in _ACTION_DATA}

# 범죄별 형량(일수)
CRIME_SENTENCES = {
    "pickpocket": {
        "인류연합국": 180,
        "거합": 90,
        "탐랑": 60,
        "전계국": 365,
    },
    "lockpick": {"인류연합국": 365, "거합": 180, "탐랑": 120, "전계국": 540},
    "hack": {"인류연합국": 120, "거합": 60, "탐랑": 90, "전계국": 240},
}

# 각 직업별 요구 능력치와 자격증 매핑
TRAININGS = {
    "도시 계획자": {
        "cert": CITY_PLANNER_CERT,
        "req": {"intelligence": 7},
        "gov": False,
    },
    "군사 요원": {
        "cert": MILITARY_CERT,
        "req": {"strength": 7, "endurance": 6},
        "gov": True,
    },
    "토지 개관자": {
        "cert": LAND_SURVEY_CERT,
        "req": {"perception": 7},
        "gov": True,
    },
    "로봇 관리자": {
        "cert": ROBOT_MANAGER_CERT,
        "req": {"intelligence": 6},
        "gov": True,
    },
    "창작자": {
        "cert": CREATOR_CERT,
        "req": {"intelligence": 6, "charisma": 6},
        "gov": False,
    },
    "사회복지사": {
        "cert": SOCIAL_WORK_CERT,
        "req": {"charisma": 7},
        "gov": False,
    },
    "탐정": {
        "cert": DETECTIVE_CERT,
        "req": {"perception": 7, "intelligence": 7},
        "gov": False,
    },
    "경비": {
        "cert": SECURITY_CERT,
        "req": {"strength": 6, "agility": 6},
        "gov": False,
    },
}

# 직업별 급여 정보 (시급 또는 월급)
JOB_PAY = {
    "임시 노동자": {"type": "hourly", "rate": 10},
    "도시 계획자": {"type": "monthly", "rate": 300},
    "군사 요원": {"type": "monthly", "rate": 250},
    "토지 개관자": {"type": "monthly", "rate": 220},
    "로봇 관리자": {"type": "monthly", "rate": 230},
    "창작자": {"type": "monthly", "rate": 200},
    "사회복지사": {"type": "monthly", "rate": 210},
    "탐정": {"type": "hourly", "rate": 40},
    "경비": {"type": "hourly", "rate": 15},
}

class Game:
    def __init__(self, player):
        self.player = player
        self.characters = NPCS

    def hospitalize(self):
        p = self.player
        print("\n의식을 잃고 병원으로 실려 왔습니다.")
        fee = 20
        cur = HOSPITAL.nation.currency
        if p.spend_money(fee, cur):
            print(f"병원비 {fee}{cur}을 지불했습니다.")
        else:
            print(f"병원비 {fee}{cur}을 지불하지 못해 빚으로 남았습니다.")
            p.loan_balance += fee
        p.location = HOSPITAL
        p.health = p.max_health // 2
        p.stamina = p.max_stamina // 2
        p.satiety = max(0, p.satiety - 10)
        p.cleanliness = max(0, p.cleanliness - 10)

    def check_health(self):
        if self.player.health <= -50:
            print("치명상을 입어 사망했습니다...")
            self.running = False
        elif self.player.health <= 0:
            self.hospitalize()

    def check_home_ambush(self, dest):
        p = self.player
        if dest != p.home or not p.home_ambush:
            return False
        print("\n집 근처에서 묘한 기운을 느낍니다.")
        detect = 30 + p.perception * 3 + p.intuition * 3
        if roll_check(detect):
            print("익숙하지 않은 냄새와 함께 어둠 속에 그림자가 어른거립니다.")
            choice = choose_option(["도망간다", "무시하고 집에 들어간다"], allow_back=False)
            if choice == 0:
                print("당신은 서둘러 그곳을 벗어났습니다.")
                return True
        p.location = dest
        print("집 안에서 로봇들이 습격해 옵니다!")
        self.kidnap_fight_sequence()
        p.home_ambush = False
        return False

    def check_infiltration(self):
        p = self.player
        if not p.has_flag("infiltrating"):
            return 0
        chance = 30 + p.location.security * 10 - p.agility - p.perception // 2
        if p.has_flag("stealth"):
            chance -= 10
        if chance < 10:
            chance = 10
        if roll_check(chance):
            print("경비에게 발각되었습니다!")
            success, seg = self.handle_detection(p.location)
            return seg
        return 0

    def handle_detection(self, location, entering=False):
        p = self.player
        danger = getattr(location, "danger", 0)
        origin = p.location if entering else (p.infiltration_origin or p.home)
        p.flags.discard("stealth")
        if danger <= 0:
            if not entering:
                p.location = origin
                p.flags.discard("infiltrating")
                p.infiltration_origin = None
            print("밖으로 끌려나왔습니다.")
            return False, 0
        guard_name = "경비 로봇" if danger == 1 else "정예 경비 로봇"
        agility = 6 if danger == 1 else 8
        guard = Character(guard_name, {}, location.nation.name, "경비", {}, agility=agility)
        win, turns = guard.fight(p, ambush="npc")
        seg = self.battle_time(turns)
        if win:
            print(f"{guard_name}을 물리쳤습니다.")
            if entering:
                p.add_flag("infiltrating")
                p.infiltration_origin = origin
                p.location = location
                print("경비를 따돌리고 내부로 침입했습니다.")
            else:
                p.add_flag("infiltrating")
            return True, seg
        else:
            self.imprison()
            return False, seg

    def save(self, filename="save.json"):
        data = {
            "player": self.player.to_dict(),
            "npcs": {c.name: {"affinity": c.affinity} for c in self.characters},
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"{filename}에 저장했습니다.")

    def load(self, filename="save.json"):
        try:
            with open(filename, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print("세이브 파일이 없습니다.")
            return
        self.player = Player.from_dict(data.get("player", {}))
        for c in self.characters:
            if c.name in data.get("npcs", {}):
                c.affinity = data["npcs"][c.name].get("affinity", c.affinity)
        print("불러오기 완료.")

    def update_characters(self):
        for npc in self.characters:
            npc.update_location(self.player.time)

    def advance_time(self, segments=1):
        for _ in range(max(1, int(segments))):
            self.player.time += 1
            self.player.pass_time()
            if self.player.time > 5:
                self.player.time = 0
                self.player.end_day()
                if self.player.kidnap_due:
                    self.handle_kidnap()

    def battle_time(self, turns):
        """Return how many time segments should pass for the given turn count."""
        agi = max(1, self.player.agility)
        factor = max(1, 12 - agi)
        segs = int(turns * factor / 24)
        return max(1, segs)

    def work(self):
        if self.player.weekday not in {0, 1, 3, 4}:
            print("오늘은 휴일이라 일을 할 수 없습니다.")
            return
        if self.player.stamina < 20 or self.player.satiety < 20:
            print("기력이 부족하거나 너무 허기가 져서 일할 수 없습니다.")
            return
        info = JOB_PAY.get(self.player.job)
        if info and info.get("type") == "hourly":
            income = info.get("rate", 0)
        else:
            income = 10 + self.player.intelligence // 2 + self.player.strength // 2
        currency = self.player.location.nation.currency
        tax = int(income * 0.2)
        net = income - tax
        self.player.add_money(net, currency)
        stamina_cost = max(10, 20 - self.player.strength)
        satiety_cost = max(5, 10 - self.player.endurance // 2)
        self.player.stamina -= stamina_cost
        self.player.satiety -= satiety_cost
        self.player.cleanliness -= 5
        self.player.experience += 1
        print(f"일해서 {net}{currency}를 벌었습니다. (세금 {tax}{currency})")

    def eat(self):
        price = 5
        currency = self.player.location.nation.currency
        if not self.player.spend_money(price, currency):
            print("음식을 살 돈이 부족합니다.")
            return
        gain_satiety = 20 + self.player.endurance
        gain_stamina = 10 + self.player.strength // 2
        self.player.satiety = min(self.player.max_satiety, self.player.satiety + gain_satiety)
        self.player.stamina = min(self.player.max_stamina, self.player.stamina + gain_stamina)
        heal = self.player.endurance
        self.player.health = min(self.player.health + heal, self.player.max_health)
        print(f"식사를 했습니다. 체력이 {heal} 회복되었습니다.")

    def sleep(self):
        if not getattr(self.player.location, "sleep_spot", False):
            print("여기서는 잠을 잘 수 없습니다.")
            return
        gain_stamina = self.player.endurance * 5 + 20
        self.player.stamina = min(self.player.max_stamina, self.player.stamina + gain_stamina)
        self.player.satiety -= 10
        if self.player.satiety < 0:
            self.player.satiety = 0
        heal = 10 + self.player.endurance
        self.player.health = min(self.player.health + heal, self.player.max_health)
        print(f"잠을 자고 기력이 회복되었습니다. 체력이 {heal} 회복되었습니다.")

    def wash(self):
        if not getattr(self.player.location, "wash_spot", False):
            print("씻을 시설이 없습니다.")
            return
        cost = 2
        currency = self.player.location.nation.currency
        if not self.player.spend_money(cost, currency):
            print("씻을 돈이 부족합니다.")
            return
        gain = 30 + self.player.charisma
        self.player.cleanliness = min(self.player.max_cleanliness, self.player.cleanliness + gain)
        self.player.stamina -= 5
        if self.player.stamina < 0:
            self.player.stamina = 0
        self.player.shower_count += 1
        print("씻고 나니 상쾌합니다.")

    def watch_media(self):
        cost = 2
        currency = self.player.location.nation.currency
        if not self.player.spend_money(cost, currency):
            print("미디어 시청료를 지불할 돈이 없습니다.")
            return
        gain = 15 + self.player.intelligence // 2
        self.player.satisfaction = min(
            self.player.max_satisfaction, self.player.satisfaction + gain
        )
        self.player.stamina = max(0, self.player.stamina - 5)
        print("미디어를 시청하며 시간을 보냈습니다.")

    def read_book(self):
        opts = ["기초 수리술", "고전 문학"]
        idx = choose_option(opts)
        if idx is None:
            return
        self.player.learn_skill(opts[idx])
        self.player.stamina = max(0, self.player.stamina - 5)
        self.player.satisfaction = min(
            self.player.max_satisfaction, self.player.satisfaction + 5
        )

    def study_video(self):
        opts = ["기초 전투술", "기초 프로그래밍"]
        idx = choose_option(opts)
        if idx is None:
            return
        if not self.player.spend_money(1, self.player.location.nation.currency):
            print("시청료가 부족합니다.")
            return
        self.player.learn_skill(opts[idx])
        self.player.stamina = max(0, self.player.stamina - 5)

    def download_data(self):
        if not self.player.has_flag("interface"):
            print("뇌 인터페이스가 필요합니다.")
            return
        opts = ["고급 설계 데이터", "희귀 지식"]
        idx = choose_option(opts)
        if idx is None:
            return
        cost = 10
        cur = self.player.location.nation.currency
        if not self.player.spend_money(cost, cur):
            print("데이터 구입 비용이 부족합니다.")
            return
        self.player.learn_skill(opts[idx])
        print("데이터를 다운로드해 지식을 획득했습니다.")

    def exercise(self):
        if self.player.stamina < 10:
            print("운동을 할 기력이 부족합니다.")
            return
        self.player.stamina -= 10
        self.player.satiety = max(0, self.player.satiety - 5)
        self.player.cleanliness = max(0, self.player.cleanliness - 5)
        self.player.health = min(
            self.player.max_health, self.player.health + 5 + self.player.endurance // 2
        )
        self.player.satisfaction = min(
            self.player.max_satisfaction, self.player.satisfaction + 10
        )
        print("운동을 마치고 땀을 흘렸습니다.")

    def explore(self):
        print(f"{self.player.location.name}을 탐험합니다. {self.player.location.description}")
        if self.player.location.zone == "빈민가" and roll_check(40):
            gang = Character("슬럼 갱단원", {}, self.player.location.nation.name, "갱단원", {}, agility=6)
            gang.weapon = IRON_PIPE
            print("슬럼 갱단원이 시비를 걸어옵니다!")
            win, turns = gang.fight(self.player, ambush="npc")
            seg = self.battle_time(turns)
            if not win:
                self.imprison("pickpocket")
                return 0
            else:
                print("갱단원을 물리쳤습니다.")
                return seg
        roll = random.randint(1, 100)
        if roll <= 20 + self.player.perception:
            event = "find_item"
        elif roll <= 50 + self.player.perception:
            event = "find_money"
        elif roll <= 85:
            event = "nothing"
        else:
            event = "injury"
        if event == "find_item":
            item = BROKEN_PART
            self.player.add_item(item)
        elif event == "find_money":
            found = random.randint(5, 20) + self.player.charisma
            currency = self.player.location.nation.currency
            self.player.add_money(found, currency)
            print(f"탐험 중에 {found}{currency}을 발견했습니다.")
        elif event == "injury":
            damage = random.randint(5, 15)
            self.player.health -= damage
            print(f"탐험 중 부상을 입어 체력이 {damage} 감소했습니다.")
        else:
            print("탐험 중 아무 일도 일어나지 않았습니다.")

        stamina_cost = max(5, 15 - self.player.endurance)
        self.player.stamina -= stamina_cost
        self.player.satiety -= 5
        self.player.cleanliness -= 5

        # check for hidden paths
        loc = self.player.location
        discovered = [dest for dest, req in loc.hidden_connections.items() if self.player.perception >= req]
        for dest in discovered:
            loc.connections.append(dest)
            dest.connections.append(loc)
            del loc.hidden_connections[dest]
            del dest.hidden_connections[loc]
            print(f"숨겨진 장소 {dest.name}을(를) 발견했습니다!")

    def modify_body(self):
        shop_type = getattr(self.player.location, "mod_shop", None)
        if not shop_type:
            print("이곳에서는 개조 시술을 받을 수 없습니다.")
            return
        if shop_type == "illegal":
            print("불법 시술소입니다. 실패하거나 가품을 사용할 위험이 있습니다.")
        opts = []
        for mod in BODY_MODS:
            req = f" - 필요 부품: {mod.required_item.name}" if mod.required_item else ""
            company = f" [{mod.company}]" if mod.company else ""
            opts.append(f"{mod.name}{company} (부위: {mod.slot}){req}")
        idx = choose_option(opts)
        if idx is None:
            return
        self.player.install_mod(BODY_MODS[idx])

    def change_equipment(self):
        from equipment import Equipment

        choices = [
            it
            for it in self.player.inventory
            if isinstance(it, Equipment) or getattr(it, "damage", 0) > 0
        ]
        if not choices:
            print("장비할 수 있는 아이템이 없습니다.")
            return
        idx = choose_option([it.name for it in choices])
        if idx is None:
            return
        item = choices[idx]
        name = item.name
        if isinstance(item, Equipment):
            if "배지" in name:
                slot = "accessory"
            elif "가방" in name or "카트" in name or "캐리어" in name:
                slot = "bag"
            else:
                slot = "clothing"
            self.player.equip(item, slot)
        else:
            self.player.equip_weapon(item)

    def wait(self):
        print("가만히 시간을 보냅니다.")

    def stealth(self):
        self.player.add_flag("stealth")
        print("은신 상태로 주변을 살핍니다.")

    def pickpocket(self):
        targets = [c for c in self.characters if c.location == self.player.location and c.inventory]
        if not targets:
            print("소매치기할 대상이 없습니다.")
            return
        idx = choose_option([t.name for t in targets])
        if idx is None:
            return
        npc = targets[idx]
        chance = 30 + self.player.agility + self.player.perception
        if self.player.has_flag("stealth"):
            chance += 20
        if roll_check(chance):
            small = [it for it in npc.inventory if getattr(it, "volume", 1) <= 1]
            if not small:
                print("훔칠 만한 작은 물건이 없습니다.")
            else:
                item = random.choice(small)
                npc.inventory.remove(item)
                self.player.add_item(item)
                print(f"{npc.name}에게서 {item.name}을 훔쳤습니다.")
        else:
            print(f"{npc.name}에게 들켰습니다!")
            npc.affinity = max(0, npc.affinity - 10)
            if roll_check(50):
                print("경찰에게 체포되었습니다!")
                self.imprison("lockpick")
                return 0
        self.player.stamina -= 5

    def lockpick(self):
        loc = self.player.location
        if not getattr(loc, "locked_relic", False) or self.player.has_flag("relic_unlocked"):
            print("따야 할 자물쇠가 없습니다.")
            return
        chance = 40 + self.player.agility + self.player.intelligence
        if roll_check(chance):
            print("자물쇠를 따는 데 성공했습니다.")
            self.player.add_flag("relic_unlocked")
        else:
            print("자물쇠따기에 실패했습니다.")
            if roll_check(50):
                print("경찰에게 체포되었습니다!")
                self.imprison("hack")
                return 0
        self.player.stamina -= 5

    def hack(self):
        chance = 30 + self.player.intelligence * 2
        if self.player.has_flag("stealth"):
            chance += 10
        if roll_check(chance):
            gain = 5
            currency = self.player.location.nation.currency
            self.player.add_money(gain, currency)
            print(f"해킹에 성공해 {gain}{currency}을 얻었습니다.")
        else:
            print("해킹에 실패했습니다.")
            if roll_check(50):
                print("경찰에게 체포되었습니다!")
                self.imprison()
                return 0
        self.player.stamina -= 5

    def print_item(self):
        if not getattr(self.player.location, "printer", False):
            print("프린터가 없는 장소입니다.")
            return
        from items import _ITEMS
        available = [key for key, p in self.player.blueprints.items() if p >= 100 and _ITEMS[key].printable]
        if not available:
            print("사용 가능한 설계도가 없습니다.")
            return
        idx = choose_option([_ITEMS[key].name for key in available])
        if idx is None:
            return
        key = available[idx]
        item = _ITEMS[key]
        cost = max(1, int(item.weight * 2))
        currency = self.player.location.nation.currency
        if not self.player.spend_money(cost, currency):
            print("재료비가 부족합니다.")
            return
        self.player.add_item(item)
        print(f"{item.name}을(를) 프린팅했습니다. 비용 {cost}{currency}")

    def deposit_money(self):
        if not getattr(self.player.location, "bank", False):
            print("은행이 없습니다.")
            return
        currencies = list(self.player.money.keys())
        if not currencies:
            print("소지한 현금이 없습니다.")
            return
        idx = choose_option([f"{cur} ({self.player.money[cur]})" for cur in currencies])
        if idx is None:
            return
        cur = currencies[idx]
        amt = input("입금할 금액을 입력하세요: ").strip()
        if not amt.isdigit():
            print("잘못된 금액입니다.")
            return
        amt = int(amt)
        if self.player.deposit(amt, cur):
            print(f"{amt}{cur}을 입금했습니다.")
        else:
            print("금액이 부족합니다.")

    def withdraw_money(self):
        if not getattr(self.player.location, "bank", False):
            print("은행이 없습니다.")
            return
        currencies = list(self.player.bank.keys())
        available = [cur for cur in currencies if self.player.bank.get(cur, 0) > 0]
        if not available:
            print("예금된 돈이 없습니다.")
            return
        idx = choose_option([f"{cur} ({self.player.bank[cur]})" for cur in available])
        if idx is None:
            return
        cur = available[idx]
        amt = input("출금할 금액을 입력하세요: ").strip()
        if not amt.isdigit():
            print("잘못된 금액입니다.")
            return
        amt = int(amt)
        if self.player.withdraw(amt, cur):
            print(f"{amt}{cur}을 출금했습니다.")
        else:
            print("금액이 부족합니다.")

    def housing_trade(self):
        loc = self.player.location
        if not (getattr(loc, "housing_office", False) or getattr(loc, "housing_market", False)):
            print("주거지를 거래할 수 있는 곳이 아닙니다.")
            return
        homes = [l for l in LOCATIONS if getattr(l, "residence", False)]
        if getattr(loc, "housing_office", False):
            homes = [h for h in homes if getattr(h, "government", False)]
        else:
            homes = [h for h in homes if not getattr(h, "government", False)]
        options = []
        actions = []
        for h in homes:
            cur = h.nation.currency
            if h.price:
                options.append(f"{h.name} 구매 {h.price}{cur}")
                actions.append(("buy", h))
            if h.rent_price:
                options.append(f"{h.name} 임대 {h.rent_price}{cur}/월")
                actions.append(("rent", h))
        if getattr(self.player.home, "price", 0):
            sell_price = int(self.player.home.price * 0.8)
            cur = self.player.home.nation.currency
            options.append(f"현재 집 판매 {sell_price}{cur}")
            actions.append(("sell", self.player.home))
        if not options:
            print("거래할 주거지가 없습니다.")
            return
        idx = choose_option(options)
        if idx is None:
            return
        action, house = actions[idx]
        cur = house.nation.currency
        if action == "buy":
            if not self.player.spend_money(house.price, cur):
                print("돈이 부족합니다.")
                return
            self.player.home = house
            self.player.monthly_rent = 0
            self.player.add_flag(f"access_{house.key}")
            print(f"{house.name}을(를) 구입했습니다.")
        elif action == "rent":
            if not self.player.spend_money(house.rent_price, cur):
                print("돈이 부족합니다.")
                return
            self.player.home = house
            self.player.monthly_rent = house.rent_price
            self.player.add_flag(f"access_{house.key}")
            print(f"{house.name}을(를) 임대했습니다.")
        elif action == "sell":
            price = int(house.price * 0.8)
            self.player.add_money(price, cur)
            self.player.flags.discard(f"access_{house.key}")
            self.player.home = SHELTER
            self.player.monthly_rent = 0
            print(f"집을 {price}{cur}에 판매하고 쉘터로 돌아갑니다.")

    def scan_remains(self, npc):
        key = getattr(npc, "blueprint_drop", None)
        if not key:
            print("스캔할 만한 잔해가 없습니다.")
            return
        progress = random.randint(20, 60)
        self.player.add_blueprint_progress(key, progress)

    def find_job(self):
        if not getattr(self.player.location, "job_office", False):
            print("이곳에서는 직업을 소개받을 수 없습니다.")
            return
        idx = choose_option(["단순 노동", "직업 교육 프로그램", "아직 결정하지 않는다"])
        if idx is None or idx == 2:
            print("결정을 미루었습니다.")
            return
        if idx == 0:
            self.player.start_job("임시 노동자")
            print("당신은 임시 노동자로 등록되었습니다.")
            return
        # training path
        cat_idx = choose_option(["정부 소속 직업", "일반 직업"])
        if cat_idx is None:
            return
        want_gov = cat_idx == 0
        jobs = [j for j, info in TRAININGS.items() if info.get("gov") == want_gov]
        if not jobs:
            print("해당 분류의 과정이 없습니다.")
            return
        job_idx = choose_option(jobs)
        if job_idx is None:
            print("등록을 취소했습니다.")
            return
        job = jobs[job_idx]
        info = TRAININGS[job]
        req = info["req"]
        meets = all(getattr(self.player, stat) >= val for stat, val in req.items())
        self.player.start_job(job)
        if info.get("gov"):
            print("정부 소속 과정으로 지정 숙소와 생활 패턴을 따라야 합니다.")
        if meets:
            cert = info["cert"]
            self.player.inventory.append(cert)
            nations = "범국가" if cert.universal else ", ".join(cert.valid_nations or [])
            print(f"{job} 자격증을 취득했습니다. (인정 국가: {nations})")
        else:
            req_text = ", ".join(f"{k} {v}+" for k, v in req.items())
            print("교육은 마쳤지만 요구 능력치가 부족해 시험에 불합격했습니다.")
            print(f"필요 능력치: {req_text}. 다음 시험 때 다시 도전하세요.")

    def attempt_enter(self, dest):
        unauthorized = getattr(dest, "restricted", False) and not self.player.has_flag(
            f"access_{getattr(dest,'key',dest.name)}"
        )
        if unauthorized:
            chance = 50 + dest.security * 10
            if self.player.has_flag("stealth"):
                chance -= 30
            if roll_check(chance):
                print("경비에게 발각되었습니다!")
                success, _ = self.handle_detection(dest, entering=True)
                return success
            print("몰래 침입에 성공했습니다.")
            self.player.flags.discard("stealth")
            self.player.add_flag("infiltrating")
            self.player.infiltration_origin = self.player.location
        else:
            self.player.flags.discard("stealth")
            self.player.flags.discard("infiltrating")
            self.player.infiltration_origin = None
        return True

    def move_walk(self):
        current = self.player.location
        options = [
            loc
            for loc in LOCATIONS
            if loc.zone == current.zone and loc != current
        ]
        if not options:
            print("이곳에서 이동할 수 있는 장소가 없습니다.")
            return
        idx = choose_option([d.name for d in options])
        if idx is None:
            return
        dest = options[idx]
        for eq in [self.player.equipment.get("bag"), self.player.equipment.get("clothing")]:
            if eq and not eq.can_enter_buildings and dest.indoors:
                print("장착 중인 장비 때문에 들어갈 수 없습니다.")
                return
        if dest.open_times and self.player.time not in dest.open_times:
            print("지금은 그곳에 들어갈 수 없습니다.")
            return
        if not self.attempt_enter(dest):
            return
        if self.check_home_ambush(dest):
            return
        if dest != self.player.location:
            self.player.location = dest
            self.player.flags.discard("stealth")
            print(f"도보로 {self.player.location.name}으로 이동했습니다.")

    def move_station(self):
        current = self.player.location
        if not current.station or not current.connections:
            print("정거장에서만 사용할 수 있습니다.")
            return
        idx = choose_option([d.name for d in current.connections])
        if idx is None:
            return
        dest = current.connections[idx]
        for eq in [self.player.equipment.get("bag"), self.player.equipment.get("clothing")]:
            if eq and not eq.can_enter_buildings and dest.indoors:
                print("장착 중인 장비 때문에 들어갈 수 없습니다.")
                return
        if dest.open_times and self.player.time not in dest.open_times:
            print("지금은 그곳에 들어갈 수 없습니다.")
            return
        if not self.attempt_enter(dest):
            return
        if self.check_home_ambush(dest):
            return
        if dest != self.player.location:
            self.player.location = dest
            self.player.flags.discard("stealth")
            print(f"{dest.name}으로 이동했습니다.")

    def move_jetpack(self):
        if not self.player.has_flag("jetpack"):
            print("제트팩이 없습니다.")
            return
        current = self.player.location
        options = [
            loc
            for loc in LOCATIONS
            if loc.nation == current.nation and loc != current
        ]
        if not options:
            print("이 나라에서 이동할 장소가 없습니다.")
            return
        idx = choose_option([l.name for l in options])
        if idx is None:
            return
        dest = options[idx]
        for eq in [self.player.equipment.get("bag"), self.player.equipment.get("clothing")]:
            if eq and not eq.can_enter_buildings and dest.indoors:
                print("장착 중인 장비 때문에 들어갈 수 없습니다.")
                return
        if dest.open_times and self.player.time not in dest.open_times:
            print("지금은 그곳에 들어갈 수 없습니다.")
            return
        if not self.attempt_enter(dest):
            return
        if self.check_home_ambush(dest):
            return
        if dest != current:
            self.player.location = dest
            self.player.flags.discard("stealth")
            print(f"제트팩으로 {dest.name}에 도착했습니다.")

    def interact(self):
        nearby = [c for c in self.characters if c.location == self.player.location]
        if not nearby:
            print("주변에 대화할 사람이 없습니다.")
            return
        idx = choose_option([f"{n.name} ({n.job})" for n in nearby])
        if idx is None:
            return
        npc = nearby[idx]
        action_idx = choose_option(["대화", "거래", "돈 빌리기", "전투"])
        if action_idx is None:
            return
        if self.player.has_flag("stealth") or self.player.has_flag("infiltrating"):
            print(f"{npc.name}이(가) 당신의 등장에 깜짝 놀랍니다!")
            change = 1 if npc.affinity >= 80 else -5
            npc.affinity = max(0, min(100, npc.affinity + change))
            if change > 0:
                print("호감도가 약간 상승했습니다.")
            else:
                print("호감도가 감소했습니다.")
            self.player.flags.discard("stealth")
            if self.player.has_flag("infiltrating"):
                self.player.flags.discard("infiltrating")
                self.player.infiltration_origin = None
        if action_idx == 0:
            npc.talk(self.player)
        elif action_idx == 1:
            npc.trade(self.player)
        elif action_idx == 2:
            npc.lend_money(self.player)
        elif action_idx == 3:
            win, turns = npc.fight(self.player)
            if win:
                scan = choose_option(["잔해 스캔", "그만두기"])
                if scan == 0:
                    self.scan_remains(npc)
            segments = self.battle_time(turns)
            return segments

    def travel(self):
        if not self.player.location.station or not self.player.location.international:
            print("국가 간 이동을 할 수 있는 정거장이 아닙니다.")
            return
        from items import BOARDING_PASS
        if BOARDING_PASS in self.player.inventory:
            use_ticket = True
        elif self.player.has_flag("transport_pass"):
            use_ticket = False
        else:
            print("탑승권이 없어 이동할 수 없습니다.")
            return
        opts = [f"{n.name} - {n.description}" for n in NATIONS]
        idx = choose_option(opts)
        if idx is None:
            return
        nation = NATIONS[idx]
        self.player.location = DEFAULT_LOCATION_BY_NATION[nation]
        if use_ticket:
            self.player.inventory.remove(BOARDING_PASS)
        print(
            f"{nation.transport}을 이용해 {nation.name}으로 이동했습니다. 현재 위치는 {self.player.location.name}입니다."
        )

    def kidnap_fight_sequence(self):
        p = self.player
        bot = Character("납치 로봇", {}, p.location.nation.name, "로봇", {}, agility=6)
        bot.health = 40
        win, turns = bot.fight(p, ambush="npc")
        segments = self.battle_time(turns)
        if not win:
            self.resolve_kidnap()
            self.advance_time(segments)
            return
        strong = Character("강화 로봇", {}, p.location.nation.name, "로봇", {}, agility=8)
        strong.health = 60
        print("더 강한 로봇이 나타났습니다!")
        win2, turns2 = strong.fight(p, ambush="npc")
        segments += self.battle_time(turns2)
        if win2:
            commander = Character("지휘관 백", {}, p.location.nation.name, "지휘관", {})
            print("지휘관 백이 다가와 당신에게 특수부대 편입을 제안합니다.")
            if p.intelligence >= 8:
                print("로봇들의 설계가 인류연합국식임을 간파했습니다.")
            choice = choose_option(["편입한다", "거절한다"], allow_back=False)
            if choice == 0:
                p.job = "특수부대 요원"
                p.add_flag("special_force")
                print("당신은 특수부대에 편입되었습니다.")
            else:
                print("제안을 거절했습니다. 하지만 정부는 당신을 주시합니다.")
            p.arrears = 0
            p.kidnap_due = False
            p.home_ambush = False
        else:
            self.resolve_kidnap()
        self.advance_time(segments)

    def handle_kidnap(self):
        p = self.player
        print("\n정부 요원들이 당신을 은밀히 납치하려 합니다!")
        detect = 20 + p.perception * 2 + p.intelligence + p.agility + p.intuition * 3
        if roll_check(detect):
            print("어둠 속에서 낯선 그림자가 스치고 익숙하지 않은 향이 느껴집니다.")
            print("불길한 기운을 감지했습니다.")
            choice = choose_option(["숨는다", "맞서 싸운다"], allow_back=False)
            if choice == 0:
                chance = 30 + p.agility * 3 + p.perception * 2
                if roll_check(chance):
                    print("겨우 몸을 숨겨 납치를 피했습니다.")
                    p.arrears = 2
                    p.kidnap_due = False
                    p.home_ambush = True
                    return
                else:
                    print("숨는 데 실패했습니다!")
            self.kidnap_fight_sequence()
        else:
            print("눈치채지 못한 채 납치당했습니다!")
            self.resolve_kidnap()

    def resolve_kidnap(self):
        p = self.player
        top = max(p.strength, p.intelligence, p.charisma)
        if top == p.strength:
            print("전계국 실험체로 팔려갔습니다...")
        elif top == p.intelligence:
            print("탐랑으로 끌려가 동료가 되었습니다...")
        elif top == p.charisma:
            print("거합에서 애완동물 취급을 받게 되었습니다...")
        else:
            print("당신은 추방당했습니다...")
        p.health = 0
        self.running = False

    def imprison(self, crime=None):
        from locations import JAIL, SLUM_MARKET
        p = self.player
        p.location = JAIL
        print("당신은 체포되어 감옥에 수감되었습니다.")
        nation = p.location.nation.name
        days = 1
        if crime and crime in CRIME_SENTENCES:
            days = CRIME_SENTENCES[crime].get(nation, 30)
        for d in range(days):
            print(f"{d+1}일차 수감 생활이 지나갑니다...")
            for msg in ["새벽", "아침", "오전", "오후", "저녁", "밤"]:
                self.advance_time(1)
            p.satiety = p.max_satiety
            p.stamina = p.max_stamina
            p.cleanliness = max(p.cleanliness, p.max_cleanliness // 2)
        if "gang_contact" not in p.flags:
            p.add_flag("gang_contact")
            print("감옥에서 범죄 조직과 연결되었습니다.")
        p.location = SLUM_MARKET
        print(f"{days}일 후 풀려나 빈민가로 돌아왔습니다.")

    def step(self, action):
        segs = action()
        if self.running:
            self.check_health()
        extra = 0
        if self.running:
            extra = self.check_infiltration()
        if self.running:
            self.advance_time((segs if isinstance(segs, int) else 1) + extra)

    def choose_move(self):
        opts = ["도보 이동"]
        moves = [self.move_walk]
        if self.player.has_flag("jetpack"):
            opts.append("제트팩 비행")
            moves.append(self.move_jetpack)
        if self.player.location.station:
            opts.append("정거장 이동")
            moves.append(self.move_station)
            if self.player.location.international:
                opts.append("국가 이동")
                moves.append(self.travel)
        idx = choose_option(opts)
        if idx is None:
            return
        action = moves[idx]
        self.step(action)

    def choose_action(self):
        opts = [
            "일하기",
            "식사",
            "잠자기",
            "탐험",
            "소지품 확인",
            "장비 장착",
            "씻기",
            "신체 개조",
            "미디어 시청",
            "운동",
            "책 읽기",
            "영상 학습",
            "데이터 다운로드",
        ]
        added = []
        for key in ACTIONS:
            name = ACTIONS[key]
            if name not in opts:
                opts.append(name)
                added.append(key)
        if getattr(self.player.location, "printer", False):
            opts.append("프린팅")
        if getattr(self.player.location, "job_office", False):
            opts.append("직업 찾기")
        if getattr(self.player.location, "housing_office", False) or getattr(self.player.location, "housing_market", False):
            opts.append("주거지 거래")
        if getattr(self.player.location, "bank", False):
            opts.extend(["입금", "출금"])
        idx = choose_option(opts)
        if idx is None:
            return
        actions = [
            self.work,
            self.eat,
            self.sleep,
            self.explore,
            self.player.show_inventory,
            self.change_equipment,
            self.wash,
            self.modify_body,
            self.watch_media,
            self.exercise,
            self.read_book,
            self.study_video,
            self.download_data,
        ]
        extra_map = {
            "wait": self.wait,
            "sleep": self.sleep,
            "stealth": self.stealth,
            "pickpocket": self.pickpocket,
            "lockpick": self.lockpick,
            "hack": self.hack,
            "explore": self.explore,
            "watch_media": self.watch_media,
            "exercise": self.exercise,
        }
        for key in added:
            actions.append(extra_map.get(key, self.wait))
        if getattr(self.player.location, "printer", False):
            actions.append(self.print_item)
        if getattr(self.player.location, "job_office", False):
            actions.append(self.find_job)
        if getattr(self.player.location, "housing_office", False) or getattr(self.player.location, "housing_market", False):
            actions.append(self.housing_trade)
        if getattr(self.player.location, "bank", False):
            actions.extend([self.deposit_money, self.withdraw_money])
        action = actions[idx]
        if action is self.player.show_inventory:
            action()
        else:
            self.step(action)

    def open_menu(self):
        options = ["스탯 확인", "소지품 확인", "데이터 확인", "저장", "불러오기", "종료"]
        idx = choose_option(options)
        if idx is None:
            return True
        if idx == 0:
            self.player.status()
            return True
        if idx == 1:
            self.player.show_inventory()
            return True
        if idx == 2:
            self.player.show_data()
            return True
        if idx == 3:
            self.save()
            return True
        if idx == 4:
            self.load()
            return True
        print("게임을 종료합니다.")
        return False

    def play(self):
        self.running = True
        while self.player.is_alive() and self.running:
            self.update_characters()
            if self.player.kidnap_due:
                self.handle_kidnap()
                if not self.running:
                    break
            draw_screen(self.player, self.characters)
            idx = choose_option(["이동", "NPC 선택", "행동", "메뉴"], allow_back=False)
            if idx == 0:
                self.choose_move()
            elif idx == 1:
                self.step(self.interact)
            elif idx == 2:
                self.choose_action()
            elif idx == 3:
                if not self.open_menu():
                    break
        if not self.player.is_alive():
            print("건강이 나빠 쓰러졌습니다. 게임 오버.")


def main():
    print("...의식을 차리니 기억이 전혀 나지 않습니다.")
    print("머릿속 인터페이스는 손상된 채로 깜빡거립니다.")
    input("계속하려면 엔터를 누르세요...")
    helper = next((c for c in NPCS if c.name == "은하"), None)
    if helper:
        print(f"{helper.name}이 당신을 발견해 도와줍니다. 인류연합국 스캔을 시작합니다.")
    name = input("새로운 이름을 정하세요: ")
    gender = input("성별을 입력하세요 (male/female/none): ")
    points = 10
    base = {"strength":5,"perception":5,"endurance":5,"charisma":5,"intelligence":5,"agility":5,"intuition":5}
    for key in list(base.keys()):
        while True:
            val = input(f"{key} 추가 포인트(남은 {points}): ")
            if val.isdigit():
                val = int(val)
                if 0 <= val <= points:
                    base[key] += val
                    points -= val
                    break
            print("잘못된 입력입니다.")
    player = Player(name, gender, base)
    player.location = SHELTER
    if helper:
        helper.location = SHELTER
        print(f"{helper.name}의 안내로 {SHELTER.name}에 도착했습니다.")
    game = Game(player)
    game.play()

if __name__ == "__main__":
    main()
