"""EquityPremiumRuleLLM Analysis - EquityPremium Dynamics Evaluation (Rule+LLM Hybrid)

Analyzes equity premium dynamics in hybrid Rule+LLM agents.
Uses same methodology as rule-based EquityPremium, reusing the shared analysis pipeline.

Usage:
    python examples/EquityPremium/RuleLLM/analysis.py -c configs/EquityPremium/RuleLLM/simulation.yml

See examples/EquityPremium/Rule/analysis.py for detailed documentation.
"""

import argparse
import os
from typing import Any, Dict

from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

from examples.EquityPremium.Rule.analysis import analyze_equity_premium, _load_data


def main() -> Dict[str, Any]:
    """Run equity premium analysis for Rule+LLM hybrid version."""
    parser = argparse.ArgumentParser(
        description="Analyze EquityPremiumRuleLLM simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/EquityPremium/RuleLLM/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("EquityPremiumRuleLLM Analysis - EquityPremium Dynamics (Rule+LLM Hybrid)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_equity_premium(data, output_dir)
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
        scenario='EquityPremium',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


if __name__ == "__main__":
    main()
