"""ReversalEffectRuleLLM Analysis - ReversalEffect Dynamics Evaluation (Rule+LLM Hybrid)

Analyzes reversal effect dynamics in hybrid Rule+LLM agents.
Uses same methodology as rule-based ReversalEffect, reusing the shared analysis pipeline.

Usage:
    python examples/ReversalEffect/RuleLLM/analysis.py -c configs/ReversalEffect/RuleLLM/simulation.yml

See examples/ReversalEffect/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.ReversalEffect.Rule.analysis import analyze_reversal, _load_data


def main():
    """Run reversal effect analysis for Rule+LLM hybrid version."""
    parser = argparse.ArgumentParser(
        description="Analyze ReversalEffectRuleLLM simulation"
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
    print("ReversalEffectRuleLLM Analysis - ReversalEffect Dynamics (Rule+LLM Hybrid)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_reversal(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
