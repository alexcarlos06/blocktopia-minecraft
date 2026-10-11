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
