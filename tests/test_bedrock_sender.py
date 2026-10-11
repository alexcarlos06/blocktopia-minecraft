import subprocess
import unittest
from unittest.mock import patch

from scripts.buildings.bedrock_sender import BedrockCommandSender


class TestBedrockCommandSender(unittest.TestCase):

    def setUp(self):
        self.sender = BedrockCommandSender()
        self.command = "setblock 350 150 -180 minecraft:stone"

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_requires_confirmation(self, run):
        with self.assertRaises(PermissionError):
            self.sender.send_setblock(self.command)

        run.assert_not_called()

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_valid_setblock(self, run):
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )

        result = self.sender.send_setblock(
            self.command,
            admin_confirmed=True,
        )

        self.assertEqual(result["status"], "ENVIADO")
        self.assertFalse(result["confirmed_in_world"])
        self.assertEqual(result["container"], "blocktopia")

        run.assert_called_once()
        args = run.call_args.args[0]

        self.assertEqual(args[0:2], ["docker", "exec"])
        self.assertIn("blocktopia", args)
        self.assertEqual(args[-1], self.command)

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_rejects_fill(self, run):
        with self.assertRaises(ValueError):
            self.sender.send_setblock(
                "fill 0 70 0 2 70 2 stone",
                admin_confirmed=True,
            )

        run.assert_not_called()

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_rejects_other_commands(self, run):
        with self.assertRaises(ValueError):
            self.sender.send_setblock(
                "op PipiMeme",
                admin_confirmed=True,
            )

        run.assert_not_called()

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_rejects_invalid_height(self, run):
        with self.assertRaises(ValueError):
            self.sender.send_setblock(
                "setblock 0 320 0 stone",
                admin_confirmed=True,
            )

        run.assert_not_called()

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_docker_failure(self, run):
        run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["docker", "exec"],
            stderr="Processo Bedrock inacessível",
        )

        with self.assertRaises(RuntimeError):
            self.sender.send_setblock(
                self.command,
                admin_confirmed=True,
            )

    @patch("scripts.buildings.bedrock_sender.subprocess.run")
    def test_timeout_has_unknown_result(self, run):
        run.side_effect = subprocess.TimeoutExpired(
            cmd=["docker", "exec"],
            timeout=10,
        )

        with self.assertRaisesRegex(
            RuntimeError, "resultado no Bedrock é desconhecido"
        ):
            self.sender.send_setblock(
                self.command,
                admin_confirmed=True,
            )


if __name__ == "__main__":
    unittest.main()
