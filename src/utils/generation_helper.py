"""
Generation helper utilities.
"""

from core.entities.faction_entity.faction import Faction
from core.types.coord import Coord


class GenerationHelper:
    """
    Static helper methods for world generation.
    
    Contains utility functions used across different generators.
    """
    
    @staticmethod
    def is_safe_zone(coord: Coord, factions: list[Faction], radius: int = 3) -> bool:
        """
        Check if coordinate is in safe zone (near any faction base).
        
        Args:
            coord: Coordinate to check
            factions: List of factions
            radius: Safe zone radius (default: 3)
        
        Returns:
            True if coordinate is within safe zone of any faction base
        """
        return any(
            coord.manhattan_distance(faction.base) <= radius
            for faction in factions
        )
    
    @staticmethod
    def calculate_tower_count(total_cells: int) -> int:
        """
        Calculate number of towers to generate (1 per 400 cells, minimum 1).
        
        Args:
            total_cells: Total number of cells on the map
        
        Returns:
            Number of towers to generate
        """
        return max(1, total_cells // 400)
    
    @staticmethod
    def calculate_portal_pairs(total_cells: int) -> int:
        """
        Calculate number of portal pairs to generate (1 pair per 1600 cells).
        
        Args:
            total_cells: Total number of cells on the map
        
        Returns:
            Number of portal pairs to generate
        """
        return max(1, total_cells // 1600)

