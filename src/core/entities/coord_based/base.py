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
    type = BuildingType.BASE
