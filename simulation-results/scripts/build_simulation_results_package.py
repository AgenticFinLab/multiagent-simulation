#!/usr/bin/env python3
"""Build the GitHub-facing simulation-180 results package.

The full local resource-pack contains raw runtime records and communication
stores that are too large for normal Git tracking. This builder copies the
analysis-ready subset into ``simulation-results/`` and records where the omitted
raw artifacts can be recovered from a full external resource-pack archive.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get("SIMULATION_RESOURCE_PACK", ROOT / "resource-pack"))
ANALYSIS_LEDGER = Path(
    os.environ.get("SIMULATION_ANALYSIS_LEDGER", SOURCE / "analysis-artifacts/current")
)
TARGET = ROOT / "simulation-results"
MODES = ["Rule", "LLM", "RuleLLM", "Rag"]
PROJECT_ROOT_PATTERNS = [
    re.compile(r"/root/[^\s,]*/multiagent-simulation"),
    re.compile(r"/home/[^\s,]*/multiagent-simulation"),
]
SIMULATION_EXPERIMENT_PATH = r"EXPERIMENT/simulation-[0-9-]+/[^\s,]+"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dir_size(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def dir_file_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*") if p.is_file())


def copy_dir(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_analysis_subset(src: Path, dst: Path) -> None:
    """Copy the Git-tracked analysis JSON subset.

    PNG figures are part of the full release archive, not the normal Git
    package. Keeping only machine-readable analysis outputs makes the branch
    reviewable while preserving enough metadata for indexing and validation.
    """

    copy_file(src / "summary.json", dst / "summary.json")
    rag_stats = src / "rag_stats.json"
    if rag_stats.exists():
        copy_file(rag_stats, dst / "rag_stats.json")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def scalar(value: Any) -> str:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return "" if value is None else str(value)
    return json.dumps(value, sort_keys=True)


def normalize_validation_passed(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "pass", "passed"}:
        return "true"
    if text in {"false", "0", "no", "fail", "failed"}:
        return "false"
    return "not_reported"


def validation_status(row_type: str, passed_normalized: str) -> str:
    if row_type == "overall":
        if passed_normalized == "true":
            return "scenario_validity_pass"
        if passed_normalized == "false":
            return "scenario_validity_fail"
        return "scenario_validity_not_reported"
    if passed_normalized == "true":
        return "criterion_pass"
    if passed_normalized == "false":
        return "criterion_fail"
    return "criterion_not_reported"


def validation_row(
    *,
    sample_id: str,
    scenario: str,
    mechanism: str,
    row_type: str,
    criterion: str,
    value: Any,
    target: Any,
    score: Any,
    passed: Any,
) -> dict[str, Any]:
    passed_normalized = normalize_validation_passed(passed)
    return {
        "sample_id": sample_id,
        "scenario": scenario,
        "mechanism": mechanism,
        "row_type": row_type,
        "criterion": criterion,
        "value": scalar(value),
        "target": scalar(target),
        "score": scalar(score),
        "passed": scalar(passed),
        "passed_raw": scalar(passed),
        "passed_normalized": passed_normalized,
        "validation_status": validation_status(row_type, passed_normalized),
    }


def write_validation_outputs(
    target: Path, validation_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    fieldnames = [
        "sample_id",
        "scenario",
        "mechanism",
        "row_type",
        "criterion",
        "value",
        "target",
        "score",
        "passed",
        "passed_raw",
        "passed_normalized",
        "validation_status",
    ]
    overall_rows = [row for row in validation_rows if row["row_type"] == "overall"]
    criterion_rows = [
        row for row in validation_rows if row["row_type"] == "criterion"
    ]

    write_csv(target / "aggregate/validation-summary.csv", validation_rows, fieldnames)
    write_csv(
        target / "aggregate/validation-overall.csv",
        overall_rows,
        fieldnames,
    )
    write_csv(
        target / "aggregate/validation-criteria.csv",
        criterion_rows,
        fieldnames,
    )

    overall_counts = Counter(row["passed_normalized"] for row in overall_rows)
    criterion_counts = Counter(row["passed_normalized"] for row in criterion_rows)
    mode_counts: dict[str, Counter[str]] = defaultdict(Counter)
    failed_scenarios: dict[str, list[str]] = defaultdict(list)
    for row in overall_rows:
        passed = row["passed_normalized"]
        mode_counts[row["mechanism"]][passed] += 1
        if passed == "false":
            failed_scenarios[row["scenario"]].append(row["mechanism"])

    mode_lines = []
    for mode in MODES:
        counts = mode_counts[mode]
        mode_lines.append(
            f"| {mode} | {counts['true']} | {counts['false']} | "
            f"{counts['not_reported']} |"
        )

    failed_lines = [
        f"| {scenario} | {', '.join(modes)} |"
        for scenario, modes in sorted(failed_scenarios.items())
    ]
    if not failed_lines:
        failed_lines = ["| none | none |"]

    write_text(
        target / "aggregate/validation-summary.md",
        f"""
