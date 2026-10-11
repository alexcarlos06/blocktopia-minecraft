import unittest
from unittest.mock import patch

from scripts.buildings.bedrock_verifier import BedrockVerifier


class TestBedrockFillVerifier(unittest.TestCase):
    COMMAND = "fill 100 100 100 102 100 102 minecraft:stone"

    def setUp(self):
        self.verifier = BedrockVerifier()

    @patch.object(BedrockVerifier, "verify_setblock")
    def test_all_nine_blocks_confirmed(self, verify):
        verify.return_value = {"status": "CONFIRMADO"}

        result = self.verifier.verify_fill(self.COMMAND)

        self.assertEqual(result["status"], "CONFIRMADO")
        self.assertEqual(result["total_blocks"], 9)
        self.assertEqual(result["confirmed_blocks"], 9)
        self.assertTrue(result["confirmed_in_world"])
        self.assertEqual(verify.call_count, 9)

    @patch.object(BedrockVerifier, "verify_setblock")
    def test_one_divergent_block(self, verify):
        verify.side_effect = (
            [{"status": "CONFIRMADO"}] * 8
            + [{"status": "DIVERGENTE"}]
        )

        result = self.verifier.verify_fill(self.COMMAND)

        self.assertEqual(result["status"], "DIVERGENTE")
        self.assertEqual(result["divergent_blocks"], 1)
        self.assertFalse(result["confirmed_in_world"])

    @patch.object(BedrockVerifier, "verify_setblock")
    def test_one_indeterminate_block(self, verify):
        verify.side_effect = (
            [{"status": "CONFIRMADO"}] * 8
            + [{"status": "INDETERMINADO"}]
        )

        result = self.verifier.verify_fill(self.COMMAND)

        self.assertEqual(result["status"], "INDETERMINADO")
        self.assertEqual(result["indeterminate_blocks"], 1)
        self.assertFalse(result["confirmed_in_world"])

    @patch.object(BedrockVerifier, "verify_setblock")
    def test_rejects_large_structure(self, verify):
        with self.assertRaisesRegex(ValueError, "64 blocos"):
            self.verifier.verify_fill(
                "fill 0 100 0 8 100 8 minecraft:stone"
            )

        verify.assert_not_called()

    @patch.object(BedrockVerifier, "verify_setblock")
    def test_rejects_setblock(self, verify):
        with self.assertRaises(ValueError):
            self.verifier.verify_fill(
                "setblock 0 100 0 minecraft:stone"
            )

        verify.assert_not_called()

    @patch.object(BedrockVerifier, "verify_setblock")
    def test_reversed_coordinates(self, verify):
        verify.return_value = {"status": "CONFIRMADO"}

        result = self.verifier.verify_fill(
            "fill 102 100 102 100 100 100 minecraft:stone"
        )

        self.assertEqual(result["confirmed_blocks"], 9)
        self.assertEqual(verify.call_count, 9)


if __name__ == "__main__":
    unittest.main()
