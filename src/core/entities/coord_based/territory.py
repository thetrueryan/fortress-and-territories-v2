from dataclasses import dataclass

from .building import Building
from src.core.types.enums.building import BuildingType


@dataclass
class Territory(Building):
    """
    Territory building - owned land of a faction.

    Territory is the basic building type that can be converted to fortress.
    Territory always has an owner (faction_id is never None).
    """

    def __post_init__(self):
        """Ensure building_type is TERRITORY and faction_id is set."""
        if self.building_type != BuildingType.TERRITORY:
            self.building_type = BuildingType.TERRITORY
        if self.faction_id is None:
            raise ValueError("Territory must have a faction_id (cannot be None)")

    @property
    def should_age(self) -> bool:
        """Territory never ages in Classic mode (only fortresses age)."""
        return False
