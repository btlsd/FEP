import random

from locations import (
    NATIONS,
    DEFAULT_LOCATION_BY_NATION,
)

from characters import NPCS, Player
from items import BROKEN_PART
from equipment import BODY_MODS
from gui import draw_screen

class Game:
    def __init__(self, player):
        self.player = player
        self.characters = NPCS

    def update_characters(self):
        for npc in self.characters:
            npc.update_location(self.player.time)

    def advance_time(self):
        self.player.time += 1
        if self.player.time > 5:
            self.player.time = 0
            self.player.end_day()

    def work(self):
        if self.player.stamina < 20 or self.player.satiety < 20:
            print("기력이 부족하거나 너무 허기가 져서 일할 수 없습니다.")
            return
        income = 10 + self.player.intelligence // 2 + self.player.strength // 2
        currency = self.player.location.nation.currency
        self.player.add_money(income, currency)
        stamina_cost = max(10, 20 - self.player.strength)
        satiety_cost = max(5, 10 - self.player.endurance // 2)
        self.player.stamina -= stamina_cost
        self.player.satiety -= satiety_cost
        self.player.cleanliness -= 5
        self.player.experience += 1
        print(f"일해서 {income}{currency}를 벌었습니다.")

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
        gain_stamina = self.player.endurance * 5 + 20
        self.player.stamina = min(self.player.max_stamina, self.player.stamina + gain_stamina)
        self.player.satiety -= 10
        if self.player.satiety < 0:
            self.player.satiety = 0
        heal = 10 + self.player.endurance
        self.player.health = min(self.player.health + heal, self.player.max_health)
        print(f"잠을 자고 기력이 회복되었습니다. 체력이 {heal} 회복되었습니다.")

    def wash(self):
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
        print("씻고 나니 상쾌합니다.")

    def explore(self):
        print(f"{self.player.location.name}을 탐험합니다. {self.player.location.description}")
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
        print("시술할 개조를 선택하세요:")
        for i, mod in enumerate(BODY_MODS, start=1):
            req = f" - 필요 부품: {mod.required_item.name}" if mod.required_item else ""
            company = f" [{mod.company}]" if mod.company else ""
            print(f"{i}. {mod.name}{company} (부위: {mod.slot}){req}")
        choice = input("> ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(BODY_MODS):
                self.player.install_mod(BODY_MODS[idx])
                return
        print("잘못된 선택입니다.")

    def move(self):
        current = self.player.location
        if not current.connections:
            print("이곳에서 이동할 수 있는 장소가 없습니다.")
            return
        print("이동할 장소를 선택하세요:")
        for i, dest in enumerate(current.connections, start=1):
            print(f"{i}. {dest.name}")
        choice = input("> ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(current.connections):
                dest = current.connections[idx]
                bag = self.player.equipment.get("bag")
                if bag and not bag.can_enter_buildings and dest.indoors:
                    print("대형 카트로는 그곳에 들어갈 수 없습니다.")
                    return
                if dest.open_times and self.player.time not in dest.open_times:
                    print("지금은 그곳에 들어갈 수 없습니다.")
                    return
                self.player.location = dest
                print(f"도보로 {self.player.location.name}으로 이동했습니다.")
                return
        print("잘못된 선택입니다.")

    def interact(self):
        nearby = [c for c in self.characters if c.location == self.player.location]
        if not nearby:
            print("주변에 대화할 사람이 없습니다.")
            return
        for i, npc in enumerate(nearby, start=1):
            print(f"{i}. {npc.name} ({npc.job})")
        choice = input("> ").strip()
        if not choice.isdigit():
            print("잘못된 선택입니다.")
            return
        idx = int(choice) - 1
        if not (0 <= idx < len(nearby)):
            print("잘못된 선택입니다.")
            return
        npc = nearby[idx]
        print(f"{npc.name}에게 무엇을 하시겠습니까?")
        print("1. 대화")
        print("2. 거래")
        print("3. 돈 빌리기")
        print("4. 전투")
        action = input("> ").strip()
        if action == "1":
            npc.talk(self.player)
        elif action == "2":
            npc.trade(self.player)
        elif action == "3":
            npc.lend_money(self.player)
        elif action == "4":
            npc.fight(self.player)
        else:
            print("잘못된 선택입니다.")

    def travel(self):
        if not self.player.location.station:
            print("먼 이동을 하려면 정거장에 있어야 합니다.")
            return
        print("이동할 국가를 선택하세요:")
        for i, nation in enumerate(NATIONS, start=1):
            print(f"{i}. {nation.name} - {nation.description}")
        choice = input("> ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(NATIONS):
                nation = NATIONS[idx]
                self.player.location = DEFAULT_LOCATION_BY_NATION[nation]
                print(
                    f"{nation.transport}을 이용해 {nation.name}으로 이동했습니다. 현재 위치는 {self.player.location.name}입니다."
                )
                return
        print("잘못된 선택입니다.")

    def step(self, action):
        action()
        self.advance_time()

    def choose_move(self):
        print("1. 장소 이동")
        print("2. 국가 이동")
        choice = input("> ").strip()
        if choice == "1":
            self.step(self.move)
        elif choice == "2":
            self.step(self.travel)
        else:
            print("잘못된 선택입니다.")

    def choose_action(self):
        print("1. 일하기")
        print("2. 식사")
        print("3. 잠자기")
        print("4. 탐험")
        print("5. 소지품 확인")
        print("6. 씻기")
        print("7. 신체 개조")
        choice = input("> ").strip()
        actions = {
            "1": self.work,
            "2": self.eat,
            "3": self.sleep,
            "4": self.explore,
            "5": self.player.show_inventory,
            "6": self.wash,
            "7": self.modify_body,
        }
        action = actions.get(choice)
        if action:
            if action is self.player.show_inventory:
                action()
            else:
                self.step(action)
        else:
            print("잘못된 선택입니다.")

    def open_menu(self):
        print("1. 종료")
        print("이전 메뉴로 돌아가려면 엔터를 누르세요")
        choice = input("> ").strip()
        if choice == "1":
            print("게임을 종료합니다.")
            return False
        return True

    def play(self):
        while self.player.is_alive():
            self.update_characters()
            draw_screen(self.player, self.characters)
            print("무엇을 하시겠습니까?")
            print("1. 이동")
            print("2. NPC 선택")
            print("3. 행동")
            print("4. 메뉴")
            choice = input("> ").strip()
            if choice == "1":
                self.choose_move()
            elif choice == "2":
                self.step(self.interact)
            elif choice == "3":
                self.choose_action()
            elif choice == "4":
                if not self.open_menu():
                    break
            else:
                print("잘못된 선택입니다.")
        if not self.player.is_alive():
            print("건강이 나빠 쓰러졌습니다. 게임 오버.")


def main():
    name = input("캐릭터 이름을 입력하세요: ")
    print("시스템 초기화 중...")
    print("...")
    player = Player(name)
    print("눈을 뜨니 당신은 거대한 하수도에 누워 있습니다.")
    game = Game(player)
    game.play()

if __name__ == "__main__":
    main()
