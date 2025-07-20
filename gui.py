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
        + f"배고픔 {player.hunger} 에너지 {player.energy}/{player.max_energy} "
        + f"돈 {player.money}원 무게 {player.current_weight()}/{player.carrying_capacity()}"
    )
    print("-" * 30)

    location = player.location
    print(f"현재 위치: {location.name}")
    print(location.description)
    nearby = [c.name for c in npcs if c.location == location]
    if nearby:
        print("주변 인물: " + ", ".join(nearby))
    else:
        print("주변 인물: 없음")
    print("-" * 30)

    if location.connections:
        print("이동 가능 장소:")
        for dest in location.connections:
            print(f"- {dest.name}")
    else:
        print("이동 가능한 장소가 없습니다.")
    print()
