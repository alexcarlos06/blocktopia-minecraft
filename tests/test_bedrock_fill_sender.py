import subprocess
import unittest
from unittest.mock import patch

from scripts.buildings.bedrock_sender import BedrockCommandSender


class TestBedrockFillSender(unittest.TestCase):
    COMMAND = "fill 100 100 100 102 100 102 minecraft:stone"

    def setUp(self):
        self.sender = BedrockCommandSender()

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_requires_confirmation(self, run):
        with self.assertRaises(PermissionError):
            self.sender.send_fill(self.COMMAND)
        run.assert_not_called()

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_valid_fill(self, run):
        run.return_value = subprocess.CompletedProcess(
            [], 0, "", ""
        )

        result = self.sender.send_fill(
            self.COMMAND,
            admin_confirmed=True,
        )

        self.assertEqual(result["status"], "ENVIADO")
        self.assertEqual(result["volume"], 9)
        self.assertFalse(result["confirmed_in_world"])
        run.assert_called_once()

        args = run.call_args.args[0]
        self.assertEqual(args[-1], self.COMMAND)

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_rejects_setblock(self, run):
        with self.assertRaises(ValueError):
            self.sender.send_fill(
                "setblock 0 70 0 minecraft:stone",
                admin_confirmed=True,
            )
        run.assert_not_called()

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_rejects_excessive_volume(self, run):
        with self.assertRaises(ValueError):
            self.sender.send_fill(
                "fill 0 70 0 100 70 400 minecraft:stone",
                admin_confirmed=True,
            )
        run.assert_not_called()

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_docker_failure(self, run):
        run.side_effect = subprocess.CalledProcessError(
            1, ["docker", "exec"], stderr="Falha simulada"
        )

        with self.assertRaises(RuntimeError):
            self.sender.send_fill(
                self.COMMAND,
                admin_confirmed=True,
            )


if __name__ == "__main__":
    unittest.main()
