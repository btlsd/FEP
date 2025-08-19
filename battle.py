import random
from collections import defaultdict
from utils import choose_option, roll_check, attach_josa
from messages import get_message


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


def melee_bonus(attacker):
    """Return damage bonus from stats when using melee weapons."""
    str_b = getattr(attacker, "strength", 5) // 2
    agi_b = getattr(attacker, "agility", 5) // 3
    return str_b + agi_b


def crit_check(attacker):
    """Return True if attacker scores a critical hit."""
    chance = (
        getattr(attacker, "agility", 5) * 2
        + getattr(attacker, "perception", 5)
        + getattr(attacker, "intelligence", 5)
    )
    chance = min(50, chance)
    return random.randint(1, 100) <= chance


def wireless_intrusion(victim, logger=print):
    """Random chance for wireless hacking damage.

    Returns the damage inflicted for logging purposes.
    """
    if getattr(victim, "has_flag", lambda x: False)("wireless"):
        if random.random() < 0.1:
            dmg = 5
            victim.health -= dmg
            logger(f"{victim.name}의 무선 인터페이스가 해킹당해 {dmg}의 피해!")
            return dmg
    return 0


def attempt_hack(attacker, defender, logger=print):
    """Try to hack the opponent.

    Returns (consumed:bool, damage:int).
    """
    if not getattr(attacker, "has_flag", lambda x: False)("wireless"):
        return False, 0
    if not getattr(defender, "has_flag", lambda x: False)("wireless"):
        return False, 0
    chance = 40 + getattr(attacker, "intelligence", 5) * 5 - getattr(defender, "intelligence", 5) * 5
    if roll_check(max(5, min(95, chance))):
        dmg = random.randint(10, 20)
        defender.health -= dmg
        logger(f"{attacker.name}의 해킹 성공! {defender.name}에게 {dmg}의 피해를 주었습니다.")
        return True, dmg
    else:
        logger(f"{attacker.name}의 해킹이 실패했습니다.")
        return True, 0