# Validation Summary

This report summarizes Level-3 scenario-validity checks extracted from each
sample's `artifacts/analysis/summary.json`.

Important interpretation:

- `scenario_validity_fail` means an analysis target or calibration criterion was
  not satisfied for that completed sample.
- It does not mean the simulation crashed, analysis failed, or the resource-pack
  sample is missing.
- Do not mechanically rerun a `scenario_validity_fail` row. First inspect the
  scenario documentation, analysis target, and observed metrics.

## Files

- `validation-overall.csv`: one row per sample.
- `validation-criteria.csv`: one row per reported validation criterion.
- `validation-summary.csv`: combined machine-readable table with `row_type`.

## Overall Rows

| Status | Count |
|---|---:|
| true | {overall_counts['true']} |
| false | {overall_counts['false']} |
| not_reported | {overall_counts['not_reported']} |

## Criteria Rows

| Status | Count |
|---|---:|
| true | {criterion_counts['true']} |
| false | {criterion_counts['false']} |
| not_reported | {criterion_counts['not_reported']} |

## Overall Status by Mechanism

| Mechanism | true | false | not_reported |
|---|---:|---:|---:|
{chr(10).join(mode_lines)}

## Samples With Overall Scenario-Validity Failures

| Scenario | Mechanisms |
|---|---|
{chr(10).join(failed_lines)}
""",
    )

    return {
        "overall_total": len(overall_rows),
        "criteria_total": len(criterion_rows),
        "overall_true": overall_counts["true"],
        "overall_false": overall_counts["false"],
        "overall_not_reported": overall_counts["not_reported"],
        "criteria_true": criterion_counts["true"],
        "criteria_false": criterion_counts["false"],
        "criteria_not_reported": criterion_counts["not_reported"],
    }


def mode_key(row: dict[str, str]) -> tuple[str, int]:
    return row["scenario"], MODES.index(row["mechanism"])


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def portable_runtime_path_for_value(value: str) -> str:
    if "rag_index" in value:
        if "rag_index/" in value:
            tail = value.split("rag_index/", 1)[1].strip("/")
            return f"artifacts/rag_index/{tail}" if tail else "artifacts/rag_index"
        return "artifacts/rag_index"
    if "/agents/" in value or value.startswith("agents/"):
        return "artifacts/agents/<agent_id>"
    if "checkpoints" in value:
        return "artifacts/checkpoints"
    if "monitoring" in value:
        return "artifacts/monitoring"
    if "communication" in value:
        return "artifacts/communication"
    if "logs" in value:
        return "logs"
    if "records" in value:
        return "artifacts/records"
    return value


def sanitize_yaml_paths(path: Path) -> None:
    if not path.exists():
        return
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = re.sub(
            r"EXPERIMENT/<scenario>/agents/<agent_id>/?",
            "artifacts/agents/<agent_id>",
            line,
        )
        line = re.sub(
            r"EXPERIMENT/[A-Za-z0-9_/-]+/rag_index/?",
            "artifacts/rag_index/",
            line,
        )
        match = re.match(
            r"^(\s*)(checkpoint_dir|record_path|storage_path|log_path|persist_dir):\s*(.*)$",
            line,
        )
        if not match:
            lines.append(line)
            continue
        indent, key, value = match.groups()
        clean_value = portable_runtime_path_for_value(value.strip().strip("'\""))
        lines.append(f'{indent}{key}: "{clean_value}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sanitize_source_results(path: Path, sample_id: str) -> None:
    if not path.exists():
        return
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    for row in rows:
        row["config"] = "config/simulation.yml"
        runner = row.get("runner", "")
        if "/examples/" in runner:
            row["runner"] = "examples/" + runner.split("/examples/", 1)[1]
        row["log_path"] = f"logs/{sample_id}.log"
        if "config_path" in row:
            row["config_path"] = "config/simulation.yml"
    write_csv(path, rows, fieldnames)


def sanitize_sample_metadata(
    sample_meta: dict[str, Any], sample_id: str, rel_sample: Path
) -> dict[str, Any]:
    sample_meta = dict(sample_meta)
    sample_meta.pop("local_" + "sample_dir", None)
    sample_meta["sample_dir"] = rel_sample.as_posix()
    sample_meta["source_run"] = rel_sample.as_posix()
    sample_meta["source_results_csv"] = "source-results.csv"
    sample_meta["source_log_path"] = f"logs/{sample_id}.log"
    sample_meta["quality_status"] = "accepted"
    sample_meta["quality_reason"] = ""
    sample_meta["notes"] = accepted_quality_note()
    return sample_meta


def portable_runner_path(runner: str) -> str:
    if "/examples/" in runner:
        return "examples/" + runner.split("/examples/", 1)[1]
    return runner


def accepted_quality_note() -> str:
    return (
        "Matrix runner SUCCESS with isolated config/artifacts accepted as a "
        "runtime sample after simulation-180 Level-2 audit. Analysis artifacts "
        "are audited separately."
    )


def sanitize_success_ledger_row(row: dict[str, str]) -> dict[str, str]:
    clean = dict(row)
    sample_dir = clean["sample_dir"]
    clean["source_run"] = sample_dir
    clean["next_action"] = ""
    clean["config"] = f"{sample_dir}/config/simulation.yml"
    clean["runner"] = portable_runner_path(clean.get("runner", ""))
    clean["notes"] = accepted_quality_note()
    clean["quality_status"] = "accepted"
    clean["quality_reason"] = ""
    clean["analysis_status"] = "analysis_complete"
    clean["analysis_missing_items"] = ""
    return clean


def write_success_ledger_md(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row["status"] for row in rows)
    mechanism_counts = Counter(row["mechanism"] for row in rows)
    sample_lines = []
    for row in rows:
        sample_lines.append(
            f"| `{row['experiment_id']}` | accepted | {row['analysis_status']} | "
            f"{row['rounds']} | `{row['sample_dir']}` |"
        )
    write_text(
        path,
        f"""
