"""
Visibility service.

Encapsulates fog-of-war calculations for determining visible cells.
"""

from typing import Optional

from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.states.gameplay import GameplayState
from src.core.types.coord import Coord


class VisibilityService:
    """
    Service for computing visible cells (fog of war).

    Calculates which cells are visible to a faction based on:
    - Base and territory (normal vision radius)
    - Captured towers (extended vision radius)
    """

    def __init__(self, gameplay_state: GameplayState) -> None:
        """
        Initialize visibility service.

        Args:
            gameplay_state: Gameplay state containing vision radius parameters
        """
        self.gameplay_state = gameplay_state

    def get_visible_cells(
        self,
        faction: Faction,
        world: World,
    ) -> set[Coord]:
        """
        Get all cells visible to the faction.

        Args:
            faction: Faction to calculate visibility for
            world: World instance for terrain and tower lookup

        Returns:
            Set of visible coordinates
        """
        visible: set[Coord] = set()

        normal_sources: set[Coord] = set()
        tower_sources: set[Coord] = set()

        # Base and territory provide normal vision
        normal_sources.add(faction.base.coord)
        normal_sources.update(faction.territory)

        # Check fortresses - towers provide extended vision
        for fort_coord in faction.fortresses:
            if world.has_neutral_tower(fort_coord) or fort_coord in faction.towers:
                tower_sources.add(fort_coord)
            else:
                normal_sources.add(fort_coord)

        # Also check captured towers directly
        for tower_coord in faction.towers:
            tower_sources.add(tower_coord)

        # Paint normal vision
        offsets_normal = self._precompute_offsets(self.gameplay_state.fog_radius)
        for coord in normal_sources:
            self._paint(coord, offsets_normal, visible, world)

        # Paint tower vision
        if tower_sources:
            offsets_tower = self._precompute_offsets(
                self.gameplay_state.tower_vision_radius
            )
            for coord in tower_sources:
                self._paint(coord, offsets_tower, visible, world)

        return visible

    def _precompute_offsets(self, radius: int) -> list[tuple[int, int]]:
        """
        Precompute offset coordinates for circular vision.

        Args:
            radius: Vision radius

        Returns:
            List of (dx, dy) offsets within radius
        """
        return [
            (dx, dy)
            for dx in range(-radius, radius + 1)
            for dy in range(-radius, radius + 1)
            if dx * dx + dy * dy <= radius * radius
        ]

    def _paint(
        self,
        center: Coord,
        offsets: list[tuple[int, int]],
        visible: set[Coord],
        world: World,
    ) -> None:
        """
        Paint visible cells from a center point.

        Args:
            center: Center coordinate
            offsets: Precomputed offsets to apply
            visible: Set to add visible coordinates to
            world: World instance for bounds checking
        """
        for dx, dy in offsets:
            coord = Coord(center.x + dx, center.y + dy)
            if world.in_bounds(coord):
                visible.add(coord)
