#!/usr/bin/env python
"""Flash Crash LLM Simulation Analysis.

Reuses the six scenario metrics implemented in
``examples/FlashCrash/Rule/analysis.py`` (see analysis-bases.md §2) and
augments the ``summary.json`` with an LLM-specific action-distribution
audit that captures buy/sell/hold frequencies, reasoning-length stats,
and decision entropy per agent (implement-simulation-skill §7.2).

Usage:
    python examples/FlashCrash/LLM/analysis.py \
        -c configs/FlashCrash/LLM/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import math
import os
from typing import Any, Dict

from masim.utils import load_config

from examples.FlashCrash.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_flash_crash,
    _write_standard_named_outputs,
)


# ---------------------------------------------------------------------------
# LLM-specific analysis
# ---------------------------------------------------------------------------


def _infer_action(payload: Dict[str, Any]) -> str:
    """Return "buy" / "sell" / "hold" from an LLM investor payload.

    Prefers an explicit ``action`` field (some LLM prompts require it),
    else classifies on signed quantity.
    """
    action = str(payload.get("action") or "").strip().lower()
    if action in {"buy", "sell", "hold"}:
        return action
    qty = float(payload.get("quantity", 0.0) or 0.0)
    if qty > 0:
        return "buy"
    if qty < 0:
        return "sell"
    return "hold"


def _shannon_entropy(counts: Dict[str, int]) -> float:
    """Base-2 Shannon entropy over ``counts`` (0 if empty)."""
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for c in counts.values():
        if c <= 0:
            continue
        p = c / total
        entropy -= p * math.log2(p)
    return float(entropy)


def analyze_action_distribution(
    agent_records: Dict[str, Dict[int, Dict[str, Any]]]
) -> Dict[str, Any]:
    """Compute per-agent LLM action metrics.

    Parameters
    ----------
    agent_records : dict
        ``{agent_id: {round_num: payload_dict}}`` — usually
        ``load_simulation_data()["investor_payloads"]``.

    Returns
    -------
    dict
        ``{
            agent_id: {
                "actions": {"buy": n, "sell": n, "hold": n},
                "mean_reasoning_len": float,   # characters
                "median_reasoning_len": float,
                "decision_entropy": float,     # base-2 bits
                "total_rounds": int,
            },
            ...,
            "aggregate": { ... },
        }``
    """
    per_agent: Dict[str, Dict[str, Any]] = {}
    all_actions_agg = {"buy": 0, "sell": 0, "hold": 0}
    all_reasoning_lens: list[int] = []

    for agent_id, rounds_payloads in agent_records.items():
        if not rounds_payloads:
            continue
        counts = {"buy": 0, "sell": 0, "hold": 0}
        reasoning_lens: list[int] = []
        for payload in rounds_payloads.values():
            if not isinstance(payload, dict):
                continue
            action = _infer_action(payload)
            counts[action] = counts.get(action, 0) + 1
            reasoning = payload.get("reasoning") or ""
            reasoning_lens.append(len(str(reasoning)))

        total_rounds = sum(counts.values())
        if total_rounds == 0:
            continue

        mean_len = float(sum(reasoning_lens) / len(reasoning_lens)) if reasoning_lens else 0.0
        sorted_lens = sorted(reasoning_lens)
        median_len = float(
            sorted_lens[len(sorted_lens) // 2] if sorted_lens else 0.0
        )
        entropy = _shannon_entropy(counts)

        per_agent[agent_id] = {
            "actions": counts,
            "mean_reasoning_len": mean_len,
            "median_reasoning_len": median_len,
            "decision_entropy": round(entropy, 4),
            "total_rounds": int(total_rounds),
        }
        for key in all_actions_agg:
            all_actions_agg[key] += counts.get(key, 0)
        all_reasoning_lens.extend(reasoning_lens)

    aggregate_total = sum(all_actions_agg.values())
    aggregate = {
        "actions": all_actions_agg,
        "action_fractions": {
            k: (v / aggregate_total if aggregate_total else 0.0)
            for k, v in all_actions_agg.items()
        },
        "decision_entropy": round(_shannon_entropy(all_actions_agg), 4),
        "mean_reasoning_len": (
            float(sum(all_reasoning_lens) / len(all_reasoning_lens))
            if all_reasoning_lens else 0.0
        ),
        "total_rounds": int(aggregate_total),
        "num_agents": len(per_agent),
    }
    return {"per_agent": per_agent, "aggregate": aggregate}


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> Dict[str, Any]:
    """Run the Rule pipeline then append LLM action-distribution stats."""
    parser = argparse.ArgumentParser(description="Analyze FlashCrash LLM simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash/LLM/simulation.yml",
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("FlashCrash LLM Analysis — Rule metrics + LLM action distribution")
    print("=" * 70)

    print("\n[1] Loading simulation data...")
    data = load_simulation_data(config)
    print(f"    Loaded {len(data['prices'])} price points")

    print("\n[2] Computing scenario metrics (from Rule.analysis)...")
    metrics = calculate_metrics(data, config)

    print("\n[3] Validating against analysis-bases.md §6 target ranges...")
    validation = validate_flash_crash(metrics)
    print(f"    Aggregate score: {validation['score']:.1%} — "
          f"{'VALID' if validation['is_valid'] else 'INVALID'}")

    print("\n[4] Generating figures (8 plots)...")
    create_visualizations(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)

    print("\n[5] Computing LLM action distribution...")
    action_dist = analyze_action_distribution(data["investor_payloads"])
    agg = action_dist["aggregate"]
    print(f"    Aggregate over {agg['num_agents']} agents / "
          f"{agg['total_rounds']} decisions:")
    print(f"      actions={agg['actions']}  "
          f"entropy={agg['decision_entropy']:.3f} bits  "
          f"mean_reasoning_len={agg['mean_reasoning_len']:.1f}")

    summary = {
        "scenario": "FlashCrash",
        "variant": "LLM",
        "record_path": record_dir,
        "total_rounds": int(len(data["prices"])),
        "metrics": metrics,
        "validation": validation,
        "llm_action_distribution": action_dist,
    }
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[6] summary.json written to {summary_path}")

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(validation["interpretation"])

    return summary


if __name__ == "__main__":
    main()


__all__ = [
    "analyze_action_distribution",
    "main",
]
