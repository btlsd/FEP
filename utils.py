"""Helper utilities for input handling."""


def choose_option(options, allow_back=True, path=None):
    """Display numbered options and return the selected index.

    If *path* is provided, it should be a sequence of strings representing
    the menu hierarchy and will be printed above the options. Returns ``None``
    if the user chooses to go back when ``allow_back`` is ``True``.
    """
    while True:
        if path:
            print(" > ".join(path))
            print("-" * 30)
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

import sys
import time


def progress_bar(prefix: str = "", length: int = 10, delay: float = 0.2) -> None:
    """Print a simple text progress bar."""
    for i in range(length):
        bar = "#" * (i + 1) + "-" * (length - i - 1)
        print(f"\r{prefix}[{bar}]", end="", flush=True)
        time.sleep(delay)
    print(f"\r{prefix}[{'#' * length}]")


def color_text(text: str, code: str) -> str:
    """Return text wrapped in an ANSI color code."""
    return f"\033[{code}m{text}\033[0m"


def find_path(start, goal):
    """Return a list of locations from ``start`` to ``goal`` using BFS."""
    from collections import deque

    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        loc, path = queue.popleft()
        if loc == goal:
            return path
        for nxt in loc.connections:
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))
    return None
