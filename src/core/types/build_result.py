from dataclasses import dataclass
from typing import Optional

from src.core.entities.faction import Faction


@dataclass(slots=True)
class BuildResult:
    """Outcome of build validation."""

    allowed: bool
    cost: int = 0
    owner: Optional[Faction] = None
    is_fortress: bool = False
