"""
Candidate evaluation helpers for AIController.
"""

import random
from dataclasses import dataclass
from typing import Optional, Sequence

from src.building.build_validator import BuildValidator
from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.states.gamemode import GameModeFlags
from src.core.types.coord import Coord
from src.core.types.build_result import BuildResult
from src.core.types.enums.terrain import TerrainType
from src.utils.ai.ai_helper import AIHelper
from src.core.types.candidate import Candidate


@dataclass
class TargetChecker:
    """Encapsulates logic for collecting and ranking capture candidates."""

    helper: AIHelper
    build_validator: BuildValidator

    def collect_candidates(
        self,
        my_faction: Faction,
        factions: Sequence[Faction],
        world: World,
        flags: GameModeFlags,
        moves_left: int,
        converted_mountains: Optional[set[Coord]] = None,
        visible_cells: Optional[set[Coord]] = None,
    ) -> list[Candidate]:
        """Collect candidate cells ready for capture/build actions."""
        converted = converted_mountains or set()

        my_cells = set(my_faction.all_buildings) | {my_faction.base}
        possible_spots: set[Coord] = set()

        for cell in my_cells:
            for neighbor in cell.neighbors():
                if world.in_bounds(neighbor):
                    possible_spots.add(neighbor)

        candidates: list[Candidate] = []
        for coord in possible_spots:
            if coord in my_cells:
                continue

            result = self.build_validator.validate(
                target_cell=coord,
                my_faction=my_faction,
                all_factions=list(factions),
                world=world,
                flags=flags,
                converted_mountains=converted,
            )
            if not result.allowed or result.cost > moves_left:
                continue

            if (
                result.owner
                and visible_cells is not None
                and coord not in visible_cells
            ):
                continue

            candidates.append(Candidate(coord, result))

        return candidates

    def choose_candidate(
        self,
        *,
        candidates: list[Candidate],
        target: Optional[Coord],
        my_faction: Faction,
        factions: Sequence[Faction],
        world: World,
        visible_cells: Optional[set[Coord]],
        roaming: bool,
    ) -> Optional[Candidate]:
        """Select the best candidate relative to the current strategic target."""
        if not candidates:
            return None

        shuffled = candidates[:]
        random.shuffle(shuffled)

        best_candidate: Optional[Candidate] = None
        min_score = float("inf")

        for candidate in shuffled:
            coord = candidate.coord
            result = candidate.result
            score = 0.0

            if target is not None:
                score += self.helper.distance(coord, target)

            score += result.cost * 2.0
            score += random.uniform(0, 1.5)

            if roaming:
                score += random.uniform(-1.5, 1.5)

            strategic_value = self._evaluate_strategic_value(
                coord=coord,
                result=result,
                my_faction=my_faction,
                factions=factions,
                world=world,
                visible_cells=visible_cells,
            )
            score -= strategic_value * 0.3

            if score < min_score:
                min_score = score
                best_candidate = candidate

        return best_candidate

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _evaluate_strategic_value(
        self,
        coord: Coord,
        result: BuildResult,
        my_faction: Faction,
        factions: Sequence[Faction],
        world: World,
        visible_cells: Optional[set[Coord]],
    ) -> float:
        value = 0.0
        owner = result.owner

        if owner and owner.alive:
            if coord == owner.base:
                value += 30.0
            elif result.is_fortress:
                value += 8.0
            else:
                value += 12.0

            enemy_power = len(owner.territory) + len(owner.fortresses)
            my_power = len(my_faction.territory) + len(my_faction.fortresses)
            if enemy_power < max(my_power * 0.7, 1):
                value += 5.0

        terrain_type = world.get_terrain_type(coord)

        if world.has_neutral_tower(coord):
            value += 18.0
        elif coord in my_faction.towers:
            value += 15.0

        if terrain_type == TerrainType.PORTAL:
            value += 20.0

        if self._is_blocking_enemy(coord, my_faction, factions, visible_cells):
            value += 10.0

        if self._is_defending_important(coord, my_faction, world):
            value += 8.0

        return value

    def _is_blocking_enemy(
        self,
        cell: Coord,
        me: Faction,
        factions: Sequence[Faction],
        visible_cells: Optional[set[Coord]],
    ) -> bool:
        if not visible_cells:
            return False

        my_base = me.base
        for faction in factions:
            if faction is me or not faction.alive:
                continue

            enemy_base = faction.base
            dx = my_base.x - enemy_base.x
            dy = my_base.y - enemy_base.y
            if dx == 0 and dy == 0:
                continue

            cell_dx = cell.x - enemy_base.x
            cell_dy = cell.y - enemy_base.y

            cross = abs(cell_dx * dy - cell_dy * dx)
            dot = cell_dx * dx + cell_dy * dy
            if cross < 3 and 0 <= dot <= dx * dx + dy * dy:
                return True

        return False

    def _is_defending_important(
        self,
        cell: Coord,
        me: Faction,
        world: World,
    ) -> bool:
        important_points = {me.base}
        important_points.update(me.fortresses)
        important_points.update(me.towers)

        for coord in me.fortresses:
            if world.get_terrain_type(coord) == TerrainType.PORTAL:
                important_points.add(coord)

        for important in important_points:
            if self.helper.distance(cell, important) <= 1:
                return True

        return False
