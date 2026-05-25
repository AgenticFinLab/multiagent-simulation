#!/usr/bin/env python
"""Run or dry-run the full examples scenario/mechanism matrix.

This is a local workspace tool. The scripts/ directory is intentionally excluded
from Git tracking until the workflow stabilizes.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import signal
import shutil
import subprocess
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Iterable, NamedTuple, Optional


MECHANISM_ORDER = {
    "Rule": 0,
    "LLM": 1,
    "RuleLLM": 2,
    "Rag": 3,
}

ARTIFACT_SUBDIRS = ("records", "communication", "monitoring", "checkpoints")


class RoundProgress(NamedTuple):
    max_round: int
    total_rounds: int


class Experiment(NamedTuple):
    scenario: str
    mechanism: str
    config: Path
    runner: Path

    @property
    def experiment_id(self) -> str:
        return f"{self.scenario}__{self.mechanism}"

    def to_manifest_dict(self) -> dict:
        return {
            "id": self.experiment_id,
            "scenario": self.scenario,
            "mechanism": self.mechanism,
            "config": str(self.config),
            "runner": str(self.runner),
        }


class RunResult(NamedTuple):
    index: int
    total: int
    scenario: str
    mechanism: str
    status: str
    exit_code: Optional[int]
    duration_seconds: float
    started_at: str
    ended_at: str
    command: list[str]
    config: str
    runner: str
    log_path: str
    failure_summary: str
    max_round: Optional[int]
    total_rounds: Optional[int]
    timeout_reason: str

    @classmethod
    def from_dry_run(cls, exp: Experiment, index: int, total: int) -> "RunResult":
        now = datetime.now().isoformat(timespec="seconds")
        return cls(
            index=index,
            total=total,
            scenario=exp.scenario,
            mechanism=exp.mechanism,
            status="DRY_RUN",
            exit_code=None,
            duration_seconds=0.0,
            started_at=now,
            ended_at=now,
            command=[],
            config=str(exp.config),
            runner=str(exp.runner),
            log_path="",
            failure_summary="",
            max_round=None,
            total_rounds=None,
            timeout_reason="",
        )

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "total": self.total,
            "scenario": self.scenario,
            "mechanism": self.mechanism,
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_seconds": round(self.duration_seconds, 3),
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "command": self.command,
            "config": self.config,
            "runner": self.runner,
            "log_path": self.log_path,
            "failure_summary": self.failure_summary,
            "max_round": self.max_round,
            "total_rounds": self.total_rounds,
            "timeout_reason": self.timeout_reason,
        }


def discover_experiments(root: Path) -> list[Experiment]:
    configs_root = root / "configs"
    examples_root = root / "examples"
    experiments: list[Experiment] = []

    for config_path in configs_root.glob("*/*/simulation.yml"):
        rel = config_path.relative_to(configs_root)
        scenario = rel.parts[0]
        mechanism = rel.parts[1]
        if scenario == "TEMPLATES":
            continue

        runner_dir = examples_root / scenario / mechanism
        runners = sorted(runner_dir.glob("run_*.py"))
        if not runners:
            continue

        experiments.append(
            Experiment(
                scenario=scenario,
                mechanism=mechanism,
                config=config_path,
                runner=runners[0],
            )
        )

    return sorted(
        experiments,
        key=lambda exp: (
            exp.scenario,
            MECHANISM_ORDER.get(exp.mechanism, 99),
            exp.mechanism,
        ),
    )


def filter_experiments(
    experiments: Iterable[Experiment],
    scenarios: Optional[set[str]] = None,
    mechanisms: Optional[set[str]] = None,
) -> list[Experiment]:
    selected = []
    for exp in experiments:
        if scenarios and exp.scenario not in scenarios:
            continue
        if mechanisms and exp.mechanism not in mechanisms:
            continue
        selected.append(exp)
    return selected


def build_command(experiment: Experiment, conda_bin: Path, conda_env: str) -> list[str]:
    return [
        str(conda_bin),
        "run",
        "--no-capture-output",
        "-n",
        conda_env,
        "python",
        str(experiment.runner),
        "-c",
        str(experiment.config),
    ]


def build_child_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("MPLCONFIGDIR", "/tmp/masim-matplotlib")
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    env.setdefault("WANDB_MODE", "disabled")
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("MASIM_RAY_NUM_CPUS", "16")
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    env.setdefault("OPENBLAS_NUM_THREADS", "1")
    env.setdefault("NUMEXPR_NUM_THREADS", "1")
    return env


def relative_or_absolute(root: Path, path: Path) -> str:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def artifact_path_for_config(
    root: Path,
    output_dir: Path,
    experiment: Experiment,
    artifact_name: str,
) -> str:
    artifact_path = (
        output_dir
        / "artifacts"
        / experiment.scenario
        / experiment.mechanism
        / artifact_name
    )
    return relative_or_absolute(root=root, path=artifact_path)


def rewrite_config_text(
    text: str,
    root: Path,
    output_dir: Path,
    experiment: Experiment,
) -> str:
    old_prefix = f"EXPERIMENT/{experiment.scenario}/{experiment.mechanism}"
    for artifact_name in ARTIFACT_SUBDIRS:
        text = text.replace(
            f"{old_prefix}/{artifact_name}",
            artifact_path_for_config(
                root=root,
                output_dir=output_dir,
                experiment=experiment,
                artifact_name=artifact_name,
            ),
        )
    return text


def copy_isolated_config_dir(
    root: Path,
    output_dir: Path,
    experiment: Experiment,
) -> Path:
    source_dir = experiment.config.parent
    snapshot_dir = output_dir / "configs" / experiment.scenario / experiment.mechanism
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    for source_path in source_dir.rglob("*"):
        relative_path = source_path.relative_to(source_dir)
        target_path = snapshot_dir / relative_path
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.suffix.lower() in {".yml", ".yaml"}:
            text = source_path.read_text(encoding="utf-8")
            target_path.write_text(
                rewrite_config_text(
                    text=text,
                    root=root,
                    output_dir=output_dir,
                    experiment=experiment,
                ),
                encoding="utf-8",
            )
        else:
            shutil.copy2(source_path, target_path)

    return snapshot_dir / experiment.config.name


def prepare_isolated_experiments(
    root: Path,
    output_dir: Path,
    experiments: Iterable[Experiment],
) -> list[Experiment]:
    prepared: list[Experiment] = []
    for experiment in experiments:
        for artifact_name in ARTIFACT_SUBDIRS:
            (
                output_dir
                / "artifacts"
                / experiment.scenario
                / experiment.mechanism
                / artifact_name
            ).mkdir(parents=True, exist_ok=True)

        snapshot_config = copy_isolated_config_dir(
            root=root,
            output_dir=output_dir,
            experiment=experiment,
        )
        prepared.append(experiment._replace(config=snapshot_config))
    return prepared


def write_manifest(output_dir: Path, experiments: Iterable[Experiment]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    data = [exp.to_manifest_dict() for exp in experiments]
    (output_dir / "manifest.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_results(output_dir: Path, results: Iterable[RunResult]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = [result.to_dict() for result in results]

    (output_dir / "results.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    csv_path = output_dir / "results.csv"
    fieldnames = [
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
        "max_round",
        "total_rounds",
        "timeout_reason",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in fieldnames})


def write_report(output_dir: Path, results: Iterable[RunResult]) -> None:
    rows = list(results)
    status_counts: dict[str, int] = {}
    for result in rows:
        status_counts[result.status] = status_counts.get(result.status, 0) + 1

    lines = [
        "# Example Run Matrix Report",
        "",
        f"Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"Total experiments: {len(rows)}",
        "",
        "## Summary",
        "",
    ]
    for status in sorted(status_counts):
        lines.append(f"- {status}: {status_counts[status]}")

    lines.extend(["", "## Results", ""])
    lines.append("| # | Scenario | Mechanism | Status | Exit | Seconds | Progress | Log | Failure |")
    lines.append("|---:|---|---|---|---:|---:|---:|---|---|")
    for result in rows:
        log_name = Path(result.log_path).name if result.log_path else ""
        failure = result.failure_summary.replace("|", "\\|")
        progress = (
            ""
            if result.max_round is None or result.total_rounds is None
            else f"{result.max_round}/{result.total_rounds}"
        )
        lines.append(
            "| {index} | {scenario} | {mechanism} | {status} | {exit_code} | "
            "{duration:.3f} | {progress} | {log} | {failure} |".format(
                index=result.index,
                scenario=result.scenario,
                mechanism=result.mechanism,
                status=result.status,
                exit_code="" if result.exit_code is None else result.exit_code,
                duration=result.duration_seconds,
                progress=progress,
                log=log_name,
                failure=failure,
            )
        )

    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize_failure(log_path: Path, exit_code: Optional[int]) -> str:
    if exit_code is None:
        return ""
    if exit_code == 0:
        return ""
    if not log_path.exists():
        return f"failed with exit code {exit_code}; log file missing"

    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    useful = [line.strip() for line in lines if line.strip()]
    for line in reversed(useful):
        if (
            "Traceback" in line
            or "Error" in line
            or "ERROR" in line
            or "Exception" in line
            or "ModuleNotFoundError" in line
            or "ValueError" in line
            or "RuntimeError" in line
        ):
            return line[:500]
    if useful:
        return useful[-1][:500]
    return f"failed with exit code {exit_code}"


def extract_round_progress(text: str) -> RoundProgress:
    matches = [
        (int(match.group(1)), int(match.group(2)))
        for match in re.finditer(r"(?:Round\s+|progress round=)(\d+)/(\d+)", text)
    ]
    if not matches:
        return RoundProgress(max_round=0, total_rounds=0)
    max_round, total_rounds = max(matches, key=lambda item: item[0])
    return RoundProgress(max_round=max_round, total_rounds=total_rounds)


def read_round_progress(log_path: Path) -> RoundProgress:
    if not log_path.is_file():
        return RoundProgress(max_round=0, total_rounds=0)
    text = log_path.read_text(encoding="utf-8", errors="replace")
    return extract_round_progress(text)


def stall_timeout_reason(
    *,
    now_perf: float,
    last_progress_perf: float,
    stall_timeout_seconds: Optional[int],
    progress: RoundProgress,
) -> Optional[str]:
    if stall_timeout_seconds is None or stall_timeout_seconds <= 0:
        return None
    idle_seconds = now_perf - last_progress_perf
    if idle_seconds <= stall_timeout_seconds:
        return None
    progress_text = (
        "no_round_progress"
        if progress.max_round <= 0
        else f"{progress.max_round}/{progress.total_rounds}"
    )
    return (
        f"stall_timeout after {stall_timeout_seconds}s without new round progress; "
        f"last_progress={progress_text}; idle_seconds={idle_seconds:.1f}"
    )


def hard_timeout_reason(
    *,
    elapsed_seconds: float,
    timeout_seconds: Optional[int],
    progress: RoundProgress,
) -> Optional[str]:
    if timeout_seconds is None or timeout_seconds <= 0:
        return None
    if elapsed_seconds <= timeout_seconds:
        return None
    progress_text = (
        "no_round_progress"
        if progress.max_round <= 0
        else f"{progress.max_round}/{progress.total_rounds}"
    )
    return (
        f"hard_timeout after {timeout_seconds}s; "
        f"last_progress={progress_text}; elapsed_seconds={elapsed_seconds:.1f}"
    )


def terminate_process_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=10)
    except Exception:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except Exception:
            process.kill()


def run_experiment(
    exp: Experiment,
    index: int,
    total: int,
    output_dir: Path,
    conda_bin: Path,
    conda_env: str,
    timeout_seconds: Optional[int],
    stall_timeout_seconds: Optional[int],
    progress_poll_seconds: float,
) -> RunResult:
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{exp.experiment_id}.log"
    command = build_command(experiment=exp, conda_bin=conda_bin, conda_env=conda_env)

    env = build_child_env()
    Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

    started = datetime.now()
    start_perf = time.perf_counter()
    exit_code: Optional[int] = None
    status = "FAILED"
    timeout_reason = ""
    progress = RoundProgress(max_round=0, total_rounds=0)

    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write(f"# {exp.experiment_id}\n")
        log_file.write(f"# Started: {started.isoformat(timespec='seconds')}\n")
        log_file.write(f"# Command: {' '.join(command)}\n\n")
        log_file.flush()

        try:
            process = subprocess.Popen(
                command,
                cwd=Path.cwd(),
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            last_progress_perf = start_perf
            while True:
                exit_code = process.poll()
                current_progress = read_round_progress(log_path)
                if current_progress.max_round > progress.max_round:
                    progress = current_progress
                    last_progress_perf = time.perf_counter()

                if exit_code is not None:
                    status = "SUCCESS" if exit_code == 0 else "FAILED"
                    break

                now_perf = time.perf_counter()
                timeout_reason = stall_timeout_reason(
                    now_perf=now_perf,
                    last_progress_perf=last_progress_perf,
                    stall_timeout_seconds=stall_timeout_seconds,
                    progress=progress,
                ) or hard_timeout_reason(
                    elapsed_seconds=now_perf - start_perf,
                    timeout_seconds=timeout_seconds,
                    progress=progress,
                ) or ""
                if timeout_reason:
                    status = "TIMEOUT"
                    exit_code = 124
                    log_file.write(f"\n# TIMEOUT {timeout_reason}\n")
                    log_file.flush()
                    terminate_process_group(process)
                    break

                time.sleep(progress_poll_seconds)
        except Exception:
            status = "FAILED"
            exit_code = 1
            log_file.write("\n# Runner exception\n")
            log_file.write(traceback.format_exc())

    ended = datetime.now()
    duration = time.perf_counter() - start_perf
    final_progress = read_round_progress(log_path)
    if final_progress.max_round > progress.max_round:
        progress = final_progress
    failure_summary = summarize_failure(log_path, exit_code)

    return RunResult(
        index=index,
        total=total,
        scenario=exp.scenario,
        mechanism=exp.mechanism,
        status=status,
        exit_code=exit_code,
        duration_seconds=duration,
        started_at=started.isoformat(timespec="seconds"),
        ended_at=ended.isoformat(timespec="seconds"),
        command=command,
        config=str(exp.config),
        runner=str(exp.runner),
        log_path=str(log_path),
        failure_summary=failure_summary,
        max_round=progress.max_round or None,
        total_rounds=progress.total_rounds or None,
        timeout_reason=timeout_reason,
    )


def default_output_dir(root: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-local-matrix")
    return root / "EXPERIMENT" / "runs" / stamp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run or dry-run all MASim example scenario/mechanism combinations."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--conda-bin", type=Path, default=Path("~/miniforge3/bin/conda").expanduser())
    parser.add_argument("--conda-env", default="LMSim")
    parser.add_argument("--scenario", action="append", help="Scenario filter; can be repeated.")
    parser.add_argument("--mechanism", action="append", help="Mechanism filter; can be repeated.")
    parser.add_argument(
        "--isolated-artifacts",
        action="store_true",
        help=(
            "Copy each selected config under OUTPUT_DIR/configs and rewrite runtime "
            "artifact paths to OUTPUT_DIR/artifacts."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="Only write manifest/results/report.")
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=None,
        help="Per-experiment hard timeout. Default: no hard timeout.",
    )
    parser.add_argument(
        "--stall-timeout-seconds",
        type=int,
        default=None,
        help=(
            "Abort a child process after this many seconds without new simulator "
            "round progress. Default: disabled."
        ),
    )
    parser.add_argument(
        "--progress-poll-seconds",
        type=float,
        default=10.0,
        help="Seconds between child log progress checks for timeout handling.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output_dir = (args.output_dir or default_output_dir(root)).resolve()

    experiments = discover_experiments(root)
    experiments = filter_experiments(
        experiments,
        scenarios=set(args.scenario) if args.scenario else None,
        mechanisms=set(args.mechanism) if args.mechanism else None,
    )
    if args.isolated_artifacts:
        experiments = prepare_isolated_experiments(
            root=root,
            output_dir=output_dir,
            experiments=experiments,
        )

    write_manifest(output_dir, experiments)

    if args.dry_run:
        results = [
            RunResult.from_dry_run(exp, index=i + 1, total=len(experiments))
            for i, exp in enumerate(experiments)
        ]
    else:
        results = []
        for i, exp in enumerate(experiments):
            print(f"[{i + 1}/{len(experiments)}] {exp.experiment_id}", flush=True)
            result = run_experiment(
                exp=exp,
                index=i + 1,
                total=len(experiments),
                output_dir=output_dir,
                conda_bin=args.conda_bin,
                conda_env=args.conda_env,
                timeout_seconds=args.timeout_seconds,
                stall_timeout_seconds=args.stall_timeout_seconds,
                progress_poll_seconds=args.progress_poll_seconds,
            )
            results.append(result)
            write_results(output_dir, results)
            write_report(output_dir, results)
            print(
                f"  {result.status} exit={result.exit_code} "
                f"seconds={result.duration_seconds:.1f}",
                flush=True,
            )

    write_results(output_dir, results)
    write_report(output_dir, results)

    print(f"Output: {output_dir}")
    print(f"Experiments: {len(experiments)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
