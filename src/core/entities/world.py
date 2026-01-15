"""
World module
============

Represents the game map (terrain + neutral structures).
"""
from src.core.types.coord import Coord
from src.core.types.enums import WorldType
from src.core.entities.coord_based import (
    Terrain,
    Building
)

class World:
    """
    Represents the game map (terrain + neutral structures).

    Manages terrain data, neutral towers, portals, and provides
    query/mutation methods for the game world.
    """

    def __init__(
        self,
        width: int,
        height: int,
        world_type: WorldType = WorldType.STANDARD,
    ) -> None:
        self.width = width
        self.height = height
        self.terrain: dict[Coord, Terrain] = {}
        self.neutral_buildings: dict[Coord, Building] = {}
        self.world_type = world_type

    def get_neutral_building(self, coord: Coord) -> Building | None:
        """Get list of all neutral tower coordinates."""
        if not coord.in_bounds(self.width, self.height):
            return None
        
        building = self.neutral_buildings.get(coord)
        if not building.faction_id:
            return building
        return None

    def get_terrain(self, coord: Coord) -> Terrain | None:
        """Get terrain type at coordinate."""
        if not coord.in_bounds(self.width, self.height):
            return None
        return self.terrain[coord]

    def set_terrain(self, tile: Terrain) -> None:
        """Set terrain type at coordinate."""
        if tile.coord.in_bounds(self.width, self.height):
            self.terrain[tile.coord] = tile

    def add_neutral_building(self, building: Building) -> None:
        """Add neutral tower entity."""
        if building.faction_id is not None:
            raise ValueError("Only neutral towers can be added to World")
        
        if not self.in_bounds(building.coord):
            raise ValueError("Building coord out of bounds")
        self.neutral_buildings[building.coord] = building
    
    def remove_neutral_building(self, coord: Coord) -> Building | None:
        """Remove neutral tower entity. Returns removed tower or None."""
        return self.neutral_buildings.pop(coord, None)

    def get_move_cost(self, coord: Coord) -> int | None:
        """Get movement cost for a tile."""
        tile = self.get_terrain(coord)
        if not tile:
            return None
        return tile.cost
