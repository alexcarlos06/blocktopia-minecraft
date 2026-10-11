import unittest
from unittest.mock import Mock

from scripts.terrain.volume_analyzer import VolumeAnalyzer


class TestVolumeAnalyzer(unittest.TestCase):

    def test_mixed_volume(self):
        reader = Mock()

        blocks = {
            (0, 70, 0): "minecraft:stone",
            (0, 71, 0): "minecraft:air",
            (0, 72, 0): None,
        }

        reader.get_block.side_effect = (
            lambda x, y, z: blocks[(x, y, z)]
        )

        report = VolumeAnalyzer(reader).analyze(
            (0, 70, 0, 0, 72, 0)
        )

        self.assertEqual(report["total_blocks"], 3)
        self.assertEqual(report["occupied_blocks"], 1)
        self.assertEqual(report["empty_blocks"], 1)
        self.assertEqual(report["unknown_blocks"], 1)
        self.assertEqual(report["status"], "PENDENTE")

    def test_empty_volume(self):
        reader = Mock()
        reader.get_block.return_value = "minecraft:air"

        report = VolumeAnalyzer(reader).analyze(
            (0, 70, 0, 1, 71, 1)
        )

        self.assertEqual(report["total_blocks"], 8)
        self.assertEqual(report["empty_blocks"], 8)
        self.assertEqual(report["occupied_blocks"], 0)
        self.assertEqual(report["unknown_blocks"], 0)
        self.assertEqual(report["status"], "PENDENTE")

    def test_liquid_is_occupied(self):
        reader = Mock()
        reader.get_block.return_value = "minecraft:water"

        report = VolumeAnalyzer(reader).analyze(
            (0, 70, 0, 0, 70, 0)
        )

        self.assertEqual(report["occupied_blocks"], 1)
        self.assertEqual(
            report["material_categories"]["LIQUIDO"], 1
        )

    def test_unknown_material_is_occupied(self):
        reader = Mock()
        reader.get_block.return_value = "minecraft:custom_block"

        report = VolumeAnalyzer(reader).analyze(
            (0, 70, 0, 0, 70, 0)
        )

        self.assertEqual(report["occupied_blocks"], 1)
        self.assertEqual(
            report["material_categories"]["DESCONHECIDO"], 1
        )

    def test_invalid_bounds(self):
        reader = Mock()
        analyzer = VolumeAnalyzer(reader)

        invalid = (
            None,
            (0, 0, 0),
            (2, 0, 0, 1, 1, 1),
            (0, 2, 0, 1, 1, 1),
            (0, 0, 2, 1, 1, 1),
            (0.5, 0, 0, 1, 1, 1),
        )

        for bounds in invalid:
            with self.subTest(bounds=bounds):
                with self.assertRaises(ValueError):
                    analyzer.analyze(bounds)

        reader.get_block.assert_not_called()

    def test_volume_limit(self):
        reader = Mock()

        with self.assertRaises(ValueError):
            VolumeAnalyzer(reader).analyze(
                (0, 0, 0, 100, 100, 100)
            )

        reader.get_block.assert_not_called()

    def test_reader_failure(self):
        reader = Mock()
        reader.get_block.side_effect = ValueError(
            "Subchunk não suportado"
        )

        with self.assertRaises(ValueError):
            VolumeAnalyzer(reader).analyze(
                (0, 70, 0, 1, 71, 1)
            )


if __name__ == "__main__":
    unittest.main()
