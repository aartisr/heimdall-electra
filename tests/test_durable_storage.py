from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from heimdall.durable_storage import atomic_write_text


class DurableStorageTests(unittest.TestCase):
    def test_atomic_write_replaces_content_without_temporary_artifact(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "bundle.json"
            atomic_write_text(path, "first\n")
            atomic_write_text(path, "second\n")
            self.assertEqual("second\n", path.read_text(encoding="utf-8"))
            self.assertEqual(["bundle.json"], sorted(item.name for item in path.parent.iterdir()))


if __name__ == "__main__":
    unittest.main()