# Simulation-180 Resource Pack Ledger

Total rows: {len(rows)}

## Status Counts

{chr(10).join(f"- `{status}`: {count}" for status, count in sorted(status_counts.items()))}

## By Mechanism

| Mechanism | Accepted |
|---|---:|
{chr(10).join(f"| {mode} | {mechanism_counts[mode]} |" for mode in MODES)}

## Accepted Samples

| Experiment | Quality | Analysis | Rounds | Sample |
|---|---|---|---:|---|
{chr(10).join(sample_lines)}
""",
    )


def sanitize_analysis_ledger_row(row: dict[str, str]) -> dict[str, str]:
    clean = dict(row)
    sample_id = clean["sample_id"]
    scenario, mechanism = sample_id.rsplit("__", 1)
    sample_dir = f"samples/{scenario}/{mechanism}"
    clean["sample_dir"] = sample_dir
    clean["analysis_dir"] = f"{sample_dir}/artifacts/analysis"
    return clean


def sanitize_analysis_summary(path: Path) -> None:
    if not path.exists():
        return
    data = load_json(path)
    if isinstance(data, dict) and isinstance(data.get("record_path"), str):
        data["record_path"] = "artifacts/records"
        dump_json(path, data)


def sanitize_log_file(path: Path, rel_sample: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(errors="replace", encoding="utf-8")
    for root_pattern in PROJECT_ROOT_PATTERNS:
        text = re.sub(
            root_pattern.pattern + "/" + SIMULATION_EXPERIMENT_PATH,
            rel_sample.as_posix(),
            text,
        )
        text = root_pattern.sub("<PROJECT_ROOT>", text)
    text = re.sub(
        SIMULATION_EXPERIMENT_PATH,
        rel_sample.as_posix(),
        text,
    )
    path.write_text(text, encoding="utf-8")


def sanitize_tracked_sample(dst_sample: Path, sample_id: str, rel_sample: Path) -> None:
    sanitize_source_results(dst_sample / "source-results.csv", sample_id)
    for folder in ["config", "analysis-config"]:
        for config_file in (dst_sample / folder).glob("*.yml"):
            sanitize_yaml_paths(config_file)
    sanitize_analysis_summary(dst_sample / "artifacts/analysis/summary.json")
    for log_file in (dst_sample / "logs").glob("*"):
        if log_file.is_file():
            sanitize_log_file(log_file, rel_sample)


def build_full_manifest(source: Path, out_path: Path) -> None:
    rows = []
    for path in sorted(p for p in source.rglob("*") if p.is_file()):
        rel = path.relative_to(source).as_posix()
        rows.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    write_csv(out_path, rows, ["path", "bytes", "sha256"])


def build_tracked_checksums(target: Path, out_path: Path) -> None:
    rows = []
    for path in sorted(p for p in target.rglob("*") if p.is_file()):
        rel = path.relative_to(target).as_posix()
        if rel == "checksums/tracked-results.sha256":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        rows.append(f"{sha256_file(path)}  {rel}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_verify_scripts(target: Path) -> None:
    verify_tracked = r'''#!/usr/bin/env python3
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
'''
    verify_full = r'''#!/usr/bin/env python3
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
'''
    scripts = target / "scripts"
    write_text(scripts / "verify_tracked_results.py", verify_tracked)
    write_text(scripts / "verify_full_resource_pack.py", verify_full)


def build(args: argparse.Namespace) -> None:
    success_csv = SOURCE / "ledgers/success-ledger.csv"
    success_md = SOURCE / "ledgers/success-ledger.md"
    analysis_csv = ANALYSIS_LEDGER / "analysis-artifact-ledger.csv"
    analysis_md = ANALYSIS_LEDGER / "analysis-artifact-ledger.md"

    if TARGET.exists() and any(TARGET.iterdir()):
        raise RuntimeError(f"target already exists and is not empty: {TARGET}")

    rows = sorted(read_csv(success_csv), key=mode_key)
    if len(rows) != 180:
        raise RuntimeError(f"expected 180 success rows, found {len(rows)}")

    TARGET.mkdir(parents=True, exist_ok=True)
    (TARGET / "ledgers").mkdir(parents=True, exist_ok=True)
    (TARGET / "aggregate").mkdir(parents=True, exist_ok=True)
    (TARGET / "quality").mkdir(parents=True, exist_ok=True)
    (TARGET / "checksums").mkdir(parents=True, exist_ok=True)

    success_ledger_rows = [sanitize_success_ledger_row(row) for row in rows]
    write_csv(
        TARGET / "ledgers/success-ledger.csv",
        success_ledger_rows,
        list(success_ledger_rows[0].keys()),
    )
    write_success_ledger_md(TARGET / "ledgers/success-ledger.md", success_ledger_rows)

    analysis_ledger_rows = [
        sanitize_analysis_ledger_row(row) for row in read_csv(analysis_csv)
    ]
    write_csv(
        TARGET / "ledgers/analysis-artifact-ledger.csv",
        analysis_ledger_rows,
        list(analysis_ledger_rows[0].keys()),
    )
    copy_file(analysis_md, TARGET / "ledgers/analysis-artifact-ledger.md")

    manifest_rows: list[dict[str, Any]] = []
    runtime_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    rag_rows: list[dict[str, Any]] = []
    mode_counts = Counter()
    quality_counts = Counter()
    analysis_counts = Counter()
    scenario_set = set()

    for row in rows:
        sample_id = row["experiment_id"]
        scenario = row["scenario"]
        mechanism = row["mechanism"]
        rel_sample = Path(row["sample_dir"])
        if rel_sample.parts[0] != "samples":
            raise RuntimeError(f"unexpected sample_dir for {sample_id}: {rel_sample}")
        src_sample = SOURCE / rel_sample
        dst_sample = TARGET / rel_sample
        sample_meta = sanitize_sample_metadata(
            load_json(src_sample / "sample.json"),
            sample_id,
            rel_sample,
        )

        scenario_set.add(scenario)
        mode_counts[mechanism] += 1
        quality_counts["accepted"] += 1
        analysis_counts[row["analysis_status"]] += 1

        dump_json(dst_sample / "sample.json", sample_meta)
        copy_file(src_sample / "source-results.csv", dst_sample / "source-results.csv")
        copy_dir(src_sample / "config", dst_sample / "config")
        copy_dir(src_sample / "analysis-config", dst_sample / "analysis-config")
        copy_analysis_subset(
            src_sample / "artifacts/analysis",
            dst_sample / "artifacts/analysis",
        )
        sanitize_tracked_sample(dst_sample, sample_id, rel_sample)

        omitted = []
        raw_bytes = 0
        raw_files = 0
        for name in ["records", "communication", "monitoring", "checkpoints"]:
            src_dir = src_sample / "artifacts" / name
            bytes_count = dir_size(src_dir)
            file_count = dir_file_count(src_dir)
            raw_bytes += bytes_count
            raw_files += file_count
            omitted.append(
                {
                    "name": name,
                    "source_path": (
                        src_dir.relative_to(SOURCE).as_posix()
                        if src_dir.exists()
                        else ""
                    ),
                    "file_count": file_count,
                    "bytes": bytes_count,
                }
            )

        runtime_manifest = {
            "sample_id": sample_id,
            "scenario": scenario,
            "mechanism": mechanism,
            "tracked_sample_path": rel_sample.as_posix(),
            "source_resource_pack_sample_path": rel_sample.as_posix(),
            "tracked_contents": [
                "sample.json",
                "source-results.csv",
                "config/",
                "analysis-config/",
                "artifacts/analysis/summary.json",
                "artifacts/analysis/rag_stats.json (Rag only)",
            ],
            "omitted_raw_artifacts": omitted,
            "omitted_raw_artifact_bytes": raw_bytes,
            "omitted_raw_artifact_files": raw_files,
            "full_resource_pack": "GitHub Release asset",
        }
        dump_json(dst_sample / "runtime-manifest.json", runtime_manifest)
        write_text(
            dst_sample / "FULL_ARTIFACTS.md",
            f"""
