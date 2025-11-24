from dataclasses import dataclass

from core.configs.terrain import TerrainConfig
from core.configs.colors import ColorConfig
from core.configs.display import DisplayConfig


@dataclass
class Settings:
    terrain: TerrainConfig = TerrainConfig()
    colors: ColorConfig = ColorConfig()
    display: DisplayConfig = DisplayConfig()


settings = Settings()