from dataclasses import dataclass

from .abstract_cord_entity import AbstractCoordEntity
from src.core.types.enums.building import BuildingType


@dataclass
class Building(AbstractCoordEntity):
    """
    Base class for all buildings on the map.
    """
    faction_id: str | None
    type: BuildingType
    age: int = 0  # For Classic mode aging

    @property
    def vision_radius(self) -> int:
        if self.faction_id:
            return 5
        return 0
    
    @property
    def should_age(self) -> bool:
        """Check if building should age in Classic mode (only regular fortresses age)."""
        return self.type == BuildingType.FORTRESS
