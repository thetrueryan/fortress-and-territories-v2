from dataclasses import dataclass

from src.core.configs.terrain import TerrainConfig
from src.core.configs.colors import ColorConfig
from src.core.configs.display import DisplayConfig


@dataclass
class Settings:
    terrain: TerrainConfig = TerrainConfig()
    colors: ColorConfig = ColorConfig()
    display: DisplayConfig = DisplayConfig()


settings = Settings()