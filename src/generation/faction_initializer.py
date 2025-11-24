"""
Faction initializer module.
"""

import random

from src.core.entities.faction_entity.faction import Faction
from src.core.main_config import settings
from src.core.states.world import WorldState
from src.core.types.coord import Coord


class FactionInitializer:
    """
    Initializes factions with bases.
    
    Handles faction creation and base placement.
    """
    
    def __init__(
        self,
        width: int,
        height: int,
        world_state: WorldState
    ) -> None:
        """
        Initialize faction initializer.
        
        Args:
            width: Map width
            height: Map height
            world_state: World generation parameters
        """
        self.width = width
        self.height = height
        self.world_state = world_state
    
    def init_factions(
        self,
        player_count: int,
        observer_mode: bool = False
    ) -> list[Faction]:
        """
        Initialize factions with bases.
        
        Args:
            player_count: Number of factions to create
            observer_mode: If True, all factions are AI bots
        
        Returns:
            List of initialized Faction objects
        """
        coords = self._generate_base_coords(player_count)
        factions = []
        
        for i, pos in enumerate(coords):
            faction = self._create_faction(i, pos, observer_mode)
            factions.append(faction)
        
        return factions
    
    def _generate_base_coords(self, player_count: int) -> list[Coord]:
        """Generate base coordinates with minimum distance between them."""
        coords: list[Coord] = []
        required_distance = self.world_state.min_base_distance
        attempts = 0
        max_attempts = self.width * self.height * 10
        
        while len(coords) < player_count:
            if attempts >= max_attempts:
                attempts = 0
                required_distance = max(1, required_distance - 1)
            attempts += 1
            
            candidate = Coord(
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )
            
            if all(candidate.manhattan_distance(existing) >= required_distance for existing in coords):
                coords.append(candidate)
            
            if required_distance == 1 and attempts >= max_attempts:
                break
        
        if len(coords) < player_count:
            raise ValueError("Unable to place all factions with required spacing. Try a larger map.")
        
        random.shuffle(coords)
        return coords
    
    def _create_faction(
        self,
        index: int,
        base_coord: Coord,
        observer_mode: bool
    ) -> Faction:
        """
        Create a single faction.
        
        Args:
            index: Faction index
            base_coord: Base coordinate
            observer_mode: If True, all factions are AI bots
        
        Returns:
            Created Faction object
        """
        is_human = False if observer_mode else (index == 0)
        
        if is_human:
            name = "PLAYER"
            color_idx = 1
        else:
            name = f"BOT {index + 1}" if observer_mode else f"BOT {index}"
            color_idx = ((index + 1) % len(settings.colors.color_map)) + 1 if observer_mode else (index % len(settings.colors.color_map)) + 1
        
        return Faction(
            name=name,
            color_pair=color_idx,
            base=base_coord,
            is_ai=not is_human,
            alive=True,
        )

