from __future__ import annotations

from dataclasses import dataclass

from src.core.types.coord import Coord


@dataclass(slots=True)
class CameraConfig:
    """Immutable configuration for viewport sizing."""

    base_view_width: int = 40
    base_view_height: int = 20
    horizontal_padding: int = 5


class CameraController:
    """
    Encapsulates camera coordinates and viewport sizing.

    Keeps viewport logic independent from GameController so it can be reused
    by other front-ends (observer mode, replays, etc.).
    """

    def __init__(self, config: CameraConfig | None = None) -> None:
        self.config = config or CameraConfig()
        self._dynamic = True
        self._world_width = 0
        self._world_height = 0
        self._camera_x = 0
        self._camera_y = 0
        self._view_width = self.config.base_view_width
        self._view_height = self.config.base_view_height

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def configure(self, *, world_width: int, world_height: int, dynamic: bool) -> None:
        """
        Configure controller for a specific world and camera mode.

        Resets the camera to the origin and recalculates viewport dimensions.
        """
        self._world_width = world_width
        self._world_height = world_height
        self._dynamic = dynamic
        self.reset()

    def reset(self) -> None:
        """Reset camera to origin and recalculate viewport."""
        self._camera_x = 0
        self._camera_y = 0
        self._update_viewport_dimensions()

    def move(self, dx: int, dy: int) -> bool:
        """Move camera by (dx, dy). Returns True if position changed."""
        if not self._dynamic or not self._has_world():
            return False
        max_x = max(0, self._world_width - self._view_width)
        max_y = max(0, self._world_height - self._view_height)
        new_x = min(max(0, self._camera_x + dx), max_x)
        new_y = min(max(0, self._camera_y + dy), max_y)
        if new_x != self._camera_x or new_y != self._camera_y:
            self._camera_x = new_x
            self._camera_y = new_y
            return True
        return False

    def focus_on(self, coord: Coord) -> None:
        """Center camera on coordinate (if dynamic camera is enabled)."""
        if not self._dynamic or not self._has_world():
            return
        max_x = max(0, self._world_width - self._view_width)
        max_y = max(0, self._world_height - self._view_height)
        target_x = max(0, min(coord.x - self._view_width // 2, max_x))
        target_y = max(0, min(coord.y - self._view_height // 2, max_y))
        self._camera_x = target_x
        self._camera_y = target_y

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def camera_x(self) -> int:
        return self._camera_x

    @property
    def camera_y(self) -> int:
        return self._camera_y

    @property
    def view_width(self) -> int:
        return self._view_width

    @property
    def view_height(self) -> int:
        return self._view_height

    @property
    def is_dynamic(self) -> bool:
        return self._dynamic

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _update_viewport_dimensions(self) -> None:
        if not self._has_world():
            return

        if not self._dynamic:
            self._view_width = self._world_width
            self._view_height = self._world_height
            self._camera_x = 0
            self._camera_y = 0
            return

        width = self._world_width
        height = self._world_height
        padding = self.config.horizontal_padding
        if width > padding * 2:
            target_width = width - padding
        else:
            target_width = width

        self._view_width = max(1, min(target_width, self.config.base_view_width))
        self._view_height = max(1, min(height, self.config.base_view_height))

        self._camera_x = min(self._camera_x, max(0, width - self._view_width))
        self._camera_y = min(self._camera_y, max(0, height - self._view_height))

    def _has_world(self) -> bool:
        return self._world_width > 0 and self._world_height > 0
