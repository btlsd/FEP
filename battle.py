import random


def gauge_cost(agility):
    """Return how much of the turn gauge is consumed per tick."""
    return min(99, 50 + agility * 5)


def start_battle(player, npc):
    """Run a simple turn-based battle between player and npc."""
    print(f"{npc.name}과(와) 전투를 시작합니다!")
    gauges = {player: 100, npc: 100}
    while player.health > 0 and npc.health > 0:
        gauges[player] -= gauge_cost(player.agility)
        gauges[npc] -= gauge_cost(npc.agility)
        if gauges[player] <= 0:
            dmg = random.randint(5, 10) + player.strength
            npc.health -= dmg
            print(f"당신의 공격! {npc.name}에게 {dmg}의 피해를 주었습니다.")
            gauges[player] = 100
            if npc.health <= 0:
                break
        if gauges[npc] <= 0:
            dmg = random.randint(5, 10)
            player.health -= dmg
            print(f"{npc.name}의 공격! {dmg}의 피해를 받았습니다.")
            gauges[npc] = 100
    if player.health <= 0:
        print("당신이 쓰러졌습니다...")
    else:
        print(f"{npc.name}을(를) 쓰러뜨렸습니다!")
        npc.affinity = max(0, npc.affinity - 20)
