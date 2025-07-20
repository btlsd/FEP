# -*- coding: utf-8 -*-
"""Simple text interface for FEP.

Displays player status, current location information, and available
movement options in Korean.
"""

from characters import NPCS, TIME_OF_DAY


def health_message(player):
    ratio = player.health / player.max_health
    if ratio > 0.7:
        return "건강 상태: 양호"
    elif ratio > 0.4:
        return "건강 상태: 주의"
    else:
        return "건강 상태: 위험"


def draw_screen(player, npcs=NPCS):
    """Print a simple status window and location information."""
    print(f"{player.day}일차 {TIME_OF_DAY[player.time]}")
    print(health_message(player))
    print(
        f"체력 {player.health}/{player.max_health} "
        + f"포만감 {player.satiety}/{player.max_satiety} "
        + f"기력 {player.stamina}/{player.max_stamina} "
        + f"청결 {player.cleanliness}/{player.max_cleanliness} "
        + "화폐 "
        + ", ".join(f"{amt}{cur}" for cur, amt in player.money.items())
        + " 무게 "
        + (
            str(player.estimated_weight())
            if player.perception >= 10
            else f"약 {player.estimated_weight()}"
        )
        + f"/{player.carrying_capacity()}"
    )
    print("-" * 30)

    location = player.location
    print(f"현재 위치: {location.name}")
    print(location.get_description(player.time))
    if location.station:
        if getattr(location, "international", False):
            print("국가 간 이동이 가능한 정거장이 있습니다.")
        else:
            print("이곳에는 장거리 이동을 위한 정거장이 있습니다.")
    nearby = [c.name for c in npcs if c.location == location]
    if nearby:
        print("주변 인물: " + ", ".join(nearby))
    else:
        print("주변 인물: 없음")
    print("-" * 30)

    from locations import LOCATIONS
    foot = [loc for loc in LOCATIONS if loc.zone == location.zone and loc != location]
    if foot:
        print("도보 이동 가능:")
        for dest in foot:
            print(f"- {dest.name}")
    else:
        print("도보로 이동할 장소가 없습니다.")
    if location.station and location.connections:
        print("정거장 이동 가능:")
        for dest in location.connections:
            print(f"- {dest.name}")
    print()
