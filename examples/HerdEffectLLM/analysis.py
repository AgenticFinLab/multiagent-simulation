"""HerdEffectLLM Analysis - LLM Reasoning Interpretability & Emergent Herding Metrics

This module extends HerdEffect analysis with LLM-specific interpretability features:
1. **Numerical Metrics**: Imported from HerdEffect.analysis
2. **Text Analysis**: LLM reasoning extraction, aggregation, and interpretability reports
3. **Per-Round Reports**: Consolidated view of all LLM decisions and reasoning chains
4. **Behavioral Pattern Analysis**: Detect reasoning patterns leading to herd behavior

Key Features:
- Extract LLM "reasoning" field from each investor decision
- Aggregate reasoning per round with market context
- Generate human-readable interpretability reports (Markdown)
- Analyze reasoning keywords and decision rationale
- Visualize reasoning-behavior correlations

Usage:
    python examples/HerdEffectLLM/analysis.py -c configs/HerdEffectLLM/simulation.yml

Output:
    - EXPERIMENT/HerdEffectLLM/analysis/ : Charts (PNG)
    - EXPERIMENT/HerdEffectLLM/analysis/text_analysis.md : Interpretability report
"""

import argparse
import json
import os
import glob
from collections import defaultdict
from typing import Dict, List, Any

import matplotlib
import numpy as np
import yaml

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Import numerical metrics from HerdEffect analysis
from examples.HerdEffect.analysis import (
    FUNDAMENTAL_VALUE,
    get_style_generator,
    load_config,
    load_messages,
    calculate_price_deviation,
    calculate_bid_convergence_cv,
    calculate_directional_agreement,
    calculate_cascade_measure,
    calculate_cross_sectional_std,
    calculate_rolling_volatility,
    calculate_bubble_magnitude,
    calculate_volume_metrics,
    calculate_autocorrelation,
    calculate_investor_correlation_matrix,
    plot_prices,
    plot_quantities,
    plot_price_deviation,
    plot_bid_convergence,
    plot_group_consensus,
    plot_volatility_analysis,
    plot_contagion_heatmap,
    plot_directional_agreement,
    plot_cascade_measure,
    plot_bubble_magnitude,
    plot_volume_analysis,
    plot_autocorrelation,
    plot_comprehensive_summary,
)


def get_paths_from_config(config: dict) -> tuple:
    """Extract data_dir and output_dir from config."""
    data_dir = config["communication"]["storage_path"]
    record_path = config["setting"]["record_path"]
    base_path = os.path.dirname(record_path)
    output_dir = os.path.join(base_path, "analysis")
    return data_dir, output_dir


# =============================================================================
# LLM-Specific Data Extraction (extends base extraction with reasoning)
# =============================================================================


def extract_llm_data(messages: list) -> dict:
    """
    Extract market prices, investor bids, AND LLM reasoning per round.

    Returns:
        {
            "market_price": {round: price},
            "market_data": {round: {price, volume, return, ...}},
            "investor_bids": {investor_id: {round: bid_price}},
            "investor_quantities": {investor_id: {round: quantity}},
            "investor_reasoning": {investor_id: {round: reasoning_text}},
            "investor_strategy": {investor_id: strategy_name},
            "round_orders": {round: [{investor, price, quantity, strategy, reasoning}, ...]}
        }
    """
    market_price = {}
    market_data = {}
    investor_bids = defaultdict(dict)
    investor_quantities = defaultdict(dict)
    investor_reasoning = defaultdict(dict)
    investor_strategy = {}
    round_orders = defaultdict(list)

    for msg in messages:
        sender = msg["sender_id"]
        payload = msg["payload"]
        content = payload["content"]
        content_type = payload["content_type"]
        round_num = msg["extras"]["round_num"]

        if content_type == "market_price" and sender == "market":
            market_price[round_num] = content["price"]
            market_data[round_num] = {
                "price": content["price"],
                "prev_price": content.get("prev_price", content["price"]),
                "return_pct": content.get("return_pct", 0),
                "volume": content.get("volume", 0),
                "net_demand": content.get("net_demand", 0),
            }

        elif content_type == "investor_bid":
            investor_bids[sender][round_num] = content["bid_price"]
            investor_quantities[sender][round_num] = content["quantity"]

            # Extract LLM reasoning
            reasoning = content.get("reasoning", "")
            investor_reasoning[sender][round_num] = reasoning

            # Track strategy
            strategy = content.get("strategy", "unknown")
            investor_strategy[sender] = strategy

            # Aggregate orders per round
            round_orders[round_num].append(
                {
                    "investor": sender,
                    "price": content["bid_price"],
                    "quantity": content["quantity"],
                    "strategy": strategy,
                    "reasoning": reasoning,
                    "cash": content.get("cash", 0),
                    "position": content.get("position", 0),
                }
            )

    return {
        "market_price": market_price,
        "market_data": dict(market_data),
        "investor_bids": dict(investor_bids),
        "investor_quantities": dict(investor_quantities),
        "investor_reasoning": dict(investor_reasoning),
        "investor_strategy": dict(investor_strategy),
        "round_orders": dict(round_orders),
    }


