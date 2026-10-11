import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.buildings.construction_runner import ConstructionRunner


class TestConstructionVerification(unittest.TestCase):
    COMMAND = "setblock 20 133 -29 minecraft:stone"

    def execute_with_verification(self, response=None, error=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            backup = root / "online-20261011-210000"
            world = backup / "worlds" / "Blocktopia"
            (world / "db").mkdir(parents=True)

            for name in (
                "level.dat",
                "levelname.txt",
                "db/CURRENT",
            ):
                (world / name).write_bytes(b"test")

            output = (
                f"BACKUP CONCLUÍDO: {backup}\n"
                "Salvamento do mundo retomado.\n"
            )

            with (
                patch.object(ConstructionRunner, "BACKUP_DIR", root),
                patch(
                    "scripts.buildings.construction_runner.subprocess.run"
                ) as backup_run,
                patch(
                    "scripts.buildings.construction_runner."
                    "BedrockCommandSender"
                ) as sender,
                patch(
                    "scripts.buildings.construction_runner."
                    "BedrockVerifier"
                ) as verifier,
            ):
                backup_run.return_value = subprocess.CompletedProcess(
                    [], 0, output, ""
                )
                sender.return_value.send_setblock.return_value = {
                    "status": "ENVIADO",
                }

                if error:
                    verifier.return_value.verify_setblock.side_effect = error
                else:
                    verifier.return_value.verify_setblock.return_value = response

                result = ConstructionRunner().execute(
                    self.COMMAND,
                    mode="FORCE",
                    admin_confirmed=True,
                )

                backup_run.assert_called_once()
                sender.return_value.send_setblock.assert_called_once()
                verifier.return_value.verify_setblock.assert_called_once_with(
                    self.COMMAND
                )

                return result

    def test_confirmado(self):
        result = self.execute_with_verification({
            "status": "CONFIRMADO",
            "message": "Bloco encontrado",
        })
        self.assertEqual(result["status"], "ENVIADO")
        self.assertEqual(result["verification_status"], "CONFIRMADO")
        self.assertTrue(result["confirmed_in_world"])

    def test_divergente(self):
        result = self.execute_with_verification({
            "status": "DIVERGENTE",
            "message": "Bloco diferente",
        })
        self.assertEqual(result["verification_status"], "DIVERGENTE")
        self.assertFalse(result["confirmed_in_world"])

    def test_indeterminado(self):
        result = self.execute_with_verification({
            "status": "INDETERMINADO",
            "message": "Consulta sem resposta",
        })
        self.assertEqual(result["verification_status"], "INDETERMINADO")
        self.assertFalse(result["confirmed_in_world"])

    def test_falha_na_verificacao(self):
        result = self.execute_with_verification(
            error=RuntimeError("Falha simulada")
        )
        self.assertEqual(result["status"], "ENVIADO")
        self.assertEqual(result["verification_status"], "INDETERMINADO")
        self.assertFalse(result["confirmed_in_world"])


if __name__ == "__main__":
    unittest.main()
