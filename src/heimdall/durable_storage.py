"""POSIX-safe local durability primitives for research artifacts.

These helpers protect local, cooperating processes from torn or interleaved
writes. They are not a replacement for object-lock retention, managed keys, or
an externally operated evidence service.
"""

from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator

try:  # POSIX is the supported local research runtime for this adapter.
    import fcntl
except ImportError:  # pragma: no cover - platform-specific guard
    fcntl = None  # type: ignore[assignment]


@contextmanager
def exclusive_file_lock(target: Path) -> Iterator[None]:
    """Hold a sidecar advisory lock for one local artifact transaction."""
    if fcntl is None:  # pragma: no cover - exercised only on non-POSIX hosts
        raise RuntimeError("local durable-storage adapter requires POSIX file locking")
    lock_path = target.with_name(target.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def append_durable_line(path: Path, line: str) -> None:
    """Append exactly one newline-terminated JSONL record and request fsync."""
    if not line.endswith("\n"):
        raise ValueError("durable JSONL records must be newline-terminated")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(line)
        stream.flush()
        os.fsync(stream.fileno())


def atomic_write_text(path: Path, content: str) -> None:
    """Atomically replace a text artifact after flushing its replacement file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary_name = stream.name
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)
