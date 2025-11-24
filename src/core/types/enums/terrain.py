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
    
    def describe(self) -> str:
        """Human-readable description of terrain type."""
        descriptions = {
            TerrainType.EMPTY: "Land",
            TerrainType.WATER: "Water",
            TerrainType.MOUNTAIN: "Mountain",
            TerrainType.BRIDGE: "Bridge",
            TerrainType.TOWER: "Neutral Tower",
            TerrainType.PORTAL: "Portal",
            TerrainType.FOG: "Fog",
        }
        return descriptions.get(self, "Unknown")

