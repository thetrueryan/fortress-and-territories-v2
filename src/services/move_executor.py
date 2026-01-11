from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence, Set

from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.states.gamemode import GameModeFlags
from src.core.types.build_result import BuildResult
from src.core.types.coord import Coord
from src.core.types.enums.terrain import TerrainType
from src.services.event_log import EventLog


@dataclass
class MoveContext:
    """Mutable context required to apply captures/builds."""

    my_faction: Faction
    factions: Sequence[Faction]
    world: World
    flags: GameModeFlags
    converted_mountains: Set[Coord] = field(default_factory=set)
    captured_towers: Set[Coord] = field(default_factory=set)
    event_log: EventLog = field(default_factory=EventLog)
    current_round: int = 0
    fortress_ages: Optional[dict[Coord, int]] = None


class MoveExecutor:
    """Updates world/faction state according to BuildResult semantics."""

    def apply(self, *, cell: Coord, result: BuildResult, context: MoveContext) -> None:
        world = context.world
        my_faction = context.my_faction
        owner = result.owner

        terrain_type = world.get_terrain_type(cell)
        is_water = terrain_type == TerrainType.WATER
        is_bridge = terrain_type == TerrainType.BRIDGE
        is_portal = terrain_type == TerrainType.PORTAL
        is_mountain = terrain_type == TerrainType.MOUNTAIN
        is_tower_tile = terrain_type == TerrainType.TOWER
        has_neutral_tower = world.has_neutral_tower(cell)
        is_tower = is_tower_tile or has_neutral_tower

        if owner and owner.alive:
            self._handle_capture_from_owner(
                cell=cell,
                owner=owner,
                result=result,
                context=context,
                is_portal=is_portal,
                is_tower=is_tower,
                is_bridge=is_bridge,
            )
        else:
            self._cleanup_dead_factions(cell, context)
            if is_water:
                world.build_bridge(cell)
                my_faction.add_bridge(cell)
                self._add_fortress(my_faction, cell, context, track_age=True)
            elif is_tower:
                self._capture_tower(cell, context)
            elif is_portal:
                self._capture_portal(cell, context)
            elif result.is_fortress or is_bridge:
                if is_bridge:
                    my_faction.add_bridge(cell)
                self._add_fortress(my_faction, cell, context, track_age=True)
            else:
                my_faction.add_territory(cell)

        if is_mountain and context.flags.mountain_efficiency:
            context.converted_mountains.add(cell)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _handle_capture_from_owner(
        self,
        *,
        cell: Coord,
        owner: Faction,
        result: BuildResult,
        context: MoveContext,
        is_portal: bool,
        is_tower: bool,
        is_bridge: bool,
    ) -> None:
        my_faction = context.my_faction

        if cell == owner.base.coord:
            owner.alive = False
            self._add_fortress(my_faction, cell, context, track_age=False)
            context.event_log.add(f"{owner.name} DEFEATED!")
            return

        self._remove_from_faction_structures(owner, cell, context)

        if is_portal:
            self._capture_portal(cell, context)
            return

        if is_tower:
            self._capture_tower(cell, context)
            return

        if is_bridge:
            my_faction.add_bridge(cell)

        self._add_fortress(my_faction, cell, context, track_age=True)

    def _capture_tower(self, cell: Coord, context: MoveContext) -> None:
        my_faction = context.my_faction
        world = context.world

        world.remove_tower(cell)
        my_faction.add_tower(cell)
        self._add_fortress(my_faction, cell, context, track_age=True)

        if cell not in context.captured_towers:
            context.captured_towers.add(cell)
            context.event_log.add(f"{my_faction.name.upper()} CAPTURED TOWER!")

    def _capture_portal(self, cell: Coord, context: MoveContext) -> None:
        my_faction = context.my_faction
        world = context.world

        for faction in context.factions:
            if faction is not my_faction:
                self._remove_from_faction_structures(faction, cell, context)

        my_faction.add_portal(cell)
        self._add_fortress(my_faction, cell, context, track_age=True)

        portal = world.get_portal(cell)
        if portal:
            portal.faction_id = my_faction.name

        linked = world.portal_links.get(cell)
        if linked:
            for faction in context.factions:
                if faction is not my_faction:
                    self._remove_from_faction_structures(faction, linked, context)

            my_faction.add_portal(linked)
            self._add_fortress(my_faction, linked, context, track_age=True)

            linked_portal = world.get_portal(linked)
            if linked_portal:
                linked_portal.faction_id = my_faction.name

    def _cleanup_dead_factions(self, cell: Coord, context: MoveContext) -> None:
        for faction in context.factions:
            if not faction.alive:
                self._remove_from_faction_structures(faction, cell, context)

    def _remove_from_faction_structures(
        self,
        faction: Faction,
        coord: Coord,
        context: MoveContext,
    ) -> None:
        if coord in faction.territory:
            faction.remove_territory(coord)
        if coord in faction.fortresses:
            faction.remove_fortress(coord)
        if coord in faction.towers:
            faction.remove_tower(coord)
        if coord in faction.bridges:
            faction.remove_bridge(coord)
        if coord in faction.portals:
            faction.remove_portal(coord)
        if context.fortress_ages and coord in context.fortress_ages:
            del context.fortress_ages[coord]

    def _add_fortress(
        self,
        faction: Faction,
        coord: Coord,
        context: MoveContext,
        *,
        track_age: bool,
    ) -> None:
        faction.add_fortress(coord)
        if track_age:
            self._record_fortress_age(coord, context)

    def _record_fortress_age(self, coord: Coord, context: MoveContext) -> None:
        if not context.flags.classic:
            return
        if context.fortress_ages is None:
            return
        context.fortress_ages[coord] = context.current_round

