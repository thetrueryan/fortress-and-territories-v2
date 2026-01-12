from dataclasses import dataclass

from .abstract_cord_entity import AbstractCoordEntity
from src.core.types.enums import TerrainType

@dataclass
class Terrain(AbstractCoordEntity):
    type: TerrainType