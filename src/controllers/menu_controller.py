from __future__ import annotations

import curses
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from src.core.configs.colors import ColorConfig
from src.core.configs.display import DisplayConfig
from src.core.types.enums.world import WorldType
from src.render.menu_renderer import MenuRenderer
from src.core.types.menu_selection import MenuSelection
from src.core.types.enums.modes import (
    FortressMode,
    CameraMode,
    ExperimentalMode
)

class MenuController:
    """Handles interactive menu flow before the game session starts."""

    def __init__(
        self,
        stdscr,
        display: DisplayConfig,
        colors: ColorConfig,
        *,
        renderer: MenuRenderer | None = None,
    ) -> None:
        self.stdscr = stdscr
        self.display = display
        self.renderer = renderer or MenuRenderer(stdscr, display, colors)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def prompt_selection(self) -> MenuSelection | None:
        """Run the multi-step menu and return the resulting configuration."""
        fortress_modes = list(FortressMode)
        fortress_idx = self._select_from_menu(
            fortress_modes,
            labels=[m.value for m in fortress_modes],
            title="SELECT FORTRESS MODE",
        )
        if fortress_idx is None:
            return None

        camera_modes = list(CameraMode)
        camera_idx = self._select_from_menu(
            camera_modes,
            labels=[m.value for m in camera_modes],
            title="SELECT CAMERA MODE",
        )
        if camera_idx is None:
            return None
        selected_camera_mode = camera_modes[camera_idx]

        map_options: list[tuple[str, tuple[int, int]]] = [
            ("10 x 10", (10, 10)),
            ("20 x 20", (20, 20)),
            ("30 x 30", (30, 30)),
            ("40 x 40", (40, 40)),
            ("100 x 100", (100, 100)),
        ]
        if selected_camera_mode == CameraMode.STATIC:
            map_options.append(("160 x 40 (STATIC ONLY)", (160, 40)))
        map_idx = self._select_from_menu(
            map_options,
            labels=[label for label, _ in map_options],
            title="SELECT MAP SIZE",
        )
        if map_idx is None:
            return None
        map_size = map_options[map_idx][1]

        max_players = self._get_max_players_for_map(*map_size)
        all_player_options = [2, 4, 8, 12, 30]
        player_options = [p for p in all_player_options if p <= max_players]
        if not player_options:
            player_options = [2]
        player_idx = self._select_from_menu(
            player_options,
            labels=[f"{n} PLAYERS" for n in player_options],
            title=f"SELECT PLAYER COUNT (MAX: {max_players})",
        )
        if player_idx is None:
            return None

        world_types = list(WorldType)
        world_idx = self._select_from_menu(
            world_types,
            labels=[wt.value for wt in world_types],
            title="SELECT WORLD TYPE",
        )
        if world_idx is None:
            return None

        exp_modes = list(ExperimentalMode)
        exp_indices = self._select_multiple_from_menu(
            exp_modes,
            labels=[m.value for m in exp_modes],
            title="EXPERIMENTAL MODES (SPACE to toggle, ENTER to confirm)",
        )
        if exp_indices is None:
            return None

        experimental_modes = tuple(exp_modes[i] for i in sorted(exp_indices))
        return MenuSelection(
            fortress_mode=fortress_modes[fortress_idx],
            player_count=player_options[player_idx],
            map_size=map_size,
            world_type=world_types[world_idx],
            camera_mode=selected_camera_mode,
            experimental_modes=experimental_modes,
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _select_from_menu(
        self,
        values: Sequence[object],
        *,
        labels: Sequence[str] | None = None,
        title: str,
    ) -> int | None:
        """Generic single-choice selector."""
        if not values:
            return None
        labels = labels or [str(v) for v in values]
        idx = 0

        while True:
            self.renderer.render_menu(idx, labels, title=title)
            key = self._safe_getch()

            if key == curses.KEY_UP:
                idx = (idx - 1) % len(values)
            elif key == curses.KEY_DOWN:
                idx = (idx + 1) % len(values)
            elif key in (10, 13):
                return idx
            elif key in (ord("q"), 27):
                return None

    def _select_multiple_from_menu(
        self,
        values: Sequence[object],
        *,
        labels: Sequence[str] | None = None,
        title: str,
    ) -> list[int] | None:
        """Multiple-choice selector with checkboxes."""
        if not values:
            return []
        labels = labels or [str(v) for v in values]
        idx = 0
        selected: set[int] = set()

        while True:
            decorated = [
                f"[{'X' if i in selected else ' '}] {label}"
                for i, label in enumerate(labels)
            ]
            self.renderer.render_menu(idx, decorated, title=title)
            key = self._safe_getch()

            if key == curses.KEY_UP:
                idx = (idx - 1) % len(values)
            elif key == curses.KEY_DOWN:
                idx = (idx + 1) % len(values)
            elif key == ord(" "):
                if idx in selected:
                    selected.remove(idx)
                else:
                    selected.add(idx)
            elif key in (10, 13):
                return sorted(selected)
            elif key in (ord("q"), 27):
                return None

    def _safe_getch(self) -> int:
        try:
            return int(self.stdscr.getch())
        except Exception:
            return -1

    def _get_max_players_for_map(self, width: int, height: int) -> int:
        """Small helper to keep tight maps manageable."""
        if (width, height) == (10, 10):
            return 4
        if (width, height) == (20, 20):
            return 8
        if (width, height) == (30, 30):
            return 12
        return 30
