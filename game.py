import random

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.hunger = 100
        self.energy = 100
        self.money = 20
        self.experience = 0
        self.day = 1

    def status(self):
        print(f"\n{self.day}일차")
        print(f"{self.name}의 상태:")
        print(f"건강: {self.health}")
        print(f"배고픔: {self.hunger}")
        print(f"에너지: {self.energy}")
        print(f"돈: {self.money}원")
        print(f"경험치: {self.experience}\n")

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

    def play(self):
        actions = {
            "1": self.work,
            "2": self.eat,
            "3": self.sleep,
            "4": self.explore,
            "q": None,
        }
        while self.player.is_alive():
            self.player.status()
            print("행동을 선택하세요:")
            print("1. 일하기")
            print("2. 식사")
            print("3. 잠자기")
            print("4. 탐험")
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
