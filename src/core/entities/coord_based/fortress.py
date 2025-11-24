from dataclasses import dataclass

from .building import Building
from src.core.types.enums.building import BuildingType


@dataclass
class Fortress(Building):
    """
    Regular fortress building.
    
    Represents captured enemy territory converted to fortress.
    """
    
    def __post_init__(self):
        """Ensure building_type is FORTRESS."""
        if self.building_type != BuildingType.FORTRESS:
            self.building_type = BuildingType.FORTRESS