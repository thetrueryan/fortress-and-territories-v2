from dataclasses import dataclass

from .enums import modes, WorldType


@dataclass(slots=True)
class MenuSelection:
    """Snapshot of menu selections used to bootstrap a game session."""

    fortress_mode: modes.FortressMode
    player_count: int
    map_size: tuple[int, int]
    world_type: WorldType
    camera_mode: modes.CameraMode
    experimental_modes: modes.ExperimentalMode