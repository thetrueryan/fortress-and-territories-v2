from dataclasses import dataclass, field

from src.core.configs.terrain import TerrainConfig
from src.core.configs.colors import ColorConfig
from src.core.configs.display import DisplayConfig


@dataclass
class Settings:
    terrain: TerrainConfig = field(default_factory=TerrainConfig)
    colors: ColorConfig = field(default_factory=ColorConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)


settings = Settings()