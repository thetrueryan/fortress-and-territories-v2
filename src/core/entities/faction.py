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
    buildings: dict[BuildingType, set[Building]]

    @property
    def all_buildings(self) -> set[Building]:
        """Get all building"""
        return {building for building in self.buildings.values()}

    @property
    def territory(self) -> set[Territory]:
        """Get territory (returns reference to actual set)."""
        return self.buildings[BuildingType.TERRITORY]
    
    @property
    def bridges(self) -> set[Bridge]:
        """Get bridge (returns reference to actual set)."""
        return self.buildings[BuildingType.BRIDGE]

    @property
    def towers(self) -> set[Tower]:
        """Get tower (returns reference to actual set)."""
        return self.buildings[BuildingType.TOWER]

    @property
    def portals(self) -> set[Portal]:
        """Get portal (returns reference to actual set)."""
        return self.buildings[BuildingType.PORTAL]

    @property
    def fortresses(self) -> set[Fortress]:
        """Get fortress (returns reference to actual set)."""
        return self.buildings[BuildingType.FORTRESS]

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

    def get_building(self, building_type: BuildingType, coord: Coord) -> Building | None:
        if building_type in self.buildings:
            buildings = self.buildings[building_type]
            for b in buildings:
                if b.coord == coord and b.type == building_type:
                    return b
            return None
        return None

    def add_building(self, building: Building) -> bool:
        if self.base and building.type == BuildingType.BASE:
            return False
        
        if building.type not in self.buildings:
            self.buildings[building.type] = set()
        self.buildings[building.type].add(building)
        return True

    def remove_building(self, building_type: BuildingType, coord: Coord) -> bool:
        if building_type in self.buildings:
            buildings = self.buildings[building_type]
            for b in buildings:
                if b.coord == coord:
                    buildings.discard(b)
                    return True
            return False
        return False           
        
