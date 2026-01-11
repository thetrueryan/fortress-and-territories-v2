from dataclasses import dataclass

from .enums.action_type import PlayerActionType
from .coord import Coord


@dataclass(slots=True)
class PlayerAction:
    """Normalized representation of player intent."""

    kind: PlayerActionType
    coord: Coord | None = None