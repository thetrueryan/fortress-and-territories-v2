from abc import ABC
from dataclasses import dataclass, field
from typing import Set

from core.types.coord import Coord


@dataclass
class AbstractClient(ABC):
    """
    Base class for all game clients (Player and AI).
    
    Represents a faction with base, territories, fortresses, and game state.
    All clients share common properties and simple operations.
    """
    client_id: str
    name: str
    color_pair: int
    base_coord: Coord
    is_ai: bool  # Must be set by subclasses (Player: False, AI: True)
    alive: bool = True
    territory: Set[Coord] = field(default_factory=set)
    fortresses: Set[Coord] = field(default_factory=set)
    
    # Simple helper methods (OK in entity)
    def kill(self) -> None:
        """Mark client as defeated."""
        self.alive = False
    
    def revive(self) -> None:
        """Revive client (for testing/debugging)."""
        self.alive = True
    
    def add_territory(self, coord: Coord) -> None:
        """Add territory coordinate."""
        self.territory.add(coord)
    
    def remove_territory(self, coord: Coord) -> None:
        """Remove territory coordinate."""
        self.territory.discard(coord)
    
    def add_fortress(self, coord: Coord) -> None:
        """Add fortress coordinate."""
        self.fortresses.add(coord)
    
    def remove_fortress(self, coord: Coord) -> None:
        """Remove fortress coordinate."""
        self.fortresses.discard(coord)
    
    def owns(self, coord: Coord) -> bool:
        """Check if client owns given coordinate (base, territory, or fortress)."""
        return coord == self.base_coord or coord in self.territory or coord in self.fortresses
    
    @property
    def score(self) -> int:
        """Calculate score (territories + fortresses count)."""
        return len(self.territory) + len(self.fortresses)
    
    def summary(self) -> str:
        """Human-readable summary for debugging/logging."""
        status = "AI" if self.is_ai else "HUMAN"
        state = "ALIVE" if self.alive else "DEAD"
        return (
            f"{self.name} ({status}, {state}) | "
            f"Territory: {len(self.territory)} tiles | "
            f"Fortresses: {len(self.fortresses)}"
        )
    

