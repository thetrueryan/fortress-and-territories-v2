from dataclasses import dataclass


@dataclass
class TerrainConfig:
    """Terrain symbols configuration."""

    empty: str = " "
    water: str = "~"
    mountain: str = "^"
    tower: str = "T"
    bridge: str = "B"
    portal: str = "H"
    fog: str = "░"
