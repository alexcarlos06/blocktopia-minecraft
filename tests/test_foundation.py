import unittest
from unittest.mock import Mock

from scripts.buildings.foundation import FoundationPlanner


class TestFoundationPlanner(unittest.TestCase):

    def setUp(self):
        self.reader = Mock()
        self.reader.get_height.side_effect = lambda x, z: {
            (0, 0): 145,
            (1, 0): 153,
            (2, 0): None,
        }[(x, z)]

        self.planner = FoundationPlanner(self.reader)

    def test_natural(self):
        report = self.planner.plan((0, 0, 2, 0), 150, "NATURAL")

        self.assertEqual(report["suggested_base_y"], 150)
        self.assertEqual(report["excavation_blocks"], 0)
        self.assertEqual(report["foundation_blocks"], 0)
        self.assertEqual(report["unknown_columns"], 1)
        self.assertEqual(report["status"], "PENDENTE")

    def test_level(self):
        report = self.planner.plan((0, 0, 2, 0), 150, "LEVEL")

        self.assertEqual(report["suggested_base_y"], 150)
        self.assertEqual(report["excavation_blocks"], 4)
        self.assertEqual(report["foundation_blocks"], 4)

    def test_elevated(self):
        report = self.planner.plan((0, 0, 2, 0), 150, "ELEVATED")

        self.assertEqual(report["suggested_base_y"], 154)
        self.assertEqual(report["elevation"], 4)
        self.assertEqual(report["foundation_blocks"], 8)

    def test_coverage(self):
        report = self.planner.plan((0, 0, 2, 0), 150, "LEVEL")

        self.assertEqual(report["total_columns"], 3)
        self.assertEqual(report["known_columns"], 2)
        self.assertEqual(report["unknown_columns"], 1)
        self.assertEqual(report["coverage_percent"], 66.67)

    def test_all_unknown(self):
        reader = Mock()
        reader.get_height.return_value = None

        report = FoundationPlanner(reader).plan(
            (0, 0, 1, 1), 150, "ELEVATED"
        )

        self.assertEqual(report["known_columns"], 0)
        self.assertEqual(report["unknown_columns"], 4)
        self.assertEqual(report["coverage_percent"], 0)
        self.assertEqual(report["suggested_base_y"], 150)
        self.assertEqual(report["status"], "PENDENTE")

    def test_invalid_footprint(self):
        with self.assertRaises(ValueError):
            self.planner.plan((2, 0, 0, 0), 150)

    def test_invalid_strategy(self):
        with self.assertRaises(ValueError):
            self.planner.plan((0, 0, 2, 0), 150, "INVALIDA")

    def test_invalid_base_height(self):
        with self.assertRaises(ValueError):
            self.planner.plan((0, 0, 2, 0), 150.5)

    def test_area_limit(self):
        with self.assertRaises(ValueError):
            self.planner.plan((0, 0, 100, 100), 150)

        self.reader.get_height.assert_not_called()

    def test_reader_failure(self):
        reader = Mock()
        reader.get_height.side_effect = ValueError("Data3D inválido")

        with self.assertRaises(ValueError):
            FoundationPlanner(reader).plan((0, 0, 0, 0), 150)


if __name__ == "__main__":
    unittest.main()
