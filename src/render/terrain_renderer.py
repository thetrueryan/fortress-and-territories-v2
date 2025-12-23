"""
Terrain renderer responsible for drawing the background terrain layer.
"""
import curses
from typing import Optional

from src.core.configs.display import DisplayConfig
from src.core.entities.world import World
from src.core.main_config import settings
from src.core.types.coord import Coord
from src.core.types.enums.terrain import TerrainType
from src.utils.renderer.renderer_helper import PaletteHandles, RendererHelper


class TerrainRenderer:
    """Renders the background terrain layer with fog of war support."""

    def __init__(
        self,
        stdscr,
        display: DisplayConfig,
        palette: PaletteHandles,
    ) -> None:
        self.stdscr = stdscr
        self.display = display
        self._palette = palette

    def draw_background(
        self,
        world: World,
        camera_x: int,
        camera_y: int,
        view_width: int,
        view_height: int,
        height: int,
        width: int,
        visible_cells: Optional[set[Coord]],
        game_over_msg: Optional[str],
    ) -> None:
        """Draw the terrain background layer."""
        max_x = min(world.width, camera_x + view_width)
        max_y = min(world.height, camera_y + view_height)

        for wy in range(camera_y, max_y):
            for wx in range(camera_x, max_x):
                coord = Coord(wx, wy)
                terrain_type = world.get_terrain_type(coord)
                char, attr, color_pair = self._terrain_style(
                    terrain_type,
                    coord,
                    visible_cells,
                    game_over_msg,
                )
                self._draw_char(
                    coord,
                    camera_x,
                    camera_y,
                    view_width,
                    view_height,
                    height,
                    width,
                    char,
                    attr,
                    color_pair,
                )

    def _terrain_style(
        self,
        terrain_type: TerrainType,
        coord: Coord,
        visible_cells: Optional[set[Coord]],
        game_over_msg: Optional[str],
    ) -> tuple[str, int, int]:
        """Determine character, attribute, and color pair for a terrain cell."""
        terrain = settings.terrain
        if (
            visible_cells is not None
            and not game_over_msg
            and coord not in visible_cells
        ):
            return terrain.fog, curses.A_DIM, self._palette.fog_pair_id

        if terrain_type == TerrainType.WATER:
            return terrain.water, curses.A_BOLD, self._palette.water_pair_id
        if terrain_type == TerrainType.MOUNTAIN:
            mountain_pair = 2 if curses.has_colors() else 0
            return terrain.mountain, curses.A_BOLD, mountain_pair
        if terrain_type == TerrainType.TOWER:
            return terrain.tower, curses.A_BOLD | curses.A_UNDERLINE, 0
        if terrain_type == TerrainType.PORTAL:
            return terrain.portal, curses.A_BOLD | curses.A_UNDERLINE, 0
        if terrain_type == TerrainType.BRIDGE:
            return terrain.bridge, curses.A_BOLD, 0
        return terrain.empty, curses.A_NORMAL, 0

    def _draw_char(
        self,
        coord: Coord,
        camera_x: int,
        camera_y: int,
        view_width: int,
        view_height: int,
        height: int,
        width: int,
        char: str,
        attr: int,
        color_pair: int,
    ) -> None:
        """Draw a single character at the given world coordinate."""
        wx, wy = coord.x, coord.y
        if not (camera_x <= wx < camera_x + view_width):
            return
        if not (camera_y <= wy < camera_y + view_height):
            return

        sx = wx - camera_x + self.display.offset_x
        sy = wy - camera_y + self.display.offset_y
        if sx >= width or sy >= height:
            return

        RendererHelper.safe_addch(self.stdscr, sy, sx, char, attr, color_pair)
