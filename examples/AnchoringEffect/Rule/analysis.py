#!/usr/bin/env python
"""AnchoringEffect Rule-Based Simulation Analysis

Analyzes simulation results for anchoring-induced price deviation and persistence.
Based on analysis-bases.md calibration targets (Campbell & Sharpe 2009).

Usage:
    python examples/AnchoringEffect/Rule/analysis.py \
        -c configs/AnchoringEffect/Rule/simulation.yml
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _batch_to_rounds(values: list) -> Dict[int, float]:
    """Convert batch store list to {round_num: value}, round_num is 1-based."""
    return {i + 1: v for i, v in enumerate(values)}


def _load_data(results) -> Dict[str, Any]:
    """Load price/fundamental batch stores and investor turn payloads.

    Returns
    -------
    dict with keys:
        market_prices       : {round_num: float}
        fundamentals        : {round_num: float}
        investor_quantities : {player_id: {round_num: float}}
        investor_bids       : {player_id: {round_num: float}}
        investor_payloads   : {player_id: {round_num: dict}}
    """
    market_prices: Dict[int, float] = {}
    fundamentals: Dict[int, float] = {}

    for player in results.players_by_role("coordinator").values():
        if "price" in player.batch_store_names:
            market_prices.update(_batch_to_rounds(player.batch("price").all()))
        if "fundamental" in player.batch_store_names:
            fundamentals.update(_batch_to_rounds(player.batch("fundamental").all()))

    investor_quantities: Dict[str, Dict[int, float]] = {}
    investor_bids: Dict[str, Dict[int, float]] = {}
    investor_payloads: Dict[str, Dict[int, dict]] = {}
    for pid, player in results.players_by_role("player").items():
        qty = player.turns.field("quantity")
        if qty:
            investor_quantities[pid] = qty
        bid = player.turns.field("bid_price")
        if bid:
            investor_bids[pid] = bid
        payloads = player.turns.payloads()
        if payloads:
            investor_payloads[pid] = payloads

    return {
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "investor_quantities": investor_quantities,
        "investor_bids": investor_bids,
        "investor_payloads": investor_payloads,
    }


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _compute_mad(prices_list: List[float], fundamental: float) -> float:
    """Mean Absolute Deviation: mean(|P(t) - F| / F)."""
    if not prices_list:
        raise ValueError("Cannot compute MAD without market prices.")
    if fundamental == 0:
        raise ValueError("Cannot compute MAD with zero fundamental value.")
    return float(np.mean(np.abs(np.array(prices_list) - fundamental) / fundamental))


def calculate_price_deviation(
    market_prices: Dict[int, float],
    fundamentals: Dict[int, float],
) -> List[float]:
    """Return signed price deviations aligned by round."""
    if not market_prices:
        raise ValueError("Cannot compute price deviation without market prices.")
    if not fundamentals:
        raise ValueError("Cannot compute price deviation without fundamentals.")

    deviations: List[float] = []
    for round_num in sorted(market_prices.keys()):
        price = market_prices[round_num]
        fundamental = fundamentals[round_num]
        if fundamental == 0:
            raise ValueError(f"Fundamental value is zero at round {round_num}.")
        deviations.append((price - fundamental) / fundamental)
    return deviations


def _compute_half_life(prices_list: List[float], fundamental: float) -> float:
    """Number of rounds for |deviation| to fall to half its initial value.

    Returns total_rounds if the deviation never decays to half.
    """
    if not prices_list:
        raise ValueError("Cannot compute half-life without market prices.")
    if fundamental == 0:
        raise ValueError("Cannot compute half-life with zero fundamental value.")

    devs = np.abs((np.array(prices_list) - fundamental) / fundamental)
    initial_dev = float(devs[0])
    if initial_dev == 0:
        return 0.0

    half_target = initial_dev / 2.0
    for idx, dev in enumerate(devs):
        if dev <= half_target:
            return float(idx)
    return float(len(prices_list))


def _compute_autocorrelation(prices_list: List[float], lag: int = 1) -> float:
    """Lag-1 autocorrelation of returns."""
    arr = np.array(prices_list)
    if len(arr) < lag + 2:
        raise ValueError("Cannot compute autocorrelation with insufficient prices.")
    returns = np.diff(arr) / arr[:-1]
    n = len(returns)
    if n <= lag:
        raise ValueError("Cannot compute autocorrelation with insufficient returns.")
    mu = np.mean(returns)
    centered = returns - mu
    autocov = np.mean(centered[: n - lag] * centered[lag:])
    var = np.var(centered)
    if var < 1e-12:
        raise ValueError("Cannot compute autocorrelation with zero return variance.")
    return float(autocov / var)


def _compute_max_drawdown(prices_list: List[float]) -> float:
    """Maximum peak-to-trough drawdown (%, negative value)."""
    arr = np.array(prices_list)
    if len(arr) < 2:
        raise ValueError("Cannot compute max drawdown with fewer than two prices.")
    peak = arr[0]
    max_dd = 0.0
    for price in arr:
        if price > peak:
            peak = price
        dd = (peak - price) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
    return float(-max_dd * 100)  # negative %


def _compute_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> List[float]:
    """Rolling volatility of returns (std dev per window)."""
    arr = np.array(prices_list)
    if len(arr) < 2:
        raise ValueError("Cannot compute rolling volatility with fewer than two prices.")
    returns = np.diff(arr) / arr[:-1] * 100
    vols = []
    for i in range(len(returns)):
        start = max(0, i - window + 1)
        vols.append(float(np.std(returns[start : i + 1])))
    return vols


def _compute_bias_magnitude(
    prices_list: List[float], fundamental: float, adjustment_factor: float
) -> float:
    """Mean anchoring bias magnitude: (1-α) × |anchor - F| / F."""
    if not prices_list:
        raise ValueError("Cannot compute bias magnitude without market prices.")
    if fundamental == 0:
        raise ValueError("Cannot compute bias magnitude with zero fundamental value.")
    anchor = prices_list[0]
    return float(abs(1 - adjustment_factor) * abs(anchor - fundamental) / fundamental)


def _get_adjustment_factor(config: dict) -> float:
    """Read the AnchoredTrader adjustment factor from a variant config."""
    players = config["players"]
    for player_cfg in players.values():
        if "config" not in player_cfg:
            continue
        extras = player_cfg["config"]["extras"]
        if "adjustment_factor" in extras:
            return float(extras["adjustment_factor"])
    raise ValueError("No adjustment_factor found in AnchoringEffect player configs.")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass
class AnchoringValidationResult:
    """Result of AnchoringEffect simulation validation."""

    is_valid: bool
    score: float  # 0–1 overall fit score
    criteria: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": round(self.score, 4),
            "criteria": self.criteria,
            "interpretation": self.interpretation,
        }


def _validate_anchoring_effect(
    mad_pct: float,
    half_life: float,
    max_drawdown_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
) -> AnchoringValidationResult:
    """Validate AnchoringEffect results against analysis-bases.md §6 calibration targets.

    Criteria
    --------
    1. MAD          target [3%, 10%]      weight 0.40  (Campbell & Sharpe 2009)
    2. Half-life    target [20, 60] rounds weight 0.40  (Campbell & Sharpe 2009)
    3. Max drawdown target [5%, 20%]       weight 0.20  (anchoring correction, not crash)
    """
    criteria = {}

    # --- Criterion 1: MAD in [3%, 10%] ---
    if 3.0 <= mad_pct <= 10.0:
        mad_score = 1.0
    elif 1.0 <= mad_pct < 3.0:
        mad_score = 0.4 + (mad_pct - 1.0) / 2.0 * 0.6
    elif 10.0 < mad_pct <= 20.0:
        mad_score = 1.0 - (mad_pct - 10.0) / 10.0 * 0.5
    elif mad_pct > 20.0:
        mad_score = 0.2
    else:
        mad_score = mad_pct / 3.0 * 0.4

    criteria["mad"] = {
        "value": round(mad_pct, 3),
        "target": "3–10%",
        "score": round(mad_score, 3),
        "passed": 1.0 <= mad_pct <= 20.0,
    }

    # --- Criterion 2: Half-life in [20, 60] rounds ---
    if 20.0 <= half_life <= 60.0:
        hl_score = 1.0
    elif 10.0 <= half_life < 20.0:
        hl_score = 0.5 + (half_life - 10.0) / 10.0 * 0.5
    elif 60.0 < half_life <= 100.0:
        hl_score = 1.0 - (half_life - 60.0) / 40.0 * 0.5
    elif half_life > 100.0:
        hl_score = 0.3
    else:
        hl_score = half_life / 20.0 * 0.5

    criteria["half_life"] = {
        "value": round(half_life, 1),
        "target": "20–60 rounds",
        "score": round(hl_score, 3),
        "passed": 5.0 <= half_life <= total_rounds,
    }

    # --- Criterion 3: Max drawdown in [5%, 20%] (absolute value) ---
    abs_dd = abs(max_drawdown_pct)
    if 5.0 <= abs_dd <= 20.0:
        dd_score = 1.0
    elif 2.0 <= abs_dd < 5.0:
        dd_score = 0.4 + (abs_dd - 2.0) / 3.0 * 0.6
    elif 20.0 < abs_dd <= 40.0:
        dd_score = 1.0 - (abs_dd - 20.0) / 20.0 * 0.7
    elif abs_dd > 40.0:
        dd_score = 0.1
    else:
        dd_score = abs_dd / 5.0 * 0.4

    criteria["max_drawdown"] = {
        "value": round(max_drawdown_pct, 3),
        "target": "−5% to −20%",
        "score": round(dd_score, 3),
        "passed": 2.0 <= abs_dd <= 40.0,
    }

    overall_score = mad_score * 0.40 + hl_score * 0.40 + dd_score * 0.20
    is_valid = overall_score > 0.50 and mad_pct >= 1.0

    interpretation = _build_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        mad_pct=mad_pct,
        half_life=half_life,
        max_drawdown_pct=max_drawdown_pct,
        autocorr_lag1=autocorr_lag1,
        total_rounds=total_rounds,
        mad_score=mad_score,
        hl_score=hl_score,
        dd_score=dd_score,
    )

    return AnchoringValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def _build_interpretation(
    is_valid: bool,
    overall_score: float,
    mad_pct: float,
    half_life: float,
    max_drawdown_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
    mad_score: float,
    hl_score: float,
    dd_score: float,
) -> str:
    lines = []
    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== ANCHORING EFFECT SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # [1] MAD
    lines.append("[1] MISPRICING MAGNITUDE (MAD)")
    lines.append(f"    Observed: MAD = {mad_pct:.2f}% across all rounds")
    lines.append(
        "    Expected: 3–10% (Campbell & Sharpe 2009: analyst forecast errors ~3–8%)"
    )
    lines.append(f"    Score: {mad_score:.1%}")
    if mad_pct < 1.0:
        lines.append(
            "    Assessment: NEGLIGIBLE — Anchoring has virtually no market effect."
        )
        lines.append(
            "    Check adjustment_factor (should be < 0.7) and that AnchoredTrader is trading."
        )
    elif mad_pct < 3.0:
        lines.append(
            "    Assessment: WEAK — Anchoring effect present but below calibration target."
        )
        lines.append(
            "    Consider reducing adjustment_factor or adding more anchoring agents."
        )
    elif mad_pct <= 10.0:
        lines.append(
            "    Assessment: OPTIMAL — MAD within calibrated target range [3%, 10%]."
        )
        lines.append(
            "    Consistent with Campbell & Sharpe (2009) analyst forecast error magnitudes."
        )
    elif mad_pct <= 20.0:
        lines.append(
            "    Assessment: ELEVATED — Anchoring stronger than typical literature estimates."
        )
        lines.append(
            "    Consider increasing adjustment_factor toward 0.5 or reducing price_impact."
        )
    else:
        lines.append("    Assessment: EXCESSIVE — Unrealistically large mispricing.")
        lines.append(
            "    Check mean_reversion (gamma) parameter; may need to increase toward 0.02."
        )
    lines.append("")

    # [2] Half-life
    lines.append("[2] ANCHORING PERSISTENCE (HALF-LIFE)")
    lines.append(
        f"    Observed: Deviation decayed to half its initial value in {half_life:.0f} rounds"
    )
    lines.append(
        "    Expected: 20–60 rounds (Campbell & Sharpe 2009: quarterly persistence)"
    )
    lines.append(f"    Score: {hl_score:.1%}")
    if half_life < 5.0:
        lines.append(
            "    Assessment: TOO FAST — Near-rational market; anchoring corrects trivially quickly."
        )
        lines.append(
            "    Possible cause: too many RationalUpdater agents or gamma too high."
        )
    elif half_life < 20.0:
        lines.append(
            "    Assessment: FASTER THAN TARGET — Correction rate above calibration target."
        )
        lines.append(
            "    Consider increasing anchor_weight or reducing RationalUpdater count."
        )
    elif half_life <= 60.0:
        lines.append(
            "    Assessment: OPTIMAL — Half-life within [20, 60] round target."
        )
        lines.append(
            "    Consistent with quarterly earnings forecast persistence documented by Campbell & Sharpe."
        )
    elif half_life <= 100.0:
        lines.append(
            "    Assessment: SLOW CORRECTION — Anchoring persists beyond target range."
        )
        lines.append(
            "    Consider increasing gamma (mean_reversion) toward 0.015–0.02."
        )
    else:
        lines.append(
            "    Assessment: VERY PERSISTENT — Deviation may not revert within simulation horizon."
        )
        lines.append(
            "    Increase gamma significantly or extend simulation to 200+ rounds."
        )
    lines.append("")

    # [3] Max drawdown
    abs_dd = abs(max_drawdown_pct)
    lines.append("[3] CORRECTION DYNAMICS (MAX DRAWDOWN)")
    lines.append(f"    Observed: Maximum price drawdown of {max_drawdown_pct:.2f}%")
    lines.append(
        "    Expected: −5% to −20% (anchoring-driven gradual correction, not a crash)"
    )
    lines.append(f"    Score: {dd_score:.1%}")
    if abs_dd < 2.0:
        lines.append(
            "    Assessment: INSUFFICIENT — Prices barely corrected toward fundamental."
        )
        lines.append(
            "    Anchoring effect too strong; rational correction forces too weak."
        )
    elif abs_dd < 5.0:
        lines.append(
            "    Assessment: MILD — Some correction observed but below target range."
        )
        lines.append("    Consider extending simulation rounds for fuller convergence.")
    elif abs_dd <= 20.0:
        lines.append(
            "    Assessment: OPTIMAL — Gradual correction consistent with anchoring literature."
        )
        lines.append(
            "    Northcraft & Neale (1987): expert anchoring → 5–20% correction from peak."
        )
    elif abs_dd <= 40.0:
        lines.append(
            "    Assessment: ELEVATED CORRECTION — Larger than typical anchoring-driven drawdown."
        )
        lines.append(
            "    May indicate MomentumTrader or NoiseTrader over-correction; check noise_std."
        )
    else:
        lines.append(
            "    Assessment: CRASH-SCALE — Drawdown magnitude inappropriate for anchoring scenario."
        )
        lines.append(
            "    Check for parameter miscalibration; reduce NoiseTrader max_order or aggressiveness."
        )
    lines.append("")

    # [SUMMARY]
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            "The simulation successfully reproduces anchoring-driven price dynamics:"
        )
        lines.append(
            "persistent mispricing above fundamental followed by gradual mean reversion."
        )
        lines.append(
            "Results are consistent with Campbell & Sharpe (2009) and Tversky & Kahneman (1974)."
        )
    else:
        missing = []
        if mad_pct < 1.0:
            missing.append("insufficient mispricing (MAD < 1%)")
        if half_life < 5.0 or half_life > total_rounds * 0.9:
            missing.append("half-life outside feasible range")
        if overall_score <= 0.5:
            missing.append("overall fit score below 50%")
        lines.append("The simulation does not fully reproduce anchoring dynamics.")
        if missing:
            lines.append(f"Key issues: {', '.join(missing)}.")
        lines.append(
            "Consider reviewing adjustment_factor, gamma, and agent composition."
        )
    lines.append(f"Fit Score: {overall_score:.1%}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------


def _create_visualizations(
    market_prices: Dict[int, float],
    fundamentals: Dict[int, float],
    investor_bids: Dict[str, Dict[int, float]],
    investor_payloads: Dict[str, Dict[int, dict]],
    rolling_vols: List[float],
    half_life: float,
    output_dir: str,
) -> None:
    """Generate analysis plots saved to output_dir.

    Plots
    -----
    00_investor_bids.png   : Primary overview — market price + each investor's
                             bid price over rounds (the "headline" chart).
    01_price_dynamics.png  : Price vs Fundamental + Deviation %.
    02_market_dynamics.png : Rolling Volatility + Return Distribution.
    03_summary.png         : Agent Trading Volume + Anchoring Persistence.
    """
    if not market_prices:
        return

    os.makedirs(output_dir, exist_ok=True)
    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    fund_value = (
        sum(fundamentals.values()) / len(fundamentals)
        if fundamentals
        else prices_list[0]
    )
    deviation_pct = [(p - fund_value) / fund_value * 100 for p in prices_list]
    round_arr = np.array(rounds_sorted)

    _BID_COLORS = [
        "#3a86ff",
        "#ff006e",
        "#8338ec",
        "#06d6a0",
        "#fb5607",
        "#ff595e",
        "#1982c4",
        "#6a4c93",
        "#ffca3a",
        "#8ac926",
        "#e07a5f",
        "#3d405b",
        "#81b29a",
        "#f2cc8f",
        "#264653",
        "#e63946",
        "#457b9d",
        "#2a9d8f",
        "#e9c46a",
        "#f4a261",
    ]

    # --- Plot 0: Investor Bid Curves (PRIMARY headline chart) ---
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.suptitle(
        "AnchoringEffect Rule \u2014 Investor Bidding Curves",
        fontsize=14,
        fontweight="bold",
    )

    ax.plot(
        round_arr,
        prices_list,
        color="#f0a500",
        linewidth=2.5,
        label="Market Price",
        zorder=10,
    )
    ax.axhline(
        y=fund_value,
        color="darkgreen",
        linestyle="--",
        linewidth=1.2,
        label=f"Fundamental (F={fund_value:.2f})",
        alpha=0.8,
    )

    for idx, (pid, bids_by_round) in enumerate(sorted(investor_bids.items())):
        bid_rounds = sorted(bids_by_round.keys())
        bid_vals = [float(bids_by_round[r]) for r in bid_rounds]
        color = _BID_COLORS[idx % len(_BID_COLORS)]
        ax.plot(
            bid_rounds,
            bid_vals,
            marker="o",
            markersize=2,
            linewidth=0.9,
            color=color,
            alpha=0.8,
            label=pid.replace("_", " ").title(),
        )

    ax.set_xlabel("Round", fontsize=12)
    ax.set_ylabel("Price", fontsize=12)
    ax.set_title("Market Price & Individual Investor Bids", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=min(5, len(investor_bids) + 2),
        fontsize=8,
        frameon=True,
        framealpha=0.7,
    )

    plt.tight_layout()
    path0 = os.path.join(output_dir, "00_investor_bids.png")
    plt.savefig(path0, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path0}")

    # --- Plot 1: Price vs Fundamental + Deviation ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "AnchoringEffect Rule — Price Dynamics", fontsize=13, fontweight="bold"
    )

    axes[0].plot(round_arr, prices_list, color="steelblue", label="Market Price")
    axes[0].axhline(
        y=fund_value,
        color="darkgreen",
        linestyle="--",
        label=f"Fundamental (F={fund_value:.1f})",
    )
    axes[0].set_title("Price vs. Fundamental")
    axes[0].set_xlabel("Round")
    axes[0].set_ylabel("Price")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(round_arr, deviation_pct, color="crimson", label="|Deviation| (%)")
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].axhline(y=3, color="orange", linestyle=":", alpha=0.7, label="3% threshold")
    axes[1].axhline(y=10, color="red", linestyle=":", alpha=0.5, label="10% threshold")
    axes[1].axhline(y=-3, color="orange", linestyle=":", alpha=0.7)
    if half_life < len(prices_list):
        axes[1].axvline(
            x=round_arr[int(half_life)],
            color="purple",
            linestyle=":",
            alpha=0.7,
            label=f"Half-life (r={int(half_life)})",
        )
    axes[1].set_title("Price Deviation from Fundamental (%)")
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path1 = os.path.join(output_dir, "01_price_dynamics.png")
    plt.savefig(path1, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path1}")

    # --- Plot 2: Rolling Volatility + Return Distribution ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "AnchoringEffect Rule — Market Dynamics", fontsize=13, fontweight="bold"
    )

    if rolling_vols:
        axes[0].plot(round_arr[1 : len(rolling_vols) + 1], rolling_vols, color="purple")
        axes[0].axhline(
            y=0.5, color="green", linestyle=":", alpha=0.7, label="0.5% target low"
        )
        axes[0].axhline(
            y=2.0, color="orange", linestyle=":", alpha=0.7, label="2.0% target high"
        )
        axes[0].set_title("Rolling Volatility (10-round window, %)")
        axes[0].set_xlabel("Round")
        axes[0].set_ylabel("Std Dev of Returns (%)")
        axes[0].legend(fontsize=8)
        axes[0].grid(True, alpha=0.3)

    if len(prices_list) > 1:
        arr = np.array(prices_list)
        returns_pct = np.diff(arr) / arr[:-1] * 100
        axes[1].hist(
            returns_pct, bins=30, color="steelblue", alpha=0.7, edgecolor="white"
        )
        axes[1].set_title("Return Distribution (%)")
        axes[1].set_xlabel("Return (%)")
        axes[1].set_ylabel("Frequency")
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path2 = os.path.join(output_dir, "02_market_dynamics.png")
    plt.savefig(path2, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path2}")

    # --- Plot 3: Agent Volume + Summary bar ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "AnchoringEffect Rule — Agent Analysis", fontsize=13, fontweight="bold"
    )

    if investor_payloads:
        agent_ids = list(investor_payloads.keys())
        buy_vols = []
        sell_vols = []
        for aid in agent_ids:
            buy = sum(
                abs(float(p["quantity"]))
                for p in investor_payloads[aid].values()
                if float(p["quantity"]) > 0
            )
            sell = sum(
                abs(float(p["quantity"]))
                for p in investor_payloads[aid].values()
                if float(p["quantity"]) < 0
            )
            buy_vols.append(buy)
            sell_vols.append(sell)

        x_pos = np.arange(len(agent_ids))
        axes[0].bar(x_pos - 0.2, buy_vols, 0.4, label="Buy", color="green", alpha=0.7)
        axes[0].bar(x_pos + 0.2, sell_vols, 0.4, label="Sell", color="red", alpha=0.7)
        axes[0].set_xticks(x_pos)
        axes[0].set_xticklabels(agent_ids, rotation=35, ha="right", fontsize=7)
        axes[0].set_title("Agent Trading Volume (Buy vs Sell)")
        axes[0].set_ylabel("Total Quantity")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

    abs_dev = [abs(d) for d in deviation_pct]
    axes[1].plot(round_arr, abs_dev, color="darkorange", label="|Deviation| (%)")
    if len(abs_dev) > 0:
        axes[1].axhline(
            y=abs_dev[0] / 2,
            color="grey",
            linestyle=":",
            alpha=0.7,
            label="Half-life target",
        )
    axes[1].axhline(
        y=3, color="green", linestyle=":", alpha=0.5, label="3% lower bound"
    )
    axes[1].axhline(
        y=10, color="red", linestyle=":", alpha=0.5, label="10% upper bound"
    )
    axes[1].set_title("Anchoring Persistence (|Deviation| Decay)")
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("|Deviation| (%)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path3 = os.path.join(output_dir, "03_summary.png")
    plt.savefig(path3, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path3}")


# ---------------------------------------------------------------------------
# Public analysis contract
# ---------------------------------------------------------------------------


def load_simulation_data(config: dict) -> Dict[str, Any]:
    """Load persisted simulation records into the standard analysis data dict."""
    return _load_data(load_results(config))


def calculate_metrics(data: Dict[str, Any], config: dict) -> Dict[str, Any]:
    """Calculate AnchoringEffect scalar metrics without writing plots."""
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]

    if not market_prices:
        raise ValueError("No market price data found. Run the simulation first.")
    if not fundamentals:
        raise ValueError("No fundamental value data found in market records.")

    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    fund_value = sum(fundamentals.values()) / len(fundamentals)
    adjustment_factor = _get_adjustment_factor(config)

    rolling_vols = _compute_rolling_volatility(prices_list)
    return {
        "mad_pct": _compute_mad(prices_list, fund_value) * 100,
        "half_life_rounds": _compute_half_life(prices_list, fund_value),
        "max_drawdown_pct": _compute_max_drawdown(prices_list),
        "return_autocorr_lag1": _compute_autocorrelation(prices_list),
        "mean_rolling_vol_pct": float(np.mean(rolling_vols)),
        "bias_magnitude_pct": (
            _compute_bias_magnitude(prices_list, fund_value, adjustment_factor) * 100
        ),
    }


def create_visualizations(
    data: Dict[str, Any],
    config: dict,
    output_dir: str,
) -> None:
    """Write the fixed AnchoringEffect analysis PNG set."""
    metrics = calculate_metrics(data, config)
    _create_visualizations(
        market_prices=data["market_prices"],
        fundamentals=data["fundamentals"],
        investor_bids=data["investor_bids"],
        investor_payloads=data["investor_payloads"],
        rolling_vols=_compute_rolling_volatility(
            [data["market_prices"][r] for r in sorted(data["market_prices"].keys())]
        ),
        half_life=metrics["half_life_rounds"],
        output_dir=output_dir,
    )


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------


def analyze_anchoring(
    data: Dict[str, Any], config: dict, output_dir: str
) -> Dict[str, Any]:
    """Run full anchoring analysis, validation, and visualization."""
    os.makedirs(output_dir, exist_ok=True)

    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    investor_payloads = data["investor_payloads"]

    if not market_prices:
        raise ValueError("No market price data found. Run simulation first.")
    if not fundamentals:
        raise ValueError("No fundamental value data found in market records.")

    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    total_rounds = len(prices_list)

    # Fundamental value — constant in AnchoringEffect (F = 100.0)
    fund_value = sum(fundamentals.values()) / len(fundamentals)
    adjustment_factor = _get_adjustment_factor(config)

    # --- Compute metrics ---
    mad_pct = _compute_mad(prices_list, fund_value) * 100
    half_life = _compute_half_life(prices_list, fund_value)
    autocorr = _compute_autocorrelation(prices_list)
    max_dd = _compute_max_drawdown(prices_list)
    rolling_vols = _compute_rolling_volatility(prices_list)
    bias_magnitude = _compute_bias_magnitude(prices_list, fund_value, adjustment_factor)

    # Agent volumes
    agent_volumes: Dict[str, Dict[str, float]] = {}
    for aid, round_payloads in investor_payloads.items():
        total_buy = sum(
            float(p["quantity"])
            for p in round_payloads.values()
            if float(p["quantity"]) > 0
        )
        total_sell = sum(
            abs(float(p["quantity"]))
            for p in round_payloads.values()
            if float(p["quantity"]) < 0
        )
        agent_volumes[aid] = {
            "total_buy": total_buy,
            "total_sell": total_sell,
            "total_volume": total_buy + total_sell,
        }

    # --- Validation ---
    validation = _validate_anchoring_effect(
        mad_pct=mad_pct,
        half_life=half_life,
        max_drawdown_pct=max_dd,
        autocorr_lag1=autocorr,
        total_rounds=total_rounds,
    )

    # --- Plots ---
    print(f"Generating analysis plots in {output_dir}/")
    _create_visualizations(
        market_prices=market_prices,
        fundamentals=fundamentals,
        investor_bids=data["investor_bids"],
        investor_payloads=investor_payloads,
        rolling_vols=rolling_vols,
        half_life=half_life,
        output_dir=output_dir,
    )

    # --- Summary ---
    summary = {
        "scenario": "AnchoringEffect",
        "variant": "Rule",
        "total_rounds": total_rounds,
        "fundamental_value": fund_value,
        "adjustment_factor": adjustment_factor,
        "metrics": {
            "mad_pct": round(mad_pct, 4),
            "half_life_rounds": round(half_life, 1),
            "max_drawdown_pct": round(max_dd, 4),
            "return_autocorr_lag1": round(autocorr, 4),
            "mean_rolling_vol_pct": round(float(np.mean(rolling_vols)), 4),
            "bias_magnitude_pct": round(bias_magnitude * 100, 4),
        },
        "price": {
            "initial": round(prices_list[0], 4),
            "final": round(prices_list[-1], 4),
            "min": round(min(prices_list), 4),
            "max": round(max(prices_list), 4),
            "mean": round(sum(prices_list) / len(prices_list), 4),
        },
        "agent_volumes": agent_volumes,
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # --- Console output ---
    print("\n" + "=" * 50)
    print("ANCHORING EFFECT ANALYSIS")
    print("=" * 50)
    print(f"MAD: {mad_pct:.2f}%  (target: 3–10%)")
    print(f"Half-life: {half_life:.0f} rounds  (target: 20–60)")
    print(f"Max drawdown: {max_dd:.2f}%  (target: −5% to −20%)")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}  (target: 0.0–0.30)")
    print(f"Bias magnitude: {bias_magnitude * 100:.2f}%  (target: 2–5%)")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run AnchoringEffect Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze AnchoringEffect simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    summary = analyze_anchoring(data, config, output_dir)
    return summary


if __name__ == "__main__":
    main()


__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "calculate_price_deviation",
    "create_visualizations",
    "analyze_anchoring",
]