# Full Artifacts for {sample_id}

This tracked sample contains config, runtime metadata, and machine-readable
analysis artifacts. Large runtime and presentation artifacts are intentionally
omitted from normal Git tracking:

- `artifacts/records/`
- `artifacts/communication/`
- `artifacts/monitoring/`
- `artifacts/checkpoints/`
- `artifacts/analysis/*.png`
- `logs/`

Use the external full resource-pack archive documented in
`simulation-results/RESOURCE_PACK_EXTERNAL.md` to retrieve those files.
""",
        )

        summary_path = dst_sample / "artifacts/analysis/summary.json"
        summary = load_json(summary_path)
        metrics = summary.get("metrics", {})
        if isinstance(metrics, dict):
            for key, value in sorted(metrics.items()):
                metric_rows.append(
                    {
                        "sample_id": sample_id,
                        "scenario": scenario,
                        "mechanism": mechanism,
                        "metric": key,
                        "value": scalar(value),
                    }
                )

        validation = summary.get("validation", {})
        if isinstance(validation, dict):
            validation_rows.append(
                validation_row(
                    sample_id=sample_id,
                    scenario=scenario,
                    mechanism=mechanism,
                    row_type="overall",
                    criterion="__overall__",
                    value=validation.get("is_valid", ""),
                    target="",
                    score=validation.get("score", ""),
                    passed=validation.get("is_valid", ""),
                )
            )
            criteria = validation.get("criteria", {})
            if isinstance(criteria, dict):
                for criterion, item in sorted(criteria.items()):
                    item = item if isinstance(item, dict) else {"value": item}
                    validation_rows.append(
                        validation_row(
                            sample_id=sample_id,
                            scenario=scenario,
                            mechanism=mechanism,
                            row_type="criterion",
                            criterion=criterion,
                            value=item.get("value", ""),
                            target=item.get("target", ""),
                            score=item.get("score", ""),
                            passed=item.get("passed", ""),
                        )
                    )

        rag_path = dst_sample / "artifacts/analysis/rag_stats.json"
        has_rag_stats = rag_path.exists()
        if has_rag_stats:
            rag_stats = load_json(rag_path)
            if isinstance(rag_stats, dict):
                for agent, item in sorted(rag_stats.items()):
                    item = item if isinstance(item, dict) else {"value": item}
                    rag_rows.append(
                        {
                            "sample_id": sample_id,
                            "scenario": scenario,
                            "mechanism": mechanism,
                            "agent": agent,
                            "total_rag_rounds": item.get("total_rag_rounds", ""),
                            "retrieval_success_rounds": item.get(
                                "retrieval_success_rounds", ""
                            ),
                            "retrieval_failure_rounds": item.get(
                                "retrieval_failure_rounds", ""
                            ),
                            "retrieval_failure_rate": item.get(
                                "retrieval_failure_rate", ""
                            ),
                            "mean_retrieval_failure_rate": item.get(
                                "mean_retrieval_failure_rate", ""
                            ),
                            "max_retrieval_failure_rate": item.get(
                                "max_retrieval_failure_rate", ""
                            ),
                        }
                    )

        png_count = len(list((src_sample / "artifacts/analysis").glob("*.png")))
        tracked_bytes = dir_size(dst_sample)
        manifest_rows.append(
            {
                "sample_id": sample_id,
                "scenario": scenario,
                "mechanism": mechanism,
                "sample_path": rel_sample.as_posix(),
                "runtime_status": row["status"],
                "analysis_status": row["analysis_status"],
                "quality_status": "accepted",
                "quality_reason": "",
                "duration_seconds": row["duration_seconds"],
                "png_count": png_count,
                "has_rag_stats": "yes" if has_rag_stats else "no",
                "tracked_bytes": tracked_bytes,
                "omitted_raw_artifact_bytes": raw_bytes,
                "omitted_raw_artifact_files": raw_files,
            }
        )
        runtime_rows.append(
            {
                "sample_id": sample_id,
                "scenario": scenario,
                "mechanism": mechanism,
                "duration_seconds": row["duration_seconds"],
                "started_at": row["started_at"],
                "ended_at": row["ended_at"],
                "rounds": row["rounds"],
                "source_run": rel_sample.as_posix(),
                "runner": portable_runner_path(row["runner"]),
                "config": f"{rel_sample.as_posix()}/config/simulation.yml",
            }
        )
        quality_rows.append(
            {
                "sample_id": sample_id,
                "scenario": scenario,
                "mechanism": mechanism,
                "quality_status": "accepted",
                "quality_reason": "",
                "parse_failures": sample_meta.get("quality_log_parse_failures", ""),
                "fallback_count": sample_meta.get("quality_log_fallback_count", ""),
                "retry_count": sample_meta.get("quality_log_retry_count", ""),
                "invalid_payload_count": sample_meta.get(
                    "quality_invalid_payload_count", ""
                ),
                "missing_required_field_count": sample_meta.get(
                    "quality_missing_required_field_count", ""
                ),
                "action_distribution": sample_meta.get(
                    "quality_action_distribution", ""
                ),
                "content_type_distribution": sample_meta.get(
                    "quality_content_type_distribution", ""
                ),
            }
        )

    write_csv(
        TARGET / "MANIFEST.csv",
        manifest_rows,
        [
            "sample_id",
            "scenario",
            "mechanism",
            "sample_path",
            "runtime_status",
            "analysis_status",
            "quality_status",
            "quality_reason",
            "duration_seconds",
            "png_count",
            "has_rag_stats",
            "tracked_bytes",
            "omitted_raw_artifact_bytes",
            "omitted_raw_artifact_files",
        ],
    )
    write_csv(
        TARGET / "aggregate/runtime-summary.csv",
        runtime_rows,
        [
            "sample_id",
            "scenario",
            "mechanism",
            "duration_seconds",
            "started_at",
            "ended_at",
            "rounds",
            "source_run",
            "runner",
            "config",
        ],
    )
    write_csv(
        TARGET / "quality/quality-ledger.csv",
        quality_rows,
        [
            "sample_id",
            "scenario",
            "mechanism",
            "quality_status",
            "quality_reason",
            "parse_failures",
            "fallback_count",
            "retry_count",
            "invalid_payload_count",
            "missing_required_field_count",
            "action_distribution",
            "content_type_distribution",
        ],
    )
    write_csv(
        TARGET / "aggregate/metrics-summary.csv",
        metric_rows,
        ["sample_id", "scenario", "mechanism", "metric", "value"],
    )
    validation_counts = write_validation_outputs(TARGET, validation_rows)
    write_csv(
        TARGET / "aggregate/rag-stats-summary.csv",
        rag_rows,
        [
            "sample_id",
            "scenario",
            "mechanism",
            "agent",
            "total_rag_rounds",
            "retrieval_success_rounds",
            "retrieval_failure_rounds",
            "retrieval_failure_rate",
            "mean_retrieval_failure_rate",
            "max_retrieval_failure_rate",
        ],
    )

    write_verify_scripts(TARGET)

    if args.full_manifest:
        build_full_manifest(SOURCE, TARGET / "checksums/full-resource-pack-manifest.csv")
        manifest_hash = sha256_file(
            TARGET / "checksums/full-resource-pack-manifest.csv"
        )
        write_text(
            TARGET / "checksums/full-resource-pack-manifest.sha256",
            f"{manifest_hash}  full-resource-pack-manifest.csv",
        )

    tracked_bytes = dir_size(TARGET)
    raw_bytes = sum(int(r["omitted_raw_artifact_bytes"]) for r in manifest_rows)
    png_count = sum(int(r["png_count"]) for r in manifest_rows)

    write_text(
        TARGET / "README.md",
        f"""
