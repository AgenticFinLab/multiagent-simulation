#!/usr/bin/env python
"""BlackMonday1987 RuleLLM Simulation Analysis

RuleLLM-variant analysis for the BlackMonday1987 simulation.
Reuses all metric/validation functions from Rule/analysis.py.

Usage:
    python examples/BlackMonday1987/RuleLLM/analysis.py \\
        -c configs/BlackMonday1987/RuleLLM/simulation.yml
"""

import argparse
import os

from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

from examples.BlackMonday1987.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_black_monday,
    _build_interpretation,
    analyze_black_monday,
)


def main() -> None:
    """Run full BlackMonday1987 RuleLLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_black_monday().
    """
    parser = argparse.ArgumentParser(
        description="Analyze BlackMonday1987 RuleLLM simulation results"
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

    summary = analyze_black_monday(data, config, output_dir)

    # [polish-hook-9] universal baseline invocation
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
        scenario='BlackMonday1987',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = ["main"]

if __name__ == "__main__":
    main()
