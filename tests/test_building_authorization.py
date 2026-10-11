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
            "blockers": blockers if blockers is not None else [
                "VOLUME_OCUPADO",
                "CRITERIOS_DE_APROVACAO_PENDENTES",
            ],
        }

    def authorize(self, validation):
        return authorize_building(
            validation,
            mode=ExecutionMode.MANUAL_OVERRIDE,
            admin_confirmed=True,
            reason="Autorizo a construção com conflitos conhecidos",
        )

    def test_dry_run_never_authorizes(self):
        result = authorize_building(
            self.make_validation(),
            mode=ExecutionMode.DRY_RUN,
        )
        self.assertFalse(result["authorized"])

    def test_strict_blocks_pending(self):
        result = authorize_building(
            self.make_validation(),
            mode=ExecutionMode.STRICT,
        )
        self.assertFalse(result["authorized"])

    def test_manual_override_known_conflict(self):
        result = self.authorize(self.make_validation())
        self.assertTrue(result["authorized"])
        self.assertEqual(
            result["authorization_type"],
            "ADMINISTRATIVE_OVERRIDE",
        )

    def test_manual_override_requires_confirmation(self):
        result = authorize_building(
            self.make_validation(),
            mode=ExecutionMode.MANUAL_OVERRIDE,
            admin_confirmed=False,
            reason="Autorizo",
        )
        self.assertFalse(result["authorized"])

    def test_manual_override_requires_reason(self):
        result = authorize_building(
            self.make_validation(),
            mode=ExecutionMode.MANUAL_OVERRIDE,
            admin_confirmed=True,
            reason="  ",
        )
        self.assertFalse(result["authorized"])

    def test_missing_data_blocks_override(self):
        for blocker in (
            "ALTURAS_AUSENTES",
            "MATERIAIS_ILEGIVEIS",
            "DADOS_SUPERIORES_AUSENTES",
            "VOLUME_INCOMPLETO",
        ):
            with self.subTest(blocker=blocker):
                result = self.authorize(
                    self.make_validation([blocker])
                )
                self.assertFalse(result["authorized"])

    def test_unrecognized_blocker_denied(self):
        result = self.authorize(
            self.make_validation(["RISCO_NAO_CLASSIFICADO"])
        )
        self.assertFalse(result["authorized"])

    def test_missing_bounds_denied(self):
        validation = self.make_validation()
        validation["bounds"] = None

        result = self.authorize(validation)
        self.assertFalse(result["authorized"])


if __name__ == "__main__":
    unittest.main()
