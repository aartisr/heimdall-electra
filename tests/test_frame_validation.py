from __future__ import annotations

from dataclasses import dataclass
import unittest

from heimdall.frame_validation import FramePayloadPolicy, PolicyFramePayloadValidator


@dataclass(frozen=True)
class Frame:
    schema_id: str
    media_type: str
    payload: bytes


class FrameValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = PolicyFramePayloadValidator(FramePayloadPolicy("payload/1", ("frame/1",), ("application/octet-stream",), 4))

    def test_accepts_only_configured_envelope(self) -> None:
        self.assertEqual("payload/1", self.validator.validate(Frame("frame/1", "application/octet-stream", b"1234")))

    def test_rejects_schema_media_type_and_size_violations(self) -> None:
        with self.assertRaisesRegex(ValueError, "schema"):
            self.validator.validate(Frame("other", "application/octet-stream", b"1"))
        with self.assertRaisesRegex(ValueError, "media type"):
            self.validator.validate(Frame("frame/1", "text/plain", b"1"))
        with self.assertRaisesRegex(ValueError, "byte limit"):
            self.validator.validate(Frame("frame/1", "application/octet-stream", b"12345"))


if __name__ == "__main__":
    unittest.main()
