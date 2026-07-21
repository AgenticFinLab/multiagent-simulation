"""DispositionEffect RAG analysis.

The RAG variant reuses the shared DispositionEffect financial metrics and adds a
retrieval-health summary over recorded RAG context payloads when present.
"""

import argparse
import json
import os
import shutil
from typing import Any, Dict, List

import matplotlib.pyplot as plt
from masim.utils import load_config
from masim.evaluation import write_universal_summary

from examples.DispositionEffect.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from examples.DispositionEffect.Rag.players import _RAG_FALLBACK


def write_standard_artifacts(output_dir: str, summary: Dict[str, Any]) -> None:
    """Add simulation-180 standard analysis filenames without removing rich plots."""
    aliases = {
        "fig1_price_dynamics.png": "01_price_dynamics.png",
        "fig2_pgr_plr_comparison.png": "02_pgr_plr_comparison.png",
    }
    for src_name, dst_name in aliases.items():
        src = os.path.join(output_dir, src_name)
        dst = os.path.join(output_dir, dst_name)
        if not os.path.isfile(src):
            raise FileNotFoundError(f"missing required analysis figure: {src}")
        shutil.copyfile(src, dst)

    rag_stats = summary["rag_knowledge_effect"]
    disposition = summary["disposition_metrics"]
    with open(os.path.join(output_dir, "rag_stats.json"), "w", encoding="utf-8") as f:
        json.dump(rag_stats, f, indent=2)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axis("off")
    lines = [
        "DispositionEffect Rag Summary",
        f"Disposition detected: {summary['disposition_effect_detected']}",
        f"PGR: {disposition['pgr']:.3f}",
        f"PLR: {disposition['plr']:.3f}",
        f"Disposition coefficient: {disposition['disposition_coefficient']:.3f}",
        f"RAG retrieval rate: {rag_stats['retrieval_rate']:.1%}",
        f"RAG fallback rate: {rag_stats['fallback_rate']:.1%}",
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

    retrieved_payloads = context_payloads - fallback_payloads
    context_rate = context_payloads / total_payloads
    retrieval_rate = retrieved_payloads / total_payloads
    fallback_rate = fallback_payloads / total_payloads
    return {
        "total_payloads": total_payloads,
        "context_payloads": context_payloads,
        "retrieved_payloads": retrieved_payloads,
        "fallback_payloads": fallback_payloads,
        "context_rate": context_rate,
        "retrieval_rate": retrieval_rate,
        "fallback_rate": fallback_rate,
        "target_met": retrieval_rate >= 0.70,
    }


def holding_period_asymmetry(
    trades: List[Dict[str, Any]],
    initial_position: float,
    initial_purchase_price: float,
) -> Dict[str, float]:
    """Calculate quantity-weighted loser/winner holding-period asymmetry (FIFO)."""
    lots: List[List[float]] = [[initial_position, initial_purchase_price, 0.0]]
    winner_rounds = 0.0
    winner_quantity = 0.0
    loser_rounds = 0.0
    loser_quantity = 0.0

    for trade in sorted(trades, key=lambda item: item["round"]):
        quantity = float(trade["quantity"])
        price = float(trade["bid_price"])
        round_num = float(trade["round"])
        if quantity > 0:
            lots.append([quantity, price, round_num])
            continue
        remaining = abs(quantity)
        while remaining > 0 and lots:
            lot_quantity, lot_price, opened_round = lots[0]
            realized = min(remaining, lot_quantity)
            held_rounds = max(0.0, round_num - opened_round)
            if price > lot_price:
                winner_rounds += held_rounds * realized
                winner_quantity += realized
            elif price < lot_price:
                loser_rounds += held_rounds * realized
                loser_quantity += realized
            lot_quantity -= realized
            remaining -= realized
            if lot_quantity == 0:
                lots.pop(0)
            else:
                lots[0][0] = lot_quantity

    avg_winner = winner_rounds / winner_quantity if winner_quantity else 0.0
    avg_loser = loser_rounds / loser_quantity if loser_quantity else 0.0
    ratio = avg_loser / avg_winner if avg_winner > 0 else 0.0
    return {
        "avg_winner_holding_rounds": avg_winner,
        "avg_loser_holding_rounds": avg_loser,
        "holding_period_asymmetry": ratio,
    }


def terminal_wealth(
    trades: List[Dict[str, Any]],
    final_price: float,
    initial_cash: float,
    initial_position: float,
) -> float:
    """Reconstruct terminal mark-to-market wealth from signed trade quantities."""
    cash = initial_cash
    position = initial_position
    for trade in trades:
        quantity = float(trade["quantity"])
        price = float(trade["bid_price"])
        cash -= quantity * price
        position += quantity
    return cash + position * final_price


def calculate_extended_metrics(
    data: Dict[str, Any], config: Dict[str, Any], strategy_results: Dict[str, Dict]
) -> Dict[str, Any]:
    """Implement analysis-bases.md §2.5–§2.7 for the Rag variant."""
    holding_periods: Dict[str, Dict[str, float]] = {}
    wealth: Dict[str, float] = {}
    disposition_wealth: List[float] = []
    rational_wealth: List[float] = []
    disposition_plr: List[float] = []
    tax_plr: List[float] = []

    for player_id, trades in data["trades"].items():
        extras = config["players"][player_id]["config"]["extras"]
        initial_cash = float(extras["initial_cash"])
        initial_position = float(extras["initial_position"])
        initial_purchase_price = float(extras["initial_purchase_price"])
        holding_periods[player_id] = holding_period_asymmetry(
            trades, initial_position, initial_purchase_price
        )
        wealth[player_id] = terminal_wealth(
            trades, float(data["prices"][-1]), initial_cash, initial_position
        )

        strategy = strategy_results[player_id]["strategy"].lower()
        if "disposition" in strategy:
            disposition_wealth.append(wealth[player_id])
            disposition_plr.append(float(strategy_results[player_id]["plr"]))
        elif "rational" in strategy:
            rational_wealth.append(wealth[player_id])
        elif "tax" in strategy:
            tax_plr.append(float(strategy_results[player_id]["plr"]))

    if not disposition_wealth or not rational_wealth:
        raise ValueError("Disposition and rational wealth are required for PDI")
    mean_disposition = sum(disposition_wealth) / len(disposition_wealth)
    mean_rational = sum(rational_wealth) / len(rational_wealth)
    pdi = (
        (mean_rational - mean_disposition) / mean_rational
        if mean_rational != 0
        else 0.0
    )
    mean_disposition_plr = sum(disposition_plr) / len(disposition_plr)
    mean_tax_plr = sum(tax_plr) / len(tax_plr) if tax_plr else 0.0
    tri = (
        mean_tax_plr / mean_disposition_plr
        if mean_disposition_plr > 0
        else 0.0
    )
    return {
        "holding_periods": holding_periods,
        "terminal_wealth": wealth,
        "performance_drag_index": pdi,
        "tax_reversal_index": tri,
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
    summary["extended_metrics"] = calculate_extended_metrics(
        data, config, strategy_results
    )

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
        scenario='DispositionEffect',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


if __name__ == "__main__":
    main()


__all__ = [
    "_RAG_FALLBACK",
    "analyze_rag_knowledge_effect",
    "holding_period_asymmetry",
    "terminal_wealth",
    "calculate_extended_metrics",
    "write_standard_artifacts",
    "main",
]
