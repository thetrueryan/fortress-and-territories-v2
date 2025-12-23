import pytest

from src.building.build_validator import BuildValidator
from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.main_config import settings
from src.core.states.gamemode import GameModeFlags
from src.core.states.gameplay import GameplayState
from src.core.types.coord import Coord


def make_faction(name: str, base: Coord) -> Faction:
    return Faction(name=name, color_pair=1, base=base, is_ai=False)


def make_validator() -> BuildValidator:
    return BuildValidator(GameplayState())


def test_validate_rejects_own_cell():
    validator = make_validator()
    world = World(5, 5)
    faction = make_faction("Blue", Coord(0, 0))
    target = Coord(1, 0)
    faction.add_territory(target)

    result = validator.validate(
        target_cell=target,
        my_faction=faction,
        all_factions=[faction],
        world=world,
        flags=GameModeFlags(),
    )

    assert result.allowed is False


def test_classic_mode_blocks_enemy_fortress_capture():
    validator = make_validator()
    world = World(5, 5)
    my_faction = make_faction("Blue", Coord(0, 0))
    neighbor = Coord(1, 0)
    target = Coord(2, 0)
    my_faction.add_territory(neighbor)

    enemy = make_faction("Red", Coord(4, 4))
    enemy.add_fortress(target)

    result = validator.validate(
        target_cell=target,
        my_faction=my_faction,
        all_factions=[my_faction, enemy],
        world=world,
        flags=GameModeFlags(classic=True),
    )

    assert result.allowed is False
    assert result.owner is enemy
    assert result.is_fortress is True


def test_conquest_mode_allows_enemy_fortress_capture():
    validator = make_validator()
    world = World(5, 5)
    my_faction = make_faction("Blue", Coord(0, 0))
    neighbor = Coord(1, 0)
    target = Coord(2, 0)
    my_faction.add_territory(neighbor)

    enemy = make_faction("Red", Coord(4, 4))
    enemy.add_fortress(target)

    result = validator.validate(
        target_cell=target,
        my_faction=my_faction,
        all_factions=[my_faction, enemy],
        world=world,
        flags=GameModeFlags(classic=False),
    )

    assert result.allowed is True
    assert result.owner is enemy
    assert result.is_fortress is True


def test_supply_mode_requires_connected_chain():
    validator = make_validator()
    world = World(5, 5)
    my_faction = make_faction("Blue", Coord(0, 0))
    disconnected = Coord(2, 0)
    target = Coord(3, 0)
    my_faction.add_territory(disconnected)

    default_result = validator.validate(
        target_cell=target,
        my_faction=my_faction,
        all_factions=[my_faction],
        world=world,
        flags=GameModeFlags(),
    )
    assert default_result.allowed is True

    supply_result = validator.validate(
        target_cell=target,
        my_faction=my_faction,
        all_factions=[my_faction],
        world=world,
        flags=GameModeFlags(supply=True),
    )
    assert supply_result.allowed is False


def test_mountain_efficiency_reduces_cost():
    validator = make_validator()
    world = World(5, 5)
    target = Coord(1, 1)
    world.set_terrain(target, settings.terrain.mountain)

    my_faction = make_faction("Blue", Coord(0, 0))
    neighbor = Coord(1, 0)
    my_faction.add_territory(neighbor)

    base_result = validator.validate(
        target_cell=target,
        my_faction=my_faction,
        all_factions=[my_faction],
        world=world,
        flags=GameModeFlags(),
    )
    assert base_result.allowed is True
    assert base_result.cost == 2

    efficiency_result = validator.validate(
        target_cell=target,
        my_faction=my_faction,
        all_factions=[my_faction],
        world=world,
        flags=GameModeFlags(mountain_efficiency=True),
        converted_mountains={target},
    )
    assert efficiency_result.allowed is True
    assert efficiency_result.cost == 1
