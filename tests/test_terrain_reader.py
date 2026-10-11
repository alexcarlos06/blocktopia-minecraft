import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.terrain.terrain_reader import TerrainReader


class TestTerrainReader(unittest.TestCase):

    def test_missing_database(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                TerrainReader(directory)

    def test_negative_coordinate_conversion(self):
        self.assertEqual(-180 // 16, -12)
        self.assertEqual(-180 % 16, 12)

    def test_positive_coordinate_conversion(self):
        self.assertEqual(350 // 16, 21)
        self.assertEqual(350 % 16, 14)

    def test_missing_subchunk_returns_none(self):
        reader = TerrainReader.__new__(TerrainReader)
        reader.cache = {}
        reader.db = unittest.mock.Mock()
        reader.db.get.side_effect = KeyError("missing")

        self.assertIsNone(reader._load_subchunk(21, -12, 10))

    def test_unsupported_vertical_index(self):
        reader = TerrainReader.__new__(TerrainReader)
        reader.cache = {}

        with self.assertRaises(ValueError):
            reader._load_subchunk(0, 0, 128)


if __name__ == "__main__":
    unittest.main()
