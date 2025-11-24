"""
Coord Type Module
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Coord:
    """
    Immutable coordinate (x, y) with helper methods.
    
    Frozen dataclass ensures it's hashable for use in sets/dicts.
    Slots reduce memory overhead (important for thousands of coordinates).
    """
    x: int
    y: int
    
    def __iter__(self):
        """Allow unpacking: x, y = coord"""
        yield self.x
        yield self.y
    
    def __getitem__(self, index: int) -> int:
        """Allow indexing: coord[0], coord[1]"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError(f"Coord index out of range: {index}")
    
    def __add__(self, other: "Coord") -> "Coord":
        """Add coordinates: coord1 + coord2"""
        return Coord(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: "Coord") -> "Coord":
        """Subtract coordinates: coord1 - coord2"""
        return Coord(self.x - other.x, self.y - other.y)
    
    def neighbors(self) -> list["Coord"]:
        """Get orthogonal neighbors (up, down, left, right)."""
        return [
            Coord(self.x + 1, self.y),
            Coord(self.x - 1, self.y),
            Coord(self.x, self.y + 1),
            Coord(self.x, self.y - 1),
        ]
    
    def manhattan_distance(self, other: "Coord") -> int:
        """Manhattan distance to another coordinate."""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def in_bounds(self, width: int, height: int) -> bool:
        """Check if coordinate is within bounds."""
        return 0 <= self.x < width and 0 <= self.y < height
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __repr__(self) -> str:
        return f"Coord({self.x}, {self.y})"