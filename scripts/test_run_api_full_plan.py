#!/usr/bin/env python
"""Tests for exact-row API full-run launcher."""

from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("run_api_full_plan.py")


def load_module():
    spec = importlib.util.spec_from_file_location("run_api_full_plan", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fixed_blockers_plan_is_exact_ordered_list() -> None:
    launcher = load_module()

    assert launcher.plan_experiment_ids("fixed-blockers") == [
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


def test_fixed_blockers_tail_split_plans_are_disjoint_exact_lists() -> None:
    launcher = load_module()

    nonrag = launcher.plan_experiment_ids("fixed-blockers-tail-nonrag")
    rag = launcher.plan_experiment_ids("fixed-blockers-tail-rag")

    assert nonrag == [
        "Volmageddon__LLM",
        "Volmageddon__RuleLLM",
        "MomentumEffect__LLM",
        "MomentumEffect__RuleLLM",
    ]
    assert rag == [
        "MarketCrash__Rag",
        "MomentumEffect__Rag",
        "DispositionEffect__Rag",
        "Volmageddon__Rag",
        "CreditCycle__Rag",
    ]
    assert set(nonrag).isdisjoint(rag)


def test_quota_affected_split_plans_are_disjoint_exact_lists() -> None:
    launcher = load_module()

    nonrag = launcher.plan_experiment_ids("quota-affected-nonrag")
    rag = launcher.plan_experiment_ids("quota-affected-rag")

    assert nonrag == [
        "AssetBubble__RuleLLM",
        "DispositionEffect__LLM",
        "DispositionEffect__RuleLLM",
        "HerdEffect__LLM",
        "HerdEffect__RuleLLM",
        "EchoChamber__LLM",
        "EchoChamber__RuleLLM",
    ]
    assert rag == [
        "AssetBubble__Rag",
        "HerdEffect__Rag",
        "RumorSpread__Rag",
    ]
    assert set(nonrag).isdisjoint(rag)


def test_round_progress_updates_are_reported_every_twenty_rounds() -> None:
    launcher = load_module()

    text = "\n".join(
        [
            "13:00:00 [INFO]     Round 1/200",
            "13:10:00 [INFO]     Round 20/200",
            "13:20:00 [INFO]     Round 45/200",
        ]
    )
    assert launcher.round_progress_updates(
        text, last_reported_round=0, every_rounds=20
    ) == [(20, 200), (40, 200)]

    text = "\n".join(
        [
            "13:30:00 [INFO]     Round 45/200",
            "13:40:00 [INFO]     Round 63/200",
        ]
    )
    assert launcher.round_progress_updates(
        text, last_reported_round=40, every_rounds=20
    ) == [(60, 200)]


def test_round_progress_updates_include_final_round_once() -> None:
    launcher = load_module()

    text = "\n".join(
        [
            "13:50:00 [INFO]     Round 181/200",
            "14:00:00 [INFO]     Round 200/200",
        ]
    )
    assert launcher.round_progress_updates(
        text, last_reported_round=180, every_rounds=20
    ) == [(200, 200)]
    assert launcher.round_progress_updates(
        text, last_reported_round=200, every_rounds=20
    ) == []


def test_matrix_command_runs_one_exact_row() -> None:
    launcher = load_module()

    with tempfile.TemporaryDirectory() as tmp:
        command = launcher.build_matrix_command(
            script=Path("scripts/run_example_matrix.py"),
            root=Path("/repo"),
            output_dir=Path(tmp) / "rows" / "CreditCycle__LLM",
            conda_bin=Path("/conda/bin/conda"),
            conda_env="LMSim",
            experiment_id="CreditCycle__LLM",
            timeout_seconds=14400,
            stall_timeout_seconds=3600,
            progress_poll_seconds=10.0,
            isolated_artifacts=True,
            dry_run=False,
        )

    assert command.count("--scenario") == 1
    assert command.count("--mechanism") == 1
    assert command[command.index("--scenario") + 1] == "CreditCycle"
    assert command[command.index("--mechanism") + 1] == "LLM"
    assert "--isolated-artifacts" in command
    assert "--dry-run" not in command
    assert command[command.index("--timeout-seconds") + 1] == "14400"
    assert command[command.index("--stall-timeout-seconds") + 1] == "3600"
    assert command[command.index("--progress-poll-seconds") + 1] == "10.0"


def main() -> int:
    test_fixed_blockers_plan_is_exact_ordered_list()
    test_fixed_blockers_tail_split_plans_are_disjoint_exact_lists()
    test_quota_affected_split_plans_are_disjoint_exact_lists()
    test_round_progress_updates_are_reported_every_twenty_rounds()
    test_round_progress_updates_include_final_round_once()
    test_matrix_command_runs_one_exact_row()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
