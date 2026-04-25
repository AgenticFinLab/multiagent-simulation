#!/usr/bin/env python
"""AnchoringEffect RuleLLM Simulation Analysis

Implements analysis-bases.md for the RuleLLM variant.
Reuses all 8 metric functions from Rule/analysis.py and adds
Rule-Adherence Analysis (analysis-bases.md §3 Dimension 2).

RuleLLM-variant note (analysis-bases.md §4):
    Rule override events occur when LLM deviates from formula direction.
    Target: >= 80% directional alignment between LLM and Rule decisions.
    Quantity deviation ratio should cluster in [0.8, 1.2].

Usage:
    python examples/AnchoringEffect/RuleLLM/analysis.py \\
        -c configs/AnchoringEffect/RuleLLM/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config

from examples.AnchoringEffect.Rule.analysis import (
    _load_agent_records,
    _load_price_records,
    calculate_anchoring_bias_magnitude,
    calculate_anchoring_persistence,
    calculate_autocorrelation,
    calculate_max_drawdown,
    calculate_mean_abs_deviation,
    calculate_price_deviation,
    calculate_rolling_volatility,
    calculate_agent_volumes,
)


def analyze_rule_adherence(
    agent_records: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Compute rule-adherence rate for RuleLLM agents — analysis-bases.md §3 Dimension 2.

    Measures the fraction of rounds where the LLM's action direction matches
    what the embedded rule would prescribe (as recorded in the decision trace).

    A round is adherent if:
        - Both Rule and LLM output the same action (buy/sell/hold)

    Target: adherence_rate >= 0.80 (analysis-bases.md §3)

    Args:
        agent_records: Dict mapping agent_id to list of decision records.

    Returns:
        Dict with adherence stats per agent and aggregate.
    """
    adherence: Dict[str, Any] = {}

    for agent_id, records in agent_records.items():
        rule_actions = []
        llm_actions = []

        for record in records:
            rule_action = record.get("rule_action", None)
            llm_action = record.get("action", None)
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


def create_visualizations_rulellm(
    prices: List[float],
    fundamentals: List[float],
    agent_records: Dict[str, List[Dict[str, Any]]],
    adherence: Dict[str, Any],
    output_path: str,
) -> None:
    """Generate RuleLLM-variant analysis visualizations — analysis-bases.md §7.

    Produces 6 plots including a rule-adherence panel unique to RuleLLM.

    Args:
        prices: Market price time series.
        fundamentals: Fundamental value time series.
        agent_records: Per-agent decision records.
        adherence: Rule-adherence analysis results.
        output_path: Directory to write PNG files.
    """
    if not prices:
        return

    price_arr = np.array(prices)
    fund_arr = np.array(fundamentals)
    rounds = np.arange(len(prices))
    deviation = (price_arr - fund_arr) / fund_arr * 100

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        "AnchoringEffect RuleLLM Variant — Analysis", fontsize=14, fontweight="bold"
    )

    # Plot 1: Price vs. Fundamental
    axes[0, 0].plot(rounds, price_arr, label="Market Price", color="steelblue")
    axes[0, 0].plot(
        rounds, fund_arr, label="Fundamental Value", color="darkgreen", linestyle="--"
    )
    axes[0, 0].set_title("Price vs. Fundamental")
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Price")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: Price Deviation
    axes[0, 1].plot(rounds, deviation, color="crimson")
    axes[0, 1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[0, 1].axhline(
        y=3, color="orange", linestyle=":", alpha=0.7, label="3% threshold"
    )
    axes[0, 1].axhline(y=-3, color="orange", linestyle=":", alpha=0.7)
    axes[0, 1].set_title("Price Deviation from Fundamental (%)")
    axes[0, 1].set_xlabel("Round")
    axes[0, 1].set_ylabel("Deviation (%)")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: Rolling Volatility
    if len(prices) > 11:
        returns = np.diff(price_arr) / price_arr[:-1] * 100
        rolling_vols = [
            np.std(returns[max(0, i - 9) : i + 1]) for i in range(len(returns))
        ]
        axes[0, 2].plot(rounds[1:], rolling_vols, color="purple")
        axes[0, 2].set_title("Rolling Volatility (10-round window, %)")
        axes[0, 2].set_xlabel("Round")
        axes[0, 2].set_ylabel("Std Dev of Returns (%)")
        axes[0, 2].grid(True, alpha=0.3)

    # Plot 4: Rule-Adherence Rates (RuleLLM-specific)
    agent_ids = [k for k in adherence if k != "aggregate"]
    rates = [adherence[k].get("adherence_rate", 0.0) or 0.0 for k in agent_ids]
    if agent_ids:
        x_pos = np.arange(len(agent_ids))
        colors = ["green" if r >= 0.80 else "red" for r in rates]
        axes[1, 0].bar(x_pos, rates, color=colors, alpha=0.7)
        axes[1, 0].axhline(y=0.80, color="black", linestyle="--", label="80% target")
        axes[1, 0].set_xticks(x_pos)
        axes[1, 0].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=8)
        axes[1, 0].set_title("Rule-Adherence Rate by Agent")
        axes[1, 0].set_ylabel("Adherence Rate")
        axes[1, 0].set_ylim(0, 1.05)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

    # Plot 5: Agent-Type Trading Volume
    if agent_records:
        vol_agent_ids = list(agent_records.keys())
        buy_vols = []
        sell_vols = []
        for agent_id in vol_agent_ids:
            total_buy = sum(
                r.get("quantity", 0)
                for r in agent_records[agent_id]
                if r.get("action") == "buy"
            )
            total_sell = sum(
                r.get("quantity", 0)
                for r in agent_records[agent_id]
                if r.get("action") == "sell"
            )
            buy_vols.append(total_buy)
            sell_vols.append(total_sell)

        x_pos = np.arange(len(vol_agent_ids))
        axes[1, 1].bar(
            x_pos - 0.2, buy_vols, 0.4, label="Buy", color="green", alpha=0.7
        )
        axes[1, 1].bar(
            x_pos + 0.2, sell_vols, 0.4, label="Sell", color="red", alpha=0.7
        )
        axes[1, 1].set_xticks(x_pos)
        axes[1, 1].set_xticklabels(vol_agent_ids, rotation=30, ha="right", fontsize=8)
        axes[1, 1].set_title("Agent-Type Trading Volume")
        axes[1, 1].set_ylabel("Total Quantity")
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

    # Plot 6: Absolute Deviation — anchoring persistence
    abs_deviation = np.abs(deviation)
    axes[1, 2].plot(rounds, abs_deviation, color="darkorange", label="|Deviation|")
    if len(abs_deviation) > 0:
        half_target = abs_deviation[0] / 2.0
        axes[1, 2].axhline(
            y=half_target,
            color="grey",
            linestyle=":",
            alpha=0.7,
            label="Half-life target",
        )
    axes[1, 2].set_title("Anchoring Persistence (|Deviation| Decay)")
    axes[1, 2].set_xlabel("Round")
    axes[1, 2].set_ylabel("|Deviation| (%)")
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_path, "anchoringeffect_rulellm_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()


