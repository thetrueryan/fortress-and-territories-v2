from dataclasses import dataclass

from .abstract_cord_entity import AbstractCoordEntity
from src.core.types.enums.building import BuildingType


@dataclass
class Building(AbstractCoordEntity):
    """
    Base class for all buildings on the map.
    """
    vision_radius: int = 5
    faction_id: str | None
    type: BuildingType
    age: int = 0  # For Classic mode aging

    @property
    def should_age(self) -> bool:
        """Check if building should age in Classic mode (only regular fortresses age)."""
        return self.type == BuildingType.FORTRESS
