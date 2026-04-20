"""FlashCrashRuleLLM Analysis - HFT Dynamics Evaluation (Rule+LLM Hybrid)

Analyzes flash crash dynamics in hybrid Rule+LLM agents.
Uses same methodology as rule-based FlashCrash, reusing the shared analysis pipeline.

Usage:
    python examples/FlashCrash/RuleLLM/analysis.py -c configs/FlashCrash/RuleLLM/simulation.yml

See examples/FlashCrash/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.FlashCrash.Rule.analysis import analyze_flash_crash, _load_data


def main():
    """Run flash crash analysis for Rule+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze FlashCrashRuleLLM simulation")
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
    print("FlashCrashRuleLLM Analysis - HFT Dynamics (Rule+LLM Hybrid)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_flash_crash(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
