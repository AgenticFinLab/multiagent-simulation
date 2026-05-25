#!/usr/bin/env python3
"""Verify the tracked simulation-results package structure."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODES = ["Rule", "LLM", "RuleLLM", "Rag"]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def main() -> None:
    samples = ROOT / "samples"
    if not samples.exists():
        fail("samples/ is missing")

    scenario_dirs = sorted(p for p in samples.iterdir() if p.is_dir())
    sample_dirs = []
    for scenario in scenario_dirs:
        for mode in MODES:
            sample = scenario / mode
            if not sample.is_dir():
                fail(f"missing sample directory: {sample.relative_to(ROOT)}")
            sample_dirs.append(sample)

            required = [
                sample / "sample.json",
                sample / "source-results.csv",
                sample / "runtime-manifest.json",
                sample / "FULL_ARTIFACTS.md",
                sample / "config/simulation.yml",
                sample / "analysis-config/simulation.yml",
                sample / "artifacts/analysis/summary.json",
            ]
            for path in required:
                if not path.exists():
                    fail(f"missing required file: {path.relative_to(ROOT)}")
            if mode == "Rag" and not (sample / "artifacts/analysis/rag_stats.json").exists():
                fail(f"missing RAG stats: {sample.relative_to(ROOT)}")

    summary_count = len(list(samples.glob("*/*/artifacts/analysis/summary.json")))
    rag_stats_count = len(list(samples.glob("*/Rag/artifacts/analysis/rag_stats.json")))
    manifest_rows = count_rows(ROOT / "MANIFEST.csv")
    success_rows = count_rows(ROOT / "ledgers/success-ledger.csv")
    analysis_rows = count_rows(ROOT / "ledgers/analysis-artifact-ledger.csv")
    validation_overall_rows = count_rows(ROOT / "aggregate/validation-overall.csv")
    validation_criteria_rows = count_rows(ROOT / "aggregate/validation-criteria.csv")
    validation_summary_rows = count_rows(ROOT / "aggregate/validation-summary.csv")
    validation_markdown = ROOT / "aggregate/validation-summary.md"
    if not validation_markdown.exists():
        fail("missing validation summary markdown")

    expected_samples = 180
    checks = {
        "scenarios": len(scenario_dirs),
        "samples": len(sample_dirs),
        "summary_json": summary_count,
        "rag_stats_json": rag_stats_count,
        "manifest_rows": manifest_rows,
        "success_ledger_rows": success_rows,
        "analysis_ledger_rows": analysis_rows,
        "validation_overall_rows": validation_overall_rows,
    }
    expected = {
        "scenarios": 45,
        "samples": expected_samples,
        "summary_json": expected_samples,
        "rag_stats_json": 45,
        "manifest_rows": expected_samples,
        "success_ledger_rows": expected_samples,
        "analysis_ledger_rows": expected_samples,
        "validation_overall_rows": expected_samples,
    }
    for key, value in checks.items():
        if value != expected[key]:
            fail(f"{key}: expected {expected[key]}, got {value}")
    if validation_criteria_rows <= 0:
        fail("validation_criteria_rows: expected at least one criterion row")
    if validation_summary_rows != validation_overall_rows + validation_criteria_rows:
        fail(
            "validation_summary_rows: expected overall + criteria rows, "
            f"got {validation_summary_rows}"
        )

    print("simulation-results package verified")
    for key in sorted(checks):
        print(f"  {key}: {checks[key]}")


if __name__ == "__main__":
    main()
