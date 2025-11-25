"""
Cost calculation utilities for build validation.
"""

from typing import Optional

from src.core.entities.faction import Faction
from src.core.states.gameplay import GameplayState
from src.core.types.tile_context import TileContext


class CostCalculator:
    """Static utility class for computing build/capture costs."""

    @staticmethod
    def compute_base_cost(
        tile: TileContext,
        owner: Optional[Faction],
        is_fortress: bool,
        gameplay_state: GameplayState,
    ) -> int:
        """
        Compute the default action cost for capturing/building on a tile.

        Args:
            tile: Tile context snapshot.
            owner: Current tile owner (if any).
            is_fortress: Whether the tile is treated as fortress.
            gameplay_state: Gameplay constants (bridge costs, etc.).
        """
        if tile.is_water and not owner:
            return gameplay_state.bridge_build_cost

        if tile.is_bridge and owner:
            return gameplay_state.bridge_capture_cost

        if tile.is_tower or tile.is_portal:
            return 1

        if is_fortress:
            return gameplay_state.fortress_capture_cost

        return tile.base_cost
