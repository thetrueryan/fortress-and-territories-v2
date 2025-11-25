"""
UI panel renderer responsible for drawing information panels (leaderboard, events, borders, info text).
"""
import curses
from typing import Optional, Sequence

from src.core.configs.display import DisplayConfig
from src.core.entities.faction import Faction
from src.utils.renderer.renderer_helper import RendererHelper


class UIPanelRenderer:
    """Renders UI panels (leaderboard, events, borders, info text)."""

    def __init__(self, stdscr, display: DisplayConfig) -> None:
        self.stdscr = stdscr
        self.display = display

    def draw_info_text(
        self,
        factions: Sequence[Faction],
        current_turn_idx: int,
        moves_left: int,
        move_budget: int,
        game_over_msg: Optional[str],
        observer_mode: bool,
    ) -> None:
        """Draw the top info bar."""
        info_text = self._build_info_text(
            factions,
            current_turn_idx,
            moves_left,
            move_budget,
            game_over_msg,
            observer_mode,
        )
        RendererHelper.safe_addstr(self.stdscr, 0, 0, info_text, curses.A_BOLD)

    def draw_leaderboard(
        self,
        factions: Sequence[Faction],
        view_width: int,
        height: int,
        width: int,
    ) -> None:
        """Draw the leaderboard panel."""
        start_x = self.display.offset_x + view_width + 4
        start_y = self.display.offset_y

        if start_x + 20 >= width:
            return

        RendererHelper.safe_addstr(
            self.stdscr,
            start_y,
            start_x,
            "LEADERBOARD",
            curses.A_BOLD | curses.A_UNDERLINE,
        )

        scored = [
            (faction, len(faction.territory) + len(faction.fortresses))
            for faction in factions
        ]
        scored.sort(key=lambda item: item[1], reverse=True)

        for idx, (faction, score) in enumerate(scored):
            row_y = start_y + 2 + idx
            if row_y >= height:
                break

            name = faction.name + (" (DEAD)" if not faction.alive else "")
            attr = curses.A_BOLD if faction.alive else curses.A_DIM
            color_pair = faction.color_pair if curses.has_colors() else 0
            RendererHelper.safe_addstr(
                self.stdscr,
                row_y,
                start_x,
                f"{score:3} {name}",
                attr | curses.color_pair(color_pair) if color_pair else attr,
            )

    def draw_events_panel(
        self,
        events: Optional[Sequence[str]],
        view_width: int,
        height: int,
        width: int,
    ) -> None:
        """Draw the events panel."""
        if not events:
            return

        leaderboard_width = 20
        spacing = 4
        start_x = self.display.offset_x + view_width + leaderboard_width + spacing
        start_y = self.display.offset_y

        if start_x + 30 >= width or start_y >= height:
            return

        RendererHelper.safe_addstr(
            self.stdscr, start_y, start_x, "EVENTS", curses.A_BOLD | curses.A_UNDERLINE
        )

        max_events = min(10, height - start_y - 2)
        to_show = events[-max_events:] if len(events) > max_events else events

        for idx, event in enumerate(to_show):
            row_y = start_y + 2 + idx
            if row_y >= height - 1:
                break

            attr = curses.A_NORMAL
            if "DEFEATED" in event or "DEAD" in event:
                attr = curses.A_DIM
            elif "VICTORY" in event or "WINS" in event:
                attr = curses.A_BOLD
            elif "TOWER" in event:
                attr = curses.A_BOLD | curses.A_UNDERLINE

            RendererHelper.safe_addstr(self.stdscr, row_y, start_x, event[:28], attr)

    def draw_borders(
        self, view_width: int, view_height: int, height: int, width: int
    ) -> None:
        """Draw borders around the game viewport."""
        start_y = self.display.offset_y - 1
        end_y = self.display.offset_y + view_height
        start_x = self.display.offset_x - 1
        end_x = self.display.offset_x + view_width

        if end_y >= height or end_x >= width:
            return

        border_attr = curses.color_pair(2) if curses.has_colors() else curses.A_NORMAL
        for x in range(start_x + 1, end_x):
            RendererHelper.safe_addch(self.stdscr, start_y, x, "=", border_attr, 0)
            RendererHelper.safe_addch(self.stdscr, end_y, x, "=", border_attr, 0)
        for y in range(start_y + 1, end_y):
            RendererHelper.safe_addch(self.stdscr, y, start_x, "|", border_attr, 0)
            RendererHelper.safe_addch(self.stdscr, y, end_x, "|", border_attr, 0)
        RendererHelper.safe_addch(self.stdscr, start_y, start_x, "+", border_attr, 0)
        RendererHelper.safe_addch(self.stdscr, start_y, end_x, "+", border_attr, 0)
        RendererHelper.safe_addch(self.stdscr, end_y, start_x, "+", border_attr, 0)
        RendererHelper.safe_addch(self.stdscr, end_y, end_x, "+", border_attr, 0)

    def _build_info_text(
        self,
        factions: Sequence[Faction],
        current_turn_idx: int,
        moves_left: int,
        move_budget: int,
        game_over_msg: Optional[str],
        observer_mode: bool,
    ) -> str:
        """Build the info text string."""
        current = factions[current_turn_idx]
        turn_name = current.name
        if not current.alive:
            turn_name += " (DEAD)"

        if game_over_msg:
            return f" {game_over_msg} | [q] Quit "

        if observer_mode:
            return (
                f" OBSERVER MODE | Turn: {turn_name} | "
                f"Moves: {moves_left}/{move_budget} | "
                "[q] Quit | [Arrows] Move Camera"
            )

        return (
            f" Turn: {turn_name} | Moves: {moves_left}/{move_budget} "
            "| [LMB] Capture | T=Tower Vision | ~=Water"
        )
