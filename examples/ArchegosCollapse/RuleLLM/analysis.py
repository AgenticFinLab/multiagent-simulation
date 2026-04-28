#!/usr/bin/env python
"""ArchegosCollapse RuleLLM Simulation Analysis

RuleLLM-variant analysis for the ArchegosCollapse simulation.
Reuses all metric/validation functions from Rule/analysis.py and adds
Rule-Adherence Analysis (analysis-bases.md §3 Dimension 2).

RuleLLM-variant note (analysis-bases.md §4):
    Rule override events occur when LLM deviates from formula direction.
    Target: >= 80% directional alignment between LLM and Rule decisions.

Usage:
    python examples/ArchegosCollapse/RuleLLM/analysis.py \\
        -c configs/ArchegosCollapse/RuleLLM/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from masim.utils import load_config, load_results

from examples.ArchegosCollapse.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_archegos_collapse,
    _build_interpretation,
    analyze_archegos_collapse,
)


def analyze_rule_adherence(
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Compute rule-adherence rate for RuleLLM agents — analysis-bases.md §3 Dimension 2.

    Measures the fraction of rounds where the LLM's action direction matches
    what the embedded rule would prescribe (as recorded in the decision trace).

    A round is adherent if:
        - Both Rule and LLM output the same action (buy/sell/hold)

    Target: adherence_rate >= 0.80 (analysis-bases.md §3)

    Args:
        investor_payloads: Dict mapping agent_id to {round_num: payload_dict}.

    Returns:
        Dict with adherence stats per agent and aggregate.
    """
    adherence: Dict[str, Any] = {}

    for agent_id, round_payloads in investor_payloads.items():
        rule_actions = []
        llm_actions = []

        for payload in round_payloads.values():
            rule_action = payload.get("rule_action", None)
            llm_action = payload.get("action", None)
            if rule_action is not None and llm_action is not None:
                rule_actions.append(rule_action)
                llm_actions.append(llm_action)

        if not rule_actions:
            adherence[agent_id] = {
                "adherence_rate": None,
                "note": "no rule_action field",
            }
            continue

        matching = sum(r == l for r, l in zip(rule_actions, llm_actions))
        total = len(rule_actions)
        adherence[agent_id] = {
            "adherence_rate": float(matching / total) if total > 0 else 0.0,
            "matching_rounds": matching,
            "total_rounds": total,
            "meets_target": (matching / total >= 0.80) if total > 0 else False,
        }

    if adherence:
        rates = [
            v["adherence_rate"]
            for v in adherence.values()
            if v.get("adherence_rate") is not None
        ]
        adherence["aggregate"] = {
            "mean_adherence_rate": float(np.mean(rates)) if rates else 0.0,
            "min_adherence_rate": float(np.min(rates)) if rates else 0.0,
            "target_80pct_met": all(r >= 0.80 for r in rates) if rates else False,
        }

    return adherence


def main() -> None:
    """Run full ArchegosCollapse RuleLLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_archegos_collapse().
    Adds Rule-Adherence Analysis (analysis-bases.md §3 Dimension 2).
    Rule-adherence target: >= 80% directional alignment (analysis-bases.md §3).
    """
    parser = argparse.ArgumentParser(
        description="Analyze ArchegosCollapse RuleLLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)

    # Core analysis via Rule/analysis.py
    summary = analyze_archegos_collapse(data, config, output_dir)

    # RuleLLM-specific: rule-adherence analysis
    adherence = analyze_rule_adherence(data["investor_payloads"])
    summary["rule_adherence"] = adherence

    adherence_path = os.path.join(output_dir, "rule_adherence.json")
    with open(adherence_path, "w", encoding="utf-8") as fh:
        json.dump(adherence, fh, indent=2)

    agg = adherence.get("aggregate", {})
    if agg:
        print(f"Mean rule-adherence rate: {agg.get('mean_adherence_rate', 0):.1%}")

    return summary


__all__ = ["analyze_rule_adherence", "main"]

if __name__ == "__main__":
    main()
