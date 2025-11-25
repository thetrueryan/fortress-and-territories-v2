"""
Tests for world generation.
"""

import pytest

from src.core.entities.faction import Faction
from src.core.entities.world import World
from src.core.main_config import settings
from src.core.states.world import WorldState
from src.core.types.coord import Coord
from src.core.types.enums.world import WorldType
from src.generation.world_generator import WorldGenerator
from src.utils.generation.generation_helper import GenerationHelper


class TestGenerationHelper:
    """Tests for GenerationHelper utility class."""

    def test_calculate_tower_count(self):
        """Test tower count calculation (1 per 400 cells, minimum 1)."""
        assert GenerationHelper.calculate_tower_count(400) == 1
        assert GenerationHelper.calculate_tower_count(800) == 2
        assert GenerationHelper.calculate_tower_count(1200) == 3
        assert GenerationHelper.calculate_tower_count(100) == 1  # minimum 1
        assert GenerationHelper.calculate_tower_count(0) == 1  # minimum 1

    def test_calculate_portal_pairs(self):
        """Test portal pairs calculation (1 pair per 1600 cells)."""
        assert GenerationHelper.calculate_portal_pairs(1600) == 1
        assert GenerationHelper.calculate_portal_pairs(3200) == 2
        assert GenerationHelper.calculate_portal_pairs(4800) == 3
        assert GenerationHelper.calculate_portal_pairs(800) == 1  # minimum 1
        assert GenerationHelper.calculate_portal_pairs(0) == 1  # minimum 1

    def test_is_safe_zone(self):
        """Test safe zone detection."""
        faction1 = Faction(
            name="Faction1", color_pair=1, base=Coord(10, 10), is_ai=True, alive=True
        )
        faction2 = Faction(
            name="Faction2", color_pair=2, base=Coord(50, 50), is_ai=True, alive=True
        )
        factions = [faction1, faction2]

        # Inside safe zone (radius 3)
        assert GenerationHelper.is_safe_zone(Coord(10, 10), factions, radius=3) is True
        assert GenerationHelper.is_safe_zone(Coord(12, 10), factions, radius=3) is True
        assert GenerationHelper.is_safe_zone(Coord(10, 13), factions, radius=3) is True

        # Outside safe zone
        assert GenerationHelper.is_safe_zone(Coord(20, 20), factions, radius=3) is False
        assert GenerationHelper.is_safe_zone(Coord(0, 0), factions, radius=3) is False


