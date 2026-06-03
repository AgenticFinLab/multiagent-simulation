#!/usr/bin/env python
"""AnchoringEffect — Cross-Variant Comparator.

Loads ``summary.json`` from each variant's ``analysis/`` output and emits a
side-by-side table plus comparison plots (MAD, half-life, drawdown,
return_autocorr_lag1, validation score) so the four variants can be inspected
together.

Usage::

    python examples/AnchoringEffect/compare_variants.py \
        --root EXPERIMENT/AnchoringEffect \
        --variants Rule LLM RuleLLM Rag \
        --output EXPERIMENT/AnchoringEffect/cross_variant
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np


_KEY_METRICS: List[Dict[str, str]] = [
    {"name": "MAD (%)",            "metric": "mad_pct",                 "key": "value_pct"},
    {"name": "Half-life (rounds)", "metric": "half_life_fitted",        "key": "value_rounds"},
    {"name": "Max drawdown (%)",   "metric": "max_drawdown_pct",        "key": "value_pct"},
    {"name": "Return AC(1)",       "metric": "return_autocorr_lag1",    "key": "value"},
    {"name": "Bias magnitude (%)", "metric": "bias_magnitude_pct",      "key": "value_pct"},
    {"name": "Under-revision",     "metric": "under_revision_ratio",    "key": "value"},
    {"name": "Order imbalance",    "metric": "order_imbalance_ts",      "key": "mean_imbalance"},
    {"name": "Silent agents",      "metric": "silent_agent_count",      "key": "silent_count"},
]


def _load_variant_summary(root: str, variant: str) -> Optional[Dict[str, Any]]:
    """Load ``<root>/<variant>/analysis/summary.json``."""
    path = os.path.join(root, variant, "analysis", "summary.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _scalar(summary: Dict[str, Any], metric: str, key: str) -> Optional[float]:
    flat = summary.get("metrics_flat", {})
    block = flat.get(metric)
    if not isinstance(block, dict):
        return None
    val = block.get(key)
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def build_comparison_table(
    summaries: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Produce a list of rows (one per metric) ready to be JSON-serialised."""
    rows: List[Dict[str, Any]] = []
    for entry in _KEY_METRICS:
        row: Dict[str, Any] = {
            "metric": entry["name"],
            "metric_key": f"{entry['metric']}.{entry['key']}",
        }
        for variant, summary in summaries.items():
            row[variant] = _scalar(summary, entry["metric"], entry["key"])
        rows.append(row)
    # Validation block
    valid_row: Dict[str, Any] = {"metric": "Validation score", "metric_key": "validation.score"}
    is_valid_row: Dict[str, Any] = {"metric": "Validation valid", "metric_key": "validation.is_valid"}
    for variant, summary in summaries.items():
        v = summary.get("validation", {})
        valid_row[variant] = v.get("score")
        is_valid_row[variant] = v.get("is_valid")
    rows.extend([valid_row, is_valid_row])
    return rows


def _print_table(rows: List[Dict[str, Any]], variants: List[str]) -> None:
    headers = ["Metric"] + variants
    widths = [max(len(h), 16) for h in headers]
    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        cells = [row["metric"]] + [
            f"{row.get(v):.4f}" if isinstance(row.get(v), (int, float))
            else str(row.get(v) if row.get(v) is not None else "—")
            for v in variants
        ]
        print(fmt.format(*cells))


def _plot_bar_grid(
    rows: List[Dict[str, Any]],
    variants: List[str],
    output_dir: str,
) -> str:
    """One bar chart per scalar metric in a grid."""
    numeric_rows = [
        r for r in rows
        if any(isinstance(r.get(v), (int, float)) for v in variants)
    ]
    if not numeric_rows:
        return ""
    cols = 3
    rows_n = (len(numeric_rows) + cols - 1) // cols
    fig, axes = plt.subplots(rows_n, cols, figsize=(5 * cols, 3.6 * rows_n))
    fig.suptitle("AnchoringEffect — Cross-Variant Comparison",
                 fontsize=15, fontweight="bold")
    flat_axes = np.array(axes).reshape(-1)
    palette = ["#264653", "#2a9d8f", "#e9c46a", "#e76f51",
               "#3a86ff", "#8338ec", "#06d6a0", "#ff006e"]
    for idx, row in enumerate(numeric_rows):
        ax = flat_axes[idx]
        vals = [
            float(row[v]) if isinstance(row.get(v), (int, float)) else 0.0
            for v in variants
        ]
        ax.bar(variants, vals,
               color=[palette[i % len(palette)] for i in range(len(variants))])
        ax.set_title(row["metric"])
        ax.grid(True, axis="y", alpha=0.3)
        for x, y in zip(variants, vals):
            ax.text(x, y, f"{y:.2f}", ha="center", va="bottom", fontsize=8)
    for j in range(len(numeric_rows), len(flat_axes)):
        flat_axes[j].axis("off")
    fig.tight_layout()
    path = os.path.join(output_dir, "cross_variant_metrics.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")
    return path


