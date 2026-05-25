"""DispositionEffect RAG analysis.

The RAG variant reuses the shared DispositionEffect financial metrics and adds a
retrieval-health summary over recorded RAG context payloads when present.
"""

import argparse
import json
import os
import shutil
from typing import Any, Dict

import matplotlib.pyplot as plt
from masim.utils import load_config

from examples.DispositionEffect.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def write_standard_artifacts(output_dir: str, summary: Dict[str, Any]) -> None:
    """Add simulation-180 standard analysis filenames without removing rich plots."""
    aliases = {
        "fig1_price_dynamics.png": "01_price_dynamics.png",
        "fig2_pgr_plr_comparison.png": "02_pgr_plr_comparison.png",
    }
    for src_name, dst_name in aliases.items():
        src = os.path.join(output_dir, src_name)
        dst = os.path.join(output_dir, dst_name)
        if os.path.isfile(src):
            shutil.copyfile(src, dst)

    rag_stats = summary.get("rag_knowledge_effect", {})
    with open(os.path.join(output_dir, "rag_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rag_stats, f, indent=2)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axis("off")
    lines = [
        "DispositionEffect Rag Summary",
        f"Disposition detected: {summary.get('disposition_effect_detected')}",
        f"Mean PGR: {summary.get('mean_pgr', 0):.3f}",
        f"Mean PLR: {summary.get('mean_plr', 0):.3f}",
        f"Disposition coefficient: {summary.get('disposition_coefficient', 0):.3f}",
        f"RAG retrieval rate: {rag_stats.get('retrieval_rate', 0):.1%}",
        f"RAG fallback rate: {rag_stats.get('fallback_rate', 0):.1%}",
    ]
    ax.text(0.03, 0.95, "\n".join(lines), va="top", ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "03_summary.png"), dpi=150)
    plt.close(fig)


def analyze_rag_knowledge_effect(trades: Dict[str, list]) -> Dict[str, Any]:
    """Measure whether RAG contexts were recorded and populated."""
    total_payloads = 0
    context_payloads = 0
    fallback_payloads = 0

    for payloads in trades.values():
        for payload in payloads:
            total_payloads += 1
            if "rag_context" not in payload:
                continue
            context_payloads += 1
            if payload["rag_context"].strip() == _RAG_FALLBACK:
                fallback_payloads += 1

    if total_payloads == 0:
        raise ValueError("No RAG trade payloads found")

    retrieval_rate = context_payloads / total_payloads
    fallback_rate = fallback_payloads / context_payloads if context_payloads else 1.0
    return {
        "total_payloads": total_payloads,
        "context_payloads": context_payloads,
        "fallback_payloads": fallback_payloads,
        "retrieval_rate": retrieval_rate,
        "fallback_rate": fallback_rate,
        "target_met": retrieval_rate >= 0.70,
    }


def main() -> Dict[str, Any]:
    """Run disposition effect analysis for the RAG variant."""
    parser = argparse.ArgumentParser(
        description="Analyze DispositionEffect Rag simulation"
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
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("DispositionEffect Rag Analysis - Prospect Theory with Retrieval")
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
            f"    {res['strategy']:24s}: PGR={res['pgr']:.3f}, "
            f"PLR={res['plr']:.3f}, "
            f"Disp={'YES' if res['disposition_effect'] else 'NO'}"
        )

    print("\n[3] Generating figures (7 plots)...")
    create_visualizations(data, metrics, output_dir)
    print(f"    All figures saved to: {output_dir}/")

    print("\n[4] Generating summary...")
    summary = metrics["summary"]
    summary["rag_knowledge_effect"] = analyze_rag_knowledge_effect(data["trades"])

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"    Saved to {summary_path}")
    write_standard_artifacts(output_dir, summary)

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(f"Disposition Effect Detected: {summary['disposition_effect_detected']}")
    print(
        "RAG Retrieval Rate: "
        f"{summary['rag_knowledge_effect']['retrieval_rate']:.1%}"
    )
    print(f"\nVALIDATION: {summary['validation']['interpretation']}")

    return summary


if __name__ == "__main__":
    main()


__all__ = [
    "_RAG_FALLBACK",
    "analyze_rag_knowledge_effect",
    "write_standard_artifacts",
    "main",
]
