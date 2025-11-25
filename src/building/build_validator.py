"""
Build validator that applies multiple game mode rules simultaneously.
"""
from typing import Optional, Set

from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.states.gamemode import GameModeFlags
from src.core.states.gameplay import GameplayState
from src.core.types.build_result import BuildResult
from src.core.types.coord import Coord
from src.core.types.enums.terrain import TerrainType
from src.core.types.tile_context import TileContext
from src.utils.build.cost import CostCalculator
from src.utils.build.ownership import OwnerInfo, OwnerResolver
from src.utils.build.reachability import ReachabilityChecker


class BuildValidator:
    """Validates build/capture attempts applying multiple game mode rules."""

    def __init__(self, gameplay_state: GameplayState) -> None:
        self.gameplay_state = gameplay_state

    def validate(
        self,
        target_cell: Coord,
        my_faction: Faction,
        all_factions: list[Faction],
        world: World,
        flags: GameModeFlags,
        converted_mountains: Optional[Set[Coord]] = None,
    ) -> BuildResult:
        converted = converted_mountains or set()
        tile = self._build_tile_context(target_cell, world)

        if self._is_impassable(tile):
            return BuildResult(False)

        my_cells = my_faction.all_buildings | {my_faction.base}
        if self._is_own_cell(target_cell, my_cells):
            return BuildResult(False)

        owner_info = OwnerResolver.resolve(
            coord=target_cell,
            my_faction=my_faction,
            factions=all_factions,
            world=world,
        )

        if not self._can_capture(owner_info, flags):
            return BuildResult(False, owner=owner_info.owner, is_fortress=True)

        if not self._has_reachable_source(
            target_cell=target_cell,
            faction=my_faction,
            my_cells=my_cells,
            world=world,
            flags=flags,
        ):
            return BuildResult(
                False, owner=owner_info.owner, is_fortress=owner_info.is_fortress
            )

        base_cost = CostCalculator.compute_base_cost(
            tile=tile,
            owner=owner_info.owner,
            is_fortress=owner_info.is_fortress,
            gameplay_state=self.gameplay_state,
        )
        final_cost = self._adjust_cost(
            base_cost=base_cost,
            coord=target_cell,
            tile=tile,
            converted_mountains=converted,
            flags=flags,
        )
        return BuildResult(True, final_cost, owner_info.owner, owner_info.is_fortress)

    # ------------------------------------------------------------------ #
    # Mode-specific validation logic
    # ------------------------------------------------------------------ #
    def _can_capture(self, owner_info: OwnerInfo, flags: GameModeFlags) -> bool:
        """Check if capture is allowed based on game mode flags."""
        if flags.classic:
            owner = owner_info.owner
            if owner_info.is_fortress and owner is not None and owner.alive:
                return False
        return True

    def _has_reachable_source(
        self,
        target_cell: Coord,
        faction: Faction,
        my_cells: set[Coord],
        world: World,
        flags: GameModeFlags,
    ) -> bool:
        """Check reachability based on game mode flags."""
        if flags.supply:
            return ReachabilityChecker.has_reachable_source_supply(
                target_cell=target_cell,
                faction=faction,
                my_cells=my_cells,
                world=world,
            )
        return ReachabilityChecker.has_reachable_source_default(
            target_cell=target_cell,
            faction=faction,
            my_cells=my_cells,
            world=world,
        )

    def _adjust_cost(
        self,
        base_cost: int,
        coord: Coord,
        tile: TileContext,
        converted_mountains: Set[Coord],
        flags: GameModeFlags,
    ) -> int:
        """Adjust cost based on game mode flags."""
        cost = base_cost
        if (
            flags.mountain_efficiency
            and tile.is_mountain
            and coord in converted_mountains
        ):
            cost = min(cost, 1)
        return cost

    # ------------------------------------------------------------------ #
    # Basic helpers
    # ------------------------------------------------------------------ #
    def _is_impassable(self, tile: TileContext) -> bool:
        return tile.base_cost >= 999 and not tile.is_water

    def _is_own_cell(self, target_cell: Coord, my_cells: set[Coord]) -> bool:
        return target_cell in my_cells

    def _build_tile_context(self, coord: Coord, world: World) -> TileContext:
        terrain_type = world.get_terrain_type(coord)
        return TileContext(
            terrain_type=terrain_type,
            base_cost=world.get_move_cost(coord),
            is_water=world.is_water(coord),
            is_bridge=world.is_bridge(coord),
            is_tower=world.is_tower(coord) or world.has_neutral_tower(coord),
            is_portal=terrain_type == TerrainType.PORTAL,
            is_mountain=terrain_type == TerrainType.MOUNTAIN,
        )
