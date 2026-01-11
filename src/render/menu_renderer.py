"""
Menu renderer responsible for drawing the main menu.
"""
import curses
from typing import Sequence

from src.core.configs.colors import ColorConfig
from src.core.configs.display import DisplayConfig
from src.utils.renderer.renderer_helper import RendererHelper


class MenuRenderer:
    """Renders menu screens using curses."""

    def __init__(
        self,
        stdscr,
        display: DisplayConfig,
        colors: ColorConfig,
    ) -> None:
        self.stdscr = stdscr
        self.display = display
        self._init_attrs(colors)

    def _init_attrs(self, colors: ColorConfig) -> None:
        """Precompute color/attribute combinations for menu text."""
        self.title_attr = curses.A_BOLD
        self.subtitle_attr = curses.A_DIM
        self.hint_attr = curses.A_DIM
        self.option_attr = curses.A_NORMAL
        self.highlight_attr = curses.A_BOLD

        if curses.has_colors() and colors.color_map:
            def pair(idx: int) -> int:
                return curses.color_pair(idx if len(colors.color_map) >= idx else 1)

            self.title_attr = pair(2) | curses.A_BOLD
            self.subtitle_attr = pair(3)
            self.hint_attr = pair(3)
            self.option_attr = pair(2)
            self.highlight_attr = pair(1) | curses.A_BOLD

    def render_menu(
        self, selected_idx: int, options: Sequence[str], *, title: str | None = None
    ) -> None:
        """
        Render the main menu with the highlighted option.
        """
        self.stdscr.erase()
        height, width = self.stdscr.getmaxyx()

        menu_title = title or self.display.title
        subtitle = self.display.subtitle
        start_y = height // 2 - len(options) // 2 - 3
        start_x = max(0, width // 2 - len(menu_title) // 2)

        try:
            RendererHelper.safe_addstr(
                self.stdscr, start_y, start_x, menu_title, self.title_attr
            )
            RendererHelper.safe_addstr(
                self.stdscr,
                start_y + 1,
                width // 2 - len(subtitle) // 2,
                subtitle,
                self.subtitle_attr,
            )

            for idx, option in enumerate(options):
                x = width // 2 - len(option) // 2
                y = start_y + 3 + idx
                if y >= height - 2:
                    break

                if idx == selected_idx:
                    RendererHelper.safe_addstr(
                        self.stdscr, y, x, f"> {option} <", self.highlight_attr
                    )
                else:
                    RendererHelper.safe_addstr(self.stdscr, y, x, option, self.option_attr)

            hint = "Use ↑/↓ to select, Enter to confirm"
            RendererHelper.safe_addstr(
                self.stdscr,
                start_y + 4 + len(options),
                width // 2 - len(hint) // 2,
                hint,
                self.hint_attr,
            )
        except curses.error:
            # Ignore drawing errors when window is too small.
            pass
        self.stdscr.refresh()
