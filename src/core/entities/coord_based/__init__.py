"""Coord-based entities (on-map entities)."""

from core.entities.coord_based.base import Base
from core.entities.coord_based.bridge import Bridge
from core.entities.coord_based.building import Building
from core.entities.coord_based.fortress import Fortress
from core.entities.coord_based.portal import Portal
from core.entities.coord_based.territory import Territory
from core.entities.coord_based.tower import Tower

__all__ = [
    "Base",
    "Bridge",
    "Building",
    "Fortress",
    "Portal",
    "Territory",
    "Tower",
]

