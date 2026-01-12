from dataclasses import dataclass

from .building import Building
from src.core.types.enums.building import BuildingType


@dataclass
class Base(Building):
    """
    Base building - the heart of a faction.

    If base is destroyed, faction is defeated.
    Base always has an owner (faction_id is never None).
    """
    icon = "@"
    is_destroyed: bool = False
    cost = 1

    def __post_init__(self):
        """Ensure building_type is BASE and faction_id is set."""
        if self.type != BuildingType.BASE:
            self.type = BuildingType.BASE
        if self.faction_id is None:
            raise ValueError("Base must have a faction_id (cannot be None)")


