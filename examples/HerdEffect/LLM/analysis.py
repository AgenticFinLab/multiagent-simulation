"""HerdEffectLLM Analysis - Emergent Herding Behavior Evaluation (LLM Version)

Analyzes herding behavior in LLM-driven agents.
Uses same methodology as rule-based HerdEffect.

Usage:
    python examples/HerdEffect/LLM/analysis.py -c configs/HerdEffect/LLM/simulation.yml

See examples/HerdEffect/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.HerdEffect.Rule.analysis import analyze_herding, _load_data


def main():
    """Run herding analysis for LLM version."""
    parser = argparse.ArgumentParser(description="Analyze HerdEffectLLM simulation")
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
    print("HerdEffectLLM Analysis - Emergent Herding (LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_herding(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