# =============================================================================
# LLM Text Analysis Functions (NEW - LLM-specific)
# =============================================================================


def analyze_reasoning_keywords(investor_reasoning: dict) -> dict:
    """
    Analyze keywords in LLM reasoning to detect behavioral patterns.

    Returns:
        {
            investor_id: {
                "buy_keywords": count,
                "sell_keywords": count,
                "trend_keywords": count,
                "value_keywords": count,
                "risk_keywords": count,
            }
        }
    """
    buy_words = [
        "buy",
        "bullish",
        "uptrend",
        "rising",
        "momentum",
        "opportunity",
        "long",
    ]
    sell_words = ["sell", "bearish", "downtrend", "falling", "decline", "exit", "short"]
    trend_words = [
        "trend",
        "momentum",
        "pattern",
        "signal",
        "continuation",
        "accelerat",
    ]
    value_words = [
        "fundamental",
        "overvalued",
        "undervalued",
        "fair value",
        "intrinsic",
    ]
    risk_words = ["risk", "volatil", "uncertain", "caution", "protect", "safe"]

    results = {}
    for investor_id, reasoning_per_round in investor_reasoning.items():
        counts = {
            "buy_keywords": 0,
            "sell_keywords": 0,
            "trend_keywords": 0,
            "value_keywords": 0,
            "risk_keywords": 0,
        }
        for round_num, reasoning in reasoning_per_round.items():
            text = reasoning.lower()
            for word in buy_words:
                if word in text:
                    counts["buy_keywords"] += 1
            for word in sell_words:
                if word in text:
                    counts["sell_keywords"] += 1
            for word in trend_words:
                if word in text:
                    counts["trend_keywords"] += 1
            for word in value_words:
                if word in text:
                    counts["value_keywords"] += 1
            for word in risk_words:
                if word in text:
                    counts["risk_keywords"] += 1
        results[investor_id] = counts

    return results


def classify_reasoning_action(reasoning: str) -> str:
    """Classify reasoning text into action category."""
    text = reasoning.lower()

    buy_signals = ["buy", "long", "bullish", "rising", "uptrend", "opportunity"]
    sell_signals = ["sell", "short", "bearish", "falling", "downtrend", "exit"]
    hold_signals = ["hold", "wait", "observe", "uncertain", "no action"]

    buy_score = sum(1 for w in buy_signals if w in text)
    sell_score = sum(1 for w in sell_signals if w in text)
    hold_score = sum(1 for w in hold_signals if w in text)

    if buy_score > sell_score and buy_score > hold_score:
        return "BUY"
    elif sell_score > buy_score and sell_score > hold_score:
        return "SELL"
    else:
        return "HOLD"


