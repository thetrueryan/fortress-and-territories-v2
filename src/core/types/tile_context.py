from dataclasses import dataclass
from src.core.types.enums.terrain import TerrainType


@dataclass(slots=True)
class TileContext:
    """Snapshot of tile attributes used during validation."""

    terrain_type: TerrainType
    base_cost: int
    is_water: bool
    is_bridge: bool
    is_tower: bool
    is_portal: bool
    is_mountain: bool
