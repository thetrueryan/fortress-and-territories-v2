from dataclasses import dataclass

from .terrain import Terrain
from src.core.types.enums.terrain import TerrainType

@dataclass
class Empty(Terrain):
    icon = " "
    cost = 1
    type = TerrainType.EMPTY