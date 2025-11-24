"""
World generator module
=====================

Orchestrates world generation using specialized generators.
"""

from typing import Optional

from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.states.world import WorldState
from src.core.types.enums.world import WorldType
from .faction_initializer import FactionInitializer
from .structure_placer import StructurePlacer
from .terrain_generator import TerrainGenerator


class WorldGenerator:
    """
    World generator orchestrator.

    Coordinates terrain generation, structure placement, and faction initialization.
    """

    def __init__(
        self, width: int, height: int, world_state: Optional[WorldState] = None
    ) -> None:
        """
        Initialize world generator.

        Args:
            width: Map width
            height: Map height
            world_state: World generation parameters (uses defaults if None)
        """
        self.width = width
        self.height = height
        self.world_state = world_state or WorldState()

        # Initialize specialized generators
        self.terrain_generator = TerrainGenerator(width, height, self.world_state)
        self.structure_placer = StructurePlacer(width, height)
        self.faction_initializer = FactionInitializer(width, height, self.world_state)

    def generate(
        self, world: World, factions: list[Faction], world_type: WorldType
    ) -> None:
        """
        Generate world terrain and structures.

        Args:
            world: World instance to populate
            factions: List of factions (for safe zone calculation)
            world_type: Type of world to generate
        """
        world.world_type = world_type

        # Generate terrain
        self.terrain_generator.generate(world, factions, world_type)

        # Place towers
        self.structure_placer.place_towers(world, factions, world_type)

        # Place portals if needed
        if world.portal_pairs > 0:
            self.structure_placer.place_portals(world, factions, world.portal_pairs)

    def init_factions(
        self, player_count: int, observer_mode: bool = False
    ) -> list[Faction]:
        """
        Initialize factions with bases.

        Args:
            player_count: Number of factions to create
            observer_mode: If True, all factions are AI bots

        Returns:
            List of initialized Faction objects
        """
        return self.faction_initializer.init_factions(player_count, observer_mode)