def generate_per_round_report(data: dict) -> str:
    """
    Generate detailed per-round text report with LLM reasoning.

    Format:
        ## Round N
        **Market State**: Price=$X, Return=+Y%, Volume=Z

        ### Investor Decisions
        | Investor | Strategy | Bid | Qty | Reasoning |
        |----------|----------|-----|-----|-----------|
    """
    report_lines = []
    report_lines.append("# HerdEffectLLM - Per-Round Interpretability Report\n")
    report_lines.append(
        "This report aggregates LLM investor decisions and reasoning per round.\n"
    )
    report_lines.append(
        "**Key**: Observe how LLM reasoning leads to behavioral convergence (herding).\n"
    )
    report_lines.append("---\n")

    rounds = sorted(data["round_orders"].keys())

    for round_num in rounds:
        orders = data["round_orders"][round_num]
        market = data["market_data"].get(round_num, {})

        # Round header
        report_lines.append(f"\n## Round {round_num}\n")

        # Market state
        if market:
            report_lines.append("### Market State\n")
            report_lines.append(f"- **Price**: ${market['price']:.2f}\n")
            report_lines.append(f"- **Return**: {market['return_pct']:+.2f}%\n")
            report_lines.append(f"- **Volume**: {market['volume']:.2f}\n")
            report_lines.append(f"- **Net Demand**: {market['net_demand']:+.2f}\n")
            report_lines.append(
                f"- **Deviation from Fundamental**: "
                f"{(market['price'] - FUNDAMENTAL_VALUE) / FUNDAMENTAL_VALUE * 100:+.2f}%\n"
            )

        # Investor decisions table
        report_lines.append("\n### LLM Investor Decisions\n")
        report_lines.append(
            "| Investor | Strategy | Bid ($) | Qty | Action | Reasoning |\n"
        )
        report_lines.append(
            "|----------|----------|---------|-----|--------|----------|\n"
        )

        for order in orders:
            investor = order["investor"].replace("investor_", "")
            strategy = order["strategy"]
            bid = order["price"]
            qty = order["quantity"]
            reasoning = (
                order["reasoning"][:80] + "..."
                if len(order["reasoning"]) > 80
                else order["reasoning"]
            )
            action = "BUY" if qty > 0 else ("SELL" if qty < 0 else "HOLD")

            report_lines.append(
                f"| {investor} | {strategy} | {bid:.2f} | {qty:+.1f} | {action} | {reasoning} |\n"
            )

        # Behavioral summary
        buy_count = sum(1 for o in orders if o["quantity"] > 0)
        sell_count = sum(1 for o in orders if o["quantity"] < 0)
        hold_count = sum(1 for o in orders if o["quantity"] == 0)
        total = len(orders)

        report_lines.append("\n### Behavioral Summary\n")
        report_lines.append(
            f"- **Buy**: {buy_count}/{total} ({buy_count/total*100:.0f}%)\n"
        )
        report_lines.append(
            f"- **Sell**: {sell_count}/{total} ({sell_count/total*100:.0f}%)\n"
        )
        report_lines.append(
            f"- **Hold**: {hold_count}/{total} ({hold_count/total*100:.0f}%)\n"
        )

        # Detect consensus
        if buy_count >= 0.8 * total:
            report_lines.append("- **HERDING DETECTED**: Strong BUY consensus!\n")
        elif sell_count >= 0.8 * total:
            report_lines.append("- **HERDING DETECTED**: Strong SELL consensus!\n")
        elif buy_count + sell_count == 0:
            report_lines.append("- All investors holding - market equilibrium.\n")

        report_lines.append("\n---\n")

    return "".join(report_lines)


