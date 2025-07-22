"""Helper utilities for input handling."""


def choose_option(options, allow_back=True):
    """Display numbered options and return the selected index.

    Returns None if the user chooses to go back when allow_back is True.
    """
    while True:
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        if allow_back:
            print("0. 뒤로 가기")
        choice = input("> ").strip()
        if allow_back and choice == "0":
            return None
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
        print("잘못된 선택입니다.")

import random


def roll_check(chance):
    """Roll 1-100 and return True if the result is <= chance.

    The function also prints the target value and the rolled number so the
    player can see how close they were to succeeding.
    """
    roll = random.randint(1, 100)
    outcome = "성공" if roll <= chance else "실패"
    print(f"목표 {chance} - 결과 {roll} => {outcome}")
    return roll <= chance
