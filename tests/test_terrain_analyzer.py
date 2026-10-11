import unittest
from unittest.mock import Mock

from scripts.buildings.engine import BuildingEngine
from scripts.terrain.analyzer import TerrainAnalyzer


class TestTerrainAnalyzer(unittest.TestCase):

    def test_complete_area(self):
        reader = Mock()
        reader.get_block.return_value = "minecraft:grass_block"
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
        reader.get_block.return_value = "minecraft:grass_block"
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
        reader.get_block.return_value = "minecraft:grass_block"
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
        reader.get_block.return_value = "minecraft:grass_block"
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
        reader.get_block.return_value = "minecraft:grass_block"

        with self.assertRaises(ValueError):
            TerrainAnalyzer(reader).analyze((0, 0, 100, 100))

        reader.get_height.assert_not_called()

    def test_reader_error_propagates(self):
        reader = Mock()
        reader.get_block.return_value = "minecraft:grass_block"
        reader.get_height.side_effect = ValueError(
            "Data3D incompleto"
        )

        with self.assertRaises(ValueError):
            TerrainAnalyzer(reader).analyze((0, 0, 1, 1))

    def test_invalid_height(self):
        reader = Mock()
        reader.get_block.return_value = "minecraft:grass_block"
        reader.get_height.return_value = "70"

        with self.assertRaises(ValueError):
            TerrainAnalyzer(reader).analyze((0, 0, 1, 1))


if __name__ == "__main__":
    unittest.main()


class TestTerrainAnalyzerMaterials(unittest.TestCase):

    def test_material_classification(self):
        reader = Mock()
        reader.get_height.return_value = 70

        blocks = {
            (0, 0): "minecraft:grass_block",
            (1, 0): "minecraft:water",
            (0, 1): "minecraft:snow_layer",
            (1, 1): "minecraft:unknown_block",
        }

        reader.get_block.side_effect = (
            lambda x, y, z: blocks[(x, z)]
        )

        report = TerrainAnalyzer(reader).analyze((0, 0, 1, 1))

        self.assertEqual(
            report["material_categories"],
            {
                "SOLO": 1,
                "LIQUIDO": 1,
                "NEVE_SUPERFICIAL": 1,
                "DESCONHECIDO": 1,
            },
        )
        self.assertEqual(
            report["unreadable_material_positions"], 0
        )
        self.assertEqual(report["status"], "PENDENTE")

    def test_missing_material_data(self):
        reader = Mock()
        reader.get_height.return_value = 70
        reader.get_block.return_value = None

        report = TerrainAnalyzer(reader).analyze((0, 0, 0, 0))

        self.assertEqual(
            report["unreadable_material_positions"], 1
        )
        self.assertEqual(report["material_categories"], {})
        self.assertEqual(report["status"], "PENDENTE")


class TestTerrainAnalyzerVertical(unittest.TestCase):

    def make_reader(self, upper_blocks):
        reader = Mock()
        reader.get_height.return_value = 70

        def get_block(x, y, z):
            if y == 70:
                return "minecraft:grass_block"
            return upper_blocks.get(y)

        reader.get_block.side_effect = get_block
        return reader

    def test_vegetation_above_ground(self):
        reader = self.make_reader({
            71: "minecraft:cornflower",
            72: "minecraft:air",
            73: "minecraft:air",
            74: "minecraft:air",
        })

        report = TerrainAnalyzer(reader).analyze((0, 0, 0, 0))

        self.assertEqual(report["overhead_obstacles"], 1)
        self.assertEqual(report["unknown_overhead_positions"], 0)
        self.assertEqual(
            report["overhead_categories"]["VEGETACAO"], 1
        )
        self.assertEqual(report["status"], "PENDENTE")

    def test_water_above_ground(self):
        reader = self.make_reader({
            71: "minecraft:water",
            72: "minecraft:air",
            73: "minecraft:air",
            74: "minecraft:air",
        })

        report = TerrainAnalyzer(reader).analyze((0, 0, 0, 0))

        self.assertEqual(report["overhead_obstacles"], 1)
        self.assertEqual(
            report["overhead_categories"]["LIQUIDO"], 1
        )
        self.assertEqual(report["status"], "PENDENTE")

    def test_missing_upper_subchunk(self):
        reader = self.make_reader({
            71: "minecraft:air",
            72: None,
            73: None,
            74: None,
        })

        report = TerrainAnalyzer(reader).analyze((0, 0, 0, 0))

        self.assertEqual(report["unknown_overhead_positions"], 3)
        self.assertEqual(report["overhead_obstacles"], 0)
        self.assertEqual(report["status"], "PENDENTE")

    def test_clear_column(self):
        reader = self.make_reader({
            71: "minecraft:air",
            72: "minecraft:air",
            73: "minecraft:air",
            74: "minecraft:air",
        })

        report = TerrainAnalyzer(reader).analyze((0, 0, 0, 0))

        self.assertEqual(report["overhead_obstacles"], 0)
        self.assertEqual(report["unknown_overhead_positions"], 0)
        self.assertEqual(report["overhead_categories"]["AR"], 4)
        self.assertEqual(reader.get_block.call_count, 5)

        # Mesmo com a coluna livre, aprovação continua bloqueada.
        self.assertEqual(report["status"], "PENDENTE")

    def test_reader_error_blocks_analysis(self):
        reader = Mock()
        reader.get_height.return_value = 70

        def get_block(x, y, z):
            if y == 70:
                return "minecraft:grass_block"
            raise ValueError("Subchunk não suportado")

        reader.get_block.side_effect = get_block

        with self.assertRaises(ValueError):
            TerrainAnalyzer(reader).analyze((0, 0, 0, 0))


class TestTerrainAnalyzerInspectionHeight(unittest.TestCase):

    def test_custom_inspection_height(self):
        reader = Mock()
        reader.get_height.return_value = 70
        reader.get_block.side_effect = (
            lambda x, y, z:
            "minecraft:grass_block" if y == 70
            else "minecraft:air"
        )

        report = TerrainAnalyzer(
            reader,
            inspection_height=10
        ).analyze((0, 0, 0, 0))

        self.assertEqual(report["overhead_categories"]["AR"], 10)
        self.assertEqual(report["overhead_obstacles"], 0)
        self.assertEqual(report["unknown_overhead_positions"], 0)
        self.assertEqual(reader.get_block.call_count, 11)
        self.assertEqual(report["status"], "PENDENTE")

    def test_default_inspection_height(self):
        reader = Mock()
        reader.get_height.return_value = 70
        reader.get_block.side_effect = (
            lambda x, y, z:
            "minecraft:grass_block" if y == 70
            else "minecraft:air"
        )

        report = TerrainAnalyzer(reader).analyze((0, 0, 0, 0))

        self.assertEqual(report["overhead_categories"]["AR"], 4)
        self.assertEqual(reader.get_block.call_count, 5)

    def test_invalid_inspection_height(self):
        reader = Mock()

        invalid_values = (0, -1, 65, 2.5, True, None)

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    TerrainAnalyzer(
                        reader,
                        inspection_height=value
                    )

        reader.get_height.assert_not_called()
