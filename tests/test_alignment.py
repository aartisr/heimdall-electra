from __future__ import annotations

from datetime import datetime, timezone
import unittest

from heimdall.alignment import (
    ContextAlignmentPolicy,
    IsoUtcTimeInterpreter,
    SourceTimeContract,
    TimeBasis,
    align_nearest_context,
)
from heimdall.context import ExternalContextRecord
from heimdall import SyntheticScenario, generate_observation


def context_record(time_tag: str) -> ExternalContextRecord:
    return ExternalContextRecord(
        context_id=f"context-{time_tag}",
        source_id="example-context",
        source_manifest_digest="manifest",
        source_artifact_digest="artifact",
        parser_id="test",
        parser_version="1",
        reported_time_tag=time_tag,
        time_interpretation="test only",
        variable_id="example.variable",
        value=1.0,
        unit="unit",
        provider_qualifier="test",
    )


class ContextAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.observation = generate_observation(SyntheticScenario("aligned", seed=1))
        self.policy = ContextAlignmentPolicy("nearest-context/0.1.0", 60.0)

    def test_refuses_unapproved_time_contract(self) -> None:
        contract = SourceTimeContract(
            "unreviewed", "example-context", TimeBasis.PROVIDER_UNVERIFIED,
            1.0, "no approved authority", False,
        )
        with self.assertRaisesRegex(ValueError, "not approved"):
            align_nearest_context(
                self.observation, (context_record("2026-01-01T00:00:00"),),
                contract, self.policy, IsoUtcTimeInterpreter(),
            )

    def test_aligns_only_with_approved_utc_contract_and_window(self) -> None:
        contract = SourceTimeContract(
            "reviewed-utc", "example-context", TimeBasis.UTC,
            1.0, "test authority", True,
        )
        alignment = align_nearest_context(
            self.observation,
            (context_record("2026-01-01T00:00:20"),),
            contract,
            self.policy,
            IsoUtcTimeInterpreter(),
        )
        self.assertIsNotNone(alignment)
        self.assertEqual(20.0, alignment.time_offset_seconds)
        self.assertEqual(self.observation.observation_id, alignment.observation_id)

    def test_returns_none_when_no_record_is_inside_window(self) -> None:
        contract = SourceTimeContract(
            "reviewed-utc", "example-context", TimeBasis.UTC,
            1.0, "test authority", True,
        )
        result = align_nearest_context(
            self.observation,
            (context_record("2026-01-01T00:02:00"),),
            contract,
            self.policy,
            IsoUtcTimeInterpreter(),
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

