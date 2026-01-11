from __future__ import annotations

import curses

from src.controllers.game_controller import GameController


def _start_game(stdscr) -> None:
    controller = GameController(stdscr)
    controller.run()

def run() -> None:
    """Entry point used by CLI/poetry scripts."""
    curses.wrapper(_start_game)


if __name__ == "__main__":
    run()