def attack_hit(attacker, defender, weapon):
    """Determine if an attack hits using stats and weapon weight."""
    base = 70 + getattr(attacker, "agility", 5) * 2 + getattr(attacker, "perception", 5)
    base -= getattr(defender, "agility", 5) * 3
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
    print("전투 전 경험치:")
    print(player.xp_bar())

    gauges = {
        player: 0 if ambush == "player" else 100,
        npc: 0 if ambush == "npc" else 100,
    }
    turns = 0
    npc_max = getattr(npc, "max_health", npc.health)
    stats = {
        "damage_dealt": 0,
        "damage_taken": 0,
        "skills_used": defaultdict(int),
        "skill_damage": defaultdict(int),
        "log": [],
    }

    def log(msg):
        stats["log"].append(msg)
        print(f"[로그] {msg}")

    skills = [
        {"name": "해킹", "cost": 10, "resource": "기력", "func": attempt_hack}
    ]

    while player.health > 0 and npc.health > 0:
        print(f"{npc.name} HP {npc.health}/{npc_max}")
        print(f"{player.name} HP {player.health}/{player.max_health}")
        gauges[player] -= gauge_cost(player)
        gauges[npc] -= gauge_cost(npc)
        dmg = wireless_intrusion(player, log)
        if dmg:
            stats["damage_taken"] += dmg
            print("\033[101m화면이 빨갛게 번쩍입니다!\033[0m")
        dmg = wireless_intrusion(npc, log)
        if dmg:
            stats["damage_dealt"] += dmg
            print("\033[107m화면이 하얗게 번쩍입니다!\033[0m")
        if gauges[player] <= 0:
            action = choose_option(["공격", "기술", "도주"], allow_back=False)
            if action == 0:
                target_idx = choose_option(["머리", "몸통", "팔", "다리"], allow_back=False)
                target_names = ["머리", "몸통", "팔", "다리"]
                t_name = target_names[target_idx]
                weapon = _active_weapon(player)
                w_dmg = getattr(weapon, "damage", getattr(weapon, "weapon_damage", 0))
                w_type = getattr(weapon, "weapon_type", None)
                dmg = random.randint(3, 7)
                if w_type == "melee" or getattr(weapon, "weapon_range", None) == "melee":
                    dmg += w_dmg + melee_bonus(player)
                else:
                    dmg += w_dmg
                extra_msg = ""
                if w_type == "냉병기" and t_name != "몸통" and random.random() < 0.3:
                    extra_msg = f" {npc.name}의 {t_name}을 절단했습니다!"
                    dmg += 10
                if w_type == "둔기" and t_name == "머리" and random.random() < 0.3:
                    extra_msg = f" {npc.name}을 기절시켰습니다!"
                    gauges[npc] += 100
                if attack_hit(player, npc, weapon):
                    if crit_check(player):
                        dmg = int(dmg * 1.5)
                        extra_msg += " " + get_message("critical_hit")
                    dmg = max(0, dmg - getattr(npc, "armor", 0))
                    npc.health -= dmg
                    stats["damage_dealt"] += dmg
                    log(f"당신의 공격! {npc.name}에게 {dmg}의 피해를 주었습니다.{extra_msg}")
                    print("\033[107m화면이 하얗게 번쩍입니다!\033[0m")
                else:
                    log("공격이 빗나갔습니다!")
            elif action == 1:
                skill_options = [f"{s['name']}({s['resource']} {s['cost']})" for s in skills]
                idx = choose_option(skill_options, allow_back=False)
                skill = skills[idx]
                if getattr(player, 'stamina', 0) >= skill['cost']:
                    player.stamina -= skill['cost']
                    used, dmg = skill['func'](player, npc, log)
                    stats['skills_used'][skill['name']] += 1
                    stats['skill_damage'][skill['name']] += dmg
                    if dmg > 0:
                        stats['damage_dealt'] += dmg
                        print("\033[107m화면이 하얗게 번쩍입니다!\033[0m")
                    if not used:
                        log("사용 가능한 기술이 없습니다.")
                else:
                    log("기력이 부족합니다.")
            else:
                flee_chance = 50 + player.agility * 5 - npc.agility * 5
                if random.randint(1, 100) <= flee_chance:
                    log("성공적으로 도망쳤습니다!")
                    return True, turns
                else:
                    log("도주에 실패했습니다!")
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
                used, dmg = attempt_hack(npc, player, log)
                if dmg > 0:
                    stats["damage_taken"] += dmg
                    print("\033[101m화면이 빨갛게 번쩍입니다!\033[0m")
            dmg = random.randint(3, 7)
            if w_type == "melee" or getattr(weapon, "weapon_range", None) == "melee":
                dmg += w_dmg + melee_bonus(npc)
            else:
                dmg += w_dmg
            if w_type == "둔기" and random.random() < 0.1:
                log(f"{attach_josa(npc.name, '이/가')} 머리를 강타하여 당신이 기절합니다!")
                gauges[player] += 100
            if attack_hit(npc, player, weapon):
                if crit_check(npc):
                    dmg = int(dmg * 1.5)
                    extra = " " + get_message("critical_hit")
                else:
                    extra = ""
                dmg = max(0, dmg - getattr(player, "armor", 0))
                player.health -= dmg
                stats["damage_taken"] += dmg
                log(f"{npc.name}의 공격! {dmg}의 피해를 받았습니다.{extra}")
                print("\033[101m화면이 빨갛게 번쩍입니다!\033[0m")
            else:
                log(f"{npc.name}의 공격이 빗나갔습니다.")
            gauges[npc] = 100
            turns += 1

    win = player.health > 0
    if win:
        log(f"{npc.name}을(를) 쓰러뜨렸습니다!")
        npc.affinity = max(0, npc.affinity - 20)
        npc.alive = False
    else:
        log("당신이 쓰러졌습니다...")

    xp_gain = 10 if win else 0
    if xp_gain:
        leveled = player.gain_experience(xp_gain)
    else:
        leveled = False

    print("전투 후 경험치:")
    print(player.xp_bar())
    if leveled:
        print(f"레벨 업! 현재 레벨 {player.level}")

    print("\n=== 전투 종료 ===")
    print(f"총 가한 피해: {stats['damage_dealt']}")
    print(f"총 받은 피해: {stats['damage_taken']}")
    for sk, cnt in stats['skills_used'].items():
        dmg = stats['skill_damage'][sk]
        print(f"{sk}: 사용 {cnt}회, 총 피해 {dmg}")
    print(f"획득 경험치: {xp_gain}")
    return win, turns
