from src.ai.ai_controller import AIController
from src.core.entities.coord_based.tower import Tower
from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.main_config import settings
from src.core.states.gamemode import GameModeFlags
from src.core.states.gameplay import GameplayState
from src.core.types.coord import Coord
from src.core.types.enums.building import BuildingType
from src.services.event_log import EventLog


def make_faction(name: str, base: Coord) -> Faction:
    return Faction(name=name, color_pair=1, base=base, is_ai=True)


def make_controller(move_budget: int = 5) -> AIController:
    return AIController(GameplayState(), move_budget=move_budget)


def test_ai_captures_neutral_tile():
    controller = make_controller(move_budget=2)
    world = World(2, 1)
    factions = [make_faction("Blue", Coord(0, 0))]

    controller.take_turn(
        faction_idx=0,
        factions=factions,
        world=world,
        flags=GameModeFlags(),
    )

    target = Coord(1, 0)
    assert target in factions[0].territory or target in factions[0].fortresses


def test_ai_captures_enemy_fortress_in_conquest():
    controller = make_controller(move_budget=3)
    world = World(4, 1)
    me = make_faction("Blue", Coord(0, 0))
    enemy = make_faction("Red", Coord(3, 0))
    target = Coord(1, 0)
    enemy.add_fortress(target)

    controller.take_turn(
        faction_idx=0,
        factions=[me, enemy],
        world=world,
        flags=GameModeFlags(),
    )

    assert target in me.fortresses
    assert target not in enemy.fortresses


def test_ai_respects_classic_mode_when_capturing_fortress():
    controller = make_controller(move_budget=3)
    world = World(4, 1)
    me = make_faction("Blue", Coord(0, 0))
    enemy = make_faction("Red", Coord(3, 0))
    target = Coord(1, 0)
    enemy.add_fortress(target)

    controller.take_turn(
        faction_idx=0,
        factions=[me, enemy],
        world=world,
        flags=GameModeFlags(classic=True),
    )

    assert target in enemy.fortresses
    assert target not in me.fortresses


def test_ai_captures_tower_and_logs_event():
    controller = make_controller(move_budget=3)
    world = World(3, 1)
    tower_coord = Coord(1, 0)
    world.add_tower(
        Tower(
            coord=tower_coord,
            faction_id=None,
            building_type=BuildingType.TOWER,
        )
    )
    me = make_faction("Blue", Coord(0, 0))
    event_log = EventLog()
    captured_towers: set[Coord] = set()

    controller.take_turn(
        faction_idx=0,
        factions=[me],
        world=world,
        flags=GameModeFlags(),
        event_log=event_log,
        captured_towers=captured_towers,
    )

    assert not world.has_neutral_tower(tower_coord)
    assert tower_coord in me.towers
    assert tower_coord in me.fortresses
    assert tower_coord in captured_towers
    assert any("CAPTURED TOWER" in msg for msg in event_log.latest())


def test_ai_marks_converted_mountains_in_efficiency_mode():
    controller = make_controller(move_budget=3)
    world = World(2, 1)
    target = Coord(1, 0)
    world.set_terrain(target, settings.terrain.mountain)
    me = make_faction("Blue", Coord(0, 0))
    converted: set[Coord] = set()

    controller.take_turn(
        faction_idx=0,
        factions=[me],
        world=world,
        flags=GameModeFlags(mountain_efficiency=True),
        converted_mountains=converted,
    )

    assert target in converted
    assert target in me.territory or target in me.fortresses
