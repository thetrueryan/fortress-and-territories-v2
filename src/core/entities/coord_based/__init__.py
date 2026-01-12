"""Coord-based entities (on-map entities)."""

from src.core.entities.coord_based.base import Base
from src.core.entities.coord_based.bridge import Bridge
from src.core.entities.coord_based.building import Building
from src.core.entities.coord_based.fortress import Fortress
from src.core.entities.coord_based.portal import Portal
from src.core.entities.coord_based.territory import Territory
from src.core.entities.coord_based.tower import Tower
from src.core.entities.coord_based.water import Water
from src.core.entities.coord_based.forest import Forest

__all__ = [
    "Base",
    "Bridge",
    "Building",
    "Fortress",
    "Portal",
    "Territory",
    "Tower",
    "Water",
    "Forest"
]
