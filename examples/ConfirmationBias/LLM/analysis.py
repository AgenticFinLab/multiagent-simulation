#!/usr/bin/env python
"""ConfirmationBias LLM Simulation Analysis

LLM-variant analysis for the ConfirmationBias simulation.
Reuses all metric/validation functions from Rule/analysis.py.

Usage:
    python examples/ConfirmationBias/LLM/analysis.py \\
        -c configs/ConfirmationBias/LLM/simulation.yml
"""

import argparse
import json
import os

from masim.utils import load_config, load_results
from masim.evaluation import analyze_action_distribution
from masim.evaluation import write_universal_summary

from examples.ConfirmationBias.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_confirmation_bias,
    _build_interpretation,
    analyze_confirmation_bias,
)


def main() -> None:
    """Run full ConfirmationBias LLM analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze ConfirmationBias LLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)

    summary = analyze_confirmation_bias(data, config, output_dir)

    action_dist = analyze_action_distribution(results)
    summary_path = os.path.join(output_dir, "summary.json")
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            persisted = json.load(f)
    except (OSError, ValueError):
        persisted = summary if isinstance(summary, dict) else {}
    persisted["llm_action_distribution"] = action_dist
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(persisted, f, indent=2, default=str)
    if isinstance(summary, dict):
        summary["llm_action_distribution"] = action_dist
    # [polish-hook-9] universal baseline invocation
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'LLM'
    _cfg_path = locals().get('args', None)
    _cfg_path = getattr(_cfg_path, 'config', None) if _cfg_path else None
    if isinstance(_cfg_path, str):
        for _v in ('RuleLLM', 'Rule', 'LLM', 'Rag'):
            if f'/{_v}/' in _cfg_path or _cfg_path.endswith(f'/{_v}'):
                _variant = _v
                break
    _universal = write_universal_summary(
        data,
        config,
        output_dir,
        scenario='ConfirmationBias',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = ["analyze_action_distribution", "main"]

if __name__ == "__main__":
    main()
