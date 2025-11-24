from dataclasses import dataclass


@dataclass
class DisplayConfig:
    """Display and rendering constants."""

    offset_x: int = 2
    offset_y: int = 2
    animation_delay: float = 0.1
