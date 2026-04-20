"""ShortSqueezeRuleLLM Analysis - ShortSqueeze Dynamics Evaluation (Rule+LLM Hybrid)

Analyzes short squeeze dynamics in hybrid Rule+LLM agents.
Uses same methodology as rule-based ShortSqueeze, reusing the shared analysis pipeline.

Usage:
    python examples/ShortSqueeze/RuleLLM/analysis.py -c configs/ShortSqueeze/RuleLLM/simulation.yml

See examples/ShortSqueeze/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.ShortSqueeze.Rule.analysis import analyze_short_squeeze, _load_data


def main():
    """Run short squeeze analysis for Rule+LLM hybrid version."""
    parser = argparse.ArgumentParser(
        description="Analyze ShortSqueezeRuleLLM simulation"
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
    print("ShortSqueezeRuleLLM Analysis - ShortSqueeze Dynamics (Rule+LLM Hybrid)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_short_squeeze(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
