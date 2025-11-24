from abc import ABC
from dataclasses import dataclass

from src.core.types.coord import Coord


@dataclass
class AbstractCoordEntity(ABC):
    """
    Base class for all entities that exist on the game map.

    All map entities have a coordinate. This class defines the common
    interface and shared fields for all map entities.
    """

    coord: Coord

    # Simple helper methods (OK in entity)
    def is_at(self, coord: Coord) -> bool:
        """Check if entity is at given coordinate."""
        return self.coord == coord

    def distance_to(self, other: "AbstractCoordEntity") -> int:
        """Manhattan distance to another map entity."""
        return self.coord.manhattan_distance(other.coord)
