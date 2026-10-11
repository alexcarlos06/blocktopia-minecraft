import unittest

from scripts.buildings.authorization import (
    ExecutionMode,
    authorize_building,
)


class TestBuildingAuthorization(unittest.TestCase):

    def make_validation(self, blockers=None):
        return {
            "status": "PENDENTE",
            "execution_allowed": False,
            "bounds": (100, 70, 100, 110, 80, 110),
            "blockers": (
                ["VOLUME_OCUPADO"]
                if blockers is None else blockers
            ),
        }

    def test_dry_run(self):
        result = authorize_building(self.make_validation())
        self.assertFalse(result["authorized"])
        self.assertEqual(result["mode"], "DRY_RUN")

    def test_strict_pending(self):
        result = authorize_building(
            self.make_validation(),
            mode="STRICT",
        )
        self.assertFalse(result["authorized"])

    def test_strict_approved(self):
        validation = self.make_validation([])
        validation["status"] = "APROVADO"
        validation["execution_allowed"] = True

        result = authorize_building(validation, mode="STRICT")
        self.assertTrue(result["authorized"])

    def test_force_known_conflict(self):
        result = authorize_building(
            self.make_validation(),
            mode="FORCE",
            admin_confirmed=True,
        )
        self.assertTrue(result["authorized"])

    def test_force_unknown_terrain(self):
        validation = self.make_validation([
            "ALTURAS_AUSENTES",
            "VOLUME_INCOMPLETO",
        ])

        result = authorize_building(
            validation,
            mode="FORCE",
            admin_confirmed=True,
        )

        self.assertTrue(result["authorized"])
        self.assertEqual(len(result["blockers"]), 2)

    def test_force_without_confirmation(self):
        result = authorize_building(
            self.make_validation(),
            mode="FORCE",
        )
        self.assertFalse(result["authorized"])

    def test_force_unknown_blocker(self):
        result = authorize_building(
            self.make_validation(["RISCO_NAO_CLASSIFICADO"]),
            mode="FORCE",
            admin_confirmed=True,
        )
        self.assertTrue(result["authorized"])

    def test_invalid_bounds(self):
        validation = self.make_validation()
        validation["bounds"] = (10, 70, 10, 5, 80, 20)

        with self.assertRaises(ValueError):
            authorize_building(
                validation, mode="FORCE", admin_confirmed=True
            )

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            authorize_building(
                self.make_validation(), mode="INVALIDO"
            )

    def test_invalid_confirmation(self):
        with self.assertRaises(ValueError):
            authorize_building(
                self.make_validation(),
                mode="FORCE",
                admin_confirmed="sim",
            )


if __name__ == "__main__":
    unittest.main()
