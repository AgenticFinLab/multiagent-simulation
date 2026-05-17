#!/usr/bin/env python
"""Run exact API full-run plans without scenario/mechanism Cartesian products."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path


FIXED_BLOCKERS = [
    "CreditCycle__LLM",
    "RumorSpread__LLM",
    "LiquidityDryup__LLM",
    "LiquidityDryup__RuleLLM",
    "LiquidityDryup__Rag",
    "MarketCrash__RuleLLM",
    "MarketCrash__Rag",
    "MomentumEffect__Rag",
    "DispositionEffect__Rag",
    "Volmageddon__LLM",
    "Volmageddon__RuleLLM",
    "Volmageddon__Rag",
    "MomentumEffect__LLM",
    "MomentumEffect__RuleLLM",
    "CreditCycle__Rag",
]

FIXED_BLOCKERS_TAIL_NONRAG = [
    "Volmageddon__LLM",
    "Volmageddon__RuleLLM",
    "MomentumEffect__LLM",
    "MomentumEffect__RuleLLM",
]

FIXED_BLOCKERS_TAIL_RAG = [
    "MarketCrash__Rag",
    "MomentumEffect__Rag",
    "DispositionEffect__Rag",
    "Volmageddon__Rag",
    "CreditCycle__Rag",
]

QUOTA_AFFECTED_NONRAG = [
    "AssetBubble__RuleLLM",
    "DispositionEffect__LLM",
    "DispositionEffect__RuleLLM",
    "HerdEffect__LLM",
    "HerdEffect__RuleLLM",
    "EchoChamber__LLM",
    "EchoChamber__RuleLLM",
]

QUOTA_AFFECTED_RAG = [
    "AssetBubble__Rag",
    "HerdEffect__Rag",
    "RumorSpread__Rag",
]


PLANS = {
    "fixed-blockers": FIXED_BLOCKERS,
    "fixed-blockers-tail-nonrag": FIXED_BLOCKERS_TAIL_NONRAG,
    "fixed-blockers-tail-rag": FIXED_BLOCKERS_TAIL_RAG,
    "quota-affected-nonrag": QUOTA_AFFECTED_NONRAG,
    "quota-affected-rag": QUOTA_AFFECTED_RAG,
}


RESULT_FIELDNAMES = [
    "index",
    "total",
    "scenario",
    "mechanism",
    "status",
    "exit_code",
    "duration_seconds",
    "started_at",
    "ended_at",
    "config",
    "runner",
    "log_path",
    "failure_summary",
    "row_output_dir",
]


def plan_experiment_ids(plan: str) -> list[str]:
    try:
        return list(PLANS[plan])
    except KeyError as exc:
        raise ValueError(f"unknown plan: {plan}") from exc


def split_experiment_id(experiment_id: str) -> tuple[str, str]:
    parts = experiment_id.split("__", 1)
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"invalid experiment id: {experiment_id}")
    return parts[0], parts[1]


def round_progress_updates(
    log_text: str,
    *,
    last_reported_round: int,
    every_rounds: int,
) -> list[tuple[int, int]]:
    if every_rounds <= 0:
        return []

    rounds = [
        (int(match.group(1)), int(match.group(2)))
        for match in re.finditer(r"Round\s+(\d+)/(\d+)", log_text)
    ]
    if not rounds:
        return []

    current_round, total_rounds = max(rounds, key=lambda item: item[0])
    checkpoints = list(range(every_rounds, current_round + 1, every_rounds))
    if current_round >= total_rounds and total_rounds not in checkpoints:
        checkpoints.append(total_rounds)

    return [
        (round_number, total_rounds)
        for round_number in checkpoints
        if round_number > last_reported_round
    ]


def maybe_print_round_progress(
    *,
    log_path: Path,
    last_reported_round: int,
    every_rounds: int,
) -> int:
    if every_rounds <= 0 or not log_path.is_file():
        return last_reported_round

    text = log_path.read_text(encoding="utf-8", errors="replace")
    updates = round_progress_updates(
        text,
        last_reported_round=last_reported_round,
        every_rounds=every_rounds,
    )
    for round_number, total_rounds in updates:
        print(f"  progress round={round_number}/{total_rounds}", flush=True)
        last_reported_round = round_number
    return last_reported_round


def run_matrix_command(
    *,
    command: list[str],
    row_output_dir: Path,
    experiment_id: str,
    progress_every_rounds: int,
    progress_poll_seconds: float,
) -> int:
    log_path = row_output_dir / "logs" / f"{experiment_id}.log"
    last_reported_round = 0
    process = subprocess.Popen(command)
    while True:
        exit_code = process.poll()
        last_reported_round = maybe_print_round_progress(
            log_path=log_path,
            last_reported_round=last_reported_round,
            every_rounds=progress_every_rounds,
        )
        if exit_code is not None:
            return exit_code
        time.sleep(progress_poll_seconds)


def build_matrix_command(
    *,
    script: Path,
    root: Path,
    output_dir: Path,
    conda_bin: Path,
    conda_env: str,
    experiment_id: str,
    timeout_seconds: int | None,
    stall_timeout_seconds: int | None,
    progress_poll_seconds: float,
    isolated_artifacts: bool,
    dry_run: bool,
) -> list[str]:
    scenario, mechanism = split_experiment_id(experiment_id)
    command = [
        "python",
        str(script),
        "--root",
        str(root),
        "--output-dir",
        str(output_dir),
        "--conda-bin",
        str(conda_bin),
        "--conda-env",
        conda_env,
        "--scenario",
        scenario,
        "--mechanism",
        mechanism,
    ]
    if isolated_artifacts:
        command.append("--isolated-artifacts")
    if dry_run:
        command.append("--dry-run")
    if timeout_seconds is not None:
        command.extend(["--timeout-seconds", str(timeout_seconds)])
    if stall_timeout_seconds is not None:
        command.extend(["--stall-timeout-seconds", str(stall_timeout_seconds)])
    if progress_poll_seconds > 0:
        command.extend(["--progress-poll-seconds", str(progress_poll_seconds)])
    return command


def read_child_result(row_output_dir: Path, index: int, total: int) -> dict[str, str]:
    result_path = row_output_dir / "results.csv"
    with result_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1:
        raise RuntimeError(f"expected one result in {result_path}, got {len(rows)}")
    row = rows[0]
    row["index"] = str(index)
    row["total"] = str(total)
    row["row_output_dir"] = str(row_output_dir)
    return row


def launch_failed_result(
    *,
    experiment_id: str,
    index: int,
    total: int,
    row_output_dir: Path,
    exit_code: int,
    started_at: str,
    ended_at: str,
) -> dict[str, str]:
    scenario, mechanism = split_experiment_id(experiment_id)
    return {
        "index": str(index),
        "total": str(total),
        "scenario": scenario,
        "mechanism": mechanism,
        "status": "LAUNCH_FAILED",
        "exit_code": str(exit_code),
        "duration_seconds": "",
        "started_at": started_at,
        "ended_at": ended_at,
        "config": "",
        "runner": "",
        "log_path": "",
        "failure_summary": "matrix runner process failed before producing a result row",
        "row_output_dir": str(row_output_dir),
    }


def write_outputs(output_dir: Path, plan: str, experiment_ids: list[str], results: list[dict[str, str]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "plan": plan,
        "experiments": experiment_ids,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with (output_dir / "results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_FIELDNAMES)
        writer.writeheader()
        for row in results:
            writer.writerow({field: row.get(field, "") for field in RESULT_FIELDNAMES})
    (output_dir / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"# API Full Plan: {plan}",
        "",
        f"Experiments: {len(experiment_ids)}",
        "",
        "| Experiment | Status | Exit | Seconds | Row Output |",
        "|---|---|---:|---:|---|",
    ]
    for row in results:
        experiment_id = f"{row['scenario']}__{row['mechanism']}"
        lines.append(
            f"| `{experiment_id}` | `{row.get('status', '')}` | "
            f"{row.get('exit_code', '')} | {row.get('duration_seconds', '')} | "
            f"`{row.get('row_output_dir', '')}` |"
        )
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_plan(args: argparse.Namespace) -> int:
    experiment_ids = list(args.experiment_id or plan_experiment_ids(args.plan))
    output_dir = args.output_dir.resolve()
    rows_dir = output_dir / "rows"
    results: list[dict[str, str]] = []
    write_outputs(output_dir, args.plan, experiment_ids, results)

    total = len(experiment_ids)
    for index, experiment_id in enumerate(experiment_ids, start=1):
        row_output_dir = rows_dir / experiment_id
        command = build_matrix_command(
            script=args.matrix_script,
            root=args.root.resolve(),
            output_dir=row_output_dir,
            conda_bin=args.conda_bin,
            conda_env=args.conda_env,
            experiment_id=experiment_id,
            timeout_seconds=args.timeout_seconds,
            stall_timeout_seconds=args.stall_timeout_seconds,
            progress_poll_seconds=args.progress_poll_seconds,
            isolated_artifacts=args.isolated_artifacts,
            dry_run=args.dry_run,
        )
        print(f"[{index}/{total}] {experiment_id}", flush=True)
        started_at = datetime.now().isoformat(timespec="seconds")
        exit_code = run_matrix_command(
            command=command,
            row_output_dir=row_output_dir,
            experiment_id=experiment_id,
            progress_every_rounds=args.progress_every_rounds,
            progress_poll_seconds=args.progress_poll_seconds,
        )
        ended_at = datetime.now().isoformat(timespec="seconds")
        if exit_code == 0 and (row_output_dir / "results.csv").is_file():
            row = read_child_result(row_output_dir, index=index, total=total)
        else:
            row = launch_failed_result(
                experiment_id=experiment_id,
                index=index,
                total=total,
                row_output_dir=row_output_dir,
                exit_code=exit_code,
                started_at=started_at,
                ended_at=ended_at,
            )
        results.append(row)
        write_outputs(output_dir, args.plan, experiment_ids, results)
        print(
            f"  {row.get('status', '')} exit={row.get('exit_code', '')} "
            f"seconds={row.get('duration_seconds', '')}",
            flush=True,
        )

    print(f"Output: {output_dir}")
    print(f"Experiments: {total}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default="fixed-blockers", choices=sorted(PLANS))
    parser.add_argument("--experiment-id", action="append")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--matrix-script", type=Path, default=Path("scripts/run_example_matrix.py"))
    parser.add_argument("--conda-bin", type=Path, default=Path("conda"))
    parser.add_argument("--conda-env", default="LMSim")
    parser.add_argument("--timeout-seconds", type=int, default=None)
    parser.add_argument(
        "--stall-timeout-seconds",
        type=int,
        default=None,
        help="Abort child matrix runner if simulator round progress stalls this long.",
    )
    parser.add_argument("--isolated-artifacts", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--progress-every-rounds",
        type=int,
        default=20,
        help="Print child log round progress every N rounds. Use 0 to disable.",
    )
    parser.add_argument(
        "--progress-poll-seconds",
        type=float,
        default=10.0,
        help="Seconds between child log progress checks.",
    )
    return parser.parse_args()


def main() -> int:
    return run_plan(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
