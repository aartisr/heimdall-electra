from __future__ import annotations

import unittest

from scripts.verify_independence import (
    project_files,
    verify_no_forbidden_references,
    verify_no_symlinks,
    verify_python_imports,
)


class IndependenceTests(unittest.TestCase):
    def test_project_has_no_workspace_links_or_external_runtime_imports(self) -> None:
        paths = project_files()
        failures = verify_no_symlinks()
        failures.extend(verify_no_forbidden_references(paths))
        failures.extend(verify_python_imports(paths))
        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()

