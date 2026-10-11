import json
import tempfile
import unittest
from pathlib import Path

from scripts.buildings.location_registry import LocationRegistry


class TestLocationRegistry(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "locations.json"
        self.path.write_text(
            json.dumps({"version": 1, "locations": {}}),
            encoding="utf-8",
        )
        self.registry = LocationRegistry(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_register_and_resolve_reference(self):
        location = self.registry.register(
            "acampamento_inicial",
            name="Acampamento do Henry",
            x=100,
            y=140,
            z=-200,
        )

        self.assertEqual(location["status"], "CONFIRMADO")
        self.assertEqual(
            self.registry.reference("acampamento_inicial"),
            (100, -200),
        )

    def test_reject_duplicate(self):
        arguments = dict(
            name="Acampamento",
            x=100,
            y=140,
            z=-200,
        )

        self.registry.register("acampamento_inicial", **arguments)

        with self.assertRaises(ValueError):
            self.registry.register(
                "acampamento_inicial", **arguments
            )

    def test_unknown_reference(self):
        with self.assertRaises(KeyError):
            self.registry.reference("vila_inicial")

    def test_reject_invalid_coordinates(self):
        with self.assertRaises(ValueError):
            self.registry.register(
                "acampamento_inicial",
                name="Acampamento",
                x=100,
                y=400,
                z=-200,
            )

    def test_reject_invalid_identifier(self):
        with self.assertRaises(ValueError):
            self.registry.register(
                "../local",
                name="Invalido",
                x=100,
                y=140,
                z=-200,
            )


if __name__ == "__main__":
    unittest.main()
