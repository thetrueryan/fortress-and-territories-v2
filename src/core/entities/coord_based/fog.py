from dataclasses import dataclass

from .terrain import Terrain
from src.core.types.enums.terrain import TerrainType

@dataclass
class Fog(Terrain):
    icon = "░"
    cost = 5
    type = TerrainType.FOG