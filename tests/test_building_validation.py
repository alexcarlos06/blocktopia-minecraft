import unittest

from scripts.terrain.building_validation import validate_building_position


class TestBuildingValidation(unittest.TestCase):

    def make_report(self, minimum, maximum, missing=0):
        return {
            "footprint": (98, 198, 102, 202),
            "min_height": minimum,
            "max_height": maximum,
            "missing_positions": missing,
        }

    def test_flat_terrain(self):
        bounds = (98, 150, 198, 102, 160, 202)
        report = self.make_report(150, 150)

        result = validate_building_position(bounds, report)

        self.assertEqual(result["maximum_excavation"], 0)
        self.assertEqual(result["maximum_foundation"], 0)
        self.assertEqual(result["status"], "PENDENTE")

    def test_sloped_terrain(self):
        bounds = (98, 150, 198, 102, 180, 202)
        report = self.make_report(145, 155)

        result = validate_building_position(bounds, report)

        self.assertEqual(result["maximum_excavation"], 5)
        self.assertEqual(result["maximum_foundation"], 5)
        self.assertEqual(result["building_top"], 180)

    def test_incomplete_terrain(self):
        bounds = (98, 150, 198, 102, 180, 202)
        report = self.make_report(145, 155, missing=3)

        result = validate_building_position(bounds, report)

        self.assertEqual(result["status"], "PENDENTE")
        self.assertNotIn("maximum_excavation", result)
        self.assertNotIn("maximum_foundation", result)

    def test_footprint_mismatch(self):
        bounds = (98, 150, 198, 102, 180, 202)
        report = self.make_report(145, 155)
        report["footprint"] = (0, 0, 1, 1)

        with self.assertRaises(ValueError):
            validate_building_position(bounds, report)

    def test_invalid_bounds(self):
        report = self.make_report(145, 155)

        invalid_bounds = [
            None,
            (0, 0, 0),
            (5, 0, 0, 1, 10, 10),
            (0.5, 0, 0, 10, 10, 10),
        ]

        for bounds in invalid_bounds:
            with self.subTest(bounds=bounds):
                with self.assertRaises(ValueError):
                    validate_building_position(bounds, report)


if __name__ == "__main__":
    unittest.main()
