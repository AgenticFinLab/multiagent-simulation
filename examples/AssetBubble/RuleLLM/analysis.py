"""AssetBubbleRuleLLM Analysis - Positive Feedback Dynamics Evaluation (Rule+LLM Hybrid)

Analyzes asset bubble dynamics in hybrid Rule+LLM agents.
Uses same methodology as rule-based AssetBubble, reusing the shared analysis pipeline.

Usage:
    python examples/AssetBubble/RuleLLM/analysis.py -c configs/AssetBubble/RuleLLM/simulation.yml

See examples/AssetBubble/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.AssetBubble.Rule.analysis import analyze_bubble, _load_data


def main():
    """Run bubble analysis for Rule+LLM hybrid version."""
    parser = argparse.ArgumentParser(
        description="Analyze AssetBubbleRuleLLM simulation"
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
    print("AssetBubbleRuleLLM Analysis - Positive Feedback Dynamics (Rule+LLM Hybrid)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_bubble(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
