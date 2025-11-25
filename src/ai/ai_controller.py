"""
High-level AI controller orchestrating automated turns.
"""

from dataclasses import dataclass, field
from typing import Optional, Sequence, Set

from src.ai.target_checker import TargetChecker
from src.ai.target_selector import TargetSelector
from src.building.build_validator import BuildValidator
from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.states.gamemode import GameModeFlags
from src.core.states.gameplay import GameplayState
from src.core.types.build_result import BuildResult
from src.core.types.coord import Coord
from src.core.types.enums.terrain import TerrainType
from src.services.event_log import EventLog
from src.services.visibility_service import VisibilityService
from src.utils.ai.ai_helper import AIHelper


@dataclass
class AITurnContext:
    """Mutable turn-scoped context shared across helper components."""

    my_faction: Faction
    factions: Sequence[Faction]
    world: World
    flags: GameModeFlags
    converted_mountains: Set[Coord] = field(default_factory=set)
    captured_towers: Set[Coord] = field(default_factory=set)
    event_log: EventLog = field(default_factory=EventLog)
    current_round: int = 0
    fortress_ages: Optional[dict[Coord, int]] = None


class AIController:
    """
    Coordinates AI decision making across helper modules.

    Stage 1: establishes structure and dependencies; detailed logic is migrated
    in subsequent stages following AI_CONTROLLER_MIGRATION_PLAN.md.
    """

    def __init__(self, gameplay_state: GameplayState, move_budget: int = 5) -> None:
        self.move_budget = move_budget
        self._helper = AIHelper()
        self._visibility = VisibilityService(gameplay_state)
        self._build_validator = BuildValidator(gameplay_state)
        self._target_selector = TargetSelector(self._helper)
        self._target_checker = TargetChecker(self._helper, self._build_validator)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def take_turn(
        self,
        faction_idx: int,
        factions: list[Faction],
        world: World,
        flags: GameModeFlags,
        *,
        converted_mountains: Optional[Set[Coord]] = None,
        captured_towers: Optional[Set[Coord]] = None,
        event_log: Optional[EventLog] = None,
        current_round: int = 0,
        fortress_ages: Optional[dict[Coord, int]] = None,
    ) -> None:
        """
        Execute a single AI turn for the faction at `faction_idx`.

        The current stage wires together high-level flow; detailed heuristics
        and state mutations will be migrated in subsequent steps.
        """
        my_faction = factions[faction_idx]
        if not my_faction.alive:
            return

        ctx = AITurnContext(
            my_faction=my_faction,
            factions=factions,
            world=world,
            flags=flags,
            converted_mountains=converted_mountains
            if converted_mountains is not None
            else set(),
            captured_towers=captured_towers if captured_towers is not None else set(),
            event_log=event_log or EventLog(),
            current_round=current_round,
            fortress_ages=fortress_ages,
        )

        visible_cells = self._visibility.get_visible_cells(my_faction, world)
        target, roaming = self._determine_strategy(ctx, visible_cells)

        moves_left = self.move_budget
        while moves_left > 0:
            candidates = self._target_checker.collect_candidates(
                my_faction=my_faction,
                factions=factions,
                world=world,
                flags=flags,
                moves_left=moves_left,
                converted_mountains=ctx.converted_mountains,
                visible_cells=visible_cells,
            )

            if not candidates:
                break

            choice = self._target_checker.choose_candidate(
                candidates=candidates,
                target=target,
                my_faction=my_faction,
                factions=factions,
                world=world,
                visible_cells=visible_cells,
                roaming=roaming,
            )
            if choice is None:
                break

            self._apply_move(
                cell=choice.coord,
                result=choice.result,
                context=ctx,
            )

            moves_left -= max(1, choice.result.cost)

    # ------------------------------------------------------------------ #
    # Internal coordination helpers
    # ------------------------------------------------------------------ #
    def _determine_strategy(
        self,
        context: AITurnContext,
        visible_cells: set[Coord],
    ) -> tuple[Optional[Coord], bool]:
        """Decide which coordinate should be prioritised this turn."""
        roaming = False

        if self._target_selector.needs_base_defense(
            context.my_faction, context.factions, visible_cells
        ):
            return context.my_faction.base, False

        target = self._target_selector.select_target(
            context.my_faction, context.factions, visible_cells
        )
        if target is None:
            target = self._target_selector.select_roaming_target(
                context.my_faction, context.world
            )
            roaming = True

        priority = self._target_selector.find_priority_target(
            context.my_faction, context.world, visible_cells
        )
        if priority is not None:
            return priority, False

        return target, roaming

    def _apply_move(
        self,
        *,
        cell: Coord,
        result: BuildResult,
        context: AITurnContext,
    ) -> None:
        """
        Apply the chosen move to the game state.

        Mirrors the legacy _apply_move behaviour using the new domain objects.
        """
        my_faction = context.my_faction
        world = context.world
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
    # State mutation helpers
    # ------------------------------------------------------------------ #
    def _handle_capture_from_owner(
        self,
        *,
        cell: Coord,
        owner: Faction,
        result: BuildResult,
        context: AITurnContext,
        is_portal: bool,
        is_tower: bool,
        is_bridge: bool,
    ) -> None:
        my_faction = context.my_faction

        if cell == owner.base:
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

    def _capture_tower(self, cell: Coord, context: AITurnContext) -> None:
        my_faction = context.my_faction
        world = context.world

        world.remove_tower(cell)
        my_faction.add_tower(cell)
        self._add_fortress(my_faction, cell, context, track_age=True)

        if cell not in context.captured_towers:
            context.captured_towers.add(cell)
            context.event_log.add(f"{my_faction.name.upper()} CAPTURED TOWER!")

    def _capture_portal(self, cell: Coord, context: AITurnContext) -> None:
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

    def _cleanup_dead_factions(self, cell: Coord, context: AITurnContext) -> None:
        for faction in context.factions:
            if not faction.alive:
                self._remove_from_faction_structures(faction, cell, context)

    def _remove_from_faction_structures(
        self,
        faction: Faction,
        coord: Coord,
        context: AITurnContext,
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
        context: AITurnContext,
        *,
        track_age: bool,
    ) -> None:
        faction.add_fortress(coord)
        if track_age:
            self._record_fortress_age(coord, context)

    def _record_fortress_age(self, coord: Coord, context: AITurnContext) -> None:
        if not context.flags.classic:
            return
        if context.fortress_ages is None:
            return
        context.fortress_ages[coord] = context.current_round
