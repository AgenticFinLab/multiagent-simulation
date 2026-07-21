#!/usr/bin/env python
"""2010 Flash Crash LLM Simulation Analysis.

Reuses the Rule-variant pipeline (identical §2 metric definitions and
figure catalogue from ``analysis-bases.md``) and augments the summary
with LLM-only diagnostics:

    * per-agent action-type histogram
    * reasoning-length statistics
    * decision entropy over the ``{buy, sell, hold}`` action space

Usage
-----
    python examples/FlashCrash2010/LLM/analysis.py \
        -c configs/FlashCrash2010/LLM/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from masim.utils import load_config, load_results

from examples.FlashCrash2010.Rule.analysis import (
    STANDARD_OUTPUT_FILES,
    _write_standard_named_outputs,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_flashcrash2010,
    # Metric functions re-exported so importers can pull them via LLM path
    cascade_trigger_rounds,
    depth_collapse_ratio,
    hft_withdrawal_rounds,
    max_drawdown,
    recovery_time,
    spread_widening_factor,
)


def _shannon_entropy(counts: Dict[str, int]) -> float:
    """Shannon entropy (bits) over an action-type distribution."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for c in counts.values():
        if c <= 0:
            continue
        p = c / total
        entropy -= p * math.log2(p)
    return float(entropy)


def analyze_action_distribution(
    agent_records: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Compute per-agent action-type histogram + reasoning stats + entropy.

    Parameters
    ----------
    agent_records : dict
        ``{agent_id: {round_num: payload}}`` — matches the shape returned by
        ``load_simulation_data(...)['per_agent_payloads']``.

    Returns
    -------
    dict with:
        * ``per_agent``       — one entry per LLM investor, containing
                                ``action_counts``, ``action_frequencies``,
                                ``reasoning_len_stats``, ``entropy_bits``,
                                ``rounds``.
        * ``aggregate``       — cross-agent totals & mean entropy.
    """
    per_agent: Dict[str, Any] = {}
    aggregate_counts: Counter = Counter()
    entropies: List[float] = []
    reasoning_lengths_all: List[int] = []

    for agent_id, rounds in agent_records.items():
        counts: Counter = Counter()
        reasoning_lens: List[int] = []
        for payload in rounds.values():
            if not isinstance(payload, dict):
                continue
            action = str(payload.get("action", "unknown"))
            counts[action] += 1
            reasoning = payload.get("reasoning", "")
            if isinstance(reasoning, str):
                reasoning_lens.append(len(reasoning))

        total = sum(counts.values())
        freqs = {k: (v / total) for k, v in counts.items()} if total else {}
        ent = _shannon_entropy(dict(counts))
        rl_stats = _length_stats(reasoning_lens)

        per_agent[agent_id] = {
            "rounds": total,
            "action_counts": dict(counts),
            "action_frequencies": freqs,
            "entropy_bits": ent,
            "reasoning_len_stats": rl_stats,
        }
        aggregate_counts.update(counts)
        if total:
            entropies.append(ent)
        reasoning_lengths_all.extend(reasoning_lens)

    aggregate = {
        "action_counts": dict(aggregate_counts),
        "mean_entropy_bits": float(sum(entropies) / len(entropies)) if entropies else 0.0,
        "reasoning_len_stats": _length_stats(reasoning_lengths_all),
        "num_agents": len(per_agent),
    }
    return {"per_agent": per_agent, "aggregate": aggregate}


def _length_stats(values: List[int]) -> Dict[str, float]:
    if not values:
        return {"count": 0, "mean": 0.0, "min": 0, "max": 0}
    return {
        "count": len(values),
        "mean": float(sum(values) / len(values)),
        "min": int(min(values)),
        "max": int(max(values)),
    }


def analyze_llm(config_path: str) -> Dict[str, Any]:
    """Run the Rule pipeline, then attach LLM-only diagnostics to summary.json."""
    config = load_config(config_path)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = load_simulation_data(config, results)
    metrics = calculate_metrics(data, config)
    validation = validate_flashcrash2010(metrics)

    create_visualizations(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)

    action_stats = analyze_action_distribution(data["per_agent_payloads"])

    summary: Dict[str, Any] = {
        "scenario": "FlashCrash2010",
        "variant": "LLM",
        "config_path": config_path,
        **metrics,
        "validation": validation,
        "llm_action_analysis": action_stats,
    }
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    return summary


def main() -> Dict[str, Any]:
    """CLI entry point for the LLM variant."""
    parser = argparse.ArgumentParser(
        description="Analyze FlashCrash2010 LLM simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/LLM/simulation.yml",
    )
    args = parser.parse_args()
    print("=" * 72)
    print("FlashCrash2010 LLM Analysis")
    print("=" * 72)
    summary = analyze_llm(args.config)
    print(f"max_drawdown          = {summary['max_drawdown']:.4f}")
    print(f"cascade_wave_count    = {summary['cascade_wave_count']}")
    print(f"recovery_time         = {summary['recovery_time']}")
    print(
        "mean_entropy_bits     ="
        f" {summary['llm_action_analysis']['aggregate']['mean_entropy_bits']:.3f}"
    )
    print(summary["validation"]["interpretation"])
    return summary


__all__ = [
    "analyze_action_distribution",
    "analyze_llm",
    "main",
]


if __name__ == "__main__":
    main()
