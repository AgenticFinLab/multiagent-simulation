"""FlashCrashRag Analysis — HFT Dynamics Evaluation (RAG+LLM Variant)

Analyzes flash crash dynamics in RAG-augmented Rule+LLM agents.
Uses the same methodology and metrics as rule-based FlashCrash,
reusing the shared analysis pipeline from FlashCrash/analysis.py.

Usage:
    python examples/FlashCrash/Rag/analysis.py -c configs/FlashCrash/Rag/simulation.yml

See examples/FlashCrash/Rule/analysis.py for detailed documentation.
"""

import argparse
import os

from masim.utils import load_config, load_results

from examples.FlashCrash.Rule.analysis import analyze_flash_crash, _load_data


def main():
    """Run flash crash analysis for RAG+LLM hybrid version."""
    parser = argparse.ArgumentParser(description="Analyze FlashCrashRag simulation")
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
    print("FlashCrashRag Analysis - HFT Dynamics (RAG+LLM Agents)")
    print("=" * 70)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_flash_crash(data, output_dir)
    return summary


if __name__ == "__main__":
    main()
