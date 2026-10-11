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


class TestTerrainHeight(unittest.TestCase):

    def test_get_height(self):
        import struct
        from unittest.mock import Mock

        reader = TerrainReader.__new__(TerrainReader)
        reader.db = Mock()

        data = bytearray(512)

        # Coordenadas X=350, Z=-180:
        # Chunk (21, -12), posição local (14, 12).
        index = 12 * 16 + 14
        struct.pack_into("<H", data, index * 2, 214)

        reader.db.get.return_value = bytes(data)

        self.assertEqual(reader.get_height(350, -180), 149)

        expected_key = struct.pack("<iiB", 21, -12, 0x2B)
        reader.db.get.assert_called_once_with(expected_key)

    def test_missing_heightmap(self):
        from unittest.mock import Mock

        reader = TerrainReader.__new__(TerrainReader)
        reader.db = Mock()
        reader.db.get.side_effect = KeyError("missing")

        self.assertIsNone(reader.get_height(350, -180))

    def test_incomplete_heightmap(self):
        from unittest.mock import Mock

        reader = TerrainReader.__new__(TerrainReader)
        reader.db = Mock()
        reader.db.get.return_value = bytes(100)

        with self.assertRaises(ValueError):
            reader.get_height(350, -180)

    def test_invalid_height_coordinates(self):
        from unittest.mock import Mock

        reader = TerrainReader.__new__(TerrainReader)
        reader.db = Mock()

        with self.assertRaises(ValueError):
            reader.get_height(350.5, -180)
