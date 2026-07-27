#!/usr/bin/env python
"""AsianFinancialCrisis RuleLLM Simulation Analysis

RuleLLM-variant analysis for the AsianFinancialCrisis simulation.
Reuses all metric/validation functions from Rule/analysis.py.

Usage:
    python examples/AsianFinancialCrisis/RuleLLM/analysis.py \\
        -c configs/AsianFinancialCrisis/RuleLLM/simulation.yml
"""

import argparse
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

from examples.AsianFinancialCrisis.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_asian_financial_crisis,
    _build_interpretation,
    analyze_asian_financial_crisis,
)


def main() -> None:
    """Run full AsianFinancialCrisis RuleLLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_asian_financial_crisis().
    """
    parser = argparse.ArgumentParser(
        description="Analyze AsianFinancialCrisis RuleLLM simulation results"
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

    summary = analyze_asian_financial_crisis(data, config, output_dir)
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'RuleLLM'
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
        scenario='AsianFinancialCrisis',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
