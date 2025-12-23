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

    def __post_init__(self):
        """Ensure building_type is BRIDGE."""
        if self.building_type != BuildingType.BRIDGE:
            self.building_type = BuildingType.BRIDGE

    @property
    def should_age(self) -> bool:
        """Bridges never age in Classic mode."""
        return False
