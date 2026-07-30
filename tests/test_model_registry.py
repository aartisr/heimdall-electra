from __future__ import annotations

from pathlib import Path
import unittest

from heimdall.model_registry import JsonModelRegistry, ModelValidityTier


class ModelRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.registry = JsonModelRegistry(root / "config" / "models" / "model_cards.json")

    def test_fixture_card_declares_limits_and_stable_digest(self) -> None:
        card = self.registry.resolve("illustrative-burst-sine", "0.1.0")
        self.assertEqual(ModelValidityTier.FIXTURE_ONLY, card.validity_tier)
        self.assertTrue(card.excluded_claims)
        self.assertEqual(card.digest, self.registry.resolve("illustrative-burst-sine", "0.1.0").digest)

    def test_missing_model_card_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.registry.resolve("not-registered", "1.0.0")


if __name__ == "__main__":
    unittest.main()

