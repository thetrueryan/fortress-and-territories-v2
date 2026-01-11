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

    vision_radius: int = 15

    def __post_init__(self):
        """Ensure building_type is TOWER."""
        if self.type != BuildingType.TOWER:
            self.type = BuildingType.TOWER

    def is_captured(self) -> bool:
        """Check if tower is captured by a faction."""
        return self.faction_id is not None

    @property
    def should_age(self) -> bool:
        """Towers never age in Classic mode."""
        return False
