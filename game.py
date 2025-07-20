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
        print(f"\nDay {self.day}")
        print(f"{self.name}'s Status:")
        print(f"Health: {self.health}")
        print(f"Hunger: {self.hunger}")
        print(f"Energy: {self.energy}")
        print(f"Money: ${self.money}")
        print(f"Experience: {self.experience}\n")

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
            print("Not enough energy or too hungry to work.")
            return
        self.player.money += 10
        self.player.energy -= 20
        self.player.hunger -= 10
        self.player.experience += 1
        print("You worked and earned $10.")

    def eat(self):
        if self.player.money < 5:
            print("Not enough money to buy food.")
            return
        self.player.money -= 5
        self.player.hunger += 20
        if self.player.hunger > 100:
            self.player.hunger = 100
        self.player.energy += 10
        if self.player.energy > 100:
            self.player.energy = 100
        print("You had a meal.")

    def sleep(self):
        self.player.energy = 100
        self.player.hunger -= 10
        if self.player.hunger < 0:
            self.player.hunger = 0
        print("You slept and feel rested.")

    def explore(self):
        event = random.choice(["find_money", "nothing", "injury"])
        if event == "find_money":
            found = random.randint(5, 20)
            self.player.money += found
            print(f"You found ${found} while exploring.")
        elif event == "injury":
            damage = random.randint(5, 15)
            self.player.health -= damage
            print(f"You got hurt while exploring and lost {damage} health.")
        else:
            print("Nothing happened during your exploration.")

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
            print("Choose an action:")
            print("1. Work")
            print("2. Eat")
            print("3. Sleep")
            print("4. Explore")
            print("q. Quit")
            choice = input("> ").strip()
            if choice == "q":
                print("Goodbye!")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid choice")
            self.player.end_day()
        if not self.player.is_alive():
            print("You have collapsed from poor health. Game over.")


def main():
    name = input("Enter your character's name: ")
    player = Player(name)
    game = Game(player)
    game.play()

if __name__ == "__main__":
    main()
