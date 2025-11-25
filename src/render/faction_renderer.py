"""
Faction renderer responsible for drawing faction entities (bases, fortresses, territory, etc.).
"""
import curses
from typing import Optional

from src.core.configs.display import DisplayConfig
from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.main_config import settings
from src.core.types.coord import Coord
from src.core.types.enums.terrain import TerrainType
from src.utils.renderer.renderer_helper import RendererHelper


class FactionRenderer:
    """Renders faction entities on the game map."""

    def __init__(self, stdscr, display: DisplayConfig) -> None:
        self.stdscr = stdscr
        self.display = display

    def draw_factions(
        self,
        factions: list[Faction],
        world: World,
        camera_x: int,
        camera_y: int,
        view_width: int,
        view_height: int,
        height: int,
        width: int,
        portal_links: Optional[dict[Coord, Coord]],
    ) -> None:
        """Draw all faction entities (bases, fortresses, territory, towers, portals)."""
        for faction in factions:
            attr = curses.A_BOLD if faction.alive else curses.A_DIM
            color_pair = faction.color_pair if curses.has_colors() else 0

            self._draw_entity(
                faction.base,
                camera_x,
                camera_y,
                view_width,
                view_height,
                height,
                width,
                settings.display.base_char,
                attr,
                color_pair,
            )

            for cell in faction.fortresses:
                char = settings.display.fortress_char
                terrain_type = world.get_terrain_type(cell)
                if terrain_type == TerrainType.TOWER:
                    char = settings.terrain.tower
                elif terrain_type == TerrainType.PORTAL:
                    char = settings.terrain.portal
                elif terrain_type == TerrainType.BRIDGE:
                    char = settings.terrain.bridge
                self._draw_entity(
                    cell,
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

            for cell in faction.territory:
                self._draw_entity(
                    cell,
                    camera_x,
                    camera_y,
                    view_width,
                    view_height,
                    height,
                    width,
                    settings.display.territory_char,
                    attr,
                    color_pair,
                )

            for cell in faction.towers:
                self._draw_entity(
                    cell,
                    camera_x,
                    camera_y,
                    view_width,
                    view_height,
                    height,
                    width,
                    settings.terrain.tower,
                    attr | curses.A_REVERSE,
                    color_pair,
                )

            if portal_links:
                for portal, linked in portal_links.items():
                    if portal in faction.portals:
                        self._draw_entity(
                            portal,
                            camera_x,
                            camera_y,
                            view_width,
                            view_height,
                            height,
                            width,
                            settings.terrain.portal,
                            attr | curses.A_REVERSE,
                            color_pair,
                        )
                        self._draw_entity(
                            linked,
                            camera_x,
                            camera_y,
                            view_width,
                            view_height,
                            height,
                            width,
                            settings.terrain.portal,
                            attr | curses.A_REVERSE,
                            color_pair,
                        )

    def _draw_entity(
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
        """Draw a single entity at the given world coordinate."""
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