def main() -> None:
    """Run full AnchoringEffect RuleLLM analysis pipeline.

    Reuses all 8 metrics from Rule/analysis.py and adds Rule-Adherence Analysis.
    Rule-adherence target: >= 80% directional alignment (analysis-bases.md §3).
    """
    parser = argparse.ArgumentParser(
        description="Analyze AnchoringEffect RuleLLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/AnchoringEffect/RuleLLM/simulation.yml",
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_path = config["setting"]["record_path"]

    prices, fundamentals = _load_price_records(record_path)

    if not prices:
        print("No simulation data found. Run simulation first.")
        return

    agent_records = _load_agent_records(record_path)

    adjustment_factor = config.get("extras", {}).get("adjustment_factor", 0.3)

    # Compute all 8 metrics from analysis-bases.md §2
    price_deviation = calculate_price_deviation(prices, fundamentals)
    mad = calculate_mean_abs_deviation(prices, fundamentals)
    persistence = calculate_anchoring_persistence(prices, fundamentals)
    rolling_vol = calculate_rolling_volatility(prices)
    autocorr = calculate_autocorrelation(prices)
    max_drawdown = calculate_max_drawdown(prices)
    agent_volumes = calculate_agent_volumes(agent_records)
    bias_magnitude = calculate_anchoring_bias_magnitude(
        prices, fundamentals, adjustment_factor
    )

    # RuleLLM-specific: rule-adherence analysis
    adherence = analyze_rule_adherence(agent_records)

    analysis_path = os.path.join(record_path, "analysis")
    os.makedirs(analysis_path, exist_ok=True)

    create_visualizations_rulellm(
        prices, fundamentals, agent_records, adherence, analysis_path
    )

    summary = {
        "variant": "RuleLLM",
        "simulation": "AnchoringEffect",
        "rounds": len(prices),
        "metrics": {
            "price_deviation": price_deviation,
            "mean_absolute_deviation_pct": float(mad * 100),
            "anchoring_persistence": persistence,
            "rolling_volatility": rolling_vol,
            "return_autocorrelation_lag1": autocorr,
            "max_drawdown": max_drawdown,
            "agent_volumes": agent_volumes,
            "anchoring_bias_magnitude": float(bias_magnitude),
        },
        "rule_adherence": adherence,
    }

    summary_path = os.path.join(analysis_path, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    agent_volumes_path = os.path.join(analysis_path, "agent_volumes.json")
    with open(agent_volumes_path, "w", encoding="utf-8") as fh:
        json.dump(agent_volumes, fh, indent=2)

    adherence_path = os.path.join(analysis_path, "rule_adherence.json")
    with open(adherence_path, "w", encoding="utf-8") as fh:
        json.dump(adherence, fh, indent=2)

    print(f"Analysis complete. Results written to: {analysis_path}")
    print(f"MAD: {mad * 100:.2f}%")
    print(f"Half-life: {persistence['half_life_rounds']:.0f} rounds")
    print(f"Max drawdown: {max_drawdown['max_drawdown_pct']:.2f}%")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}")
    agg = adherence.get("aggregate", {})
    if agg:
        print(f"Mean rule-adherence rate: {agg.get('mean_adherence_rate', 0):.1%}")


if __name__ == "__main__":
    main()
