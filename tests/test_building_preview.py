import unittest
from unittest.mock import Mock, patch

from scripts.buildings.engine import BuildingEngine
from scripts.buildings.preview import generate_building_preview


class TestBuildingPreview(unittest.TestCase):

    def setUp(self):
        self.reader = Mock()
        self.reader.get_height.return_value = 153

        self.building = BuildingEngine(0, 150, 0)
        self.building.block(0, 0, 0, "stone")

        self.validation = {
            "terrain": {
                "min_height": 153,
                "max_height": 153,
                "height_difference": 0,
                "overhead_obstacles": 0,
                "missing_positions": 0,
            },
            "volume": {
                "total_blocks": 1,
                "occupied_blocks": 0,
                "unknown_blocks": 0,
            },
            "blockers": [
                "CRITERIOS_DE_APROVACAO_PENDENTES"
            ],
        }

    def preview(self, strategy):
        with patch(
            "scripts.buildings.preview.BuildingValidator"
        ) as validator:
            validator.return_value.validate.return_value = (
                self.validation
            )

            report = generate_building_preview(
                self.building,
                self.reader,
                foundation_strategy=strategy,
            )

            validated = (
                validator.return_value.validate.call_args.args[0]
            )

        return report, validated

    def test_natural_position(self):
        report, validated = self.preview("NATURAL")

        self.assertEqual(report["elevation"], 0)
        self.assertEqual(
            validated.bounds,
            (0, 150, 0, 0, 150, 0),
        )
        self.assertEqual(report["total_commands"], 1)

    def test_elevated_position(self):
        report, validated = self.preview("ELEVATED")

        self.assertEqual(report["elevation"], 4)
        self.assertEqual(report["suggested_base_y"], 154)
        self.assertEqual(
            validated.bounds,
            (0, 154, 0, 0, 154, 0),
        )
        self.assertEqual(
            report["commands"],
            ["setblock 0 154 0 minecraft:stone"],
        )

    def test_volume_and_blockers(self):
        self.validation["volume"]["occupied_blocks"] = 1
        self.validation["blockers"].append("VOLUME_OCUPADO")

        report, _ = self.preview("ELEVATED")

        self.assertEqual(report["volume"]["occupied_blocks"], 1)
        self.assertIn("VOLUME_OCUPADO", report["blockers"])
        self.assertFalse(report["execution_allowed"])

    def test_original_building_preserved(self):
        original_commands = list(self.building.commands)
        original_bounds = self.building.bounds

        self.preview("ELEVATED")

        self.assertEqual(
            self.building.commands,
            original_commands,
        )
        self.assertEqual(
            self.building.bounds,
            original_bounds,
        )


if __name__ == "__main__":
    unittest.main()
