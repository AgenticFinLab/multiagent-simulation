#!/usr/bin/env python
"""Flash Crash Rag Simulation Analysis.

Produces the same six-metric scenario report as ``Rule/analysis.py``
(see ``examples/FlashCrash/analysis-bases.md §2``), plus a
retrieval-quality audit tailored to the Rag variant.

Standardized output contract from ``implement-simulation-skill`` — the
following files are always written under
``<record_path>/../analysis/``:

    - ``summary.json``
    - ``00_investor_bids.png``
    - ``01_flashcrash_dynamics.png``
    - ``02_flashcrash_analysis.png``
    - ``03_summary.png``
    - ``rag_stats.json`` (Rag-specific)

The RAG audit relies on the sentinel
``_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"``
recorded by ``examples/FlashCrash/Rag/players.py`` whenever the
retrieval layer fails to return relevant knowledge for that round.
``liquidity_field_missing`` marks rounds where the RAG context omits
the ``liquidity`` field required by the market state prompt.

Usage:
    python examples/FlashCrash/Rag/analysis.py \
        -c configs/FlashCrash/Rag/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

from examples.FlashCrash.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    validate_flash_crash,
    _write_standard_named_outputs,
)
from examples.FlashCrash.Rag.players import _RAG_FALLBACK


# ---------------------------------------------------------------------------
# RAG payload extraction / audit
# ---------------------------------------------------------------------------

def _load_rag_payloads(results: Any) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Extract recorded RAG contexts by player and round."""
    payloads: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for pid, player in results.players_by_role("player").items():
        round_payloads: Dict[int, Dict[str, Any]] = {}
        for round_num, rag_context in player.turns.field("rag_context").items():
            round_payloads[round_num] = {"rag_context": rag_context}
        for round_num, missing in player.turns.field(
            "liquidity_field_missing"
        ).items():
            round_payloads.setdefault(round_num, {})[
                "liquidity_field_missing"
            ] = bool(missing)
        if round_payloads:
            payloads[pid] = round_payloads
    return payloads


