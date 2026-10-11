import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.buildings.construction_runner import ConstructionRunner


class TestConstructionFill(unittest.TestCase):
    COMMAND = "fill 100 100 100 102 100 102 minecraft:stone"

    def test_dry_run_does_not_send(self):
        with patch(
            "scripts.buildings.construction_runner.subprocess.run"
        ) as run:
            result = ConstructionRunner().execute(self.COMMAND)
            self.assertEqual(result["status"], "DRY_RUN")
            self.assertFalse(result["sent"])
            run.assert_not_called()

    def test_requires_confirmation(self):
        with patch(
            "scripts.buildings.construction_runner.subprocess.run"
        ) as run:
            with self.assertRaises(PermissionError):
                ConstructionRunner().execute(
                    self.COMMAND,
                    mode="FORCE",
                )
            run.assert_not_called()

    def test_rejects_more_than_64_before_backup(self):
        with patch(
            "scripts.buildings.construction_runner.subprocess.run"
        ) as run:
            with self.assertRaisesRegex(ValueError, "64 blocos"):
                ConstructionRunner().execute(
                    "fill 0 100 0 8 100 8 minecraft:stone",
                    mode="FORCE",
                    admin_confirmed=True,
                )
            run.assert_not_called()

    def execute_mocked(self, verification):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            backup = root / "online-20261011-220000"
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

                verifier.MAX_FILL_VERIFICATION_BLOCKS = 64

                sender.return_value.send_fill.return_value = {
                    "status": "ENVIADO",
                }
                verifier.return_value.verify_fill.return_value = (
                    verification
                )

                result = ConstructionRunner().execute(
                    self.COMMAND,
                    mode="FORCE",
                    admin_confirmed=True,
                )

                backup_run.assert_called_once()
                sender.return_value.send_fill.assert_called_once_with(
                    self.COMMAND,
                    admin_confirmed=True,
                )
                sender.return_value.send_setblock.assert_not_called()
                verifier.return_value.verify_fill.assert_called_once_with(
                    self.COMMAND
                )

                return result

    def test_confirmed_fill(self):
        result = self.execute_mocked({
            "status": "CONFIRMADO",
            "confirmed_blocks": 9,
            "total_blocks": 9,
        })

        self.assertEqual(result["status"], "ENVIADO")
        self.assertEqual(result["verification_status"], "CONFIRMADO")
        self.assertTrue(result["confirmed_in_world"])

    def test_indeterminate_fill(self):
        result = self.execute_mocked({
            "status": "INDETERMINADO",
            "confirmed_blocks": 8,
            "indeterminate_blocks": 1,
        })

        self.assertEqual(
            result["verification_status"], "INDETERMINADO"
        )
        self.assertFalse(result["confirmed_in_world"])

    def test_divergent_fill(self):
        result = self.execute_mocked({
            "status": "DIVERGENTE",
            "confirmed_blocks": 8,
            "divergent_blocks": 1,
        })

        self.assertEqual(
            result["verification_status"], "DIVERGENTE"
        )
        self.assertFalse(result["confirmed_in_world"])


if __name__ == "__main__":
    unittest.main()
