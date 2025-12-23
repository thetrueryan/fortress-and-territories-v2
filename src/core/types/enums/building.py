from enum import Enum


class BuildingType(Enum):
    """Types of fortresses in the game."""

    BASE = "base"  # Base of a faction
    TERRITORY = "territory"  # Territory of a faction
    FORTRESS = "fortress"  # Standard fortress
    TOWER = "tower"  # Captured watchtower
    BRIDGE = "bridge"  # Bridge over water
    PORTAL = "portal"  # Portal/teleporter