def generate_reasoning_chain_analysis(data: dict) -> str:
    """
    Generate analysis of how LLM reasoning chains lead to herding.

    Traces the "thought process" across rounds for each investor type.
    """
    report_lines = []
    report_lines.append("\n# LLM Reasoning Chain Analysis\n")
    report_lines.append(
        "This section traces each investor's reasoning evolution across rounds.\n"
    )
    report_lines.append("---\n")

    # Group by investor
    for investor_id in sorted(data["investor_reasoning"].keys()):
        reasoning_per_round = data["investor_reasoning"][investor_id]
        strategy = data["investor_strategy"].get(investor_id, "unknown")
        bids = data["investor_bids"].get(investor_id, {})
        quantities = data["investor_quantities"].get(investor_id, {})

        report_lines.append(f"\n## {investor_id} ({strategy})\n")

        rounds = sorted(reasoning_per_round.keys())
        for r in rounds:
            reasoning = reasoning_per_round[r]
            bid = bids.get(r, 0)
            qty = quantities.get(r, 0)
            action = "BUY" if qty > 0 else ("SELL" if qty < 0 else "HOLD")

            report_lines.append(f"\n### Round {r}\n")
            report_lines.append(f"- **Action**: {action}\n")
            report_lines.append(f"- **Bid**: ${bid:.2f}\n")
            report_lines.append(f"- **Quantity**: {qty:+.2f}\n")
            report_lines.append(f"- **Reasoning**: {reasoning}\n")

        report_lines.append("\n---\n")

    return "".join(report_lines)


def generate_herding_interpretation(data: dict) -> str:
    """
    Generate high-level interpretation of emergent herding from LLM behavior.
    """
    report_lines = []
    report_lines.append("\n# Emergent Herding Interpretation\n")
    report_lines.append(
        "Analysis of how herding emerges from independent LLM reasoning.\n"
    )
    report_lines.append("---\n")

    # Calculate metrics
    cv_series = calculate_bid_convergence_cv(data["investor_bids"])
    agreement_series = calculate_directional_agreement(data["investor_bids"])
    cascade_series = calculate_cascade_measure(
        data["investor_bids"], data["market_price"]
    )

    # Keyword analysis
    keyword_analysis = analyze_reasoning_keywords(data["investor_reasoning"])

    # Summary statistics
    report_lines.append("\n## Numerical Herding Indicators\n")

    if cv_series:
        cv_values = list(cv_series.values())
        report_lines.append(
            f"- **Bid Convergence (CV)**: Avg={np.mean(cv_values):.4f}, Min={min(cv_values):.4f}\n"
        )
        report_lines.append(f"  - CV < 0.05 indicates strong herding\n")

    if agreement_series:
        agree_values = list(agreement_series.values())
        herding_rounds = sum(1 for v in agree_values if v > 0.8)
        report_lines.append(
            f"- **Directional Agreement**: Avg={np.mean(agree_values):.4f}, "
            f"Herding Rounds (DA>0.8)={herding_rounds}/{len(agree_values)}\n"
        )

    if cascade_series:
        cascade_values = list(cascade_series.values())
        report_lines.append(
            f"- **Information Cascade**: Avg={np.mean(cascade_values):.4f}\n"
        )

    # Reasoning keyword analysis
    report_lines.append("\n## LLM Reasoning Keyword Analysis\n")
    report_lines.append(
        "| Investor | Buy Keywords | Sell Keywords | Trend | Value | Risk |\n"
    )
    report_lines.append(
        "|----------|--------------|---------------|-------|-------|------|\n"
    )

    for investor_id, counts in keyword_analysis.items():
        label = investor_id.replace("investor_", "")
        report_lines.append(
            f"| {label} | {counts['buy_keywords']} | {counts['sell_keywords']} | "
            f"{counts['trend_keywords']} | {counts['value_keywords']} | {counts['risk_keywords']} |\n"
        )

    # Behavioral pattern interpretation
    report_lines.append("\n## Behavioral Pattern Interpretation\n")

    # Identify feedback investors (momentum + aggressive)
    feedback_investors = [
        inv
        for inv in data["investor_strategy"].keys()
        if "momentum" in inv.lower() or "aggressive" in inv.lower()
    ]

    if feedback_investors:
        report_lines.append("\n### Feedback Investors (Destabilizing)\n")
        for inv in feedback_investors:
            strategy = data["investor_strategy"][inv]
            keywords = keyword_analysis.get(inv, {})
            trend_count = keywords.get("trend_keywords", 0)
            report_lines.append(
                f"- **{inv}** ({strategy}): {trend_count} trend-following keywords detected\n"
            )

    # Identify stabilizing investors
    stabilizing_investors = [
        inv
        for inv in data["investor_strategy"].keys()
        if "contrarian" in inv.lower() or "risk" in inv.lower()
    ]

    if stabilizing_investors:
        report_lines.append("\n### Stabilizing Investors\n")
        for inv in stabilizing_investors:
            strategy = data["investor_strategy"][inv]
            keywords = keyword_analysis.get(inv, {})
            value_count = keywords.get("value_keywords", 0)
            risk_count = keywords.get("risk_keywords", 0)
            report_lines.append(
                f"- **{inv}** ({strategy}): {value_count} value keywords, {risk_count} risk keywords\n"
            )

    # Emergent herding conclusion
    report_lines.append("\n## Conclusion: Emergent Herding from LLM Reasoning\n")

    if cv_series and agreement_series:
        avg_cv = np.mean(list(cv_series.values()))
        avg_agree = np.mean(list(agreement_series.values()))

        if avg_cv < 0.1 and avg_agree > 0.6:
            report_lines.append(
                "**STRONG EMERGENT HERDING DETECTED**\n\n"
                "LLM investors independently converged on similar decisions despite having "
                "different system prompts (personalities). This demonstrates that herding can "
                "emerge from positive feedback dynamics without explicit imitation.\n"
            )
        elif avg_cv < 0.2 and avg_agree > 0.5:
            report_lines.append(
                "**MODERATE HERDING BEHAVIOR**\n\n"
                "LLM investors showed partial convergence. The feedback investors (Momentum, "
                "Aggressive) may have influenced price direction, but stabilizing forces "
                "(Contrarian, RiskAverse) partially dampened the effect.\n"
            )
        else:
            report_lines.append(
                "**WEAK OR NO HERDING**\n\n"
                "LLM investors maintained diverse behaviors. This could indicate that "
                "stabilizing investors were effective, or that the market conditions did not "
                "trigger positive feedback cascades.\n"
            )

    return "".join(report_lines)


