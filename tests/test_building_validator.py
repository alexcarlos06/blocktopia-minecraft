import unittest
from unittest.mock import Mock

from scripts.buildings.engine import BuildingEngine
from scripts.buildings.validator import BuildingValidator


class TestBuildingValidator(unittest.TestCase):

    def make_building(self):
        building = BuildingEngine(100, 70, 200)
        building.block(0, 0, 0, "stone")
        return building

    def make_reader(self, ground=70, block="minecraft:air"):
        reader = Mock()
        reader.get_height.return_value = ground
        reader.get_block.return_value = block
        return reader

    def test_empty_building(self):
        reader = self.make_reader()
        building = BuildingEngine(100, 70, 200)

        with self.assertRaises(ValueError):
            BuildingValidator(reader).validate(building)

        reader.get_height.assert_not_called()

    def test_occupied_volume_blocks_execution(self):
        reader = self.make_reader(block="minecraft:stone")

        report = BuildingValidator(reader).validate(
            self.make_building()
        )

        self.assertIn("VOLUME_OCUPADO", report["blockers"])
        self.assertFalse(report["execution_allowed"])
        self.assertEqual(report["status"], "PENDENTE")

    def test_empty_volume_still_not_approved(self):
        reader = self.make_reader()

        report = BuildingValidator(reader).validate(
            self.make_building()
        )

        self.assertEqual(report["volume"]["occupied_blocks"], 0)
        self.assertFalse(report["execution_allowed"])
        self.assertIn(
            "CRITERIOS_DE_APROVACAO_PENDENTES",
            report["blockers"],
        )

    def test_missing_height_blocks_execution(self):
        reader = self.make_reader(ground=None)

        report = BuildingValidator(reader).validate(
            self.make_building()
        )

        self.assertIn("ALTURAS_AUSENTES", report["blockers"])
        self.assertFalse(report["execution_allowed"])

    def test_missing_volume_blocks_execution(self):
        reader = self.make_reader(block=None)

        report = BuildingValidator(reader).validate(
            self.make_building()
        )

        self.assertIn("VOLUME_INCOMPLETO", report["blockers"])
        self.assertFalse(report["execution_allowed"])

    def test_reader_error_is_not_ignored(self):
        reader = self.make_reader()
        reader.get_height.side_effect = ValueError(
            "Data3D incompleto"
        )

        with self.assertRaises(ValueError):
            BuildingValidator(reader).validate(
                self.make_building()
            )

    def test_invalid_inspection_height(self):
        reader = self.make_reader()

        with self.assertRaises(ValueError):
            BuildingValidator(reader, inspection_height=0)


if __name__ == "__main__":
    unittest.main()
