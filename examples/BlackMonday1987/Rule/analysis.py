#!/usr/bin/env python
"""BlackMonday1987 Rule-Based Simulation Analysis

Analyzes simulation results for 1987-style portfolio-insurance-driven crash
cascade dynamics.  Based on analysis-bases.md §6 calibration targets
(Brady Commission 1988; Lo & MacKinlay 1988).

Usage:
    python examples/BlackMonday1987/Rule/analysis.py \
        -c configs/BlackMonday1987/Rule/simulation.yml
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation.data_loader import batch_to_rounds, load_data
from masim.evaluation.finance import (
    calculate_autocorrelation,
    calculate_max_drawdown,
    calculate_rolling_volatility,
)

__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "_validate_black_monday",
    "_build_interpretation",
    "analyze_black_monday",
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _batch_to_rounds(values: list) -> Dict[int, float]:
    """Legacy alias. See ``masim.evaluation.data_loader.batch_to_rounds``."""
    return batch_to_rounds(values)


def _load_data(results) -> Dict[str, Any]:
    """Legacy adapter delegating to ``masim.evaluation.data_loader.load_data``.

    Returns the canonical eval-first shape (market_prices, fundamentals,
    investor_quantities, investor_bids, investor_payloads) — extra keys are
    tolerated by every downstream consumer in this scenario.
    """
    return load_data(results)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _compute_max_drawdown(prices_list: List[float]) -> float:
    """Peak-to-trough drawdown (%, positive value).

    Thin adapter over ``masim.evaluation.finance.calculate_max_drawdown``.
    """
    if len(prices_list) < 2:
        return 0.0
    # ``calculate_max_drawdown`` returns a signed percent (negative for a
    # drop); the legacy Rule convention is a positive magnitude.
    return float(abs(calculate_max_drawdown(list(prices_list))[0]))


def _compute_crash_onset(
    prices_list: List[float], fundamental: float, threshold: float = -0.05
) -> Optional[int]:
    """First round where deviation crosses threshold (default -5%)."""
    for i, p in enumerate(prices_list):
        if fundamental > 0 and (p - fundamental) / fundamental < threshold:
            return i + 1
    return None


def _compute_peak_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> float:
    """Peak rolling volatility of percent returns (scenario-specific: uses
    percent scale, not fractional). Built on top of the eval rolling
    volatility helper for consistency."""
    vols = _compute_rolling_volatility(prices_list, window=window)
    return max(vols) if vols else 0.0


def _compute_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> List[float]:
    """Rolling volatility of percent returns (scenario-specific percent scale).

    Uses the same window-expanding convention as
    ``masim.evaluation.finance.calculate_rolling_volatility`` but reports the
    per-window std of percent returns (returns × 100) to preserve the legacy
    calibration targets in analysis-bases.md.
    """
    arr = np.asarray(prices_list, dtype=float)
    if len(arr) < 2:
        return []
    returns_pct = np.diff(arr) / arr[:-1] * 100.0
    vols: List[float] = []
    for i in range(len(returns_pct)):
        start = max(0, i - window + 1)
        vols.append(float(np.std(returns_pct[start : i + 1])))
    return vols


def _compute_autocorrelation(prices_list: List[float], lag: int = 1) -> float:
    """Lag-`lag` autocorrelation of simple returns.

    Adapter around ``masim.evaluation.finance.calculate_autocorrelation``.
    """
    if len(prices_list) < lag + 2:
        return 0.0
    arr = np.asarray(prices_list, dtype=float)
    returns = np.diff(arr) / arr[:-1]
    acf = calculate_autocorrelation(list(returns), max_lag=lag)
    if not acf or len(acf) < lag:
        return 0.0
    return float(acf[lag - 1])


def _compute_crash_velocity(prices_list: List[float]) -> float:
    """Peak single-round negative return (%, absolute value)."""
    arr = np.array(prices_list)
    if len(arr) < 2:
        return 0.0
    returns = np.diff(arr) / arr[:-1] * 100
    return float(abs(np.min(returns)))


def _compute_agent_vwap(
    investor_payloads: Dict[str, Dict[int, dict]],
    market_prices: Dict[int, float],
) -> Dict[str, Dict[str, float]]:
    """Compute VWAP and total volume by agent."""
    vwap_data: Dict[str, Dict[str, float]] = {}
    for aid, round_payloads in investor_payloads.items():
        price_volume_sum = 0.0
        total_vol = 0.0
        total_buy = 0.0
        total_sell = 0.0
        for rnd, payload in round_payloads.items():
            qty = float(payload["quantity"])
            action = payload["action"]
            price = market_prices[rnd]
            abs_qty = abs(qty)
            price_volume_sum += abs_qty * price
            total_vol += abs_qty
            if action == "buy":
                total_buy += qty
            elif action == "sell":
                total_sell += abs_qty
        vwap_data[aid] = {
            "vwap": price_volume_sum / total_vol if total_vol > 0 else 0.0,
            "total_volume": total_vol,
            "total_buy": total_buy,
            "total_sell": total_sell,
        }
    return vwap_data


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclass
class BlackMondayValidationResult:
    """Result of BlackMonday1987 simulation validation."""

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


def _validate_black_monday(
    max_drawdown_pct: float,
    crash_onset_round: Optional[int],
    crash_velocity_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
) -> BlackMondayValidationResult:
    """Validate BlackMonday1987 results against analysis-bases.md §6 calibration targets.

    Criteria
    --------
    1. Max drawdown     target [15%, 35%]   weight 0.35  (Brady Commission; DJIA -22.6%)
    2. Crash onset      target [5, 20]      weight 0.30  (Brady Commission intraday timeline)
    3. Crash velocity   target >= 2%/round  weight 0.20  (Brady Commission 30-min intervals)
    4. AC1 cascade      target >= 0.30      weight 0.15  (Lo & MacKinlay 1988)
    """
    criteria = {}

    # --- Criterion 1: Max drawdown in [15%, 35%] ---
    if 15.0 <= max_drawdown_pct <= 35.0:
        dd_score = 1.0
    elif 8.0 <= max_drawdown_pct < 15.0:
        dd_score = 0.4 + (max_drawdown_pct - 8.0) / 7.0 * 0.6
    elif 35.0 < max_drawdown_pct <= 50.0:
        dd_score = 1.0 - (max_drawdown_pct - 35.0) / 15.0 * 0.5
    elif max_drawdown_pct > 50.0:
        dd_score = 0.1
    else:
        dd_score = max_drawdown_pct / 15.0 * 0.4

    criteria["max_drawdown"] = {
        "value": round(max_drawdown_pct, 3),
        "target": "15–35%",
        "score": round(dd_score, 3),
        "passed": 8.0 <= max_drawdown_pct <= 50.0,
    }

    # --- Criterion 2: Crash onset round in [5, 20] ---
    if crash_onset_round is None:
        onset_score = 0.0
    elif 5 <= crash_onset_round <= 20:
        onset_score = 1.0
    elif 3 <= crash_onset_round < 5:
        onset_score = 0.5 + (crash_onset_round - 3) / 2.0 * 0.5
    elif 20 < crash_onset_round <= 35:
        onset_score = 1.0 - (crash_onset_round - 20) / 15.0 * 0.5
    else:
        onset_score = 0.1

    criteria["crash_onset"] = {
        "value": crash_onset_round,
        "target": "rounds 5–20",
        "score": round(onset_score, 3),
        "passed": crash_onset_round is not None and 3 <= crash_onset_round <= 35,
    }

    # --- Criterion 3: Crash velocity >= 2% per round ---
    if crash_velocity_pct >= 2.0:
        vel_score = min(1.0, 0.6 + (crash_velocity_pct - 2.0) / 6.0 * 0.4)
    elif crash_velocity_pct >= 1.0:
        vel_score = 0.3 + (crash_velocity_pct - 1.0) / 1.0 * 0.3
    else:
        vel_score = crash_velocity_pct / 1.0 * 0.3

    criteria["crash_velocity"] = {
        "value": round(crash_velocity_pct, 3),
        "target": "≥2% per round",
        "score": round(vel_score, 3),
        "passed": crash_velocity_pct >= 1.0,
    }

    # --- Criterion 4: AC1 >= 0.30 ---
    if autocorr_lag1 >= 0.30:
        ac_score = min(1.0, 0.6 + (autocorr_lag1 - 0.30) / 0.35 * 0.4)
    elif 0.15 <= autocorr_lag1 < 0.30:
        ac_score = 0.3 + (autocorr_lag1 - 0.15) / 0.15 * 0.3
    elif autocorr_lag1 < 0.0:
        ac_score = max(0.0, 0.1 + autocorr_lag1 * 0.5)
    else:
        ac_score = autocorr_lag1 / 0.30 * 0.3

    criteria["autocorrelation"] = {
        "value": round(autocorr_lag1, 4),
        "target": "≥0.30",
        "score": round(ac_score, 3),
        "passed": autocorr_lag1 >= 0.15,
    }

    overall_score = (
        dd_score * 0.35 + onset_score * 0.30 + vel_score * 0.20 + ac_score * 0.15
    )
    is_valid = overall_score > 0.50 and max_drawdown_pct >= 5.0

    interpretation = _build_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        max_drawdown_pct=max_drawdown_pct,
        crash_onset_round=crash_onset_round,
        crash_velocity_pct=crash_velocity_pct,
        autocorr_lag1=autocorr_lag1,
        total_rounds=total_rounds,
        dd_score=dd_score,
        onset_score=onset_score,
        vel_score=vel_score,
        ac_score=ac_score,
    )

    return BlackMondayValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def _build_interpretation(
    is_valid: bool,
    overall_score: float,
    max_drawdown_pct: float,
    crash_onset_round: Optional[int],
    crash_velocity_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
    dd_score: float,
    onset_score: float,
    vel_score: float,
    ac_score: float,
) -> str:
    """Build structured validation report following analysis-bases.md §6."""
    verdict = "VALID" if is_valid else "INVALID"
    lines = []
    lines.append(f"=== BLACK MONDAY 1987 SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Criterion 1
    if max_drawdown_pct >= 15.0:
        dd_assess = (
            "PASS — Crash depth consistent with 1987 DJIA −22.6% historical reference."
        )
    elif max_drawdown_pct >= 8.0:
        dd_assess = "WEAK — Crash present but below Brady Commission calibration; increase price_impact (λ)."
    else:
        dd_assess = "FAIL — Crash too shallow; portfolio insurance cascade not generating sufficient selling."
    lines.append("[1] CRASH DEPTH (MAX DRAWDOWN)")
    lines.append(f"    Observed: Max drawdown = {max_drawdown_pct:.2f}%")
    lines.append(
        "    Expected: 15–35% (Brady Commission 1988; DJIA −22.6%, S&P 500 −20.5%)"
    )
    lines.append(f"    Score: {dd_score:.1%}")
    lines.append(f"    Assessment: {dd_assess}")
    lines.append("")

    # Criterion 2
    onset_str = (
        str(crash_onset_round) if crash_onset_round else "N/A (never reached −5%)"
    )
    if crash_onset_round and 5 <= crash_onset_round <= 20:
        onset_assess = "PASS — Crash onset timing matches Brady Commission intraday cascade timeline."
    elif crash_onset_round and crash_onset_round < 5:
        onset_assess = "EARLY — Crash starts before agents deploy capital; check trigger_threshold."
    elif crash_onset_round:
        onset_assess = "LATE — Cascade too slow; check rebalance_threshold."
    else:
        onset_assess = (
            "FAIL — Crash never started; PortfolioInsurer not triggering cascade."
        )
    lines.append("[2] CRASH TIMING (ONSET ROUND)")
    lines.append(f"    Observed: Crash onset round = {onset_str}")
    lines.append("    Expected: Rounds 5–20 (Brady Commission 1988 intraday timeline)")
    lines.append(f"    Score: {onset_score:.1%}")
    lines.append(f"    Assessment: {onset_assess}")
    lines.append("")

    # Criterion 3
    if crash_velocity_pct >= 2.0:
        vel_assess = "PASS — Crash velocity consistent with Brady Commission 5–8% per 30-minute interval data."
    elif crash_velocity_pct >= 1.0:
        vel_assess = (
            "WEAK — Crash active but velocity below target; increase feedback_strength."
        )
    else:
        vel_assess = (
            "FAIL — No significant crash velocity; ProgramTrader amplification absent."
        )
    lines.append("[3] CRASH VELOCITY (PEAK SINGLE-ROUND DECLINE)")
    lines.append(
        f"    Observed: Peak crash velocity = {crash_velocity_pct:.2f}% per round"
    )
    lines.append(
        "    Expected: ≥2% per round (Brady Commission 1988: 5–8% per 30-min intervals)"
    )
    lines.append(f"    Score: {vel_score:.1%}")
    lines.append(f"    Assessment: {vel_assess}")
    lines.append("")

    # Criterion 4
    if autocorr_lag1 >= 0.30:
        ac_assess = "PASS — Positive momentum confirms portfolio-insurance feedback loop self-reinforcement."
    elif autocorr_lag1 >= 0.15:
        ac_assess = "WEAK — Mild momentum; cascade partially self-reinforcing."
    else:
        ac_assess = "FAIL — No momentum signature; cascade not self-reinforcing."
    lines.append("[4] CASCADE SELF-REINFORCEMENT (RETURN AUTOCORRELATION AC1)")
    lines.append(f"    Observed: Lag-1 autocorrelation = {autocorr_lag1:.3f}")
    lines.append(
        "    Expected: ≥0.30 (Lo & MacKinlay 1988; estimated 0.40–0.65 on Black Monday)"
    )
    lines.append(f"    Score: {ac_score:.1%}")
    lines.append(f"    Assessment: {ac_assess}")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            f"The simulation successfully reproduces Black Monday 1987 crash dynamics: "
            f"a {max_drawdown_pct:.1f}% drawdown with "
            + (
                f"crash onset at round {crash_onset_round}"
                if crash_onset_round
                else "no crash onset"
            )
            + f", peak velocity {crash_velocity_pct:.1f}% per round, and lag-1 AC1 {autocorr_lag1:.2f}. "
            f"The portfolio-insurance feedback mechanism (selling → price fall → more selling) is "
            f"operating as designed. Fit Score: {overall_score:.1%}."
        )
    else:
        lines.append(
            f"The simulation does not fully reproduce Black Monday 1987 crash dynamics. "
            f"Overall Fit Score {overall_score:.1%} is below the 50% threshold. "
            f"Key issues: "
            + ("drawdown too low; " if max_drawdown_pct < 15.0 else "")
            + ("crash never started; " if crash_onset_round is None else "")
            + ("velocity insufficient; " if crash_velocity_pct < 2.0 else "")
            + ("no momentum; " if autocorr_lag1 < 0.15 else "")
            + "Review analysis-bases.md §6 Validation Failure Diagnostics for parameter fixes."
        )
    lines.append(f"Fit Score: {overall_score:.1%}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------------


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


def _create_visualizations(
    market_prices: Dict[int, float],
    fundamentals: Dict[int, float],
    investor_bids: Dict[str, Dict[int, float]],
    investor_payloads: Dict[str, Dict[int, dict]],
    rolling_vols: List[float],
    crash_onset_round: Optional[int],
    output_dir: str,
) -> None:
    """Create 4 analysis plots per analysis-bases.md §7.

    Plots
    -----
    00_investor_bids.png   : Investor Bidding Curves (headline chart)
    01_blackmonday1987_dynamics.png  : Price vs Fundamental + Deviation %
    02_blackmonday1987_analysis.png  : Rolling Volatility + Return Autocorrelation
    03_summary.png         : Agent VWAP comparison + Volume
    """
    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    fund_list = [fundamentals[r] for r in rounds_sorted]
    rounds_arr = np.array(rounds_sorted)
    prices_arr = np.array(prices_list)
    fund_arr = np.array(fund_list)
    deviation = (prices_arr - fund_arr) / fund_arr * 100

    # --- Plot 0: Investor Bid Curves (PRIMARY headline chart) ---
    _fv = float(np.mean(fund_list))
    fig0, ax0 = plt.subplots(figsize=(16, 8))
    fig0.suptitle(
        "BlackMonday1987 Rule \u2014 Investor Bidding Curves",
        fontsize=14,
        fontweight="bold",
    )
    ax0.plot(
        rounds_arr,
        prices_arr,
        color="#f0a500",
        linewidth=2.5,
        label="Market Price",
        zorder=10,
    )
    ax0.axhline(
        y=_fv,
        color="darkgreen",
        linestyle="--",
        linewidth=1.2,
        label=f"Fundamental (F={_fv:.2f})",
        alpha=0.8,
    )
    for _i, (_pid, _bids) in enumerate(sorted(investor_bids.items())):
        _br = sorted(_bids.keys())
        _bv = [float(_bids[r]) for r in _br]
        ax0.plot(
            _br,
            _bv,
            marker="o",
            markersize=2,
            linewidth=0.9,
            color=_BID_COLORS[_i % len(_BID_COLORS)],
            alpha=0.8,
            label=_pid.replace("_", " ").title(),
        )
    ax0.set_xlabel("Round", fontsize=12)
    ax0.set_ylabel("Price", fontsize=12)
    ax0.set_title("Market Price & Individual Investor Bids", fontsize=12)
    ax0.grid(True, alpha=0.3)
    ax0.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=min(5, len(investor_bids) + 2),
        fontsize=8,
        frameon=True,
        framealpha=0.7,
    )
    plt.tight_layout()
    _p0 = os.path.join(output_dir, "00_investor_bids.png")
    plt.savefig(_p0, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {_p0}")

    # ---- Plot 01: Price Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "BlackMonday1987 — Price Crash Dynamics", fontsize=13, fontweight="bold"
    )

    axes[0].plot(
        rounds_arr, prices_arr, label="Market Price", color="red", linewidth=1.5
    )
    axes[0].plot(
        rounds_arr,
        fund_arr,
        label="Fundamental",
        color="blue",
        linestyle="--",
        linewidth=1.2,
    )
    if crash_onset_round:
        axes[0].axvline(
            x=crash_onset_round,
            color="orange",
            linestyle=":",
            label=f"Crash onset (r={crash_onset_round})",
        )
    axes[0].set_xlabel("Round")
    axes[0].set_ylabel("Price")
    axes[0].set_title("Price vs. Fundamental")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(rounds_arr, deviation, color="purple", linewidth=1.2)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    for th in [-5, -10, -15, -20]:
        axes[1].axhline(y=th, color="gray", linestyle=":", alpha=0.4)
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].set_title("Price Deviation from Fundamental")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "01_blackmonday1987_dynamics.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 02: Crash Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "BlackMonday1987 — Crash Intensity Dynamics", fontsize=13, fontweight="bold"
    )

    if rolling_vols:
        vol_rounds = rounds_arr[1:] if len(rounds_arr) > 1 else rounds_arr
        if len(vol_rounds) == len(rolling_vols):
            axes[0].plot(vol_rounds, rolling_vols, color="darkorange", linewidth=1.2)
        else:
            axes[0].plot(rolling_vols, color="darkorange", linewidth=1.2)
        axes[0].axhline(
            y=3.0, color="red", linestyle=":", alpha=0.5, label="3% threshold"
        )
        axes[0].set_xlabel("Round")
        axes[0].set_ylabel("Rolling Volatility (%)")
        axes[0].set_title("10-Round Rolling Volatility")
        axes[0].legend(fontsize=8)
        axes[0].grid(True, alpha=0.3)

    if len(prices_arr) > 1:
        returns = np.diff(prices_arr) / prices_arr[:-1] * 100
        axes[1].bar(rounds_arr[1:], returns, color="crimson", alpha=0.7)
        axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[1].set_xlabel("Round")
        axes[1].set_ylabel("Return (%)")
        axes[1].set_title("Per-Round Returns")
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "02_blackmonday1987_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 03: Agent Summary ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "BlackMonday1987 — Agent Activity Summary", fontsize=13, fontweight="bold"
    )

    agent_ids = sorted(investor_payloads.keys())
    if agent_ids:
        vwap_data = _compute_agent_vwap(investor_payloads, market_prices)
        vwaps = [vwap_data[a]["vwap"] for a in agent_ids]
        volumes = [vwap_data[a]["total_volume"] for a in agent_ids]
        x_pos = np.arange(len(agent_ids))
        bar_colors = ["steelblue" if v > 0 else "gray" for v in vwaps]
        axes[0].bar(x_pos, vwaps, color=bar_colors, alpha=0.8)
        if fund_arr.size > 0:
            axes[0].axhline(
                y=float(fund_arr[0]),
                color="blue",
                linestyle="--",
                alpha=0.7,
                label=f"Fundamental={fund_arr[0]:.1f}",
            )
        axes[0].set_xticks(x_pos)
        axes[0].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=8)
        axes[0].set_title("Agent VWAP")
        axes[0].set_ylabel("VWAP ($)")
        axes[0].legend(fontsize=8)
        axes[0].grid(True, alpha=0.3)

        axes[1].bar(x_pos, volumes, color="coral", alpha=0.8)
        axes[1].set_xticks(x_pos)
        axes[1].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=8)
        axes[1].set_title("Agent Total Trading Volume")
        axes[1].set_ylabel("Total Volume (shares)")
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "03_summary.png"), dpi=150, bbox_inches="tight"
    )
    plt.close()


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def analyze_black_monday(
    data: Dict[str, Any],
    config: dict,
    output_dir: str,
) -> Dict[str, Any]:
    """Run full BlackMonday1987 analysis pipeline.

    Args:
        data: Output of _load_data().
        config: Loaded simulation config.
        output_dir: Directory to write output files.

    Returns:
        summary dict (also written to summary.json).
    """
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    investor_payloads = data["investor_payloads"]

    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    if not fundamentals:
        raise ValueError("No fundamental data recorded - simulation data is incomplete")
    fund_value = float(np.mean(list(fundamentals.values())))
    total_rounds = len(rounds_sorted)

    # Metrics
    max_drawdown_pct = _compute_max_drawdown(prices_list)
    crash_onset_round = _compute_crash_onset(prices_list, fund_value, threshold=-0.05)
    crash_velocity_pct = _compute_crash_velocity(prices_list)
    rolling_vols = _compute_rolling_volatility(prices_list)
    autocorr = _compute_autocorrelation(prices_list)

    # Agent VWAP
    vwap_data = _compute_agent_vwap(investor_payloads, market_prices)

    # Validation
    validation = _validate_black_monday(
        max_drawdown_pct=max_drawdown_pct,
        crash_onset_round=crash_onset_round,
        crash_velocity_pct=crash_velocity_pct,
        autocorr_lag1=autocorr,
        total_rounds=total_rounds,
    )

    # Plots
    print(f"Generating analysis plots in {output_dir}/")
    _create_visualizations(
        market_prices=market_prices,
        fundamentals=fundamentals,
        investor_bids=data["investor_bids"],
        investor_payloads=investor_payloads,
        rolling_vols=rolling_vols,
        crash_onset_round=crash_onset_round,
        output_dir=output_dir,
    )

    # Summary
    summary = {
        "scenario": "BlackMonday1987",
        "variant": "Rule",
        "total_rounds": total_rounds,
        "fundamental_value": round(fund_value, 4),
        "metrics": {
            "max_drawdown_pct": round(max_drawdown_pct, 4),
            "crash_onset_round": crash_onset_round,
            "crash_velocity_pct": round(crash_velocity_pct, 4),
            "return_autocorr_lag1": round(autocorr, 4),
        },
        "price": {
            "initial": round(prices_list[0], 4),
            "final": round(prices_list[-1], 4),
            "min": round(min(prices_list), 4),
            "max": round(max(prices_list), 4),
        },
        "agent_vwap": {
            k: {sk: round(sv, 4) for sk, sv in v.items()} for k, v in vwap_data.items()
        },
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Console output
    print("\n" + "=" * 50)
    print("BLACK MONDAY 1987 ANALYSIS")
    print("=" * 50)
    print(f"Max drawdown: {max_drawdown_pct:.2f}%  (target: 15–35%)")
    onset_str = str(crash_onset_round) if crash_onset_round else "N/A"
    print(f"Crash onset: round {onset_str}  (target: 5–20)")
    print(f"Crash velocity: {crash_velocity_pct:.2f}% per round  (target: ≥2%)")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}  (target: ≥0.30)")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run BlackMonday1987 Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze BlackMonday1987 simulation")
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
    summary = analyze_black_monday(data, config, output_dir)
    return summary


if __name__ == "__main__":
    main()
