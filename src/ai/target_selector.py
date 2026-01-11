"""
Target selection helpers used by AIController.
"""

import random
from dataclasses import dataclass
from typing import Optional, Sequence

from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.types.coord import Coord
from src.core.types.enums.terrain import TerrainType
from src.utils.ai.ai_helper import AIHelper


@dataclass
class TargetSelector:
    """
    Encapsulates heuristics responsible for picking AI targets.
    """

    helper: AIHelper

    def select_target(
        self,
        me: Faction,
        factions: Sequence[Faction],
        visible_cells: Optional[set[Coord]],
    ) -> Optional[Coord]:
        """
        Pick a strategic target using defensive/attack heuristics.
        """
        threat_pos: Optional[Coord] = None
        min_threat_score = float("inf")
        defense_radius = 12

        my_power = len(me.territory) + len(me.fortresses)

        for faction in factions:
            if faction is me or not faction.alive:
                continue

            enemy_power = len(faction.territory) + len(faction.fortresses)
            power_ratio = enemy_power / max(my_power, 1)

            enemy_cells = (
                set(faction.territory) | set(faction.fortresses) | {faction.base.coord}
            )
            for cell in enemy_cells:
                if visible_cells is not None and cell not in visible_cells:
                    continue
                dist = self.helper.distance(cell, me.base.coord)
                if dist < defense_radius:
                    threat_score = dist * (1.0 + power_ratio * 0.5)
                    if threat_score < min_threat_score:
                        min_threat_score = threat_score
                        threat_pos = cell

        if threat_pos:
            return threat_pos

        best_target: Optional[Coord] = None
        best_score = float("inf")

        for faction in factions:
            if faction is me or not faction.alive:
                continue

            if visible_cells is not None and faction.base.coord not in visible_cells:
                continue

            enemy_power = len(faction.territory) + len(faction.fortresses)
            dist = self.helper.distance(me.base.coord, faction.base.coord)

            score = dist * (1.0 + enemy_power * 0.1)
            if enemy_power < max(my_power * 0.5, 1):
                score *= 0.7

            if score < best_score:
                best_score = score
                best_target = faction.base.coord

        return best_target

    def select_roaming_target(self, me: Faction, world: World) -> Coord:
        """
        Pick a roaming/exploration target near existing territory.
        """
        my_cells = list(set(me.territory) | set(me.fortresses) | {me.base.coord})
        if not my_cells:
            return me.base.coord

        anchor = random.choice(my_cells)
        neighbors = anchor.neighbors()
        random.shuffle(neighbors)

        for neighbor in neighbors:
            if world.in_bounds(neighbor):
                return neighbor

        return anchor

    def find_priority_target(
        self,
        me: Faction,
        world: World,
        visible_cells: Optional[set[Coord]],
    ) -> Optional[Coord]:
        """
        Locate immediate priority targets (neutral towers / portals).
        """
        if not visible_cells:
            return None

        my_cells = set(me.territory) | set(me.fortresses) | {me.base.coord}
        best_target: Optional[Coord] = None
        min_dist = float("inf")

        for tower in world.get_tower_coords():
            if tower not in visible_cells:
                continue
            if any(self.helper.distance(tower, cell) == 1 for cell in my_cells):
                dist = self.helper.distance(tower, me.base.coord)
                if dist < min_dist:
                    min_dist = dist
                    best_target = tower

        for portal in world.portal_links.keys():
            if portal not in visible_cells:
                continue
            if world.get_terrain_type(portal) != TerrainType.PORTAL:
                continue
            if any(self.helper.distance(portal, cell) == 1 for cell in my_cells):
                dist = self.helper.distance(portal, me.base.coord)
                if dist < min_dist:
                    min_dist = dist
                    best_target = portal

        return best_target

    def needs_base_defense(
        self,
        me: Faction,
        factions: Sequence[Faction],
        visible_cells: Optional[set[Coord]],
    ) -> bool:
        """
        Decide if we should switch into defensive mode (enemies near base).
        """
        if not visible_cells:
            return False

        my_base = me.base.coord
        defense_radius = 8
        enemy_count = 0

        for faction in factions:
            if faction is me or not faction.alive:
                continue

            enemy_cells = (
                set(faction.territory) | set(faction.fortresses) | {faction.base.coord}
            )
            for cell in enemy_cells:
                if cell not in visible_cells:
                    continue
                dist = self.helper.distance(cell, my_base)
                if dist < defense_radius:
                    enemy_count += 1
                    if dist <= 5:
                        return True

        return enemy_count >= 3
