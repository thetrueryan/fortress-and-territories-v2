from enum import Enum


class FortressMode(Enum):
    """High-level fortress rules."""

    CLASSIC = "CLASSIC"
    CONQUEST = "CONQUEST"

class CameraMode(Enum):
    """Camera behaviour options."""

    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"

class ExperimentalMode(Enum):
    """Optional modifiers toggled from the menu."""

    ANTHILL = "Anthill (Муравейник)"
    OBSERVER = "Observer (Наблюдатель)"
    MOUNTAIN_EFFICIENCY = "Mountain Efficiency"
    SUPPLY = "Supply Lines"