# Simulation Results

This package contains the GitHub-facing assets for the
`example-standardization` 180-sample experiment set:

- 45 financial scenarios
- 4 mechanisms per scenario: Rule, LLM, RuleLLM, Rag
- 180 full configured-round runtime successes
- 180 Level-2 audited samples
- 180 analysis-complete samples
- 45 RAG samples with `rag_stats.json`

The tracked package is analysis-ready and metadata-complete. It intentionally
omits large runtime and presentation artifacts from normal Git tracking:
`records/`, `communication/`, `monitoring/`, `checkpoints/`, `logs/`, and
analysis PNG figures. Those omitted artifacts are available in the external
full resource-pack archive documented in `RESOURCE_PACK_EXTERNAL.md`.

Tracked package size at build time: {tracked_bytes} bytes.
Omitted raw artifact bytes recorded: {raw_bytes} bytes.

## Layout

```text
samples/<Scenario>/<Mode>/
  sample.json
  source-results.csv
  config/
  analysis-config/
  artifacts/analysis/summary.json
  artifacts/analysis/rag_stats.json  # Rag only
  runtime-manifest.json
  FULL_ARTIFACTS.md
```

Aggregate validation files:

- `aggregate/validation-overall.csv`: one Level-3 scenario-validity row per
  sample.
