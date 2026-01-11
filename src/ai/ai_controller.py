"""
High-level AI controller orchestrating automated turns.
"""
from typing import Callable, Optional, Sequence, Set

from src.ai.target_checker import TargetChecker
from src.ai.target_selector import TargetSelector
from src.building.build_validator import BuildValidator
from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.states.gamemode import GameModeFlags
from src.core.states.gameplay import GameplayState
from src.core.types.coord import Coord
from src.services.event_log import EventLog
from src.services.move_executor import MoveContext, MoveExecutor
from src.services.visibility_service import VisibilityService
from src.utils.ai.ai_helper import AIHelper


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
        self._move_executor = MoveExecutor()

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
        render_callback: Optional[Callable[[int], None]] = None,
    ) -> None:
        """
        Execute a single AI turn for the faction at `faction_idx`.

        The current stage wires together high-level flow; detailed heuristics
        and state mutations will be migrated in subsequent steps.
        """
        my_faction = factions[faction_idx]
        if not my_faction.alive:
            return

        ctx = MoveContext(
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

            self._move_executor.apply(
                cell=choice.coord,
                result=choice.result,
                context=ctx,
            )

            moves_left -= max(1, choice.result.cost)
            if render_callback:
                render_callback(max(moves_left, 0))

    # ------------------------------------------------------------------ #
    # Internal coordination helpers
    # ------------------------------------------------------------------ #
    def _determine_strategy(
        self,
        context: MoveContext,
        visible_cells: set[Coord],
    ) -> tuple[Optional[Coord], bool]:
        """Decide which coordinate should be prioritised this turn."""
        roaming = False

        if self._target_selector.needs_base_defense(
            context.my_faction, context.factions, visible_cells
        ):
            return context.my_faction.base.coord, False

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