# =============================================================================
# LLM-Specific Visualization Functions
# =============================================================================


def plot_reasoning_keyword_distribution(data: dict, output_path: str = None):
    """Plot reasoning keyword distribution per investor type."""
    keyword_analysis = analyze_reasoning_keywords(data["investor_reasoning"])

    if not keyword_analysis:
        print("No reasoning data for keyword analysis")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    investors = sorted(keyword_analysis.keys())
    labels = [inv.replace("investor_", "") for inv in investors]

    categories = [
        "buy_keywords",
        "sell_keywords",
        "trend_keywords",
        "value_keywords",
        "risk_keywords",
    ]
    colors = ["green", "red", "blue", "purple", "orange"]

    x = np.arange(len(investors))
    width = 0.15

    for i, (cat, color) in enumerate(zip(categories, colors)):
        values = [keyword_analysis[inv][cat] for inv in investors]
        ax.bar(
            x + i * width,
            values,
            width,
            label=cat.replace("_", " ").title(),
            color=color,
            alpha=0.7,
        )

    ax.set_ylabel("Keyword Count", fontsize=12)
    ax.set_title("LLM Reasoning Keyword Analysis by Investor Type", fontsize=14)
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {output_path}")
    plt.close()


def print_summary(data: dict):
    """Print comprehensive summary."""
    market_price = data["market_price"]
    investor_bids = data["investor_bids"]
    investor_reasoning = data["investor_reasoning"]

    print("\n" + "=" * 70)
    print("  HERDEFFECTLLM - LLM INTERPRETABILITY ANALYSIS")
    print("=" * 70)

    # Market stats
    prices = list(market_price.values())
    print(f"\n[1] MARKET PRICE")
    print(f"    Initial: ${prices[0]:.2f}")
    print(f"    Final:   ${prices[-1]:.2f}")
    print(f"    Max:     ${max(prices):.2f}")
    print(f"    Rounds:  {len(prices)}")

    # Herding metrics
    cv_series = calculate_bid_convergence_cv(investor_bids)
    if cv_series:
        cv_values = list(cv_series.values())
        print(f"\n[2] BID CONVERGENCE (CV)")
        print(f"    Avg CV: {np.mean(cv_values):.4f}")
        print(f"    Min CV: {min(cv_values):.4f}")

    agreement = calculate_directional_agreement(investor_bids)
    if agreement:
        agree_values = list(agreement.values())
        print(f"\n[3] DIRECTIONAL AGREEMENT")
        print(f"    Avg:    {np.mean(agree_values):.4f}")
        print(
            f"    DA>0.8: {sum(1 for v in agree_values if v > 0.8)}/{len(agree_values)} rounds"
        )

    # LLM reasoning stats
    print(f"\n[4] LLM REASONING COLLECTED")
    total_reasoning = sum(len(r) for r in investor_reasoning.values())
    print(f"    Total reasoning entries: {total_reasoning}")
    print(f"    Investors with reasoning: {len(investor_reasoning)}")

    # Keyword analysis
    keyword_analysis = analyze_reasoning_keywords(investor_reasoning)
    print(f"\n[5] REASONING KEYWORD SUMMARY")
    for inv_id, counts in keyword_analysis.items():
        label = inv_id.replace("investor_", "")
        print(
            f"    {label}: buy={counts['buy_keywords']}, sell={counts['sell_keywords']}, trend={counts['trend_keywords']}"
        )

    print("\n" + "=" * 70)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyze HerdEffectLLM simulation results"
    )
    parser.add_argument(
        "-c", "--config", required=True, help="Path to simulation config"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load config
    config = load_config(args.config)
    data_dir, output_dir = get_paths_from_config(config)

    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found: {data_dir}")
        print("Run the simulation first:")
        print(f"  python examples/HerdEffectLLM/run_herd_llm.py -c {args.config}")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Load data
    print(f"Loading messages from: {data_dir}")
    messages = load_messages(data_dir)
    print(f"Loaded {len(messages)} messages")

    data = extract_llm_data(messages)

    # Print summary
    print_summary(data)

    # Generate numerical charts
    print("\nGenerating charts...")
    plot_prices(data, os.path.join(output_dir, "01_price_chart.png"))
    plot_quantities(data, os.path.join(output_dir, "02_quantity_chart.png"))
    plot_bid_convergence(data, os.path.join(output_dir, "03_bid_convergence.png"))
    plot_directional_agreement(
        data, os.path.join(output_dir, "04_directional_agreement.png")
    )
    plot_reasoning_keyword_distribution(
        data, os.path.join(output_dir, "05_reasoning_keywords.png")
    )
    plot_comprehensive_summary(data, os.path.join(output_dir, "00_summary_panel.png"))

    # Generate text analysis report
    print("\nGenerating interpretability report...")
    text_report = []
    text_report.append(generate_per_round_report(data))
    text_report.append(generate_reasoning_chain_analysis(data))
    text_report.append(generate_herding_interpretation(data))

    report_path = os.path.join(output_dir, "text_analysis.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("".join(text_report))
    print(f"Saved: {report_path}")

    print(f"\n" + "=" * 60)
    print(f"HerdEffectLLM Analysis Complete!")
    print(f"Charts: {output_dir}")
    print(f"Text Report: {report_path}")
    print(f"=" * 60)
    print("\nGenerated outputs:")
    print("  00_summary_panel.png     - Comprehensive 6-panel summary")
    print("  01_price_chart.png       - Price & LLM investor bids")
    print("  02_quantity_chart.png    - Trading quantities")
    print("  03_bid_convergence.png   - Bid CV (herding indicator)")
    print("  04_directional_agreement.png - Behavioral alignment")
    print("  05_reasoning_keywords.png    - LLM reasoning keywords")
    print("  text_analysis.md         - Per-round interpretability report")


if __name__ == "__main__":
    main()
