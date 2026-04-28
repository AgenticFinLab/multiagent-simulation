#!/usr/bin/env python
"""AsianFinancialCrisis Rule Simulation Analysis

Validate and analyse AsianFinancialCrisis simulation results against
calibrated academic targets from analysis-bases.md §6.

Validation criteria (analysis-bases.md §6):
    [1] Max drawdown           [30%, 60%]   weight 0.35  Kaminsky & Reinhart 1999
    [2] Crisis onset round     [10, 20]     weight 0.30  Kaminsky & Reinhart 1999
    [3] Crisis velocity        > 2%/round   weight 0.20  Radelet & Sachs 1998
    [4] Return AC1 (crisis)    [0.25, 0.50] weight 0.15  Kaminsky & Reinhart 1999

Usage:
    python examples/AsianFinancialCrisis/Rule/analysis.py \\
        -c configs/AsianFinancialCrisis/Rule/simulation.yml
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _batch_to_rounds(values: list) -> Dict[int, float]:
    """Convert 0-based batch list to 1-based round dict."""
    return {i + 1: v for i, v in enumerate(values)}


def _load_data(results) -> Dict[str, Any]:
    """Load simulation data from masim results object.

    Args:
        results: masim SimulationResults object.

    Returns:
        Dict with keys: market_prices, fundamentals, investor_payloads.
    """
    market_prices: Dict[int, float] = {}
    fundamentals: Dict[int, float] = {}

    for player in results.players_by_role("coordinator").values():
        if "price" in player.batch_store_names:
            market_prices.update(_batch_to_rounds(player.batch("price").all()))
        if "fundamental" in player.batch_store_names:
            fundamentals.update(_batch_to_rounds(player.batch("fundamental").all()))

    investor_payloads: Dict[str, Dict[int, dict]] = {}
    for pid, player in results.players_by_role("player").items():
        payloads = player.turns.payloads()
        if payloads:
            investor_payloads[pid] = payloads

    return {
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "investor_payloads": investor_payloads,
    }


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------


def _compute_max_drawdown(prices: np.ndarray) -> float:
    """Compute peak-to-trough max drawdown as a percentage."""
    if len(prices) < 2:
        return 0.0
    peak = np.maximum.accumulate(prices)
    drawdown = (peak - prices) / np.where(peak > 0, peak, 1.0)
    return float(np.max(drawdown) * 100.0)


def _compute_crisis_onset(
    prices: np.ndarray, fundamentals: np.ndarray
) -> Optional[int]:
    """Return first round (1-based) where deviation < -10%."""
    if len(prices) == 0 or len(fundamentals) == 0:
        return None
    f0 = fundamentals[0] if fundamentals[0] > 0 else 100.0
    for i, p in enumerate(prices):
        if (p - f0) / f0 < -0.10:
            return i + 1  # 1-based
    return None


def _compute_crisis_velocity(prices: np.ndarray) -> float:
    """Compute maximum round-to-round absolute return (%) during crisis."""
    if len(prices) < 2:
        return 0.0
    returns = (
        np.abs(np.diff(prices) / np.where(prices[:-1] > 0, prices[:-1], 1.0)) * 100.0
    )
    return float(np.max(returns))


def _compute_rolling_ac1(returns: np.ndarray, window: int = 10) -> float:
    """Compute maximum rolling lag-1 autocorrelation over any window of crisis returns."""
    if len(returns) < window + 1:
        if len(returns) > 2:
            return float(np.corrcoef(returns[:-1], returns[1:])[0, 1])
        return 0.0
    best = 0.0
    for start in range(len(returns) - window):
        seg = returns[start : start + window]
        if len(seg) > 2:
            ac = float(np.corrcoef(seg[:-1], seg[1:])[0, 1])
            if not np.isnan(ac) and ac > best:
                best = ac
    return best


# ---------------------------------------------------------------------------
# Validation dataclass
# ---------------------------------------------------------------------------


@dataclass
class AsianFinancialCrisisValidationResult:
    """Structured validation result for an AsianFinancialCrisis simulation run."""

    is_valid: bool
    score: float
    criteria: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": round(self.score, 4),
            "criteria": self.criteria,
            "interpretation": self.interpretation,
        }


# ---------------------------------------------------------------------------
# Core validation
# ---------------------------------------------------------------------------


def _validate_asian_financial_crisis(
    max_drawdown_pct: float,
    crisis_onset_round: Optional[int],
    crisis_velocity_pct: float,
    ac1_crisis: float,
    total_rounds: int,
) -> AsianFinancialCrisisValidationResult:
    """Validate simulation output against analysis-bases.md §6 calibration targets.

    Scoring (each criterion 0–1, linear interpolation):
        [1] Max drawdown [30%, 60%]  weight 0.35  Kaminsky & Reinhart 1999
        [2] Crisis onset [10, 20]   weight 0.30  Kaminsky & Reinhart 1999
        [3] Velocity > 2%/round     weight 0.20  Radelet & Sachs 1998
        [4] AC1 (crisis) [0.25, 0.5] weight 0.15  Kaminsky & Reinhart 1999

    Args:
        max_drawdown_pct: Max drawdown (%).
        crisis_onset_round: First round where deviation < −10% (1-based), or None.
        crisis_velocity_pct: Max round-to-round absolute return (%).
        ac1_crisis: Peak rolling lag-1 autocorrelation during crisis phase.
        total_rounds: Total simulation rounds.

    Returns:
        AsianFinancialCrisisValidationResult with weighted Fit Score.
    """
    # --- [1] Max drawdown target [30%, 60%], weight 0.35 ---
    dd_lo, dd_hi = 30.0, 60.0
    if dd_lo <= max_drawdown_pct <= dd_hi:
        dd_score = 1.0
    elif max_drawdown_pct < dd_lo:
        dd_score = max(0.0, max_drawdown_pct / dd_lo)
    else:
        dd_score = max(0.0, 1.0 - (max_drawdown_pct - dd_hi) / dd_hi)

    # --- [2] Crisis onset [10, 20], weight 0.30 ---
    if crisis_onset_round is None:
        onset_score = 0.0
        onset_observed = "None (deviation never reached −10%)"
    else:
        onset_lo, onset_hi = 10, 20
        if onset_lo <= crisis_onset_round <= onset_hi:
            onset_score = 1.0
        elif crisis_onset_round < onset_lo:
            onset_score = max(0.0, float(crisis_onset_round) / onset_lo)
        else:
            onset_score = max(0.0, 1.0 - (crisis_onset_round - onset_hi) / onset_hi)
        onset_observed = f"round {crisis_onset_round}"

    # --- [3] Crisis velocity > 2%/round, weight 0.20 ---
    vel_target = 2.0
    vel_score = (
        min(1.0, crisis_velocity_pct / (vel_target * 2))
        if crisis_velocity_pct > 0
        else 0.0
    )
    if crisis_velocity_pct >= vel_target:
        vel_score = 1.0

    # --- [4] AC1 (crisis phase) [0.25, 0.50], weight 0.15 ---
    ac_lo, ac_hi = 0.25, 0.50
    if ac_lo <= ac1_crisis <= ac_hi:
        ac_score = 1.0
    elif ac1_crisis < ac_lo:
        ac_score = max(0.0, ac1_crisis / ac_lo) if ac_lo > 0 else 0.0
    else:
        ac_score = max(0.0, 1.0 - (ac1_crisis - ac_hi) / ac_hi)

    overall_score = (
        dd_score * 0.35 + onset_score * 0.30 + vel_score * 0.20 + ac_score * 0.15
    )
    is_valid = overall_score > 0.50 and max_drawdown_pct >= 15.0

    criteria = {
        "max_drawdown": {
            "observed": round(max_drawdown_pct, 2),
            "target_range": "[30%, 60%]",
            "score": round(dd_score, 3),
            "weight": 0.35,
            "citation": "Kaminsky & Reinhart 1999",
        },
        "crisis_onset_round": {
            "observed": onset_observed,
            "target_range": "[10, 20]",
            "score": round(onset_score, 3),
            "weight": 0.30,
            "citation": "Kaminsky & Reinhart 1999",
        },
        "crisis_velocity": {
            "observed": round(crisis_velocity_pct, 3),
            "target_range": "> 2.0% / round",
            "score": round(vel_score, 3),
            "weight": 0.20,
            "citation": "Radelet & Sachs 1998",
        },
        "ac1_crisis_phase": {
            "observed": round(ac1_crisis, 4),
            "target_range": "[0.25, 0.50]",
            "score": round(ac_score, 3),
            "weight": 0.15,
            "citation": "Kaminsky & Reinhart 1999",
        },
    }

    return AsianFinancialCrisisValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
    )


# ---------------------------------------------------------------------------
# Interpretation builder
# ---------------------------------------------------------------------------


def _build_interpretation(
    result: AsianFinancialCrisisValidationResult,
    max_drawdown_pct: float,
    crisis_onset_round: Optional[int],
    crisis_velocity_pct: float,
    ac1_crisis: float,
    total_rounds: int,
) -> str:
    """Build human-readable validation interpretation string."""
    status = "VALID" if result.is_valid else "INVALID"
    lines: List[str] = [
        f"=== ASIAN FINANCIAL CRISIS SIMULATION VALIDATION: {status} ===",
        f"Overall Fit Score: {result.score:.1%} (threshold: 50%)",
        "",
    ]

    # [1] Max drawdown
    dd = result.criteria["max_drawdown"]
    if max_drawdown_pct >= 30.0:
        dd_assess = (
            "PASS — drawdown within calibrated range (Kaminsky & Reinhart 1999: 30–60%)"
        )
    elif max_drawdown_pct >= 15.0:
        dd_assess = (
            "MARGINAL — crisis too mild; increase λ or HotMoneyFunder sell_ratio"
        )
    else:
        dd_assess = "FAIL — crisis depth insufficient; max drawdown < 15%"
    lines += [
        "[1] CRISIS DEPTH (MAX DRAWDOWN)",
        f"    Observed: {max_drawdown_pct:.1f}%   Expected: 30–60% (Kaminsky & Reinhart 1999)",
        f"    Score: {dd['score']:.3f}   Assessment: {dd_assess}",
        "",
    ]

    # [2] Crisis onset
    cr = result.criteria["crisis_onset_round"]
    if crisis_onset_round is None:
        onset_str = "None"
        onset_assess = "FAIL — deviation never reached −10%; crisis too shallow"
    elif 10 <= crisis_onset_round <= 20:
        onset_str = f"round {crisis_onset_round}"
        onset_assess = "PASS — onset within calibrated window (Kaminsky & Reinhart 1999: rounds 10–20)"
    elif crisis_onset_round < 10:
        onset_str = f"round {crisis_onset_round}"
        onset_assess = (
            "FAST — crisis onset early; reduce λ or HotMoneyFunder initial_position"
        )
    else:
        onset_str = f"round {crisis_onset_round}"
        onset_assess = (
            "SLOW — crisis onset late; increase λ or reduce reversal_threshold"
        )
    lines += [
        "[2] CRISIS ONSET TIMING",
        f"    Observed: {onset_str}   Expected: rounds 10–20 (Kaminsky & Reinhart 1999)",
        f"    Score: {cr['score']:.3f}   Assessment: {onset_assess}",
        "",
    ]

    # [3] Crisis velocity
    vel = result.criteria["crisis_velocity"]
    if crisis_velocity_pct >= 2.0:
        vel_assess = (
            "PASS — sudden-stop velocity confirmed (Radelet & Sachs 1998: > 2%/round)"
        )
    else:
        vel_assess = (
            "FAIL — crisis too gradual; increase λ or HotMoneyFunder sell_ratio"
        )
    lines += [
        "[3] CRISIS VELOCITY (MAX ROUND-TO-ROUND DROP)",
        f"    Observed: {crisis_velocity_pct:.2f}%/round   Expected: > 2.0% (Radelet & Sachs 1998)",
        f"    Score: {vel['score']:.3f}   Assessment: {vel_assess}",
        "",
    ]

    # [4] AC1
    ac = result.criteria["ac1_crisis_phase"]
    if ac1_crisis >= 0.25:
        ac_assess = "PASS — positive momentum autocorrelation during cascade (Kaminsky & Reinhart 1999)"
    else:
        ac_assess = "FAIL — cascade not self-reinforcing; check ContagionTrader composite signal"
    lines += [
        "[4] CONTAGION SELF-REINFORCEMENT (RETURN AC1 DURING CRISIS)",
        f"    Observed: {ac1_crisis:.4f}   Expected: 0.25–0.50 (Kaminsky & Reinhart 1999)",
        f"    Score: {ac['score']:.3f}   Assessment: {ac_assess}",
        "",
    ]

    # [SUMMARY]
    lines += [
        "[SUMMARY]",
        f"    Max Drawdown Score:       {result.criteria['max_drawdown']['score']:.3f} × 0.35",
        f"    Crisis Onset Score:       {result.criteria['crisis_onset_round']['score']:.3f} × 0.30",
        f"    Velocity Score:           {result.criteria['crisis_velocity']['score']:.3f} × 0.20",
        f"    AC1 Score:                {result.criteria['ac1_crisis_phase']['score']:.3f} × 0.15",
        f"    Fit Score: {result.score:.1%}",
        f"    Status: {'VALID — simulation reproduces 1997 Asian crisis dynamics' if result.is_valid else 'INVALID — calibration targets not met'}",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------------


def _create_visualizations(
    market_prices: Dict[int, float],
    fundamentals: Dict[int, float],
    investor_payloads: Dict[str, Dict[int, dict]],
    result: AsianFinancialCrisisValidationResult,
    output_dir: str,
) -> List[str]:
    """Generate three analysis plots.

    Plot 01: Price vs Fundamental + Deviation % (crisis threshold lines)
    Plot 02: Crisis Velocity (round returns) + Rolling Volatility
    Plot 03: Summary — Agent Volume by Type

    Returns:
        List of output file paths.
    """
    if not market_prices:
        return []

    rounds_sorted = sorted(market_prices.keys())
    prices = np.array([market_prices[r] for r in rounds_sorted])
    rounds = np.array(rounds_sorted)

    fund0 = 100.0
    if fundamentals:
        fund_sorted = [fundamentals.get(r, fund0) for r in rounds_sorted]
        fund_arr = np.array(fund_sorted)
    else:
        fund_arr = np.full_like(prices, fund0)

    returns = np.diff(prices) / np.where(prices[:-1] > 0, prices[:-1], 1.0) * 100.0
    deviation_pct = (prices - fund_arr) / np.where(fund_arr > 0, fund_arr, 1.0) * 100.0

    crisis_onset = result.criteria["crisis_onset_round"]["observed"]
    if isinstance(crisis_onset, str) and crisis_onset.startswith("round "):
        try:
            onset_round = int(crisis_onset.split()[-1])
        except ValueError:
            onset_round = None
    else:
        onset_round = None

    paths: List[str] = []

    # --- Plot 01: Price dynamics ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle(
        "AsianFinancialCrisis — Price Dynamics", fontsize=13, fontweight="bold"
    )

    ax1.plot(rounds, prices, color="firebrick", linewidth=1.8, label="Market Price")
    ax1.plot(
        rounds,
        fund_arr,
        color="navy",
        linestyle="--",
        linewidth=1.2,
        label="Fundamental",
    )
    if onset_round is not None and onset_round in market_prices:
        ax1.axvline(
            x=onset_round,
            color="darkorange",
            linestyle=":",
            linewidth=1.5,
            label=f"Crisis Onset (r{onset_round})",
        )
    ax1.set_ylabel("Price")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    ax2.plot(rounds, deviation_pct, color="purple", linewidth=1.5)
    ax2.axhline(y=0.0, color="black", linestyle="--", alpha=0.5)
    ax2.axhline(
        y=-5.0,
        color="gold",
        linestyle=":",
        alpha=0.8,
        linewidth=1.2,
        label="−5% (IMF trigger)",
    )
    ax2.axhline(
        y=-10.0,
        color="orange",
        linestyle=":",
        alpha=0.8,
        linewidth=1.2,
        label="−10% (crisis onset)",
    )
    ax2.axhline(
        y=-30.0,
        color="red",
        linestyle=":",
        alpha=0.8,
        linewidth=1.2,
        label="−30% (target low)",
    )
    ax2.set_ylabel("Deviation from Fundamental (%)")
    ax2.set_xlabel("Round")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    p01 = os.path.join(output_dir, "01_price_dynamics.png")
    plt.savefig(p01, dpi=150, bbox_inches="tight")
    plt.close()
    paths.append(p01)

    # --- Plot 02: Crisis dynamics ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
    fig.suptitle(
        "AsianFinancialCrisis — Crisis Dynamics", fontsize=13, fontweight="bold"
    )

    ret_rounds = rounds[1:]
    colors_ret = ["red" if r < 0 else "steelblue" for r in returns]
    ax1.bar(ret_rounds, returns, color=colors_ret, alpha=0.7, width=0.8)
    ax1.axhline(y=0, color="black", linestyle="--", alpha=0.5)
    ax1.axhline(
        y=-2.0,
        color="orange",
        linestyle=":",
        alpha=0.8,
        linewidth=1.2,
        label="−2% velocity target",
    )
    ax1.set_ylabel("Round Return (%)")
    ax1.set_title("Round Returns (Crisis Velocity Signal)")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    if len(returns) >= 5:
        window = min(10, len(returns))
        rolling_vol = [
            np.std(returns[max(0, i - window + 1) : i + 1]) for i in range(len(returns))
        ]
        ax2.plot(
            ret_rounds,
            rolling_vol,
            color="darkorange",
            linewidth=1.5,
            label=f"Rolling Volatility ({window}-round)",
        )
        ax2.axhline(
            y=2.0,
            color="red",
            linestyle=":",
            alpha=0.7,
            linewidth=1.2,
            label="2% threshold",
        )
        ax2.set_ylabel("Volatility (std of returns, %)")
        ax2.set_xlabel("Round")
        ax2.set_title("Rolling Volatility")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    p02 = os.path.join(output_dir, "02_crisis_dynamics.png")
    plt.savefig(p02, dpi=150, bbox_inches="tight")
    plt.close()
    paths.append(p02)

    # --- Plot 03: Summary — Agent Volume by Type ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("AsianFinancialCrisis — Agent Summary", fontsize=13, fontweight="bold")

    # Sub-plot A: Agent buy/sell volume
    if investor_payloads:
        agent_ids = sorted(investor_payloads.keys())
        buy_vols = []
        sell_vols = []
        for aid in agent_ids:
            b = sum(
                p.get("quantity", 0)
                for p in investor_payloads[aid].values()
                if p.get("quantity", 0) > 0
            )
            s = sum(
                abs(p.get("quantity", 0))
                for p in investor_payloads[aid].values()
                if p.get("quantity", 0) < 0
            )
            buy_vols.append(b)
            sell_vols.append(s)
        x_pos = np.arange(len(agent_ids))
        axes[0].bar(
            x_pos - 0.2, buy_vols, 0.4, label="Buy Volume", color="steelblue", alpha=0.8
        )
        axes[0].bar(
            x_pos + 0.2,
            sell_vols,
            0.4,
            label="Sell Volume",
            color="firebrick",
            alpha=0.8,
        )
        axes[0].set_xticks(x_pos)
        axes[0].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=8)
        axes[0].set_title("Agent Volume by Type")
        axes[0].set_ylabel("Total Quantity")
        axes[0].legend(fontsize=9)
        axes[0].grid(True, alpha=0.3)
    else:
        axes[0].text(
            0.5,
            0.5,
            "No agent data",
            ha="center",
            va="center",
            transform=axes[0].transAxes,
        )

    # Sub-plot B: Validation score summary
    crit_names = [
        "Max Drawdown\n[30%,60%]",
        "Crisis Onset\n[10,20]",
        "Velocity\n>2%/round",
        "AC1 Crisis\n[0.25,0.50]",
    ]
    crit_scores = [
        result.criteria["max_drawdown"]["score"],
        result.criteria["crisis_onset_round"]["score"],
        result.criteria["crisis_velocity"]["score"],
        result.criteria["ac1_crisis_phase"]["score"],
    ]
    crit_colors = [
        "green" if s >= 0.7 else "orange" if s >= 0.4 else "red" for s in crit_scores
    ]
    axes[1].bar(range(len(crit_names)), crit_scores, color=crit_colors, alpha=0.8)
    axes[1].axhline(
        y=0.7,
        color="black",
        linestyle="--",
        linewidth=1.2,
        label="Pass threshold (0.7)",
    )
    axes[1].set_xticks(range(len(crit_names)))
    axes[1].set_xticklabels(crit_names, fontsize=8)
    axes[1].set_ylim(0, 1.1)
    axes[1].set_title(f"Validation Criteria Scores\n(Fit Score: {result.score:.1%})")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    if onset_round is not None:
        axes[1].annotate(
            f"Onset: r{onset_round}",
            xy=(1, crit_scores[1]),
            xytext=(1.5, crit_scores[1] + 0.1),
            arrowprops=dict(arrowstyle="->", color="gray"),
            fontsize=8,
            color="gray",
        )

    plt.tight_layout()
    p03 = os.path.join(output_dir, "03_summary.png")
    plt.savefig(p03, dpi=150, bbox_inches="tight")
    plt.close()
    paths.append(p03)

    return paths


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def analyze_asian_financial_crisis(
    data: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Orchestrate full AsianFinancialCrisis analysis pipeline.

    Computes metrics, validates against calibration targets, builds
    interpretation text, generates three plots, prints Fit Score to console.

    Args:
        data: Output from _load_data().
        config: Parsed simulation config dict.
        output_dir: Directory to write PNG/JSON outputs.

    Returns:
        Summary dict with validation result and metrics.
    """
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    investor_payloads = data["investor_payloads"]

    if not market_prices:
        print("No simulation data found. Run simulation first.")
        return {}

    rounds_sorted = sorted(market_prices.keys())
    prices = np.array([market_prices[r] for r in rounds_sorted])
    fund0 = 100.0
    if fundamentals:
        fund_arr = np.array([fundamentals.get(r, fund0) for r in rounds_sorted])
    else:
        fund_arr = np.full_like(prices, fund0)

    total_rounds = len(rounds_sorted)

    max_drawdown_pct = _compute_max_drawdown(prices)
    crisis_onset_round = _compute_crisis_onset(prices, fund_arr)
    crisis_velocity_pct = _compute_crisis_velocity(prices)

    returns = np.diff(prices) / np.where(prices[:-1] > 0, prices[:-1], 1.0)
    ac1_crisis = _compute_rolling_ac1(returns, window=10)

    result = _validate_asian_financial_crisis(
        max_drawdown_pct=max_drawdown_pct,
        crisis_onset_round=crisis_onset_round,
        crisis_velocity_pct=crisis_velocity_pct,
        ac1_crisis=ac1_crisis,
        total_rounds=total_rounds,
    )

    interpretation = _build_interpretation(
        result=result,
        max_drawdown_pct=max_drawdown_pct,
        crisis_onset_round=crisis_onset_round,
        crisis_velocity_pct=crisis_velocity_pct,
        ac1_crisis=ac1_crisis,
        total_rounds=total_rounds,
    )
    result.interpretation = interpretation
    print(interpretation)

    _create_visualizations(
        market_prices=market_prices,
        fundamentals=fundamentals,
        investor_payloads=investor_payloads,
        result=result,
        output_dir=output_dir,
    )

    summary = result.to_dict()
    summary["metrics"] = {
        "max_drawdown_pct": round(max_drawdown_pct, 3),
        "crisis_onset_round": crisis_onset_round,
        "crisis_velocity_pct": round(crisis_velocity_pct, 3),
        "ac1_crisis_phase": round(ac1_crisis, 4),
        "total_rounds": total_rounds,
    }

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run AsianFinancialCrisis Rule analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze AsianFinancialCrisis Rule simulation results"
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
    summary = analyze_asian_financial_crisis(data, config, output_dir)
    return summary


__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "_validate_asian_financial_crisis",
    "_build_interpretation",
    "analyze_asian_financial_crisis",
]

if __name__ == "__main__":
    main()