def _plot_validation(
    summaries: Dict[str, Dict[str, Any]],
    output_dir: str,
) -> str:
    """Side-by-side bar chart of weighted validation scores per variant."""
    variants = list(summaries)
    scores = [
        float(summaries[v].get("validation", {}).get("score") or 0.0)
        for v in variants
    ]
    is_valid = [
        bool(summaries[v].get("validation", {}).get("is_valid")) for v in variants
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    colours = ["#06d6a0" if iv else "#ef476f" for iv in is_valid]
    ax.bar(variants, scores, color=colours, alpha=0.85)
    ax.axhline(y=0.6, color="black", linestyle="--", linewidth=1.0,
               label="Pass gate (0.60)")
    for v, s, iv in zip(variants, scores, is_valid):
        ax.text(v, s + 0.01, f"{s:.2%}", ha="center", va="bottom", fontsize=9)
        ax.text(v, 0.02, "VALID" if iv else "INVALID",
                ha="center", va="bottom", fontsize=8, color="white",
                fontweight="bold")
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Weighted score")
    ax.set_title("AnchoringEffect — Validation Score per Variant")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = os.path.join(output_dir, "cross_variant_validation.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")
    return path


def compare_variants(
    root: str,
    variants: List[str],
    output_dir: str,
) -> Dict[str, Any]:
    """Load every available variant summary and emit comparison artefacts."""
    os.makedirs(output_dir, exist_ok=True)
    summaries: Dict[str, Dict[str, Any]] = {}
    missing: List[str] = []
    for variant in variants:
        summary = _load_variant_summary(root, variant)
        if summary is None:
            missing.append(variant)
            continue
        summaries[variant] = summary

    if not summaries:
        raise FileNotFoundError(
            f"No variant summary.json found under {root}. "
            f"Looked for: {variants}."
        )

    rows = build_comparison_table(summaries)
    available = list(summaries.keys())

    print("\n=== AnchoringEffect — Cross-Variant Comparison ===")
    print(f"Variants found:  {available}")
    if missing:
        print(f"Variants missing: {missing}")
    print()
    _print_table(rows, available)
    print()

    table_path = os.path.join(output_dir, "cross_variant_table.json")
    with open(table_path, "w", encoding="utf-8") as fh:
        json.dump({"rows": rows, "available": available, "missing": missing},
                  fh, indent=2, default=str)
    print(f"Saved: {table_path}")

    metrics_plot = _plot_bar_grid(rows, available, output_dir)
    validation_plot = _plot_validation(summaries, output_dir)

    return {
        "available": available,
        "missing": missing,
        "rows": rows,
        "metrics_plot": metrics_plot,
        "validation_plot": validation_plot,
        "table_path": table_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare AnchoringEffect simulation variants side-by-side."
    )
    parser.add_argument(
        "--root", type=str, default="EXPERIMENT/AnchoringEffect",
        help="Directory containing one subdir per variant.",
    )
    parser.add_argument(
        "--variants", nargs="+",
        default=["Rule", "LLM", "RuleLLM", "Rag"],
        help="Variant directory names to load.",
    )
    parser.add_argument(
        "--output", type=str,
        default="EXPERIMENT/AnchoringEffect/cross_variant",
        help="Where to write comparison artefacts.",
    )
    args = parser.parse_args()
    compare_variants(args.root, args.variants, args.output)


if __name__ == "__main__":
    main()