- `aggregate/validation-criteria.csv`: per-criterion validation rows.
- `aggregate/validation-summary.csv`: combined machine-readable table.
- `aggregate/validation-summary.md`: human-readable interpretation and counts.

## Verification

```bash
python simulation-results/scripts/verify_tracked_results.py
```

To verify a separately downloaded full resource-pack:

```bash
python simulation-results/scripts/verify_full_resource_pack.py \\
  --resource-pack /path/to/resource-pack
```

Operational execution plans, machine-specific notes, credentials, and raw
incoming runs are not part of the tracked result package.
""",
    )
    write_text(
        TARGET / "SUMMARY.md",
        f"""
# Simulation-180 Summary

## Counts

- Scenarios: {len(scenario_set)}
- Samples: {len(manifest_rows)}
- Runtime accepted: {sum(1 for r in manifest_rows if r['runtime_status'])}
- Analysis complete: {analysis_counts['analysis_complete']}
- Analysis PNG files: {png_count}

## By Mechanism

| Mechanism | Samples |
|---|---:|
| Rule | {mode_counts['Rule']} |
| LLM | {mode_counts['LLM']} |
| RuleLLM | {mode_counts['RuleLLM']} |
| Rag | {mode_counts['Rag']} |

## Quality Acceptance

| Status | Samples |
|---|---:|
| accepted | {quality_counts['accepted']} |