class TestWorldGenerator:
    """Tests for WorldGenerator."""

    @pytest.fixture
    def world_state(self):
        """Create default world state."""
        return WorldState(
            water_coverage=0.1, mountain_coverage=0.15, min_base_distance=8
        )

    @pytest.fixture
    def generator_40x40(self, world_state):
        """Create generator for 40x40 map."""
        return WorldGenerator(40, 40, world_state)

    @pytest.fixture
    def generator_100x100(self, world_state):
        """Create generator for 100x100 map."""
        return WorldGenerator(100, 100, world_state)

    def test_init_factions(self, generator_40x40):
        """Test faction initialization."""
        factions = generator_40x40.init_factions(player_count=4, observer_mode=False)

        assert len(factions) == 4
        assert factions[0].name == "PLAYER"
        assert factions[0].is_ai is False
        assert factions[1].name == "BOT 1"
        assert factions[1].is_ai is True

        # Check that bases are placed
        base_coords = {faction.base for faction in factions}
        assert len(base_coords) == 4  # All bases are unique

    def test_init_factions_observer_mode(self, generator_40x40):
        """Test faction initialization in observer mode."""
        factions = generator_40x40.init_factions(player_count=3, observer_mode=True)

        assert len(factions) == 3
        assert all(faction.is_ai for faction in factions)
        assert factions[0].name == "BOT 1"
        assert factions[1].name == "BOT 2"
        assert factions[2].name == "BOT 3"

    def test_base_distance(self, generator_40x40):
        """Test that bases are placed with minimum distance."""
        factions = generator_40x40.init_factions(player_count=4, observer_mode=True)

        base_coords = [faction.base for faction in factions]

        # Check minimum distance between bases
        for i, base1 in enumerate(base_coords):
            for base2 in base_coords[i + 1 :]:
                distance = base1.manhattan_distance(base2)
                assert (
                    distance >= 7
                )  # Allow some flexibility (min_base_distance=8, but can reduce)

    def test_generate_standard(self, generator_40x40):
        """Test standard world generation."""
        world = World(40, 40, WorldType.STANDARD)
        factions = generator_40x40.init_factions(player_count=2, observer_mode=True)

        generator_40x40.generate(world, factions, WorldType.STANDARD)

        # Check that terrain was generated
        assert len(world.terrain) == 40 * 40

        # Check that towers were placed
        tower_coords = world.get_tower_coords()
        expected_towers = GenerationHelper.calculate_tower_count(40 * 40)
        assert len(tower_coords) == expected_towers

    def test_generate_islands(self, generator_40x40):
        """Test islands world generation."""
        world = World(40, 40, WorldType.ISLANDS)
        factions = generator_40x40.init_factions(player_count=2, observer_mode=True)

        generator_40x40.generate(world, factions, WorldType.ISLANDS)

        # Check that terrain was generated
        assert len(world.terrain) == 40 * 40

        # Check that there are some empty tiles (islands carved from water)
        empty_count = 0
        for x in range(40):
            for y in range(40):
                coord = Coord(x, y)
                terrain = world.get_terrain(coord)
                if terrain == settings.terrain.empty:
                    empty_count += 1

        # Should have some empty tiles (islands)
        assert empty_count > 0

    def test_generate_wasteland(self, generator_40x40):
        """Test wasteland world generation."""
        world = World(40, 40, WorldType.WASTELAND)
        factions = generator_40x40.init_factions(player_count=2, observer_mode=True)

        generator_40x40.generate(world, factions, WorldType.WASTELAND)

        # Check that terrain was generated
        assert len(world.terrain) == 40 * 40

        # Check that towers were placed
        tower_coords = world.get_tower_coords()
        expected_towers = GenerationHelper.calculate_tower_count(40 * 40)
        assert len(tower_coords) == expected_towers

    def test_generate_mountain_madness(self, generator_40x40):
        """Test mountain madness world generation."""
        world = World(40, 40, WorldType.MOUNTAIN_MADNESS)
        factions = generator_40x40.init_factions(player_count=2, observer_mode=True)

        generator_40x40.generate(world, factions, WorldType.MOUNTAIN_MADNESS)

        # Check that terrain was generated
        assert len(world.terrain) == 40 * 40

    def test_tower_count_scaling(self, generator_100x100):
        """Test that tower count scales with map size."""
        world = World(100, 100, WorldType.STANDARD)
        factions = generator_100x100.init_factions(player_count=2, observer_mode=True)

        generator_100x100.generate(world, factions, WorldType.STANDARD)

        tower_coords = world.get_tower_coords()
        expected_towers = GenerationHelper.calculate_tower_count(100 * 100)
        assert len(tower_coords) == expected_towers
        assert expected_towers == 25  # 10000 / 400 = 25

    def test_portal_generation(self, generator_100x100):
        """Test portal generation."""
        total_cells = 100 * 100
        portal_pairs = GenerationHelper.calculate_portal_pairs(total_cells)

        world = World(100, 100, WorldType.STANDARD, portal_pairs=portal_pairs)
        factions = generator_100x100.init_factions(player_count=2, observer_mode=True)

        generator_100x100.generate(world, factions, WorldType.STANDARD)

        portal_coords = world.get_portal_coords()
        expected_portals = portal_pairs * 2
        assert len(portal_coords) == expected_portals

        # Check that portals are linked
        assert len(world.portal_links) == expected_portals
        for portal1, portal2 in world.portal_links.items():
            assert world.portal_links[portal2] == portal1  # Bidirectional link

    def test_safe_zone_protection(self, generator_40x40):
        """Test that structures are not placed in safe zones."""
        world = World(40, 40, WorldType.STANDARD)
        factions = generator_40x40.init_factions(player_count=2, observer_mode=True)

        generator_40x40.generate(world, factions, WorldType.STANDARD)

        # Check that no towers are in safe zones
        tower_coords = world.get_tower_coords()
        for tower_coord in tower_coords:
            assert not GenerationHelper.is_safe_zone(tower_coord, factions, radius=3)

        # Check portals if generated
        if world.portal_pairs > 0:
            portal_coords = world.get_portal_coords()
            for portal_coord in portal_coords:
                assert not GenerationHelper.is_safe_zone(
                    portal_coord, factions, radius=3
                )
