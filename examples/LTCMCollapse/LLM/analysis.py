#!/usr/bin/env python
"""LTCMCollapse LLM analysis using the scenario output contract."""

from __future__ import annotations

import argparse
import os
from collections import Counter
from pathlib import Path

from examples.LTCMCollapse.Rule.analysis import (
    _universal_data,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_metrics,
)
from masim.utils import load_config
from masim.evaluation.llm_harness import finalize_llm_analysis

DEFAULT_CONFIG = "configs/LTCMCollapse/LLM/simulation.yml"


def analyze_action_distribution(agent_records: dict) -> dict[str, int]:
    """Count categorical API decisions across agent-round records."""
    counts: Counter[str] = Counter()
    for round_records in agent_records.values():
        for record in round_records.values():
            action = record["action"]
            if action not in ("buy", "sell", "hold"):
                raise ValueError(f"Invalid recorded action: {action}")
            counts[action] += 1
    return {action: counts[action] for action in ("buy", "sell", "hold")}


def main() -> None:
    """Run LLM analysis with an LLM-specific default config."""
    parser = argparse.ArgumentParser(description="Analyze LTCMCollapse LLM results")
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    metrics = calculate_metrics(data)
    validation = validate_metrics(metrics)
    analysis_path = Path(os.path.dirname(config["setting"]["record_path"])) / "analysis"
    analysis_path.mkdir(parents=True, exist_ok=True)
    create_visualizations(data, str(analysis_path))
    from examples.LTCMCollapse.Rule.analysis import _write_summary

    _write_summary(analysis_path, metrics, validation)
    summary = {
        "metrics": metrics,
        "validation": validation.to_dict(),
        "action_distribution": analyze_action_distribution(data["agent_records"]),
    }
    finalize_llm_analysis(
        _universal_data(data),
        config,
        str(analysis_path),
        "LTCMCollapse",
        summary,
        config_path=args.config,
    )



__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_action_distribution",
    "main",
]


if __name__ == "__main__":
    main()