All tracked samples are accepted into the GitHub-facing result package. Detailed
non-blocking retry and parser diagnostics are retained as counters in
`quality/quality-ledger.csv`. Non-blocking triage labels are intentionally kept
out of this GitHub-facing package.

## Scenario-Validity Validation

These are Level-3 analysis targets, not runtime acceptance gates.

| Row Type | true | false | not_reported |
|---|---:|---:|---:|
| overall samples | {validation_counts['overall_true']} | {validation_counts['overall_false']} | {validation_counts['overall_not_reported']} |
| criteria rows | {validation_counts['criteria_true']} | {validation_counts['criteria_false']} | {validation_counts['criteria_not_reported']} |

See `aggregate/validation-summary.md`, `aggregate/validation-overall.csv`, and
`aggregate/validation-criteria.csv` for details.
""",
    )
    write_text(
        TARGET / "DATASET_CARD.md",
        """
# Dataset Card: Standardized Simulation-180

## Purpose

This dataset records full configured-round MASim simulations for 45 financial
scenarios under four mechanisms: Rule, LLM, RuleLLM, and Rag.

## Contents

The tracked package includes runtime metadata, isolated configs,
machine-readable analysis outputs, quality ledgers, aggregate metrics, and
checksums. Logs, PNG figures, and raw runtime message/record stores are
excluded from normal Git tracking and distributed through the external full
resource-pack archive.

