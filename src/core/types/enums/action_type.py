from enum import Enum


class PlayerActionType(Enum):
    """Possible actions triggered by player input."""

    BUILD = "build"
    SKIP = "skip"