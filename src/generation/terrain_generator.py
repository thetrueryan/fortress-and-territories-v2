"""
Terrain generator module.
"""

import random

from src.core.entities.world_entity.world import World
from src.core.entities.faction_entity.faction import Faction
from src.core.main_config import settings
from src.core.states.world import WorldState
from src.core.types.coord import Coord
from src.core.types.enums.world import WorldType
from src.utils.generation_helper import GenerationHelper


class TerrainGenerator:
    """
    Generates terrain for different world types.
    
    Handles terrain generation logic: water, mountains, islands, etc.
    """
    
    def __init__(
        self,
        width: int,
        height: int,
        world_state: WorldState
    ) -> None:
        """
        Initialize terrain generator.
        
        Args:
            width: Map width
            height: Map height
            world_state: World generation parameters
        """
        self.width = width
        self.height = height
        self.world_state = world_state
    
    def generate(
        self,
        world: World,
        factions: list[Faction],
        world_type: WorldType
    ) -> None:
        """
        Generate terrain based on world type.
        
        Args:
            world: World instance to populate
            factions: List of factions (for safe zone calculation)
            world_type: Type of world to generate
        """
        if world_type == WorldType.ISLANDS:
            self._generate_islands(world, factions)
        elif world_type == WorldType.MOUNTAIN_MADNESS:
            self._generate_mountain_madness(world, factions)
        elif world_type == WorldType.WASTELAND:
            self._generate_wasteland(world, factions)
        else:  # STANDARD
            self._generate_standard(world, factions)
    
    def _generate_standard(self, world: World, factions: list[Faction]) -> None:
        """Generate standard terrain with water, mountains."""
        # Initialize all terrain as empty
        for x in range(self.width):
            for y in range(self.height):
                world.set_terrain(Coord(x, y), settings.terrain.empty)
        
        self._grow_patch(
            world,
            factions,
            settings.terrain.water,
            int(self.width * self.height * self.world_state.water_coverage)
        )
        self._grow_patch(
            world,
            factions,
            settings.terrain.mountain,
            int(self.width * self.height * self.world_state.mountain_coverage)
        )
    
    def _generate_islands(self, world: World, factions: list[Faction]) -> None:
        """Generate islands world type."""
        # Initialize all as water
        for x in range(self.width):
            for y in range(self.height):
                world.set_terrain(Coord(x, y), settings.terrain.water)
        
        base_coords = [faction.base for faction in factions]
        
        # Carve islands for each base
        for base in base_coords:
            self._carve_island(world, base, radius=3)
        
        # Scatter small sandbars
        for _ in range(len(base_coords) * 3):
            sx = random.randint(0, self.width - 1)
            sy = random.randint(0, self.height - 1)
            self._carve_island(world, Coord(sx, sy), radius=1)
    
    def _generate_mountain_madness(self, world: World, factions: list[Faction]) -> None:
        """Generate mountain madness world type (50% mountains)."""
        # Start with standard generation
        self._generate_standard(world, factions)
        
        # Convert 50% of empty tiles to mountains
        total_cells = self.width * self.height
        target_mountains = int(total_cells * 0.5)
        count = 0
        
        while count < target_mountains:
            cx = random.randint(0, self.width - 1)
            cy = random.randint(0, self.height - 1)
            coord = Coord(cx, cy)
            
            if world.get_terrain(coord) == settings.terrain.empty:
                world.set_terrain(coord, settings.terrain.mountain)
                count += 1
    
    def _generate_wasteland(self, world: World, factions: list[Faction]) -> None:
        """Generate wasteland world type (only empty terrain)."""
        # Initialize all terrain as empty
        for x in range(self.width):
            for y in range(self.height):
                world.set_terrain(Coord(x, y), settings.terrain.empty)
    
    def _grow_patch(
        self,
        world: World,
        factions: list[Faction],
        tile: str,
        target_count: int
    ) -> None:
        """Grow a patch of terrain (water or mountain)."""
        count = 0
        attempts = 0
        max_attempts = target_count * 10 if target_count else 0
        
        while count < target_count and attempts < max_attempts:
            attempts += 1
            cx = random.randint(0, self.width - 1)
            cy = random.randint(0, self.height - 1)
            coord = Coord(cx, cy)
            
            if tile == settings.terrain.water and GenerationHelper.is_safe_zone(coord, factions):
                continue
            
            patch_size = random.randint(5, 20)
            for _ in range(patch_size):
                if tile == settings.terrain.water and GenerationHelper.is_safe_zone(coord, factions):
                    pass
                elif world.get_terrain(coord) == settings.terrain.empty:
                    world.set_terrain(coord, tile)
                    count += 1
                
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                cx = max(0, min(self.width - 1, cx + dx))
                cy = max(0, min(self.height - 1, cy + dy))
                coord = Coord(cx, cy)
                
                if count >= target_count:
                    break
    
    def _carve_island(self, world: World, center: Coord, radius: int = 3) -> None:
        """Carve out an island at center coordinate."""
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                coord = Coord(center.x + dx, center.y + dy)
                if world.in_bounds(coord):
                    if abs(dx) + abs(dy) <= radius:
                        world.set_terrain(coord, settings.terrain.empty)

