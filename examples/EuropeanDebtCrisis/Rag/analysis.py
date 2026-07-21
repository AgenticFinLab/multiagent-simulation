#!/usr/bin/env python
"""EuropeanDebtCrisis Rag analysis.

Runs the shared Rule pipeline (metrics + plots + summary.json) and augments
it with a retrieval-quality audit derived from the recorded ``rag_context``
turn field.  The retrieval marker
``_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`` from
``Rag/players.py`` is treated as a retrieval failure (analysis-bases.md
§2.7 API-and-RAG Quality metric).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from examples.EuropeanDebtCrisis.Rag.players import _RAG_FALLBACK
from examples.EuropeanDebtCrisis.Rule.analysis import (
    SCENARIO,
    STANDARD_OUTPUT_FILES,
    analyze_europeandebtcrisis,
    calculate_metrics,
    create_visualizations,
    load_simulation_data as _load_rule_simulation_data,
    validate_european_debt_crisis,
)
from masim.utils import load_config, load_results


DEFAULT_CONFIG = "configs/EuropeanDebtCrisis/Rag/simulation.yml"


def _load_rag_payloads(results: Any) -> Dict[str, Dict[int, Any]]:
    """Return ``{player_id: {round_num: rag_context}}`` for every player."""
    rag_contexts: Dict[str, Dict[int, Any]] = {}
    for pid, player in results.players_by_role("player").items():
        contexts = player.turns.field("rag_context")
        if contexts:
            rag_contexts[pid] = contexts
    return rag_contexts


def load_simulation_data(
    config: Dict[str, Any],
    results: Optional[Any] = None,
) -> Dict[str, Any]:
    """Load Rule data plus recorded ``rag_context`` payloads."""
    if results is None:
        results = load_results(config)
    data = _load_rule_simulation_data(config, results)
    data["rag_contexts"] = _load_rag_payloads(results)
    return data


def analyze_rag_knowledge_effect(
    rag_contexts: Dict[str, Dict[int, Any]],
) -> Dict[str, Any]:
    """Summarize RAG retrieval coverage per agent + aggregate statistics.

    A round's retrieved context that equals the sentinel

        _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"

    (defined in ``examples/EuropeanDebtCrisis/Rag/players.py``) is counted
    as a retrieval failure.  All other non-empty contexts are counted as
    successful retrievals.

    Returns a dict::

        {
            player_id: {
                "total_rag_rounds": int,
                "retrieval_success_rounds": int,
                "retrieval_failure_rounds": int,
                "retrieval_failure_rate": float,
                "mean_context_chars": float,
            },
            ...
            "aggregate": {
                "mean_retrieval_failure_rate": float,
                "max_retrieval_failure_rate": float,
                "total_rag_rounds": int,
                "total_failure_rounds": int,
                "overall_failure_rate": float,
            },
        }
    """
    rag_stats: Dict[str, Any] = {}
    for agent_id, round_contexts in rag_contexts.items():
        total = 0
        failures = 0
        context_chars_sum = 0
        for context in round_contexts.values():
            total += 1
            text = str(context) if context is not None else ""
            if text.strip() == _RAG_FALLBACK:
                failures += 1
            context_chars_sum += len(text)
        if total:
            rag_stats[agent_id] = {
                "total_rag_rounds": total,
                "retrieval_success_rounds": total - failures,
                "retrieval_failure_rounds": failures,
                "retrieval_failure_rate": float(failures / total),
                "mean_context_chars": round(float(context_chars_sum / total), 2),
            }

    rates = [
        stats["retrieval_failure_rate"]
        for stats in rag_stats.values()
        if "retrieval_failure_rate" in stats
    ]
    if rates:
        total_rounds = sum(
            stats["total_rag_rounds"] for stats in rag_stats.values()
        )
        total_failures = sum(
            stats["retrieval_failure_rounds"] for stats in rag_stats.values()
        )
        rag_stats["aggregate"] = {
            "mean_retrieval_failure_rate": float(np.mean(rates)),
            "max_retrieval_failure_rate": float(np.max(rates)),
            "total_rag_rounds": int(total_rounds),
            "total_failure_rounds": int(total_failures),
            "overall_failure_rate": float(total_failures / total_rounds)
            if total_rounds
            else 0.0,
            "player_count": len(rates),
        }
    return rag_stats


def main() -> Dict[str, Any]:
    """Run the Rule pipeline and write ``rag_stats.json`` alongside summary."""
    parser = argparse.ArgumentParser(
        description="Analyze EuropeanDebtCrisis Rag results"
    )
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    summary = analyze_europeandebtcrisis(config, output_dir, results=results)

    rag_contexts = _load_rag_payloads(results)
    rag_stats = analyze_rag_knowledge_effect(rag_contexts)
    with (Path(output_dir) / "rag_stats.json").open("w", encoding="utf-8") as fh:
        json.dump(rag_stats, fh, indent=2)

    summary["rag_stats"] = rag_stats
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    aggregate = rag_stats.get("aggregate", {})
    if aggregate:
        print("\n" + "=" * 60)
        print("RAG RETRIEVAL QUALITY")
        print("=" * 60)
        print(
            f"Players: {aggregate.get('player_count', 0)}  "
            f"total_rounds={aggregate.get('total_rag_rounds', 0)}  "
            f"mean_failure_rate={aggregate.get('mean_retrieval_failure_rate', 0.0):.3f}  "
            f"max_failure_rate={aggregate.get('max_retrieval_failure_rate', 0.0):.3f}"
        )
    return summary


__all__ = [
    "SCENARIO",
    "DEFAULT_CONFIG",
    "STANDARD_OUTPUT_FILES",
    "_RAG_FALLBACK",
    "load_simulation_data",
    "calculate_metrics",
    "validate_european_debt_crisis",
    "create_visualizations",
    "analyze_europeandebtcrisis",
    "analyze_rag_knowledge_effect",
    "main",
]


if __name__ == "__main__":
    main()
