import unittest
from unittest.mock import Mock

from scripts.buildings.engine import BuildingEngine
from scripts.buildings.plan import BuildingPlan


class TestBuildingPlan(unittest.TestCase):

    def setUp(self):
        self.reader = Mock()
        self.reader.get_height.side_effect = lambda x, z: {
            (0, 0): 145,
            (1, 0): 153,
            (2, 0): None,
        }[(x, z)]

        self.building = BuildingEngine(0, 150, 0)
        self.building.fill(0, 0, 0, 2, 2, 0, "stone")
        self.building.block(1, 3, 0, "glass")

    def generate(self, strategy):
        return BuildingPlan(
            building=self.building,
            reader=self.reader,
            foundation_strategy=strategy,
        ).generate()

    def test_natural_keeps_original_position(self):
        result = self.generate("NATURAL")

        self.assertEqual(result["elevation"], 0)
        self.assertEqual(result["foundation_commands"], [])
        self.assertEqual(
            result["structure_commands"],
            self.building.commands,
        )

    def test_level_generates_preparation(self):
        result = self.generate("LEVEL")

        self.assertEqual(result["elevation"], 0)
        self.assertEqual(result["excavation_blocks"], 4)
        self.assertEqual(result["foundation_blocks"], 4)
        self.assertEqual(len(result["foundation_commands"]), 2)

    def test_elevated_moves_entire_structure(self):
        result = self.generate("ELEVATED")

        self.assertEqual(result["elevation"], 4)
        self.assertEqual(result["suggested_base_y"], 154)
        self.assertEqual(
            result["adjusted_bounds"],
            (0, 154, 0, 2, 157, 0),
        )
        self.assertEqual(
            result["structure_commands"],
            [
                "fill 0 154 0 2 156 0 minecraft:stone",
                "setblock 1 157 0 minecraft:glass",
            ],
        )

    def test_foundation_precedes_structure(self):
        result = self.generate("LEVEL")

        self.assertEqual(
            result["commands"],
            result["foundation_commands"]
            + result["structure_commands"],
        )

    def test_original_building_unchanged(self):
        original_commands = list(self.building.commands)
        original_bounds = self.building.bounds
        original_origin = self.building.origin

        self.generate("ELEVATED")

        self.assertEqual(self.building.commands, original_commands)
        self.assertEqual(self.building.bounds, original_bounds)
        self.assertEqual(self.building.origin, original_origin)

    def test_unknown_terrain_is_reported(self):
        result = self.generate("ELEVATED")

        self.assertEqual(result["known_columns"], 2)
        self.assertEqual(result["unknown_columns"], 1)
        self.assertEqual(result["terrain_coverage_percent"], 66.67)

    def test_execution_never_automatic(self):
        for strategy in ("NATURAL", "LEVEL", "ELEVATED"):
            with self.subTest(strategy=strategy):
                result = self.generate(strategy)
                self.assertFalse(result["execution_allowed"])
                self.assertEqual(result["status"], "PENDENTE")

    def test_empty_building_rejected(self):
        empty = BuildingEngine(0, 150, 0)

        with self.assertRaises(ValueError):
            BuildingPlan(
                building=empty,
                reader=self.reader,
            ).generate()

    def test_invalid_strategy_rejected(self):
        with self.assertRaises(ValueError):
            self.generate("INVALIDA")

    def test_shift_above_world_limit_rejected(self):
        reader = Mock()
        reader.get_height.return_value = 319

        building = BuildingEngine(0, 318, 0)
        building.block(0, 1, 0, "stone")

        with self.assertRaises(ValueError):
            BuildingPlan(
                building=building,
                reader=reader,
                foundation_strategy="ELEVATED",
            ).generate()


if __name__ == "__main__":
    unittest.main()
