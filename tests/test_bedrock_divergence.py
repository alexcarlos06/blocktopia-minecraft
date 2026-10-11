import subprocess
import unittest
from unittest.mock import patch

from scripts.buildings.bedrock_verifier import BedrockVerifier


class TestBedrockDivergence(unittest.TestCase):

    def check(self, message, command):
        responses = [
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess([], 0, message, ""),
        ]

        with patch(
            "scripts.buildings.bedrock_verifier.subprocess.run",
            side_effect=responses,
        ):
            return BedrockVerifier().verify_setblock(command)

    def test_stone_instead_of_air(self):
        result = self.check(
            "[INFO] The block at 23,133,-29 "
            "is Stone (expected: Air).\n",
            "setblock 23 133 -29 minecraft:air",
        )

        self.assertEqual(result["status"], "DIVERGENTE")
        self.assertEqual(result["found_block"], "Stone")
        self.assertEqual(result["expected_block"], "Air")
        self.assertFalse(result["confirmed_in_world"])

    def test_grass_instead_of_air(self):
        result = self.check(
            "[ERROR] The block at 24,134,-29 "
            "is Grass Block (expected: Air).\n",
            "setblock 24 134 -29 minecraft:air",
        )

        self.assertEqual(result["status"], "DIVERGENTE")
        self.assertEqual(result["found_block"], "Grass Block")

    def test_success_remains_confirmed(self):
        result = self.check(
            "[INFO] Successfully found the block at 23,133,-28.\n",
            "setblock 23 133 -28 minecraft:stone",
        )

        self.assertEqual(result["status"], "CONFIRMADO")
        self.assertTrue(result["confirmed_in_world"])


if __name__ == "__main__":
    unittest.main()
