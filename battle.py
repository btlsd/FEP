import random
from utils import choose_option


def gauge_cost(agility):
    """Return how much of the turn gauge is consumed per tick."""
    return min(99, 50 + agility * 5)


def start_battle(player, npc, ambush=None):
    """Run a simple turn-based battle between player and npc.

    Returns (win:bool, turns:int) where turns is the number of actions taken
    by both sides combined.
    """
    print(f"{npc.name}과(와) 전투를 시작합니다!")
    gauges = {
        player: 0 if ambush == "player" else 100,
        npc: 0 if ambush == "npc" else 100,
    }
    turns = 0
    while player.health > 0 and npc.health > 0:
        gauges[player] -= gauge_cost(player.agility)
        gauges[npc] -= gauge_cost(npc.agility)
        if gauges[player] <= 0:
            action = choose_option(["공격", "기술", "도주"], allow_back=False)
            if action == 0:
                target_idx = choose_option(["머리", "몸통", "팔", "다리"], allow_back=False)
                target_names = ["머리", "몸통", "팔", "다리"]
                t_name = target_names[target_idx]
                weapon = getattr(player, "weapon", None)
                w_dmg = getattr(weapon, "damage", 0)
                w_type = getattr(weapon, "weapon_type", None)
                if not weapon:
                    for mod in getattr(player, "mods", {}).values():
                        w_dmg = max(w_dmg, getattr(mod, "weapon_damage", 0))
                        w_type = w_type or getattr(mod, "weapon_type", None)
                dmg = random.randint(5, 10) + getattr(player, "strength", 5) + w_dmg
                extra_msg = ""
                if w_type == "냉병기" and t_name != "몸통" and random.random() < 0.3:
                    extra_msg = f" {npc.name}의 {t_name}을 절단했습니다!"
                    dmg += 10
                if w_type == "둔기" and t_name == "머리" and random.random() < 0.3:
                    extra_msg = f" {npc.name}을 기절시켰습니다!"
                    gauges[npc] += 100
                npc.health -= dmg
                print(f"당신의 공격! {npc.name}에게 {dmg}의 피해를 주었습니다.{extra_msg}")
            elif action == 1:
                print("사용 가능한 기술이 없습니다.")
            else:
                flee_chance = 50 + player.agility * 5 - npc.agility * 5
                if random.randint(1, 100) <= flee_chance:
                    print("성공적으로 도망쳤습니다!")
                    return True
                else:
                    print("도주에 실패했습니다!")
            gauges[player] = 100
            turns += 1
            if npc.health <= 0:
                break
        if gauges[npc] <= 0 and npc.health > 0:
            weapon = getattr(npc, "weapon", None)
            w_dmg = getattr(weapon, "damage", 0)
            w_type = getattr(weapon, "weapon_type", None)
            if not weapon:
                for mod in getattr(npc, "mods", {}).values():
                    w_dmg = max(w_dmg, getattr(mod, "weapon_damage", 0))
                    w_type = w_type or getattr(mod, "weapon_type", None)
            dmg = random.randint(5, 10) + getattr(npc, "strength", 5) + w_dmg
            if w_type == "둔기" and random.random() < 0.1:
                print(f"{npc.name}이(가) 머리를 강타하여 당신이 기절합니다!")
                gauges[player] += 100
            player.health -= dmg
            print(f"{npc.name}의 공격! {dmg}의 피해를 받았습니다.")
            gauges[npc] = 100
            turns += 1
    if player.health <= 0:
        print("당신이 쓰러졌습니다...")
        return False, turns
    else:
        print(f"{npc.name}을(를) 쓰러뜨렸습니다!")
        npc.affinity = max(0, npc.affinity - 20)
        return True, turns
