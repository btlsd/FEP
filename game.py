import random

from locations import (
    NATIONS,
    DEFAULT_LOCATION_BY_NATION,
)

from characters import NPCS, Player
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
        if self.player.time > 2:
            self.player.time = 0
            self.player.end_day()

    def work(self):
        if self.player.energy < 20 or self.player.hunger < 20:
            print("에너지가 부족하거나 너무 배가 고파서 일할 수 없습니다.")
            return
        income = 10 + self.player.intelligence // 2 + self.player.strength // 2
        self.player.money += income
        self.player.energy -= 20
        self.player.hunger -= 10
        self.player.experience += 1
        print(f"일해서 {income}원을 벌었습니다.")

    def eat(self):
        if self.player.money < 5:
            print("음식을 살 돈이 부족합니다.")
            return
        self.player.money -= 5
        self.player.hunger += 20
        if self.player.hunger > 100:
            self.player.hunger = 100
        self.player.energy += 10
        if self.player.energy > self.player.max_energy:
            self.player.energy = self.player.max_energy
        heal = self.player.endurance
        self.player.health = min(self.player.health + heal, self.player.max_health)
        print(f"식사를 했습니다. 체력이 {heal} 회복되었습니다.")

    def sleep(self):
        self.player.energy = self.player.max_energy
        self.player.hunger -= 10
        if self.player.hunger < 0:
            self.player.hunger = 0
        heal = 10 + self.player.endurance
        self.player.health = min(self.player.health + heal, self.player.max_health)
        print(f"잠을 자고 기력이 회복되었습니다. 체력이 {heal} 회복되었습니다.")

    def explore(self):
        print(f"{self.player.location.name}을 탐험합니다. {self.player.location.description}")
        roll = random.randint(1, 100)
        if roll <= 30 + self.player.perception:
            event = "find_money"
        elif roll <= 80:
            event = "nothing"
        else:
            event = "injury"
        if event == "find_money":
            found = random.randint(5, 20) + self.player.charisma
            self.player.money += found
            print(f"탐험 중에 {found}원을 발견했습니다.")
        elif event == "injury":
            damage = random.randint(5, 15)
            self.player.health -= damage
            print(f"탐험 중 부상을 입어 체력이 {damage} 감소했습니다.")
        else:
            print("탐험 중 아무 일도 일어나지 않았습니다.")

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
                self.player.location = current.connections[idx]
                print(f"{self.player.location.name}으로 이동했습니다.")
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
        print("이동할 국가를 선택하세요:")
        for i, nation in enumerate(NATIONS, start=1):
            print(f"{i}. {nation.name} - {nation.description}")
        choice = input("> ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(NATIONS):
                nation = NATIONS[idx]
                self.player.location = DEFAULT_LOCATION_BY_NATION[nation]
                print(f"{nation.name}으로 이동했습니다. 현재 위치는 {self.player.location.name}입니다.")
                return
        print("잘못된 선택입니다.")

    def step(self, action):
        action()
        self.advance_time()

    def play(self):
        actions = {
            "1": self.work,
            "2": self.eat,
            "3": self.sleep,
            "4": self.explore,
            "5": self.move,
            "6": self.travel,
            "7": self.interact,
            "q": None,
        }
        while self.player.is_alive():
            self.update_characters()
            draw_screen(self.player, self.characters)
            print("행동을 선택하세요:")
            print("1. 일하기")
            print("2. 식사")
            print("3. 잠자기")
            print("4. 탐험")
            print("5. 장소 이동")
            print("6. 국가 이동")
            print("7. 캐릭터와 상호작용")
            print("q. 종료")
            choice = input("> ").strip()
            if choice == "q":
                print("게임을 종료합니다.")
                break
            action = actions.get(choice)
            if action:
                self.step(action)
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
