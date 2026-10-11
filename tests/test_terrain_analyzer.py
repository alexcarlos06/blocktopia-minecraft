import unittest
from unittest.mock import Mock

from scripts.buildings.engine import BuildingEngine
from scripts.terrain.analyzer import TerrainAnalyzer


class TestTerrainAnalyzer(unittest.TestCase):

    def test_complete_area(self):
        reader = Mock()
        reader.get_height.return_value = 70

        report = TerrainAnalyzer(reader).analyze((0, 0, 2, 2))

        self.assertEqual(report["total_positions"], 9)
        self.assertEqual(report["available_positions"], 9)
        self.assertEqual(report["missing_positions"], 0)
        self.assertEqual(report["min_height"], 70)
        self.assertEqual(report["max_height"], 70)
        self.assertEqual(report["height_difference"], 0)
        self.assertEqual(report["status"], "PENDENTE")
        self.assertEqual(reader.get_height.call_count, 9)

    def test_missing_height(self):
        reader = Mock()
        reader.get_height.side_effect = (
            lambda x, z: None if (x, z) == (1, 1) else 70
        )

        report = TerrainAnalyzer(reader).analyze((0, 0, 2, 2))

        self.assertEqual(report["available_positions"], 8)
        self.assertEqual(report["missing_positions"], 1)
        self.assertEqual(
            report["missing_coordinates"],
            [(1, 1)]
        )
        self.assertEqual(report["status"], "PENDENTE")

    def test_building_engine_integration(self):
        engine = BuildingEngine(100, 70, 200)
        engine.fill(-1, 0, -1, 1, 3, 1, "stone")

        reader = Mock()
        reader.get_height.return_value = 70

        report = TerrainAnalyzer(reader).analyze(engine.footprint)

        self.assertEqual(
            report["footprint"],
            (99, 199, 101, 201)
        )
        self.assertEqual(report["width"], 3)
        self.assertEqual(report["depth"], 3)

    def test_invalid_footprint(self):
        reader = Mock()
        analyzer = TerrainAnalyzer(reader)

        invalid = [
            None,
            (0, 0, 1),
            (2, 0, 1, 1),
            (0, 2, 1, 1),
            (0.5, 0, 1, 1),
        ]

        for footprint in invalid:
            with self.subTest(footprint=footprint):
                with self.assertRaises(ValueError):
                    analyzer.analyze(footprint)

        reader.get_height.assert_not_called()

    def test_area_limit(self):
        reader = Mock()

        with self.assertRaises(ValueError):
            TerrainAnalyzer(reader).analyze((0, 0, 100, 100))

        reader.get_height.assert_not_called()

    def test_reader_error_propagates(self):
        reader = Mock()
        reader.get_height.side_effect = ValueError(
            "Data3D incompleto"
        )

        with self.assertRaises(ValueError):
            TerrainAnalyzer(reader).analyze((0, 0, 1, 1))

    def test_invalid_height(self):
        reader = Mock()
        reader.get_height.return_value = "70"

        with self.assertRaises(ValueError):
            TerrainAnalyzer(reader).analyze((0, 0, 1, 1))


if __name__ == "__main__":
    unittest.main()
