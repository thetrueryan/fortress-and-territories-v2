"""
Ownership resolution utilities for build validation.
"""

from dataclasses import dataclass
from typing import Optional

from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.types.coord import Coord
from src.core.types.enums.terrain import TerrainType


@dataclass(slots=True)
class OwnerInfo:
    """Snapshot describing who controls a tile and whether it's a fortress."""

    owner: Optional[Faction]
    is_fortress: bool


class OwnerResolver:
    """Static utility class for resolving tile ownership."""

    @staticmethod
    def resolve(
        coord: Coord,
        my_faction: Faction,
        factions: list[Faction],
        world: World,
    ) -> OwnerInfo:
        """Resolve active owner for a tile, prioritising alive factions."""
        owner, is_fortress = OwnerResolver._find_owner(
            coord, my_faction, factions, world, alive_first=True
        )
        if owner is not None:
            return OwnerInfo(owner=owner, is_fortress=is_fortress)

        owner, is_fortress = OwnerResolver._find_owner(
            coord, my_faction, factions, world, alive_first=False
        )
        return OwnerInfo(owner=owner, is_fortress=is_fortress)

    @staticmethod
    def _find_owner(
        coord: Coord,
        my_faction: Faction,
        factions: list[Faction],
        world: World,
        alive_first: bool,
    ) -> tuple[Optional[Faction], bool]:
        for faction in factions:
            if faction == my_faction:
                continue
            if alive_first and not faction.alive:
                continue
            if not alive_first and faction.alive:
                continue

            owner, is_fortress = OwnerResolver._classify_owner(coord, faction, world)
            if owner:
                return owner, is_fortress

        return None, False

    @staticmethod
    def _classify_owner(
        coord: Coord,
        faction: Faction,
        world: World,
    ) -> tuple[Optional[Faction], bool]:
        if coord == faction.base.coord:
            return faction, False

        if coord in faction.fortresses:
            return faction, True

        if coord in faction.territory:
            terrain_type = world.get_terrain_type(coord)
            if terrain_type in {
                TerrainType.BRIDGE,
                TerrainType.PORTAL,
                TerrainType.TOWER,
            }:
                return faction, True
            return faction, False

        if (
            coord in faction.towers
            or coord in faction.bridges
            or coord in faction.portals
        ):
            return faction, True

        return None, False
