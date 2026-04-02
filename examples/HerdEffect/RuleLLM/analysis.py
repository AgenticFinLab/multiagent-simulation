"""HerdEffectRuleLLM Analysis - Emergent Herding Evaluation (Rule+LLM Hybrid)

Analyzes herding dynamics in hybrid Rule+LLM agents.
Uses same methodology as rule-based HerdEffect, reusing the shared analysis pipeline.

Usage:
    python examples/HerdEffect/RuleLLM/analysis.py -c configs/HerdEffect/RuleLLM/simulation.yml

See examples/HerdEffect/Rule/analysis.py for detailed documentation.
"""

import argparse
import os
import sys

from masim.utils import load_config, load_results

# Import analysis functions from rule-based version
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from HerdEffect.analysis import analyze_herding, _load_data


def main():
    """Run herding analysis for Rule+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze HerdEffectRuleLLM simulation")
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
    print("HerdEffectRuleLLM Analysis - Emergent Herding (Rule+LLM Hybrid)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_herding(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
