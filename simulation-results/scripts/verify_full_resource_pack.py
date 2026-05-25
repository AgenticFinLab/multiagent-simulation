#!/usr/bin/env python3
"""Verify a full external resource-pack against the tracked manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource-pack", required=True, type=Path)
    parser.add_argument(
        "--manifest",
        default=None,
        type=Path,
        help="Optional file-level manifest CSV for deep checksum validation.",
    )
    args = parser.parse_args()

    if not args.resource_pack.exists():
        print(f"FAIL: resource pack not found: {args.resource_pack}")
        sys.exit(1)

    samples = args.resource_pack / "samples"
    if not samples.exists():
        print("FAIL: missing samples/")
        sys.exit(1)

    modes = ["Rule", "LLM", "RuleLLM", "Rag"]
    scenarios = sorted(p for p in samples.iterdir() if p.is_dir())
    checked_samples = 0
    for scenario in scenarios:
        for mode in modes:
            sample = scenario / mode
            required = [
                sample / "sample.json",
                sample / "source-results.csv",
                sample / "config/simulation.yml",
                sample / "analysis-config/simulation.yml",
                sample / "logs",
                sample / "artifacts/analysis/summary.json",
                sample / "artifacts/records",
                sample / "artifacts/communication",
                sample / "artifacts/monitoring",
            ]
            for path in required:
                if not path.exists():
                    print(f"FAIL: missing {path.relative_to(args.resource_pack)}")
                    sys.exit(1)
            if not list((sample / "artifacts/analysis").glob("*.png")):
                print(f"FAIL: missing analysis PNGs for {scenario.name}__{mode}")
                sys.exit(1)
            if mode == "Rag" and not (
                sample / "artifacts/analysis/rag_stats.json"
            ).exists():
                print(f"FAIL: missing RAG stats for {scenario.name}__{mode}")
                sys.exit(1)
            checked_samples += 1

    if len(scenarios) != 45 or checked_samples != 180:
        print(
            "FAIL: expected 45 scenarios / 180 samples, "
            f"got {len(scenarios)} / {checked_samples}"
        )
        sys.exit(1)

    if args.manifest is not None:
        checked_files = 0
        with args.manifest.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                path = args.resource_pack / row["path"]
                if not path.exists():
                    print(f"FAIL: missing {row['path']}")
                    sys.exit(1)
                if str(path.stat().st_size) != row["bytes"]:
                    print(f"FAIL: size mismatch {row['path']}")
                    sys.exit(1)
                if sha256_file(path) != row["sha256"]:
                    print(f"FAIL: sha256 mismatch {row['path']}")
                    sys.exit(1)
                checked_files += 1
        print(f"full resource-pack verified: {checked_files} files")
    else:
        print("full resource-pack structure verified")
        print(f"  scenarios: {len(scenarios)}")
        print(f"  samples: {checked_samples}")


if __name__ == "__main__":
    main()
