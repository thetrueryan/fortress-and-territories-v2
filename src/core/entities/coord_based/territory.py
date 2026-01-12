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
    icon = "*"
    cost = 1
    type = BuildingType.TERRITORY
