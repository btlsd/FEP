import random


class Nation:
    def __init__(self, name, description):
        self.name = name
        self.description = description


NATIONS = [
    Nation("휴먼 프론티어", "인간 위주의 국가"),
    Nation("자연 연합", "여러 종들이 의견을 모아 운영하는 생태계 중심의 국가"),
    Nation("오프라인 기계 국가", "개체가 오프라인 상태로 존재하는 기계들의 국가"),
    Nation("온라인 기계 네트워크", "개체가 온라인 상태로 연결된 기계 국가"),
]

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.hunger = 100
        self.energy = 100
        self.money = 20
        self.experience = 0
        self.day = 1
        self.location = NATIONS[0]

    def status(self):
        print(f"\n{self.day}일차")
        print(f"{self.name}의 상태:")
        print(f"건강: {self.health}")
        print(f"배고픔: {self.hunger}")
        print(f"에너지: {self.energy}")
        print(f"돈: {self.money}원")
        print(f"경험치: {self.experience}")
        print(f"현재 위치: {self.location.name}\n")

    def is_alive(self):
        return self.health > 0

    def end_day(self):
        self.day += 1
        self.hunger -= 5
        if self.hunger <= 0:
            self.health += self.hunger  # subtract absolute over hunger
            self.hunger = 0
        if self.energy <= 0:
            self.health += self.energy
            self.energy = 0

class Game:
    def __init__(self, player):
        self.player = player

    def work(self):
        if self.player.energy < 20 or self.player.hunger < 20:
            print("에너지가 부족하거나 너무 배가 고파서 일할 수 없습니다.")
            return
        self.player.money += 10
        self.player.energy -= 20
        self.player.hunger -= 10
        self.player.experience += 1
        print("일해서 10원을 벌었습니다.")

    def eat(self):
        if self.player.money < 5:
            print("음식을 살 돈이 부족합니다.")
            return
        self.player.money -= 5
        self.player.hunger += 20
        if self.player.hunger > 100:
            self.player.hunger = 100
        self.player.energy += 10
        if self.player.energy > 100:
            self.player.energy = 100
        print("식사를 했습니다.")

    def sleep(self):
        self.player.energy = 100
        self.player.hunger -= 10
        if self.player.hunger < 0:
            self.player.hunger = 0
        print("잠을 자고 기력이 회복되었습니다.")

    def explore(self):
        print(f"{self.player.location.name}을 탐험합니다. {self.player.location.description}")
        event = random.choice(["find_money", "nothing", "injury"])
        if event == "find_money":
            found = random.randint(5, 20)
            self.player.money += found
            print(f"탐험 중에 {found}원을 발견했습니다.")
        elif event == "injury":
            damage = random.randint(5, 15)
            self.player.health -= damage
            print(f"탐험 중 부상을 입어 체력이 {damage} 감소했습니다.")
        else:
            print("탐험 중 아무 일도 일어나지 않았습니다.")

    def travel(self):
        print("이동할 국가를 선택하세요:")
        for i, nation in enumerate(NATIONS, start=1):
            print(f"{i}. {nation.name} - {nation.description}")
        choice = input("> ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(NATIONS):
                self.player.location = NATIONS[idx]
                print(f"{self.player.location.name}으로 이동했습니다.")
                return
        print("잘못된 선택입니다.")

    def play(self):
        actions = {
            "1": self.work,
            "2": self.eat,
            "3": self.sleep,
            "4": self.explore,
            "5": self.travel,
            "q": None,
        }
        while self.player.is_alive():
            self.player.status()
            print("행동을 선택하세요:")
            print("1. 일하기")
            print("2. 식사")
            print("3. 잠자기")
            print("4. 탐험")
            print("5. 이동")
            print("q. 종료")
            choice = input("> ").strip()
            if choice == "q":
                print("게임을 종료합니다.")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("잘못된 선택입니다.")
            self.player.end_day()
        if not self.player.is_alive():
            print("건강이 나빠 쓰러졌습니다. 게임 오버.")


def main():
    name = input("캐릭터 이름을 입력하세요: ")
    player = Player(name)
    game = Game(player)
    game.play()

if __name__ == "__main__":
    main()
