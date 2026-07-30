from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.replay_protection import JsonMonotonicReplayProtector, SequencePolicy


class ReplayProtectionTests(unittest.TestCase):
    def test_sequence_acceptance_replay_and_gap_limits(self) -> None:
        with TemporaryDirectory() as directory:
            guard = JsonMonotonicReplayProtector(Path(directory) / "state.json", SequencePolicy("policy/1", 2))
            self.assertEqual(0, guard.accept("stream", 4).gap)
            self.assertEqual(1, guard.accept("stream", 6).gap)
            with self.assertRaisesRegex(ValueError, "replayed"):
                guard.accept("stream", 6)
            with self.assertRaisesRegex(ValueError, "gap"):
                guard.accept("stream", 10)

    def test_state_cannot_be_reused_with_another_policy(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            JsonMonotonicReplayProtector(path, SequencePolicy("policy/1", 1)).accept("stream", 1)
            with self.assertRaisesRegex(ValueError, "policy"):
                JsonMonotonicReplayProtector(path, SequencePolicy("policy/2", 1)).accept("stream", 2)


if __name__ == "__main__":
    unittest.main()
