from dataclasses import dataclass

from src.core.types.coord import Coord
from .building import Building
from src.core.types.enums.building import BuildingType


@dataclass
class Portal(Building):
    """
    Portal/teleporter building.
    
    Can be neutral (faction_id=None) or captured (faction_id set).
    Has a linked portal coordinate for teleportation.
    """
    linked_portal_coord: Coord
    
    def __post_init__(self):
        """Ensure building_type is PORTAL."""
        if self.building_type != BuildingType.PORTAL:
            self.building_type = BuildingType.PORTAL
    
    def is_captured(self) -> bool:
        """Check if portal is captured by a faction."""
        return self.faction_id is not None
    
    def get_linked_coord(self) -> Coord:
        """Get coordinate of linked portal."""
        return self.linked_portal_coord
    
    @property
    def should_age(self) -> bool:
        """Portals never age in Classic mode."""
        return False

