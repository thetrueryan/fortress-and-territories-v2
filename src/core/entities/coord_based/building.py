from dataclasses import dataclass

from .abstract_cord_entity import AbstractCoordEntity
from src.core.types.enums.building import BuildingType


@dataclass
class Building(AbstractCoordEntity):
    """
    Base class for all buildings on the map.
    
    Buildings can be:
    - Base (faction's heart)
    - Territory (owned land)
    - Fortress (regular captured territory)
    - Tower (captured watchtower)
    - Bridge (built over water)
    - Portal (captured teleporter)
    """
    faction_id: str | None
    building_type: BuildingType
    age: int = 0  # For Classic mode aging
    
    def is_owned_by(self, faction_id: str) -> bool:
        """Check if fortress is owned by given faction."""
        return self.faction_id == faction_id
    
    def is_neutral(self) -> bool:
        """Check if fortress is neutral (unowned)."""
        return self.faction_id is None
    
    def is_regular(self) -> bool:
        """Check if this is a regular fortress (not special structure)."""
        return self.building_type == BuildingType.FORTRESS
    
    @property
    def should_age(self) -> bool:
        """Check if building should age in Classic mode (only regular fortresses age)."""
        return self.building_type == BuildingType.FORTRESS

