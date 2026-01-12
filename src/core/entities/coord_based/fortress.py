from dataclasses import dataclass

from .building import Building
from src.core.types.enums.building import BuildingType


@dataclass
class Fortress(Building):
    """
    Regular fortress building.

    Represents captured enemy territory converted to fortress.
    """
    icon = "#"
    cost = 999 # For classic mode, fortress is unbreakable, but in conqueror mode it eq 2
    def __post_init__(self):
        """Ensure building_type is FORTRESS."""
        if self.type != BuildingType.FORTRESS:
            self.type = BuildingType.FORTRESS
