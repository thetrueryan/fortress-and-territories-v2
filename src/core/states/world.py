from dataclasses import dataclass


@dataclass
class WorldState:
    water_coverage: float = 0.10
    mountain_coverage: float = 0.15
    tower_count: int = 4