"""
Faction module
==============

Faction representation for game state management.
"""

from dataclasses import dataclass

from .coord_based import (
    Base, 
    Territory,
    Building,
    Bridge,
    Tower,
    Fortress,
    Portal
)
from src.core.types import Coord
from src.core.types.enums import BuildingType


@dataclass
class Faction:
    """
    Faction representation.

    Represents a game faction with base, territories, and buildings.
    Can be either human player (is_ai=False) or AI bot (is_ai=True).

    For future AI-specific functionality, can create AIFaction subclass.
    """

    name: str
    color_pair: int
    base: Base
    is_ai: bool
    alive: bool = True
    buildings: list[Building]

    @property
    def all_buildings(self) -> set[Building]:
        """Get all building (excluding base, as it's stored separately)."""
        return [building.coord for building in self.buildings]

    @property
    def territory(self) -> set[Territory]:
        """Get territory (returns reference to actual set)."""
        return [building.coord for building in self.buildings if building.type == BuildingType.TERRITORY]
    
    @property
    def bridges(self) -> set[Bridge]:
        """Get bridge (returns reference to actual set)."""
        return [building.coord for building in self.buildings if building.type == BuildingType.BRIDGE]

    @property
    def towers(self) -> set[Tower]:
        """Get tower (returns reference to actual set)."""
        return [building.coord for building in self.buildings if building.type == BuildingType.TOWER]

    @property
    def portals(self) -> set[Portal]:
        """Get portal (returns reference to actual set)."""
        return [building.coord for building in self.buildings if building.type == BuildingType.PORTAL]

    @property
    def fortresses(self) -> set[Fortress]:
        """Get fortress (returns reference to actual set)."""
        return [building.coord for building in self.buildings if building.type == BuildingType.FORTRESS]

    @property
    def score(self) -> int:
        """Calculate score (all buildings count)."""
        return len(self.all_buildings)
    
    # Simple helper methods (same as Client)
    def kill(self) -> None:
        """Mark faction as defeated."""
        self.alive = False

    def revive(self) -> None:
        """Revive faction."""
        self.alive = True

    def get_building(self, coord: Coord) -> Building | None:
        for b in self.buildings:
            if b.coord == coord:
                return b
        return None

    def add_building(self, building: Building) -> bool:
        if self.base and building.type == BuildingType.BASE:
            return False
        self.buildings.append(building)
        return True

    def remove_building(self, coord: Coord) -> bool:
        for idx, b in enumerate(self.buildings):
            if b.coord == coord:
               removed_building = self.buildings.pop(idx)
               if removed_building:
                   return True
        return False           
    
    def owns(self, coord: Coord) -> bool:
        """Check if faction owns given coordinate."""
        if self.base.coord == coord:
            return True
        else:
            for b in self.buildings:
                if b.coord == coord:
                    return True
        return False
