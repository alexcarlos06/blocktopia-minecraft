import unittest
from unittest.mock import Mock

from scripts.buildings.foundation import FoundationPlanner
from scripts.buildings.foundation_commands import (
    generate_foundation_commands,
)


class TestFoundationCommands(unittest.TestCase):

    def setUp(self):
        reader = Mock()
        reader.get_height.side_effect = lambda x, z: {
            (0, 0): 145,
            (1, 0): 153,
            (2, 0): None,
        }[(x, z)]

        self.planner = FoundationPlanner(reader)

    def generate(self, strategy, material="cobblestone"):
        report = self.planner.plan(
            (0, 0, 2, 0),
            150,
            strategy,
        )
        return generate_foundation_commands(report, material)

    def test_natural_has_no_commands(self):
        result = self.generate("NATURAL")

        self.assertEqual(result["commands"], [])
        self.assertEqual(result["command_count"], 0)

    def test_level_excavation_and_foundation(self):
        result = self.generate("LEVEL")

        self.assertEqual(
            result["commands"],
            [
                "fill 0 146 0 0 149 0 cobblestone",
                "fill 1 150 0 1 153 0 air",
            ],
        )

    def test_elevated_foundation(self):
        result = self.generate("ELEVATED")

        self.assertEqual(
            result["commands"],
            [
                "fill 0 146 0 0 153 0 cobblestone",
            ],
        )

    def test_unknown_column_skipped(self):
        result = self.generate("LEVEL")

        self.assertEqual(result["unknown_columns_skipped"], 1)

        for command in result["commands"]:
            self.assertNotIn("fill 2 ", command)

    def test_custom_material(self):
        result = self.generate("LEVEL", "stone")

        self.assertTrue(
            result["commands"][0].endswith("stone")
        )

    def test_invalid_material(self):
        with self.assertRaises(ValueError):
            self.generate("LEVEL", "stone replace air")

    def test_invalid_strategy(self):
        with self.assertRaises(ValueError):
            generate_foundation_commands({
                "strategy": "INVALID",
                "suggested_base_y": 150,
                "columns": [],
            })

    def test_never_authorizes_execution(self):
        for strategy in ("NATURAL", "LEVEL", "ELEVATED"):
            with self.subTest(strategy=strategy):
                result = self.generate(strategy)
                self.assertFalse(result["execution_allowed"])


if __name__ == "__main__":
    unittest.main()
