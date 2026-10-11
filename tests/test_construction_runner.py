import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.buildings.construction_runner import (
    ConstructionRunner,
)


class TestConstructionRunner(unittest.TestCase):

    def setUp(self):
        self.runner = ConstructionRunner()
        self.command = "setblock 350 150 -180 minecraft:stone"

    @patch(
        "scripts.buildings.construction_runner.subprocess.run"
    )
    def test_dry_run_does_not_execute(self, run):
        result = self.runner.execute(self.command)

        self.assertEqual(result["status"], "DRY_RUN")
        self.assertFalse(result["sent"])
        run.assert_not_called()

    @patch(
        "scripts.buildings.construction_runner.subprocess.run"
    )
    def test_force_requires_confirmation(self, run):
        with self.assertRaises(PermissionError):
            self.runner.execute(
                self.command,
                mode="FORCE",
            )

        run.assert_not_called()

    @patch(
        "scripts.buildings.construction_runner.subprocess.run"
    )
    @patch(
        "scripts.buildings.construction_runner."
        "BedrockCommandSender"
    )
    def test_backup_failure_blocks_execution(
        self, sender, run
    ):
        run.side_effect = subprocess.CalledProcessError(
            1, ["python", "backup-world.py"],
            stderr="Falha simulada",
        )

        with self.assertRaises(RuntimeError):
            self.runner.execute(
                self.command,
                mode="FORCE",
                admin_confirmed=True,
            )

        sender.assert_not_called()

    @patch(
        "scripts.buildings.construction_runner.subprocess.run"
    )
    @patch(
        "scripts.buildings.construction_runner."
        "BedrockCommandSender"
    )
    def test_successful_backup_before_send(
        self, sender, run
    ):
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

            run.return_value = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=output,
                stderr="",
            )

            sender.return_value.send_setblock.return_value = {
                "status": "ENVIADO",
            }

            with patch.object(
                self.runner, "BACKUP_DIR", root
            ):
                result = self.runner.execute(
                    self.command,
                    mode="FORCE",
                    admin_confirmed=True,
                )

            self.assertTrue(result["sent"])
            self.assertEqual(result["status"], "ENVIADO")
            self.assertFalse(result["confirmed_in_world"])

            run.assert_called_once()
            sender.return_value.send_setblock.assert_called_once_with(
                self.command,
                admin_confirmed=True,
            )


if __name__ == "__main__":
    unittest.main()
