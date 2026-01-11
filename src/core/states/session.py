from dataclasses import dataclass

from .gamemode import GameModeFlags
from src.core.types.menu_selection import MenuSelection


@dataclass(slots=True)
class GameSessionState:
    """Derived configuration/state once menu selection is confirmed."""

    selection: MenuSelection
    flags: GameModeFlags
    observer_mode: bool
    dynamic_camera: bool