def analyze_rag_knowledge_effect(
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Measure retrieval coverage for FlashCrash Rag runs.

    For every player we tally:

    * ``total_rag_rounds`` — rounds where a ``rag_context`` string was
      recorded (the retrieval layer executed).
    * ``retrieval_success_rounds`` — ``rag_context`` differs from the
      sentinel ``_RAG_FALLBACK`` (i.e., the store returned something).
    * ``retrieval_failure_rounds`` — ``rag_context`` matches
      ``_RAG_FALLBACK`` verbatim (empty retrieval).
    * ``retrieval_failure_rate`` — failures divided by total rounds.
    * ``liquidity_field_missing_rounds`` — rounds where the retrieved
      snippet was missing the ``liquidity`` slot needed by the market
      state prompt (indicates schema drift in the knowledge base).

    A single aggregate block reports mean / max failure rate across all
    players that generated any RAG round.
    """
    rag_stats: Dict[str, Any] = {}

    for agent_id, round_payloads in investor_payloads.items():
        failure_rounds = 0
        success_rounds = 0
        total_rag_rounds = 0
        liquidity_field_missing_rounds = 0

        for payload in round_payloads.values():
            if payload.get("liquidity_field_missing"):
                liquidity_field_missing_rounds += 1

            rag_context = payload.get("rag_context")
            if rag_context is None:
                continue
            total_rag_rounds += 1
            if str(rag_context).strip() == _RAG_FALLBACK.strip():
                failure_rounds += 1
            else:
                success_rounds += 1

        if total_rag_rounds == 0:
            rag_stats[agent_id] = {"note": "no rag_context field in records"}
            continue

        rag_stats[agent_id] = {
            "total_rag_rounds": total_rag_rounds,
            "retrieval_success_rounds": success_rounds,
            "retrieval_failure_rounds": failure_rounds,
            "retrieval_failure_rate": float(failure_rounds / total_rag_rounds),
            "liquidity_field_missing_rounds": liquidity_field_missing_rounds,
        }

    agents_with_data = [
        v for v in rag_stats.values() if "retrieval_failure_rate" in v
    ]
    if agents_with_data:
        failure_rates = [v["retrieval_failure_rate"] for v in agents_with_data]
        rag_stats["aggregate"] = {
            "mean_retrieval_failure_rate": float(np.mean(failure_rates)),
            "max_retrieval_failure_rate": float(np.max(failure_rates)),
            "n_players_with_rag_records": len(agents_with_data),
        }

    return rag_stats


# ---------------------------------------------------------------------------
# Entry point — Rule pipeline + RAG audit
# ---------------------------------------------------------------------------

def main() -> Dict[str, Any]:
    """Run the full FlashCrash Rag analysis pipeline.

    Steps:
        1. Load config / results.
        2. Delegate to the ``Rule`` pipeline for the six scenario
           metrics, validation, and the eight diagnostic PNGs
           (aliased to ``00_investor_bids.png``, ``01_flashcrash_dynamics.png``,
           ``02_flashcrash_analysis.png``, ``03_summary.png``).
        3. Compute RAG retrieval statistics from investor turn
           payloads; write ``rag_stats.json``.
        4. Augment ``summary.json`` with ``rag_knowledge_effect``.
    """
    parser = argparse.ArgumentParser(description="Analyze FlashCrash Rag simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash/Rag/simulation.yml",
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("FlashCrash Rag Analysis — analysis-bases.md §2 metrics + RAG audit")
    print("=" * 70)

    print("\n[1] Loading simulation data...")
    results = load_results(config)
    data = load_simulation_data(config)
    print(f"    Loaded {len(data['prices'])} price points")
    print(f"    Loaded orders from {len(data['investor_payloads'])} investors")

    print("\n[2] Computing scenario metrics...")
    metrics = calculate_metrics(data, config)
    sm = metrics["scenario_metrics"]
    print(f"    crash_depth                             = {sm['crash_depth']:.4f}")
    print(f"    liquidity_vacuum_duration               = {sm['liquidity_vacuum_duration']}")
    print(f"    stop_loss_cascade_volume                = {sm['stop_loss_cascade_volume']:.1f}")
    print(f"    recovery_speed                          = {sm['recovery_speed']}")
    print(f"    liquidity_provider_withdrawal_fraction  = {sm['liquidity_provider_withdrawal_fraction']:.4f}")
    print(f"    price_amplification_ratio               = {sm['price_amplification_ratio']:.4f}")

    print("\n[3] Validating against analysis-bases.md §6 target ranges...")
    validation = validate_flash_crash(metrics)
    print(f"    Aggregate score: {validation['score']:.1%} — "
          f"{'VALID' if validation['is_valid'] else 'INVALID'}")

    print("\n[4] Generating figures (8 plots)...")
    create_visualizations(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)
    print(f"    All figures saved to: {output_dir}/")

    print("\n[5] Computing RAG retrieval statistics...")
    rag_stats = analyze_rag_knowledge_effect(_load_rag_payloads(results))
    rag_path = os.path.join(output_dir, "rag_stats.json")
    with open(rag_path, "w", encoding="utf-8") as f:
        json.dump(rag_stats, f, indent=2)
    aggregate = rag_stats.get("aggregate", {})
    if aggregate:
        print(f"    mean_retrieval_failure_rate = "
              f"{aggregate.get('mean_retrieval_failure_rate', 0.0):.4f}")
        print(f"    max_retrieval_failure_rate  = "
              f"{aggregate.get('max_retrieval_failure_rate', 0.0):.4f}")
    print(f"    rag_stats.json written to {rag_path}")

    summary = {
        "scenario": "FlashCrash",
        "variant": "Rag",
        "record_path": record_dir,
        "total_rounds": int(len(data["prices"])),
        "metrics": metrics,
        "validation": validation,
        "rag_knowledge_effect": rag_stats,
    }
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[6] summary.json written to {summary_path}")

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(validation["interpretation"])

    # [polish-hook-9] universal baseline invocation
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'Rag'
    _cfg_path = locals().get('args', None)
    _cfg_path = getattr(_cfg_path, 'config', None) if _cfg_path else None
    if isinstance(_cfg_path, str):
        for _v in ('RuleLLM', 'Rule', 'LLM', 'Rag'):
            if f'/{_v}/' in _cfg_path or _cfg_path.endswith(f'/{_v}'):
                _variant = _v
                break
    _universal = write_universal_summary(
        data,
        config,
        output_dir,
        scenario='FlashCrash',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = [
    "analyze_rag_knowledge_effect",
    "_load_rag_payloads",
    "_RAG_FALLBACK",
    "main",
]


if __name__ == "__main__":
    main()
