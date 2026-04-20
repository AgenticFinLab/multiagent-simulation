"""MomentumEffectRuleLLM Analysis - MomentumEffect Dynamics Evaluation (Rule+LLM Hybrid)

Analyzes momentum effect dynamics in hybrid Rule+LLM agents.
Uses same methodology as rule-based MomentumEffect, reusing the shared analysis pipeline.

Usage:
    python examples/MomentumEffect/RuleLLM/analysis.py -c configs/MomentumEffect/RuleLLM/simulation.yml

See examples/MomentumEffect/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.MomentumEffect.Rule.analysis import analyze_momentum, _load_data


def main():
    """Run momentum effect analysis for Rule+LLM hybrid version."""
    parser = argparse.ArgumentParser(
        description="Analyze MomentumEffectRuleLLM simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("MomentumEffectRuleLLM Analysis - MomentumEffect Dynamics (Rule+LLM Hybrid)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_momentum(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
