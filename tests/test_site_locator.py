import unittest

from scripts.buildings.site_locator import SiteLocator


class FakeTerrain:
    def get_height(self, x, z):
        return 100


class MissingTerrain:
    def get_height(self, x, z):
        return None


class TestSiteLocator(unittest.TestCase):

    def test_find_candidates(self):
        locator = SiteLocator(FakeTerrain())
        result = locator.find(
            reference=(0, 0),
            footprint_size=(3, 3),
            min_distance=32,
            max_distance=64,
        )

        self.assertGreater(len(result["candidates"]), 0)

        for site in result["candidates"]:
            self.assertEqual(site["suggested_y"], 101)
            self.assertEqual(site["slope"], 0)
            self.assertFalse(site["execution_allowed"])
            self.assertGreaterEqual(site["distance"], 32)
            self.assertLessEqual(site["distance"], 64)

    def test_missing_heights_are_rejected(self):
        result = SiteLocator(MissingTerrain()).find(
            reference=(0, 0),
            footprint_size=(3, 3),
            min_distance=32,
            max_distance=64,
        )

        self.assertEqual(result["candidates"], [])

    def test_invalid_distance(self):
        with self.assertRaises(ValueError):
            SiteLocator(FakeTerrain()).find(
                reference=(0, 0),
                footprint_size=(3, 3),
                min_distance=200,
                max_distance=100,
            )

    def test_search_does_not_require_exact_building_location(self):
        result = SiteLocator(FakeTerrain()).find(
            reference=(100, -200),
            footprint_size=(5, 5),
            min_distance=50,
            max_distance=100,
        )
        self.assertTrue(result["candidates"])
        self.assertEqual(result["reference"], (100, -200))


if __name__ == "__main__":
    unittest.main()
