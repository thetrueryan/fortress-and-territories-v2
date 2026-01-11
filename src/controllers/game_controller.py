from __future__ import annotations

import curses
import time
from dataclasses import dataclass
from typing import Optional

from src.ai.ai_controller import AIController
from src.building.build_validator import BuildValidator
from src.controllers.camera_controller import CameraController
from src.controllers.input_handler import InputHandler, PlayerActionType
from src.controllers.menu_controller import (
    CameraMode,
    ExperimentalMode,
    FortressMode,
    MenuController,
    MenuSelection,
)
from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.main_config import settings
from src.core.states.gamemode import GameModeFlags
from src.core.states.gameplay import GameplayState
from src.core.states.world import WorldState
from src.core.types.coord import Coord
from src.generation.world_generator import WorldGenerator
from src.render.game_renderer import GameRenderParams, GameRenderer
from src.services.event_log import EventLog
from src.services.move_executor import MoveContext, MoveExecutor
from src.services.turn_manager import TurnManager
from src.utils.renderer.renderer_helper import RendererHelper


@dataclass(slots=True)
class GameSessionState:
    """Derived configuration/state once menu selection is confirmed."""

    selection: MenuSelection
    flags: GameModeFlags
    observer_mode: bool
    dynamic_camera: bool


class GameController:
    """High-level coordinator that owns the curses loop and game services."""

    def __init__(
        self,
        stdscr,
        *,
        gameplay_state: GameplayState | None = None,
        world_state: WorldState | None = None,
    ) -> None:
        self.stdscr = stdscr
        self.settings = settings
        self.display = settings.display
        self.colors = settings.colors
        self.gameplay_state = gameplay_state or GameplayState()
        self.world_state = world_state or WorldState()

        self._init_curses()

        self.menu_controller = MenuController(stdscr, self.display, self.colors)
        self.camera = CameraController()
        self.input_handler = InputHandler(self.display, self.camera)
        self.game_renderer = GameRenderer(stdscr, self.display, self.colors)
        self.turn_manager = TurnManager(self.gameplay_state)
        self.event_log = EventLog()
        self.ai_controller = AIController(
            gameplay_state=self.gameplay_state,
            move_budget=self.turn_manager.move_budget,
        )
        self.build_validator = BuildValidator(self.gameplay_state)
        self.move_executor = MoveExecutor()

        self.session: GameSessionState | None = None
        self.world: World | None = None
        self.factions: list[Faction] = []
        self.player_faction_idx: int = -1
        self.experimental_modes: tuple[ExperimentalMode, ...] = tuple()

        self.game_over = False
        self.game_over_message: Optional[str] = None
        self.quit_requested = False
        self.current_round = 0

        self.ai_move_delay = 0.5
        self.converted_mountains: set[Coord] = set()
        self.captured_towers: set[Coord] = set()
        self.fortress_ages: dict[Coord, int] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        """Entry point from main. Shows menu and starts the game loop."""
        selection = self.menu_controller.prompt_selection()
        if selection is None:
            return
        self._bootstrap_session(selection)
        self._game_loop()

    # ------------------------------------------------------------------ #
    # Session setup
    # ------------------------------------------------------------------ #
    def _bootstrap_session(self, selection: MenuSelection) -> None:
        flags = self._build_game_mode_flags(selection)
        session = GameSessionState(
            selection=selection,
            flags=flags,
            observer_mode=ExperimentalMode.OBSERVER in selection.experimental_modes,
            dynamic_camera=selection.camera_mode == CameraMode.DYNAMIC,
        )
        self.session = session
        self.experimental_modes = tuple(selection.experimental_modes)
        self.gameplay_state = self._build_gameplay_state(selection)
        self.turn_manager = TurnManager(self.gameplay_state)
        self.ai_controller = AIController(
            gameplay_state=self.gameplay_state,
            move_budget=self.turn_manager.move_budget,
        )
        self.build_validator = BuildValidator(self.gameplay_state)
        self._create_world_and_factions(selection)
        self._focus_on_player_base()

    def _build_game_mode_flags(self, selection: MenuSelection) -> GameModeFlags:
        has_supply = ExperimentalMode.SUPPLY in selection.experimental_modes
        has_efficiency = (
            ExperimentalMode.MOUNTAIN_EFFICIENCY in selection.experimental_modes
        )
        return GameModeFlags(
            classic=selection.fortress_mode == FortressMode.CLASSIC,
            supply=has_supply,
            mountain_efficiency=has_efficiency,
        )

    def _build_gameplay_state(self, selection: MenuSelection) -> GameplayState:
        state = GameplayState()
        if ExperimentalMode.ANTHILL in selection.experimental_modes:
            state.fog_radius = 1
            state.tower_vision_radius = 3
        return state

    def _create_world_and_factions(self, selection: MenuSelection) -> None:
        width, height = selection.map_size
        world = World(
            width=width,
            height=height,
            world_type=selection.world_type,
            portal_pairs=self._calculate_portal_pairs(width, height),
        )
        generator = WorldGenerator(width, height, self.world_state)
        factions = generator.init_factions(
            selection.player_count, observer_mode=self._observer_mode
        )
        generator.generate(world, factions, selection.world_type)

        session = self.session
        if session is None:
            raise RuntimeError("Game session must be initialized before creating world.")

        self.world = world
        self.factions = factions
        self.turn_manager.reset()
        self.event_log = EventLog()
        self.converted_mountains.clear()
        self.captured_towers.clear()
        self.fortress_ages.clear()
        self.current_round = 0
        self.game_over = False
        self.game_over_message = None
        self.quit_requested = False
        self.player_faction_idx = next(
            (idx for idx, faction in enumerate(factions) if not faction.is_ai), -1
        )

        self.camera.configure(
            world_width=width,
            world_height=height,
            dynamic=session.dynamic_camera,
        )

    # ------------------------------------------------------------------ #
    # Main loop
    # ------------------------------------------------------------------ #
    def _game_loop(self) -> None:
        if not self.world or not self.factions or not self.session:
            return

        self._render_state()
        while not self.quit_requested:
            self._update_game_state()
            if self.game_over:
                self._render_state()

            key = self._safe_getch()
            if key in (ord("q"), 27):
                break

            if self._handle_camera_input(key):
                self._render_state()
                continue

            if self.game_over:
                time.sleep(0.1)
                continue

            current_index = self.turn_manager.current_index
            current_faction = self.factions[current_index]
            if not current_faction.alive:
                self._advance_turn()
                continue

            needs_refresh = False
            if current_faction.is_ai or self._observer_mode:
                self._render_state()
                self._run_ai_turn(current_index)
                needs_refresh = True
            else:
                needs_refresh = self._handle_player_turn(key, current_faction)

            if needs_refresh:
                self._render_state()

            time.sleep(self.display.animation_delay)

    def _run_ai_turn(self, faction_idx: int) -> None:
        if not self.world or not self.session:
            return

        self.ai_controller.take_turn(
            faction_idx,
            self.factions,
            self.world,
            self.session.flags,
            converted_mountains=self.converted_mountains,
            captured_towers=self.captured_towers,
            event_log=self.event_log,
            current_round=self.current_round,
            fortress_ages=self.fortress_ages,
            render_callback=self._on_ai_move,
        )
        if not self.quit_requested:
            self._advance_turn()

    def _on_ai_move(self, moves_left: int) -> None:
        if self.quit_requested:
            return
        self._render_state(moves_override=moves_left)
        time.sleep(self.ai_move_delay)

    # ------------------------------------------------------------------ #
    # State helpers
    # ------------------------------------------------------------------ #
    def _update_game_state(self) -> None:
        if not self.session:
            return
        if not self._observer_mode and self.player_faction_idx >= 0:
            player = self.factions[self.player_faction_idx]
            if not player.alive:
                self.game_over = True
                self.game_over_message = "DEFEAT! You were eliminated."

        alive = [f for f in self.factions if f.alive]
        if len(alive) == 1 and not self.game_over:
            winner = alive[0]
            self.game_over = True
            if self._observer_mode:
                self.game_over_message = f"{winner.name} wins!"
            elif (
                self.player_faction_idx >= 0
                and winner is self.factions[self.player_faction_idx]
            ):
                self.game_over_message = "VICTORY! All enemies defeated."
            else:
                self.game_over_message = f"DEFEAT! {winner.name} prevailed."
            msg = f"{winner.name.upper()} WINS!"
            if msg not in self.event_log.latest():
                self.event_log.add(msg)

    def _advance_turn(self) -> None:
        if not self.session or not self.factions:
            return
        previous_index = self.turn_manager.current_index
        self.turn_manager.advance(len(self.factions))
        if self.turn_manager.current_index == 0 and previous_index != 0:
            self.current_round += 1
            if self.session.flags.classic:
                self._age_fortresses_classic()

    def _age_fortresses_classic(self) -> None:
        if not self.session or not self.world or not self.session.flags.classic:
            return

        terrain = self.world
        for faction in self.factions:
            if not faction.alive:
                continue

            expired: list[Coord] = []
            for coord in list(faction.fortresses):
                if coord == faction.base:
                    continue

                tile = terrain.get_terrain(coord)
                if tile in (
                    self.settings.terrain.bridge,
                    self.settings.terrain.tower,
                    self.settings.terrain.portal,
                ):
                    continue
                if terrain.has_neutral_tower(coord):
                    continue

                placed_at = self.fortress_ages.get(coord)
                if placed_at is None:
                    continue
                if self.current_round - placed_at > 5:
                    expired.append(coord)

            for coord in expired:
                faction.remove_fortress(coord)
                faction.add_territory(coord)
                self.fortress_ages.pop(coord, None)

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def _render_state(self, moves_override: int | None = None) -> None:
        if not self.world or not self.session:
            return
        moves_left = (
            self.turn_manager.moves_left
            if moves_override is None
            else moves_override
        )
        params = GameRenderParams(
            factions=self.factions,
            world=self.world,
            current_turn_idx=self.turn_manager.current_index,
            moves_left=moves_left,
            move_budget=self.turn_manager.move_budget,
            camera_x=self.camera.camera_x,
            camera_y=self.camera.camera_y,
            view_width=self.camera.view_width,
            view_height=self.camera.view_height,
            gameplay_state=self.gameplay_state,
            game_over_msg=self.game_over_message,
            observer_mode=self._observer_mode,
            events=self.event_log.latest(),
            portal_links=self.world.portal_links,
        )
        self.game_renderer.render(params)

    # ------------------------------------------------------------------ #
    # Input helpers
    # ------------------------------------------------------------------ #
    def _handle_camera_input(self, key: int) -> bool:
        if not self.session or not self.camera.is_dynamic:
            return False
        if key == curses.KEY_LEFT:
            return self.camera.move(-1, 0)
        if key == curses.KEY_RIGHT:
            return self.camera.move(1, 0)
        if key == curses.KEY_UP:
            return self.camera.move(0, -1)
        if key == curses.KEY_DOWN:
            return self.camera.move(0, 1)
        return False

    def _focus_on_player_base(self) -> None:
        if (
            not self.session
            or not self.camera.is_dynamic
            or self.player_faction_idx < 0
            or not self.factions
        ):
            return
        base = self.factions[self.player_faction_idx].base
        self.camera.focus_on(base)

    # ------------------------------------------------------------------ #
    # Misc helpers
    # ------------------------------------------------------------------ #
    def _calculate_portal_pairs(self, width: int, height: int) -> int:
        area = width * height
        if area < 1600:
            return 0
        return area // 1600

    def _safe_getch(self) -> int:
        try:
            return int(self.stdscr.getch())
        except Exception:
            return -1

    def _init_curses(self) -> None:
        curses.curs_set(0)
        #self.stdscr.refresh()
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        except Exception:
            pass
        if curses.has_colors():
            RendererHelper.init_palette(self.colors)

    @property
    def _observer_mode(self) -> bool:
        return bool(self.session and self.session.observer_mode)

    # ------------------------------------------------------------------ #
    # Player interaction
    # ------------------------------------------------------------------ #
    def _handle_player_turn(self, key: int, faction: Faction) -> bool:
        if not self.world or not self.session:
            return False

        action = self.input_handler.interpret(key, self.world)
        if action is None:
            return False

        if action.kind is PlayerActionType.SKIP:
            return self._skip_action()

        if action.kind is PlayerActionType.BUILD and action.coord is not None:
            return self._attempt_build(faction, action.coord)

        return False

    def _attempt_build(self, faction: Faction, coord: Coord) -> bool:
        if not self.world or not self.session:
            return False

        result = self.build_validator.validate(
            target_cell=coord,
            my_faction=faction,
            all_factions=self.factions,
            world=self.world,
            flags=self.session.flags,
            converted_mountains=self.converted_mountains,
        )
        if not result.allowed:
            return False

        cost = max(1, result.cost)
        if self.turn_manager.moves_left < cost:
            return False

        context = MoveContext(
            my_faction=faction,
            factions=self.factions,
            world=self.world,
            flags=self.session.flags,
            converted_mountains=self.converted_mountains,
            captured_towers=self.captured_towers,
            event_log=self.event_log,
            current_round=self.current_round,
            fortress_ages=self.fortress_ages,
        )
        self.move_executor.apply(cell=coord, result=result, context=context)

        self.turn_manager.consume(cost)
        if self.turn_manager.needs_advance():
            self._advance_turn()
        return True

    def _skip_action(self) -> bool:
        if self.turn_manager.moves_left <= 0:
            return False
        self.turn_manager.consume(1)
        if self.turn_manager.needs_advance():
            self._advance_turn()
        return True
