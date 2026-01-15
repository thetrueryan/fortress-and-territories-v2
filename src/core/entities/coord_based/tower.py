from dataclasses import dataclass

from .building import Building
from src.core.types.enums.building import BuildingType


@dataclass
class Tower(Building):
    """
    Watchtower building.

    Can be neutral (faction_id=None) or captured (faction_id set).
    Provides extended vision radius.
    """
    icon = "T"
    cost = 1


    @property
    def vision_radius(self) -> int:
        if self.faction_id:
            return 15
        return 0

    def is_captured(self) -> bool:
        """Check if tower is captured by a faction."""
        return self.faction_id is not None
