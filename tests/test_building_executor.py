import unittest

from scripts.buildings.executor import BuildingExecutor


class TestBuildingExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = BuildingExecutor()
        self.preview = {
            "total_commands": 2,
            "foundation": {
                "command_count": 1,
                "coverage_percent": 80.0,
                "unknown_columns": 5,
            },
            "structure_command_count": 1,
            "blockers": ["VOLUME_INCOMPLETO"],
            "commands": [
                "fill 0 69 0 2 69 2 cobblestone",
                "setblock 1 70 1 minecraft:stone",
            ],
        }

    def test_valid_dry_run(self):
        result = self.executor.dry_run(self.preview)

        self.assertEqual(result["status"], "DRY_RUN")
        self.assertFalse(result["execution_allowed"])
        self.assertEqual(result["command_count"], 2)
        self.assertEqual(result["total_command_volume"], 10)

    def test_unknown_terrain_is_reported(self):
        result = self.executor.dry_run(self.preview)

        self.assertEqual(result["terrain_coverage_percent"], 80.0)
        self.assertEqual(result["unknown_columns"], 5)
        self.assertIn("VOLUME_INCOMPLETO", result["blockers"])

    def test_rejects_other_commands(self):
        with self.assertRaises(ValueError):
            self.executor.validate_command("op PipiMeme")

    def test_rejects_invalid_material(self):
        with self.assertRaises(ValueError):
            self.executor.validate_command(
                "setblock 0 70 0 stone replace air"
            )

    def test_rejects_world_height(self):
        with self.assertRaises(ValueError):
            self.executor.validate_command(
                "setblock 0 320 0 stone"
            )

    def test_rejects_large_fill(self):
        with self.assertRaises(ValueError):
            self.executor.validate_command(
                "fill 0 70 0 100 100 100 stone"
            )

    def test_rejects_inconsistent_command_count(self):
        self.preview["total_commands"] = 3

        with self.assertRaises(ValueError):
            self.executor.dry_run(self.preview)

    def test_rejects_empty_commands(self):
        self.preview["commands"] = []

        with self.assertRaises(ValueError):
            self.executor.dry_run(self.preview)


if __name__ == "__main__":
    unittest.main()
