from dataclasses import dataclass
from typing import Tuple

import curses

@dataclass
class ColorConfig:
    """Color palette configuration for factions."""
    color_map: Tuple[int, ...] = (
        curses.COLOR_RED,
        curses.COLOR_GREEN,
        curses.COLOR_BLUE,
        curses.COLOR_YELLOW,
        curses.COLOR_CYAN,
        curses.COLOR_MAGENTA,
        curses.COLOR_WHITE,
        208,  # Orange
        46,   # Lime
        201,  # Pink
        130,  # Brown
        245,  # Grey
        27,
        33,
        39,
        75,
        81,
        99,
        123,
        141,
        149,
        165,
        177,
        184,
        190,
        196,
        202,
        210,
        214,
        220,
        34,
        118,
        140,
        160,
        94,
        136,
        206,
        213,
    )