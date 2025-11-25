"""
Reachability helpers for build validation.
"""

from collections import deque

from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.types.coord import Coord


class ReachabilityChecker:
    """Static utility class for checking source reachability."""

    @staticmethod
    def has_reachable_source_default(
        target_cell: Coord,
        faction: Faction,
        my_cells: set[Coord],
        world: World,
    ) -> bool:
        return ReachabilityChecker._has_reachable_source(
            target_cell=target_cell,
            faction=faction,
            my_cells=my_cells,
            world=world,
            supply_mode=False,
        )

    @staticmethod
    def has_reachable_source_supply(
        target_cell: Coord,
        faction: Faction,
        my_cells: set[Coord],
        world: World,
    ) -> bool:
        return ReachabilityChecker._has_reachable_source(
            target_cell=target_cell,
            faction=faction,
            my_cells=my_cells,
            world=world,
            supply_mode=True,
        )

    @staticmethod
    def _has_reachable_source(
        target_cell: Coord,
        faction: Faction,
        my_cells: set[Coord],
        world: World,
        supply_mode: bool,
    ) -> bool:
        for neighbor in target_cell.neighbors():
            if neighbor in my_cells and ReachabilityChecker._is_source_active(
                neighbor, faction, world, supply_mode
            ):
                return True
        return False

    @staticmethod
    def _is_source_active(
        cell: Coord,
        faction: Faction,
        world: World,
        supply_mode: bool,
    ) -> bool:
        if cell == faction.base:
            return True

        if supply_mode:
            if cell in world.portal_links:
                linked = world.portal_links[cell]
                if linked in faction.fortresses or linked in faction.territory:
                    if ReachabilityChecker._check_supply_connection(
                        linked, faction, world
                    ):
                        return True
            return ReachabilityChecker._check_supply_connection(cell, faction, world)

        if cell in faction.territory:
            return True

        if cell in faction.fortresses:
            if cell in world.portal_links:
                return True
            return ReachabilityChecker._check_fortress_connection(cell, faction)

        if cell in faction.towers or cell in faction.bridges or cell in faction.portals:
            return True

        return False

    @staticmethod
    def _check_fortress_connection(start: Coord, faction: Faction) -> bool:
        visited: set[Coord] = {start}
        queue: deque[Coord] = deque([start])

        while queue:
            current = queue.popleft()
            for neighbor in current.neighbors():
                if neighbor == faction.base or neighbor in faction.territory:
                    return True
                if neighbor in faction.fortresses and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False

    @staticmethod
    def _check_supply_connection(cell: Coord, faction: Faction, world: World) -> bool:
        if cell == faction.base:
            return True

        if cell not in faction.territory and cell not in faction.fortresses:
            return False

        visited: set[Coord] = {faction.base}
        queue: deque[Coord] = deque([faction.base])

        while queue:
            current = queue.popleft()
            for neighbor in current.neighbors():
                if neighbor == cell:
                    return True

                if neighbor in faction.territory or neighbor in faction.fortresses:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        if neighbor in world.portal_links:
                            linked = world.portal_links[neighbor]
                            if (
                                linked in faction.territory
                                or linked in faction.fortresses
                            ) and linked not in visited:
                                visited.add(linked)
                                queue.append(linked)

        return False
