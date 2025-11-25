"""
Shared helpers for curses-based renderers.
"""
import curses
from dataclasses import dataclass

from src.core.configs.colors import ColorConfig


@dataclass(slots=True)
class PaletteHandles:
    """Holds IDs for special color pairs used by renderers."""

    fog_pair_id: int = 0
    water_pair_id: int = 0


class RendererHelper:
    """Static utility class for common rendering operations."""

    @staticmethod
    def init_palette(color_config: ColorConfig) -> PaletteHandles:
        """
        Initialize curses color pairs based on the provided color config.

        Returns:
            PaletteHandles: IDs for special color pairs (fog/water).
        """
        handles = PaletteHandles()

        if not curses.has_colors():
            return handles

        curses.start_color()
        curses.use_default_colors()

        for idx, color in enumerate(color_config.color_map, start=1):
            try:
                curses.init_pair(idx, color, -1)
            except curses.error:
                pass

        last_pair = len(color_config.color_map)
        handles.fog_pair_id = last_pair + 1
        handles.water_pair_id = last_pair + 2

        curses.init_pair(handles.fog_pair_id, curses.COLOR_BLACK, -1)
        curses.init_pair(handles.water_pair_id, curses.COLOR_CYAN, -1)

        return handles

    @staticmethod
    def safe_addstr(
        stdscr, y: int, x: int, text: str, attr: int = curses.A_NORMAL
    ) -> None:
        """Wrapper around addstr that ignores curses errors."""
        try:
            stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass

    @staticmethod
    def safe_addch(
        stdscr, y: int, x: int, ch: str, attr: int, color_pair: int = 0
    ) -> None:
        """Wrapper around addch that ignores curses errors."""
        try:
            if curses.has_colors() and color_pair > 0:
                stdscr.addch(y, x, ch, curses.color_pair(color_pair) | attr)
            else:
                stdscr.addch(y, x, ch, attr)
        except curses.error:
            pass

    @staticmethod
    def has_required_space(
        height: int,
        width: int,
        offset_x: int,
        offset_y: int,
        view_width: int,
        view_height: int,
    ) -> bool:
        """Check if the terminal window is large enough for the viewport."""
        min_height = offset_y + view_height + 2
        min_width = offset_x + view_width + 2
        return height >= min_height and width >= min_width

    @staticmethod
    def render_size_warning(
        stdscr,
        height: int,
        width: int,
        offset_x: int,
        offset_y: int,
        view_width: int,
        view_height: int,
    ) -> None:
        """Render a size warning message."""
        needed_w = offset_x + view_width + 2
        needed_h = offset_y + view_height + 2
        warning = f"Terminal too small! Need {needed_w}x{needed_h}"
        RendererHelper.safe_addstr(
            stdscr,
            0,
            0,
            warning,
            curses.A_REVERSE if not curses.has_colors() else curses.color_pair(1),
        )
