"""
Faction module
==============

Faction representation for game state management.
"""

from dataclasses import dataclass, field

from src.core.types.coord import Coord
from src.core.types.enums.building import BuildingType


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
    base: Coord
    is_ai: bool
    alive: bool = True
    # Unified storage for all building types (including base, territory, fortresses, etc.)
    buildings: dict[BuildingType, set[Coord]] = field(
        default_factory=lambda: {
            BuildingType.BASE: set(),  # Base is also a building (can be captured in future modes)
            BuildingType.TERRITORY: set(),  # Territory is also a building
            BuildingType.BRIDGE: set(),
            BuildingType.TOWER: set(),
            BuildingType.PORTAL: set(),
            BuildingType.FORTRESS: set(),
        }
    )
    
    def __post_init__(self):
        """Initialize base in buildings after object creation."""
        if BuildingType.BASE not in self.buildings:
            self.buildings[BuildingType.BASE] = set()
        # Add base to buildings if not already present
        if self.base not in self.buildings[BuildingType.BASE]:
            self.buildings[BuildingType.BASE].add(self.base)
    
    @property
    def all_buildings(self) -> set[Coord]:
        """Get all building coordinates (excluding base, as it's stored separately)."""
        return {coord for bt, coords in self.buildings.items() 
                if bt != BuildingType.BASE for coord in coords}
    
    @property
    def territory(self) -> set[Coord]:
        """Get territory coordinates (returns reference to actual set)."""
        if BuildingType.TERRITORY not in self.buildings:
            self.buildings[BuildingType.TERRITORY] = set()
        return self.buildings[BuildingType.TERRITORY]
    
    # Convenience properties for specific building types
    # These return references to the actual sets, so modifications are preserved
    @property
    def bridges(self) -> set[Coord]:
        """Get bridge coordinates (returns reference to actual set)."""
        if BuildingType.BRIDGE not in self.buildings:
            self.buildings[BuildingType.BRIDGE] = set()
        return self.buildings[BuildingType.BRIDGE]
    
    @property
    def towers(self) -> set[Coord]:
        """Get tower coordinates (returns reference to actual set)."""
        if BuildingType.TOWER not in self.buildings:
            self.buildings[BuildingType.TOWER] = set()
        return self.buildings[BuildingType.TOWER]
    
    @property
    def portals(self) -> set[Coord]:
        """Get portal coordinates (returns reference to actual set)."""
        if BuildingType.PORTAL not in self.buildings:
            self.buildings[BuildingType.PORTAL] = set()
        return self.buildings[BuildingType.PORTAL]
    
    @property
    def fortresses(self) -> set[Coord]:
        """Get fortress coordinates (returns reference to actual set)."""
        if BuildingType.FORTRESS not in self.buildings:
            self.buildings[BuildingType.FORTRESS] = set()
        return self.buildings[BuildingType.FORTRESS]
    
    # Simple helper methods (same as Client)
    def kill(self) -> None:
        """Mark faction as defeated."""
        self.alive = False
    
    def revive(self) -> None:
        """Revive faction."""
        self.alive = True
    
    def add_territory(self, coord: Coord) -> None:
        """Add territory coordinate."""
        self.add_building(coord, BuildingType.TERRITORY)
    
    def remove_territory(self, coord: Coord) -> None:
        """Remove territory coordinate."""
        self.remove_building(coord, BuildingType.TERRITORY)
    
    def add_building(self, coord: Coord, building_type: BuildingType) -> None:
        """Add building coordinate of specified type."""
        if building_type not in self.buildings:
            self.buildings[building_type] = set()
        self.buildings[building_type].add(coord)
    
    def remove_building(self, coord: Coord, building_type: BuildingType) -> None:
        """Remove building coordinate of specified type."""
        if building_type in self.buildings:
            self.buildings[building_type].discard(coord)
    
    def get_buildings(self, building_type: BuildingType) -> set[Coord]:
        """Get buildings of specified type."""
        return self.buildings.get(building_type, set())
    
    # Convenience methods for specific building types
    def add_fortress(self, coord: Coord) -> None:
        """Add fortress coordinate."""
        self.add_building(coord, BuildingType.FORTRESS)
    
    def remove_fortress(self, coord: Coord) -> None:
        """Remove fortress coordinate."""
        self.remove_building(coord, BuildingType.FORTRESS)
    
    def owns(self, coord: Coord) -> bool:
        """Check if faction owns given coordinate."""
        return (
            coord == self.base 
            or coord in self.territory 
            or coord in self.all_buildings
            or coord in self.buildings.get(BuildingType.BASE, set())
        )
    
    @property
    def score(self) -> int:
        """Calculate score (territories + all buildings count)."""
        return len(self.territory) + len(self.all_buildings)
    
    def add_bridge(self, coord: Coord) -> None:
        """Add bridge coordinate."""
        self.add_building(coord, BuildingType.BRIDGE)
    
    def remove_bridge(self, coord: Coord) -> None:
        """Remove bridge coordinate."""
        self.remove_building(coord, BuildingType.BRIDGE)
    
    def add_tower(self, coord: Coord) -> None:
        """Add tower coordinate."""
        self.add_building(coord, BuildingType.TOWER)
    
    def remove_tower(self, coord: Coord) -> None:
        """Remove tower coordinate."""
        self.remove_building(coord, BuildingType.TOWER)
    
    def add_portal(self, coord: Coord) -> None:
        """Add portal coordinate."""
        self.add_building(coord, BuildingType.PORTAL)
    
    def remove_portal(self, coord: Coord) -> None:
        """Remove portal coordinate."""
        self.remove_building(coord, BuildingType.PORTAL)
    
    def summary(self) -> str:
        """Human-readable summary."""
        status = "AI" if self.is_ai else "HUMAN"
        state = "ALIVE" if self.alive else "DEAD"
        bases = len(self.buildings.get(BuildingType.BASE, set()))
        return (
            f"{self.name} ({status}, {state}) | "
            f"Territory: {len(self.territory)} tiles | "
            f"Buildings: {len(self.all_buildings)} "
            f"(Base:{bases} F:{len(self.fortresses)} B:{len(self.bridges)} "
            f"T:{len(self.towers)} P:{len(self.portals)})"
        )
