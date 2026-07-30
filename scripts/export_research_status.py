"""Export a provenance-aware snapshot for the read-only TanStack console."""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

from heimdall.status_snapshot import build_snapshot


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at", type=str)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    generated_at = datetime.fromisoformat(args.generated_at.replace("Z", "+00:00")) if args.generated_at else None
    snapshot = build_snapshot(root, generated_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(snapshot.to_ui_json(), encoding="utf-8")


if __name__ == "__main__":
    main()

