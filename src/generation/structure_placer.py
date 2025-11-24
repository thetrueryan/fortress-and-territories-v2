"""
Structure placer module.
"""

import random

from src.core.entities.world_entity.world import World
from src.core.entities.faction_entity.faction import Faction
from src.core.entities.coord_based.tower import Tower
from src.core.entities.coord_based.portal import Portal
from src.core.main_config import settings
from src.core.types.coord import Coord
from src.core.types.enums.building import BuildingType
from src.core.types.enums.world import WorldType
from src.utils.generation_helper import GenerationHelper


class StructurePlacer:
    """
    Places structures (towers, portals) on the map.
    
    Handles placement logic for neutral structures.
    """
    
    def __init__(self, width: int, height: int) -> None:
        """
        Initialize structure placer.
        
        Args:
            width: Map width
            height: Map height
        """
        self.width = width
        self.height = height
    
    def place_towers(
        self,
        world: World,
        factions: list[Faction],
        world_type: WorldType
    ) -> None:
        """
        Place towers on the map.
        
        Args:
            world: World instance to populate
            factions: List of factions (for safe zone calculation)
            world_type: World type (affects placement rules)
        """
        total_cells = self.width * self.height
        tower_count = GenerationHelper.calculate_tower_count(total_cells)
        
        attempts = 0
        max_attempts = total_cells * 2
        
        while len(world.get_tower_coords()) < tower_count and attempts < max_attempts:
            attempts += 1
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            coord = Coord(tx, ty)
            
            # Check if valid placement location
            if world.get_terrain(coord) != settings.terrain.empty:
                continue
            
            # For standard/wasteland, avoid safe zones
            if world_type in (WorldType.STANDARD, WorldType.WASTELAND):
                if GenerationHelper.is_safe_zone(coord, factions):
                    continue
            
            # Place tower
            world.set_terrain(coord, settings.terrain.tower)
            tower = Tower(
                coord=coord,
                faction_id=None,
                building_type=BuildingType.TOWER,
                vision_radius=15
            )
            world.add_tower(tower)
    
    def place_portals(
        self,
        world: World,
        factions: list[Faction],
        portal_pairs: int
    ) -> None:
        """
        Place portals on the map in pairs.
        
        Args:
            world: World instance to populate
            factions: List of factions (for safe zone calculation)
            portal_pairs: Number of portal pairs to generate
        """
        if portal_pairs == 0:
            return
        
        total_portals = portal_pairs * 2
        portals: list[Coord] = []
        attempts = 0
        max_attempts = self.width * self.height * 2
        
        # Generate portal coordinates
        while len(portals) < total_portals and attempts < max_attempts:
            attempts += 1
            px = random.randint(0, self.width - 1)
            py = random.randint(0, self.height - 1)
            coord = Coord(px, py)
            
            if (world.get_terrain(coord) == settings.terrain.empty 
                and not GenerationHelper.is_safe_zone(coord, factions)
                and coord not in portals):
                world.set_terrain(coord, settings.terrain.portal)
                portals.append(coord)
        
        # Link portals in pairs
        random.shuffle(portals)
        for i in range(0, len(portals) - 1, 2):
            portal1_coord = portals[i]
            portal2_coord = portals[i + 1]
            
            # Create portal entities
            portal1 = Portal(
                coord=portal1_coord,
                faction_id=None,
                building_type=BuildingType.PORTAL,
                linked_portal_coord=portal2_coord
            )
            portal2 = Portal(
                coord=portal2_coord,
                faction_id=None,
                building_type=BuildingType.PORTAL,
                linked_portal_coord=portal1_coord
            )
            
            world.add_portal(portal1)
            world.add_portal(portal2)
            
            # Store links
            world.portal_links[portal1_coord] = portal2_coord
            world.portal_links[portal2_coord] = portal1_coord

