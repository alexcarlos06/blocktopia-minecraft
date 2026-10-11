import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from buildings.engine import BuildingEngine


class TestBuildingEngine(unittest.TestCase):

    def test_setblock(self):
        engine = BuildingEngine(100, 70, 200)
        engine.block(1, 2, 3, "stone")

        self.assertEqual(
            engine.commands[0],
            "setblock 101 72 203 minecraft:stone"
        )

    def test_fill(self):
        engine = BuildingEngine(100, 70, 200)
        engine.fill(0, 0, 0, 4, 0, 4, "oak_planks")

        self.assertEqual(
            engine.commands[0],
            "fill 100 70 200 104 70 204 minecraft:oak_planks"
        )

    def test_fill_limit(self):
        engine = BuildingEngine(0, 70, 0)

        with self.assertRaises(ValueError):
            engine.fill(
                0, 0, 0,
                100, 100, 100,
                "stone"
            )

    def test_invalid_material(self):
        engine = BuildingEngine(0, 70, 0)

        with self.assertRaises(ValueError):
            engine.block(0, 0, 0, "stone; say invalid")

    def test_negative_coordinates(self):
        engine = BuildingEngine(350, 65, -180)
        engine.block(-5, 1, 9, "glowstone")

        self.assertEqual(
            engine.commands[0],
            "setblock 345 66 -171 minecraft:glowstone"
        )


if __name__ == "__main__":
    unittest.main()


class TestBuildingDimensions(unittest.TestCase):

    def test_empty_building(self):
        engine = BuildingEngine(100, 70, 200)

        self.assertIsNone(engine.bounds)
        self.assertIsNone(engine.dimensions)
        self.assertIsNone(engine.footprint)

    def test_fill_and_block_bounds(self):
        engine = BuildingEngine(100, 70, 200)

        engine.fill(-5, 0, -5, 5, 3, 5, "stone")
        engine.block(0, 8, 0, "torch")

        self.assertEqual(
            engine.bounds,
            (95, 70, 195, 105, 78, 205)
        )

        self.assertEqual(
            engine.dimensions,
            (11, 9, 11)
        )

        self.assertEqual(
            engine.footprint,
            (95, 195, 105, 205)
        )

    def test_reversed_fill_coordinates(self):
        engine = BuildingEngine(0, 64, 0)

        engine.fill(5, 3, 5, -5, 0, -5, "stone")

        self.assertEqual(
            engine.bounds,
            (-5, 64, -5, 5, 67, 5)
        )
