"""
Menu renderer responsible for drawing the main menu.
"""
import curses
from typing import Sequence

from src.core.configs.display import DisplayConfig
from src.utils.renderer.renderer_helper import RendererHelper


class MenuRenderer:
    """Renders menu screens using curses."""

    def __init__(self, stdscr, display: DisplayConfig) -> None:
        self.stdscr = stdscr
        self.display = display

    def render_menu(
        self, selected_idx: int, options: Sequence[str], *, title: str | None = None
    ) -> None:
        """
        Render the main menu with the highlighted option.
        """
        stdscr = self.stdscr
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        menu_title = title or self.display.title
        subtitle = self.display.subtitle
        start_y = height // 2 - len(options) // 2 - 3
        start_x = max(0, width // 2 - len(menu_title) // 2)

        try:
            RendererHelper.safe_addstr(
                stdscr, start_y, start_x, menu_title, curses.A_BOLD
            )
            RendererHelper.safe_addstr(
                stdscr,
                start_y + 1,
                width // 2 - len(subtitle) // 2,
                subtitle,
                curses.A_DIM,
            )

            for idx, option in enumerate(options):
                x = width // 2 - len(option) // 2
                y = start_y + 3 + idx
                if y >= height - 2:
                    break

                if idx == selected_idx:
                    RendererHelper.safe_addstr(
                        stdscr, y, x, f"> {option} <", curses.A_BOLD
                    )
                else:
                    RendererHelper.safe_addstr(stdscr, y, x, option)

            hint = "Use ↑/↓ to select, Enter to confirm"
            RendererHelper.safe_addstr(
                stdscr,
                start_y + 4 + len(options),
                width // 2 - len(hint) // 2,
                hint,
                curses.A_DIM,
            )
        except curses.error:
            # Ignore drawing errors when window is too small.
            pass

        stdscr.refresh()