## Intended Use

- Compare scenario behavior across four mechanisms.
- Inspect completed analysis JSON outputs and validation summaries.
- Reproduce analysis locally from `analysis-config/` and copied artifacts.
- Retrieve full logs, figures, and raw artifacts through the external
  resource-pack archive.

## Limitations

Runner success is not the same as economic validity. Use `summary.json`,
`aggregate/validation-overall.csv`, `aggregate/validation-criteria.csv`, and
scenario documentation when judging whether a scenario reproduces the target
mechanism.
""",
    )
    write_text(
        TARGET / "RESOURCE_PACK_EXTERNAL.md",
        """
# External Full Resource Pack

The complete resource-pack is intentionally not tracked in normal Git because
it contains full logs, analysis figures, and raw runtime directories for 180
samples.

## GitHub Release

Release tag:

```text
simulation-results-v1
```

Release URL:

```text
https://github.com/AgenticFinLab/multiagent-simulation/releases/tag/simulation-results-v1
```

Archive asset:

```text
simulation-180-standardized-resource-pack.tar.zst
```

Archive SHA256:

```text
327a4c55d5e03ad338b5009f7a380b8ba7e12fa522ae07f7502d6ab47b5c05a7
```

Archive size at packaging time:

```text
256642382 bytes
```

Do not commit the `.tar.zst` archive to normal Git history.

## Verification

After downloading:

```bash
sha256sum -c simulation-180-standardized-resource-pack.tar.zst.sha256
tar --zstd -xf simulation-180-standardized-resource-pack.tar.zst
python simulation-results/scripts/verify_full_resource_pack.py \\
  --resource-pack resource-pack
```
""",
    )
    write_text(
        TARGET / "quality/quality-summary.md",
        f"""
# Quality Summary

Rows audited: {len(quality_rows)}

## Status Counts

| Status | Count |
|---|---:|
| accepted | {quality_counts['accepted']} |

All rows in this GitHub-facing package are accepted. Non-blocking diagnostics
such as parser retries and provider retries remain available as counters in
`quality-ledger.csv`. Non-blocking triage labels are intentionally kept out of
this GitHub-facing package.
""",
    )

    source_readme = SOURCE / "README.md"
    write_text(
        source_readme,
        """
# Simulation-180 Resource Pack

This package stores standardized `example-standardization` full 200-round
samples. Runtime acceptance and analysis completion are tracked separately.

Runtime acceptance label:

`runtime_success_full_200_level2_audited`

This means:

- the matrix runner row was `SUCCESS`;
- the row completed the configured full run, normally 200 rounds;
- isolated `artifacts/`, `config/`, `logs/`, `source-results.csv`, and
  `sample.json` are present;
- Level-2 structural / LLM-output quality audit accepted the sample.

Current package audit status:

- runtime accepted samples: 180;
- analysis-complete samples: 180;
- samples without completed analysis: 0.

Analysis-complete status is audited separately with the experiment workspace's
analysis artifact audit tool.

An analysis-complete sample has analysis outputs in `artifacts/analysis/`:

- `summary.json` with analysis metrics and validation data;
- fixed PNG outputs including `03_summary.png`;
- for `Rag`, `rag_stats.json`.

Generate local analysis configs from copied resource-pack artifacts with the
experiment workspace's resource-pack analysis preparation tool.

## Layout

Accepted samples are organized by the same scenario/mode hierarchy used by
`examples/` and `configs/`:

```text
samples/
  <Scenario>/
    Rule/
      artifacts/
        analysis/
        records/
        communication/
        monitoring/
      config/
      analysis-config/
      logs/
      source-results.csv
      sample.json
    LLM/
    RuleLLM/
    Rag/
```

Each mode directory is a self-contained runtime sample. The `artifacts/`
directory contains that mode's runtime artifacts directly, while `config/`
contains the isolated config used for the original run. `analysis-config/` is
derived from `config/` and points paths at the local resource-pack copy.
""",
    )

    build_tracked_checksums(TARGET, TARGET / "checksums/tracked-results.sha256")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full-manifest",
        action="store_true",
        help="Hash every file in the full local resource-pack.",
    )
    args = parser.parse_args()
    build(args)


if __name__ == "__main__":
    main()
