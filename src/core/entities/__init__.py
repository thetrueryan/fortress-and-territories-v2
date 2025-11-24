"""Game entities module."""

from core.entities.clients import AI, Player
from core.entities.coord_based import (
    Base,
    Bridge,
    Building,
    Fortress,
    Portal,
    Territory,
    Tower,
)

__all__ = [
    # Clients
    "AI",
    "Player",
    # Coord-based
    "Base",
    "Bridge",
    "Building",
    "Fortress",
    "Portal",
    "Territory",
    "Tower",
]

