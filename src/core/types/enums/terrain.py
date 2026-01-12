"""
Terrain type enum.
"""

from enum import Enum


class TerrainType(str, Enum):
    """Types of terrain tiles on the map."""

    EMPTY = "empty"
    WATER = "water"
    FOREST = "forest"
    FOG = "fog"
