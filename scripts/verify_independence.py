"""Verify that the Heimdall reference implementation remains workspace-independent."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_SUFFIXES = {".py", ".ts", ".tsx", ".css", ".md", ".toml", ".json", ".yaml", ".yml"}
EXCLUDED_PARTS = {".git", "node_modules", "dist", "build", "__pycache__"}
FORBIDDEN = (
    "salus-pramana-medical",
    "/users/rraviku2/aarti/laureate",
    "/users/rraviku2/aarti/salus-pramana-medical",
    "@evidence-platform",
    "evidence-medical-platform",
)
ALLOWED_STDLIB_ROOTS = {
    "__future__", "abc", "argparse", "ast", "dataclasses", "datetime", "enum", "hashlib", "json",
    "concurrent", "contextlib", "fcntl", "io", "itertools", "logging", "math", "os", "pathlib",
    "random", "re", "statistics", "struct", "sys", "tempfile", "threading", "time",
    "typing", "unittest", "urllib", "uuid",
}


def project_files() -> list[Path]:
    return [
        path for path in ROOT.rglob("*")
        if (
            path.is_file()
            and not EXCLUDED_PARTS.intersection(path.parts)
            and "docs" not in path.parts
            and path != Path(__file__).resolve()
            and path.suffix in SCAN_SUFFIXES
        )
    ]


def verify_no_symlinks() -> list[str]:
    return [
        f"symbolic link is prohibited: {path.relative_to(ROOT)}"
        for path in ROOT.rglob("*")
        if path.is_symlink() and not EXCLUDED_PARTS.intersection(path.parts)
    ]


def verify_no_forbidden_references(paths: list[Path]) -> list[str]:
    failures: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN:
            if phrase in text:
                failures.append(f"forbidden workspace reference in {path.relative_to(ROOT)}: {phrase}")
    return failures


def verify_python_imports(paths: list[Path]) -> list[str]:
    failures: list[str] = []
    for path in paths:
        if path.suffix != ".py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root not in ALLOWED_STDLIB_ROOTS and root not in {"heimdall", "scripts"}:
                        failures.append(f"non-standard import in {path.relative_to(ROOT)}: {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                root = node.module.split(".")[0]
                # tests/ may import from scripts/ by dynamic sys.path injection
                in_tests = "tests" in path.parts
                if root not in ALLOWED_STDLIB_ROOTS and root not in {"heimdall", "scripts"} and not in_tests:
                    failures.append(f"non-standard import in {path.relative_to(ROOT)}: {node.module}")
    return failures


def main() -> int:
    paths = project_files()
    failures = verify_no_symlinks()
    failures.extend(verify_no_forbidden_references(paths))
    failures.extend(verify_python_imports(paths))
    if failures:
        print("Independence verification failed:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print(f"Independence verification passed for {len(paths)} project files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
