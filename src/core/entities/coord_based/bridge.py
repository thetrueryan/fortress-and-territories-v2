from dataclasses import dataclass

from .building import Building
from src.core.types.enums.building import BuildingType


@dataclass
class Bridge(Building):
    """
    Bridge building over water.

    Always owned (faction_id is never None) - bridges are built by players.
    Build cost is defined in settings, not here.
    """
    icon = "B"
    cost = 1

    def __post_init__(self):
        """Ensure building_type is BRIDGE."""
        if self.type != BuildingType.BRIDGE:
            self.type = BuildingType.BRIDGE
