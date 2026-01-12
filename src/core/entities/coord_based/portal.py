from dataclasses import dataclass, field

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
    type = BuildingType.PORTAL
    icon = "H"
    linked_portal_coord: Coord = field(kw_only=True)
    cost = 1

    def is_captured(self) -> bool:
        """Check if portal is captured by a faction."""
        return self.faction_id is not None

    def get_linked_coord(self) -> Coord:
        """Get coordinate of linked portal."""
        return self.linked_portal_coord
