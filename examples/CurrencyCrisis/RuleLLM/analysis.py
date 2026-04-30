#!/usr/bin/env python
"""CurrencyCrisis RuleLLM Simulation Analysis

RuleLLM-variant analysis for the CurrencyCrisis simulation.
Reuses all metric/validation functions from Rule/analysis.py and adds
rule-adherence analysis comparing LLM decisions with Rule prescriptions.

Usage:
    python examples/CurrencyCrisis/RuleLLM/analysis.py \
        -c configs/CurrencyCrisis/RuleLLM/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict

import numpy as np

from masim.utils import load_config, load_results

from examples.CurrencyCrisis.Rule.analysis import (
    _batch_to_rounds,
    _load_data,
    _validate_currency_crisis,
    _build_interpretation,
    analyze_currency_crisis,
)


def analyze_rule_adherence(
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Compute rule-adherence rate for RuleLLM agents — analysis-bases.md §5 RuleLLM.

    Measures the fraction of rounds where the LLM's action direction matches
    what the embedded rule would prescribe (as recorded in the decision trace).

    Target: adherence_rate >= 0.80 (analysis-bases.md §5)

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
            rule_action = payload["rule_action"]
            llm_action = payload["action"]
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
            if v["adherence_rate"] is not None
        ]
        if not rates:
            raise ValueError("No adherence rates collected - all agents failed")
        adherence["aggregate"] = {
            "mean_adherence_rate": float(np.mean(rates)),
            "min_adherence_rate": float(np.min(rates)),
            "target_80pct_met": all(r >= 0.80 for r in rates),
        }

    return adherence


def main() -> None:
    """Run full CurrencyCrisis RuleLLM analysis pipeline.

    Reuses all metrics from Rule/analysis.py via analyze_currency_crisis(),
    then adds rule-adherence analysis.
    """
    parser = argparse.ArgumentParser(
        description="Analyze CurrencyCrisis RuleLLM simulation results"
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

    summary = analyze_currency_crisis(data, config, output_dir)

    # Rule-adherence analysis
    adherence = analyze_rule_adherence(data["investor_payloads"])
    with open(
        os.path.join(output_dir, "rule_adherence.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(adherence, f, indent=2)

    return summary


__all__ = ["analyze_rule_adherence", "main"]

if __name__ == "__main__":
    main()
