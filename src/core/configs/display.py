from dataclasses import dataclass


@dataclass(slots=True)
class DisplayConfig:
    """Display and rendering constants."""

    offset_x: int = 2
    offset_y: int = 2
    animation_delay: float = 0.05
    min_view_width: int = 80
    min_view_height: int = 30
    title: str = "FORTRESS & TERRITORIES"
    subtitle: str = "CHAOS EDITION"
    base_char: str = "@"
    fortress_char: str = "#"
    territory_char: str = "*"
    