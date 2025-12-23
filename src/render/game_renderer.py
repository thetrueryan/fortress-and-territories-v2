"""
Game renderer responsible for orchestrating the rendering of the battlefield and UI panels.
"""
from dataclasses import dataclass
from typing import Optional, Sequence

from src.core.configs.display import DisplayConfig
from src.core.configs.colors import ColorConfig
from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.states.gameplay import GameplayState
from src.core.types.coord import Coord
from src.render.faction_renderer import FactionRenderer
from src.render.terrain_renderer import TerrainRenderer
from src.render.ui_panel_renderer import UIPanelRenderer
from src.services.visibility_service import VisibilityService
from src.utils.renderer.renderer_helper import PaletteHandles, RendererHelper


@dataclass(slots=True)
class GameRenderParams:
    """Snapshot of data required to render the main gameplay view."""

    factions: Sequence[Faction]
    world: World
    current_turn_idx: int
    moves_left: int
    move_budget: int
    camera_x: int
    camera_y: int
    view_width: int
    view_height: int
    gameplay_state: GameplayState
    game_over_msg: Optional[str] = None
    observer_mode: bool = False
    events: Optional[Sequence[str]] = None
    portal_links: Optional[dict[Coord, Coord]] = None


class GameRenderer:
    """Orchestrates rendering of the main gameplay screen using curses."""

    def __init__(self, stdscr, display: DisplayConfig, colors: ColorConfig) -> None:
        self.stdscr = stdscr
        self.display = display
        palette = RendererHelper.init_palette(colors)

        self._terrain_renderer = TerrainRenderer(stdscr, display, palette)
        self._faction_renderer = FactionRenderer(stdscr, display)
        self._ui_panel_renderer = UIPanelRenderer(stdscr, display)

    def render(self, params: GameRenderParams) -> None:
        """Render the complete game screen."""
        stdscr = self.stdscr
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if not RendererHelper.has_required_space(
            height,
            width,
            self.display.offset_x,
            self.display.offset_y,
            params.view_width,
            params.view_height,
        ):
            RendererHelper.render_size_warning(
                stdscr,
                height,
                width,
                self.display.offset_x,
                self.display.offset_y,
                params.view_width,
                params.view_height,
            )
            stdscr.refresh()
            return

        visible_cells = self._compute_visible_cells(params)

        self._ui_panel_renderer.draw_info_text(
            params.factions,
            params.current_turn_idx,
            params.moves_left,
            params.move_budget,
            params.game_over_msg,
            params.observer_mode,
        )
        self._ui_panel_renderer.draw_borders(
            params.view_width, params.view_height, height, width
        )

        self._terrain_renderer.draw_background(
            params.world,
            params.camera_x,
            params.camera_y,
            params.view_width,
            params.view_height,
            height,
            width,
            visible_cells,
            params.game_over_msg,
        )

        self._faction_renderer.draw_factions(
            list(params.factions),
            params.world,
            params.camera_x,
            params.camera_y,
            params.view_width,
            params.view_height,
            height,
            width,
            params.portal_links,
            visible_cells,
            params.game_over_msg,
            params.observer_mode,
        )

        self._ui_panel_renderer.draw_leaderboard(
            params.factions, params.view_width, height, width
        )
        self._ui_panel_renderer.draw_events_panel(
            params.events, params.view_width, height, width
        )

        stdscr.refresh()

    def _compute_visible_cells(self, params: GameRenderParams) -> Optional[set[Coord]]:
        """Compute visible cells for fog of war."""
        if params.observer_mode:
            return None

        human = next((f for f in params.factions if not f.is_ai and f.alive), None)
        if not human:
            return None

        visibility = VisibilityService(params.gameplay_state)
        return visibility.get_visible_cells(human, params.world)
