from dataclasses import dataclass

from .terrain import Terrain
from src.core.types.enums.terrain import TerrainType

@dataclass
class Forest(Terrain):
    icon = "^"
    cost = 2
    type = TerrainType.FOREST