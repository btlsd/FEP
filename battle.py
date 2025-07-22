import random
from utils import choose_option, roll_check


def _active_weapon(combatant):
    """Return equipped weapon or weapon-providing mod if any."""
    weapon = getattr(combatant, "weapon", None)
    if not weapon:
        for mod in getattr(combatant, "mods", {}).values():
            if getattr(mod, "weapon_damage", 0) > 0:
                weapon = mod
                break
    return weapon


def gauge_cost(combatant):
    """Return how much of the turn gauge is consumed per tick."""
    agility = getattr(combatant, "agility", 5)
    cost = min(99, 50 + agility * 5)
    weapon = _active_weapon(combatant)
    if weapon and getattr(weapon, "weapon_range", None) == "melee":
        weight = getattr(weapon, "weight", 0)
        cost = max(10, cost - int(weight * 2))
    return cost


def wireless_intrusion(victim):
    """Random chance for wireless hacking damage."""
    if getattr(victim, "has_flag", lambda x: False)("wireless"):
        if random.random() < 0.1:
            dmg = 5
            victim.health -= dmg
            print(f"{victim.name}의 무선 인터페이스가 해킹당해 {dmg}의 피해!")


def attempt_hack(attacker, defender):
    """Try to hack the opponent, returning True if action consumed."""
    if not getattr(attacker, "has_flag", lambda x: False)("wireless"):
        return False
    if not getattr(defender, "has_flag", lambda x: False)("wireless"):
        return False
    chance = 40 + getattr(attacker, "intelligence", 5) * 5 - getattr(defender, "intelligence", 5) * 5
    if roll_check(max(5, min(95, chance))):
        dmg = random.randint(10, 20)
        defender.health -= dmg
        print(f"{attacker.name}의 해킹 성공! {defender.name}에게 {dmg}의 피해를 주었습니다.")
    else:
        print(f"{attacker.name}의 해킹이 실패했습니다.")
    return True


def attack_hit(attacker, defender, weapon):
    """Determine if an attack hits using stats and weapon weight."""
    base = 70 + getattr(attacker, "agility", 5) * 2 + getattr(attacker, "perception", 5)
    base -= getattr(defender, "agility", 5) * 2
    weight = getattr(weapon, "weight", 0)
    w_range = getattr(weapon, "weapon_range", None)
    if w_range:
        base -= int(weight * 2)
    base = max(5, min(95, base))
    return roll_check(base)


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
        gauges[player] -= gauge_cost(player)
        gauges[npc] -= gauge_cost(npc)
        wireless_intrusion(player)
        wireless_intrusion(npc)
        if gauges[player] <= 0:
            action = choose_option(["공격", "기술", "도주"], allow_back=False)
            if action == 0:
                target_idx = choose_option(["머리", "몸통", "팔", "다리"], allow_back=False)
                target_names = ["머리", "몸통", "팔", "다리"]
                t_name = target_names[target_idx]
                weapon = _active_weapon(player)
                w_dmg = getattr(weapon, "damage", getattr(weapon, "weapon_damage", 0))
                w_type = getattr(weapon, "weapon_type", None)
                dmg = random.randint(5, 10) + getattr(player, "strength", 5) + w_dmg
                extra_msg = ""
                if w_type == "냉병기" and t_name != "몸통" and random.random() < 0.3:
                    extra_msg = f" {npc.name}의 {t_name}을 절단했습니다!"
                    dmg += 10
                if w_type == "둔기" and t_name == "머리" and random.random() < 0.3:
                    extra_msg = f" {npc.name}을 기절시켰습니다!"
                    gauges[npc] += 100
                if attack_hit(player, npc, weapon):
                    npc.health -= dmg
                    print(f"당신의 공격! {npc.name}에게 {dmg}의 피해를 주었습니다.{extra_msg}")
                else:
                    print("공격이 빗나갔습니다!")
            elif action == 1:
                if not attempt_hack(player, npc):
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
            weapon = _active_weapon(npc)
            w_dmg = getattr(weapon, "damage", getattr(weapon, "weapon_damage", 0))
            w_type = getattr(weapon, "weapon_type", None)
            if (
                npc.has_flag("wireless")
                and player.has_flag("wireless")
                and random.random() < 0.3
            ):
                attempt_hack(npc, player)
            dmg = random.randint(5, 10) + getattr(npc, "strength", 5) + w_dmg
            if w_type == "둔기" and random.random() < 0.1:
                print(f"{npc.name}이(가) 머리를 강타하여 당신이 기절합니다!")
                gauges[player] += 100
            if attack_hit(npc, player, weapon):
                player.health -= dmg
                print(f"{npc.name}의 공격! {dmg}의 피해를 받았습니다.")
            else:
                print(f"{npc.name}의 공격이 빗나갔습니다.")
            gauges[npc] = 100
            turns += 1
    if player.health <= 0:
        print("당신이 쓰러졌습니다...")
        return False, turns
    else:
        print(f"{npc.name}을(를) 쓰러뜨렸습니다!")
        npc.affinity = max(0, npc.affinity - 20)
        npc.alive = False
        return True, turns


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