"""
Utility helpers shared across AI components.
"""

from dataclasses import dataclass

from src.core.types.coord import Coord


@dataclass(frozen=True)
class AIHelper:
    """
    Static helper methods used by AI subsystems.

    Keeping helpers in a dedicated dataclass (instead of free functions)
    simplifies mocking/replacing behaviour during tests.
    """

    @staticmethod
    def distance(p1: Coord, p2: Coord) -> int:
        """Return Manhattan distance between two coordinates."""
        return p1.manhattan_distance(p2)

    @staticmethod
    def clamp(value: int, min_value: int, max_value: int) -> int:
        """Clamp an integer value into the inclusive [min_value, max_value] range."""
        return max(min_value, min(value, max_value))
