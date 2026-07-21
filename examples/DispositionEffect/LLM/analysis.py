"""DispositionEffectLLM Analysis - Prospect Theory Evaluation (LLM Version)

Analyzes disposition effect in LLM-driven agents.
Uses same methodology as rule-based DispositionEffect.

Usage:
    python examples/DispositionEffect/LLM/analysis.py -c configs/DispositionEffect/LLM/simulation.yml

See examples/DispositionEffect/Rule/analysis.py for detailed documentation.
"""

import argparse
import json
import os
import sys

project_root = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)
sys.path.insert(0, project_root)

from masim.utils.config import load_config
from masim.utils import load_results
from masim.evaluation import analyze_action_distribution
from examples.DispositionEffect.Rule.analysis import (
    _write_standard_named_outputs,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)


def main():
    """Run disposition effect analysis for LLM version."""
    parser = argparse.ArgumentParser(
        description="Analyze DispositionEffectLLM simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/DispositionEffect/LLM/simulation.yml",
        help="Path to simulation configuration file (YAML)",
    )
    parser.add_argument(
        "--run-dir",
        help="Run directory to analyze; defaults to the newest timestamped run",
    )
    args = parser.parse_args()

    run_dir = args.run_dir
    if run_dir is None:
        runs_root = os.path.join(
            project_root, "EXPERIMENT", "DispositionEffect", "LLM", "runs"
        )
        if os.path.isdir(runs_root):
            candidates = [
                os.path.join(runs_root, name)
                for name in os.listdir(runs_root)
                if os.path.isdir(os.path.join(runs_root, name, "records"))
            ]
            if candidates:
                run_dir = max(candidates, key=os.path.getmtime)
    if run_dir is not None:
        os.environ["DISPOSITION_LLM_OUTPUT_DIR"] = run_dir

    # Load config and derive paths
    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("DispositionEffectLLM Analysis - Prospect Theory (LLM Agents)")
    print(f"Run directory: {base_dir}")
    print("=" * 70)

    print("\n[1] Loading simulation data...")
    data = load_simulation_data(config)
    print(f"    Loaded {len(data['prices'])} price points")
    print(f"    Loaded trades from {len(data['trades'])} players")

    print("\n[2] Calculating PGR/PLR metrics...")
    metrics = calculate_metrics(data)
    strategy_results = metrics["strategy_results"]

    for _, res in strategy_results.items():
        print(
            f"    {res['strategy']:24s}: PGR={res['pgr']:.3f}, PLR={res['plr']:.3f}, "
            f"Disp={'YES' if res['disposition_effect'] else 'NO'}"
        )

    print("\n[3] Generating figures (7 plots)...")
    create_visualizations(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)
    print(f"    All figures saved to: {output_dir}/")

    print("\n[4] Generating summary...")
    summary = metrics["summary"]

    # implement-simulation-skill §7.2 — LLM variants must expose an
    # action-distribution audit and inject it into summary.json.
    try:
        results = load_results(config)
        action_dist = analyze_action_distribution(results)
    except Exception as exc:  # noqa: BLE001 — never fail the whole analysis
        print(f"    [warn] action-distribution audit failed: {exc}")
        action_dist = analyze_action_distribution({})
    summary["llm_action_distribution"] = action_dist

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")

    # Print key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Disposition Effect Detected: {summary['disposition_effect_detected']}")
    if summary["disposition_investor"]:
        disp = summary["disposition_investor"]
        print(f"Disposition Investor: PGR={disp['pgr']:.3f}, PLR={disp['plr']:.3f}")
        print(
            f"  -> Sells winners {disp['pgr']/disp['plr']:.1f}x more readily than losers"
            if disp["plr"] > 0
            else ""
        )
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")
    print(f"Fit Score: {summary['validation']['score']:.1%}")

    return summary


if __name__ == "__main__":
    main()


__all__ = ["analyze_action_distribution", "main"]
