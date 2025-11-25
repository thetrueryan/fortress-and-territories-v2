from dataclasses import dataclass

from .coord import Coord
from .build_result import BuildResult


@dataclass(frozen=True)
class Candidate:
    """Represents a potential build/capture action."""

    coord: Coord
    result: BuildResult
