#!/usr/bin/env python
"""EuropeanDebtCrisis LLM analysis.

Reuses the Rule pipeline for the seven scenario metrics and adds an
LLM-specific per-agent action-distribution audit (analysis-bases.md §5
"API quality" dimension).
"""

from __future__ import annotations

import argparse
import json
import math
import os
from collections import Counter
from typing import Any, Dict, List, Optional

from examples.EuropeanDebtCrisis.Rule.analysis import (
    SCENARIO,
    STANDARD_OUTPUT_FILES,
    analyze_europeandebtcrisis,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_european_debt_crisis,
)
from masim.utils import load_config, load_results


DEFAULT_CONFIG = "configs/EuropeanDebtCrisis/LLM/simulation.yml"


def _decision_entropy(action_counts: Dict[str, int]) -> float:
    """Shannon entropy (base 2) of the categorical action distribution."""
    total = sum(action_counts.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for count in action_counts.values():
        if count <= 0:
            continue
        p = count / total
        entropy -= p * math.log2(p)
    return float(entropy)


def analyze_action_distribution(
    agent_records: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """Return per-LLM-agent action-type counts, mean reasoning length, entropy.

    Parameters
    ----------
    agent_records : dict
        ``{player_id: {round_num: payload_dict}}`` — the raw turn payloads
        for each LLM investor player.  Payloads must carry ``action``,
        ``bid_price``, ``quantity`` and (optionally) ``reasoning`` /
        ``agent_type`` fields as emitted by ``_build_order`` in
        ``LLM/players.py``.

    Returns
    -------
    dict keyed by player_id with an extra ``"_aggregate"`` entry.  Each
    per-agent record contains::

        {
            "agent_type":               canonical class name,
            "total_decisions":          int,
            "action_counts":            {"buy": int, "sell": int, "hold": int},
            "action_fractions":         {"buy": float, "sell": float, "hold": float},
            "mean_reasoning_length":    float (characters),
            "median_reasoning_length":  float (characters),
            "empty_reasoning_rate":     float,
            "decision_entropy_bits":    float (Shannon entropy in bits, base 2),
        }
    """
    per_agent: Dict[str, Dict[str, Any]] = {}

    for player_id, payloads in agent_records.items():
        if not payloads:
            continue
        counts = Counter()
        reasoning_lengths: List[int] = []
        empty_reasoning = 0
        agent_type = ""
        for payload in payloads.values():
            if not isinstance(payload, dict):
                continue
            action = payload.get("action", "hold")
            if action not in ("buy", "sell", "hold"):
                action = "hold"
            counts[action] += 1
            reasoning = str(payload.get("reasoning", "") or "").strip()
            if reasoning:
                reasoning_lengths.append(len(reasoning))
            else:
                empty_reasoning += 1
            if not agent_type:
                agent_type = str(
                    payload.get("agent_type") or payload.get("strategy") or ""
                )

        total = int(sum(counts.values()))
        if total == 0:
            continue
        fractions = {
            key: counts.get(key, 0) / total for key in ("buy", "sell", "hold")
        }
        mean_len = (
            float(sum(reasoning_lengths) / len(reasoning_lengths))
            if reasoning_lengths
            else 0.0
        )
        median_len = 0.0
        if reasoning_lengths:
            sorted_lengths = sorted(reasoning_lengths)
            mid = len(sorted_lengths) // 2
            if len(sorted_lengths) % 2 == 1:
                median_len = float(sorted_lengths[mid])
            else:
                median_len = float(
                    (sorted_lengths[mid - 1] + sorted_lengths[mid]) / 2.0
                )
        per_agent[player_id] = {
            "agent_type": agent_type,
            "total_decisions": total,
            "action_counts": {
                "buy": int(counts.get("buy", 0)),
                "sell": int(counts.get("sell", 0)),
                "hold": int(counts.get("hold", 0)),
            },
            "action_fractions": {
                key: round(float(value), 4) for key, value in fractions.items()
            },
            "mean_reasoning_length": round(mean_len, 2),
            "median_reasoning_length": round(median_len, 2),
            "empty_reasoning_rate": round(empty_reasoning / total, 4),
            "decision_entropy_bits": round(_decision_entropy(dict(counts)), 4),
        }

    if per_agent:
        agg_counts = Counter()
        for record in per_agent.values():
            for action, count in record["action_counts"].items():
                agg_counts[action] += count
        agg_total = int(sum(agg_counts.values()))
        per_agent["_aggregate"] = {
            "total_decisions": agg_total,
            "action_counts": dict(agg_counts),
            "action_fractions": {
                key: round(agg_counts.get(key, 0) / agg_total, 4)
                for key in ("buy", "sell", "hold")
            }
            if agg_total
            else {},
            "decision_entropy_bits": round(_decision_entropy(dict(agg_counts)), 4),
            "player_count": len(
                [pid for pid in per_agent.keys() if pid != "_aggregate"]
            ),
        }
    return per_agent


def _agent_records_from_results(results: Any) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Collect raw turn payloads keyed by player_id for the LLM audit."""
    records: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for pid, player in results.players_by_role("player").items():
        payloads = player.turns.payloads()
        if payloads:
            records[pid] = payloads
    return records


def main() -> Dict[str, Any]:
    """Run the Rule pipeline plus the LLM action-distribution audit."""
    parser = argparse.ArgumentParser(
        description="Analyze EuropeanDebtCrisis LLM results"
    )
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    summary = analyze_europeandebtcrisis(config, output_dir, results=results)

    agent_records = _agent_records_from_results(results)
    action_dist = analyze_action_distribution(agent_records)
    summary["llm_action_distribution"] = action_dist

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print("\n" + "=" * 60)
    print("LLM ACTION DISTRIBUTION")
    print("=" * 60)
    for pid, record in action_dist.items():
        if pid == "_aggregate":
            continue
        counts = record["action_counts"]
        print(
            f"  {pid:40s} buy={counts['buy']:4d}  sell={counts['sell']:4d}  "
            f"hold={counts['hold']:4d}  entropy={record['decision_entropy_bits']:.2f}"
        )
    agg = action_dist.get("_aggregate")
    if agg:
        print(
            f"  AGGREGATE ({agg['player_count']} agents)  "
            f"buy={agg['action_counts'].get('buy', 0)} "
            f"sell={agg['action_counts'].get('sell', 0)} "
            f"hold={agg['action_counts'].get('hold', 0)} "
            f"entropy={agg['decision_entropy_bits']:.2f}"
        )
    return summary


__all__ = [
    "SCENARIO",
    "DEFAULT_CONFIG",
    "STANDARD_OUTPUT_FILES",
    "load_simulation_data",
    "calculate_metrics",
    "validate_european_debt_crisis",
    "create_visualizations",
    "analyze_europeandebtcrisis",
    "analyze_action_distribution",
    "main",
]


if __name__ == "__main__":
    main()
