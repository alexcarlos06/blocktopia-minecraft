import subprocess
import unittest
from unittest.mock import patch

from scripts.buildings.bedrock_verifier import BedrockVerifier


class TestBedrockVerifier(unittest.TestCase):

    def setUp(self):
        self.verifier = BedrockVerifier()
        self.command = "setblock 20 133 -29 minecraft:stone"

    @patch("scripts.buildings.bedrock_verifier.subprocess.run")
    def test_confirmed_block(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess(
                [], 0,
                "[2026-10-11T20:58:34Z] "
                "Successfully found the block at 20,133,-29.\n",
                "",
            ),
        ]

        result = self.verifier.verify_setblock(self.command)

        self.assertEqual(result["status"], "CONFIRMADO")
        self.assertTrue(result["confirmed_in_world"])
        self.assertEqual(run.call_count, 2)

    @patch("scripts.buildings.bedrock_verifier.subprocess.run")
    def test_send_failure_is_indeterminate(self, run):
        run.side_effect = subprocess.CalledProcessError(
            1, ["docker", "exec"], stderr="falha simulada"
        )

        result = self.verifier.verify_setblock(self.command)

        self.assertEqual(result["status"], "INDETERMINADO")
        self.assertFalse(result["confirmed_in_world"])

    @patch("scripts.buildings.bedrock_verifier.subprocess.run")
    def test_rejects_fill(self, run):
        with self.assertRaises(ValueError):
            self.verifier.verify_setblock(
                "fill 0 70 0 2 70 2 minecraft:stone"
            )

        run.assert_not_called()

    @patch("scripts.buildings.bedrock_verifier.subprocess.run")
    def test_does_not_accept_old_unrelated_response(self, run):
        run.side_effect = [
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess(
                [], 0,
                "Successfully found the block at 51,139,-29.\n",
                "",
            ),
        ]

        with patch.object(self.verifier, "TIMEOUT_SECONDS", 0.01):
            result = self.verifier.verify_setblock(self.command)

        self.assertEqual(result["status"], "INDETERMINADO")
        self.assertFalse(result["confirmed_in_world"])


if __name__ == "__main__":
    unittest.main()
