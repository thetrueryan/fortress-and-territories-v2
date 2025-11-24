"""
World module
============

Represents the game map (terrain + neutral structures).
"""

from typing import Optional

from core.entities.coord_based.tower import Tower
from core.entities.coord_based.portal import Portal
from core.main_config import settings
from core.types.coord import Coord
from core.types.enums.terrain import TerrainType
from core.types.enums.world import WorldType


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
        portal_pairs: int = 0
    ) -> None:
        self.width = width
        self.height = height
        self.terrain: dict[Coord, str] = {}
        # Use dict for O(1) lookup by coordinate
        self._towers: dict[Coord, Tower] = {}  # Neutral towers only
        self._portals: dict[Coord, Portal] = {}  # Neutral portals only
        self.portal_links: dict[Coord, Coord] = {}  # portal -> linked_portal
        self.world_type = world_type
        self.portal_pairs = portal_pairs
    
    def get_tower_coords(self) -> list[Coord]:
        """Get list of all neutral tower coordinates."""
        return list(self._towers.keys())
    
    def get_portal_coords(self) -> list[Coord]:
        """Get list of all neutral portal coordinates."""
        return list(self._portals.keys())
    
    def in_bounds(self, coord: Coord) -> bool:
        """Check if coordinate is within world bounds."""
        return coord.in_bounds(self.width, self.height)
    
    def get_terrain(self, coord: Coord, default: Optional[str] = None) -> Optional[str]:
        """Get terrain type at coordinate."""
        if not self.in_bounds(coord):
            return default
        return self.terrain.get(coord, default if default is not None else settings.terrain.empty)
    
    def set_terrain(self, coord: Coord, tile: str) -> None:
        """Set terrain type at coordinate."""
        if self.in_bounds(coord):
            self.terrain[coord] = tile
    
    def is_water(self, coord: Coord) -> bool:
        """Check if coordinate is water."""
        return self.get_terrain(coord) == settings.terrain.water
    
    def is_mountain(self, coord: Coord) -> bool:
        """Check if coordinate is mountain."""
        return self.get_terrain(coord) == settings.terrain.mountain
    
    def is_bridge(self, coord: Coord) -> bool:
        """Check if coordinate is bridge."""
        return self.get_terrain(coord) == settings.terrain.bridge
    
    def is_tower(self, coord: Coord) -> bool:
        """Check if coordinate has tower terrain."""
        return self.get_terrain(coord) == settings.terrain.tower
    
    def has_neutral_tower(self, coord: Coord) -> bool:
        """Check if coordinate has a neutral tower entity."""
        return coord in self._towers
    
    def get_tower(self, coord: Coord) -> Optional[Tower]:
        """Get tower entity at coordinate (if exists)."""
        return self._towers.get(coord)
    
    def add_tower(self, tower: Tower) -> None:
        """Add neutral tower entity."""
        if tower.faction_id is not None:
            raise ValueError("Only neutral towers can be added to World")
        self._towers[tower.coord] = tower
        self.set_terrain(tower.coord, settings.terrain.tower)
    
    def remove_tower(self, coord: Coord) -> Optional[Tower]:
        """Remove neutral tower entity. Returns removed tower or None."""
        return self._towers.pop(coord, None)
    
    def get_portal(self, coord: Coord) -> Optional[Portal]:
        """Get portal entity at coordinate (if exists)."""
        return self._portals.get(coord)
    
    def add_portal(self, portal: Portal) -> None:
        """Add neutral portal entity."""
        if portal.faction_id is not None:
            raise ValueError("Only neutral portals can be added to World")
        self._portals[portal.coord] = portal
        self.set_terrain(portal.coord, settings.terrain.portal)
    
    def remove_portal(self, coord: Coord) -> Optional[Portal]:
        """Remove neutral portal entity. Returns removed portal or None."""
        return self._portals.pop(coord, None)
    
    def get_move_cost(self, coord: Coord) -> int:
        """Get movement cost for a tile."""
        tile = self.get_terrain(coord, settings.terrain.empty)
        if tile == settings.terrain.water:
            return 999
        if tile == settings.terrain.mountain:
            return 2
        return 1
    
    def build_bridge(self, coord: Coord) -> None:
        """Convert water tile into a bridge."""
        if self.is_water(coord):
            self.set_terrain(coord, settings.terrain.bridge)
    
    def restore_to_empty(self, coord: Coord) -> None:
        """Reset a tile to plain terrain."""
        if self.in_bounds(coord):
            self.set_terrain(coord, settings.terrain.empty)
    
    def neighbors(self, coord: Coord) -> list[Coord]:
        """Get orthogonal neighbors within bounds."""
        return [n for n in coord.neighbors() if self.in_bounds(n)]
    
    def get_terrain_type(self, coord: Coord) -> TerrainType:
        """Get terrain type enum at coordinate."""
        tile = self.get_terrain(coord, settings.terrain.empty)
        terrain_map = {
            settings.terrain.empty: TerrainType.EMPTY,
            settings.terrain.water: TerrainType.WATER,
            settings.terrain.mountain: TerrainType.MOUNTAIN,
            settings.terrain.bridge: TerrainType.BRIDGE,
            settings.terrain.tower: TerrainType.TOWER,
            settings.terrain.portal: TerrainType.PORTAL,
        }
        return terrain_map.get(tile, TerrainType.EMPTY)
    
    def describe_tile(self, coord: Coord) -> str:
        """Human-readable label for debug/telemetry."""
        return self.get_terrain_type(coord).describe()
    
    def clone(self) -> "World":
        """Create a shallow copy of the world."""
        new_world = World(
            width=self.width,
            height=self.height,
            world_type=self.world_type,
            portal_pairs=self.portal_pairs
        )
        new_world.terrain = dict(self.terrain)
        new_world._towers = dict(self._towers)
        new_world._portals = dict(self._portals)
        new_world.portal_links = dict(self.portal_links)
        return new_world

