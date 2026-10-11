import unittest

from scripts.terrain.materials import (
    MaterialCategory,
    classify_material,
)


class TestTerrainMaterials(unittest.TestCase):

    def test_ground(self):
        self.assertEqual(
            classify_material("minecraft:grass_block"),
            MaterialCategory.GROUND,
        )

    def test_liquids(self):
        for material in ("minecraft:water", "minecraft:lava"):
            with self.subTest(material=material):
                self.assertEqual(
                    classify_material(material),
                    MaterialCategory.LIQUID,
                )

    def test_vegetation(self):
        self.assertEqual(
            classify_material("minecraft:cornflower"),
            MaterialCategory.VEGETATION,
        )

    def test_snow_layer(self):
        self.assertEqual(
            classify_material("minecraft:snow_layer"),
            MaterialCategory.SNOW_LAYER,
        )

    def test_air(self):
        self.assertEqual(
            classify_material("minecraft:air"),
            MaterialCategory.AIR,
        )

    def test_unknown_material(self):
        self.assertEqual(
            classify_material("minecraft:unlisted_block"),
            MaterialCategory.UNKNOWN,
        )

    def test_missing_material(self):
        self.assertEqual(
            classify_material(None),
            MaterialCategory.UNKNOWN,
        )


if __name__ == "__main__":
    unittest.main()
