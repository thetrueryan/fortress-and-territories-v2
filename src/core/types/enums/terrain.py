"""
Terrain type enum.
"""

from enum import Enum


class TerrainType(str, Enum):
    """Types of terrain tiles on the map."""

    EMPTY = "empty"
    WATER = "water"
    MOUNTAIN = "mountain"
    BRIDGE = "bridge"
    TOWER = "tower"
    PORTAL = "portal"
    FOG = "fog"
