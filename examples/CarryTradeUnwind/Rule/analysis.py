#!/usr/bin/env python
"""CarryTradeUnwind Rule-Based Simulation Analysis

Analyzes simulation results for FX carry-trade cascade dynamics.
Based on analysis-bases.md §6 calibration targets
(Brunnermeier, Nagel & Pedersen 2009; Rogoff 1996; Lo & MacKinlay 1988).

Usage:
    python examples/CarryTradeUnwind/Rule/analysis.py \
        -c configs/CarryTradeUnwind/Rule/simulation.yml
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.data_loader import batch_to_rounds, load_data
from masim.evaluation.finance import (
    calculate_autocorrelation,
    calculate_max_drawdown,
)
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "_compute_max_drawdown",
    "_compute_unwind_velocity",
    "_compute_unwind_duration",
    "_compute_recovery_ratio",
    "_compute_cascade_onset",
    "_compute_peak_rolling_volatility",
    "_compute_autocorrelation",
    "_validate_carry_trade_unwind",
    "_build_interpretation",
    "analyze_carry_trade_unwind",
]


# ---------------------------------------------------------------------------
# Data loading (thin adapters over ``masim.evaluation``)
# ---------------------------------------------------------------------------


def _batch_to_rounds(values: list) -> Dict[int, float]:
    """Legacy alias. Delegates to ``masim.evaluation.data_loader.batch_to_rounds``."""
    return batch_to_rounds(values)


def _load_data(results) -> Dict[str, Any]:
    """Legacy alias. Delegates to ``masim.evaluation.data_loader.load_data``."""
    return load_data(results)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def _compute_max_drawdown(prices_list: List[float]) -> float:
    """Maximum peak-to-trough drawdown (%, positive value).

    Thin adapter over ``masim.evaluation.finance.calculate_max_drawdown`` —
    the shared helper returns *signed* percent so ``abs()`` preserves the
    legacy positive-magnitude semantics.
    """
    if len(prices_list) < 2:
        return 0.0
    return float(abs(calculate_max_drawdown(list(prices_list))[0]))


def _compute_unwind_velocity(prices_list: List[float]) -> float:
    """Maximum absolute one-round FX-rate change."""
    arr = np.array(prices_list)
    if len(arr) < 2:
        return 0.0
    return float(np.max(np.abs(np.diff(arr))))


def _compute_unwind_duration(
    prices_list: List[float], fundamental: float, threshold: float = -0.05
) -> int:
    """Count rounds where price deviation is below the crisis threshold."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive for unwind duration")
    return sum(
        1
        for price in prices_list
        if (price - fundamental) / fundamental < threshold
    )


def _compute_recovery_ratio(prices_list: List[float]) -> float:
    """Recovery ratio: (final - trough) / (peak - trough)."""
    arr = np.array(prices_list)
    if len(arr) < 2:
        return 0.0
    peak = float(np.max(arr))
    trough = float(np.min(arr))
    if peak == trough:
        return 1.0
    return float((arr[-1] - trough) / (peak - trough))


def _compute_cascade_onset(
    prices_list: List[float], fundamental: float, threshold: float = -0.05
) -> Optional[int]:
    """First round where deviation crosses threshold."""
    for i, p in enumerate(prices_list):
        if fundamental > 0 and (p - fundamental) / fundamental < threshold:
            return i + 1
    return None


def _compute_peak_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> float:
    """Peak rolling volatility of returns (std dev per window, %).

    Delegates to :func:`_compute_rolling_volatility` to avoid duplicating
    the percent-scale return-volatility loop.
    """
    vols = _compute_rolling_volatility(prices_list, window=window)
    return max(vols) if vols else 0.0


def _compute_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> List[float]:
    """Rolling volatility time series (percent std of returns).

    The shared ``masim.evaluation.finance.calculate_rolling_volatility``
    operates on prices (not returns) and does not multiply by 100, so we
    keep the legacy return-space, percent-scale implementation locally for
    calibration continuity.
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
    """Lag-N autocorrelation of returns.

    Thin adapter over ``masim.evaluation.finance.calculate_autocorrelation``
    with the same low-variance early return semantics.
    """
    if len(prices_list) < lag + 2:
        return 0.0
    arr = np.asarray(prices_list, dtype=float)
    returns = np.diff(arr) / arr[:-1]
    acf = calculate_autocorrelation(list(returns), max_lag=lag)
    if not acf or len(acf) < lag:
        return 0.0
    return float(acf[lag - 1])


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
            price = market_prices[rnd]
            abs_qty = abs(qty)
            price_volume_sum += abs_qty * price
            total_vol += abs_qty
            if qty > 0:
                total_buy += qty
            else:
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
class CarryTradeUnwindValidationResult:
    """Result of CarryTradeUnwind simulation validation."""

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


def _validate_carry_trade_unwind(
    max_drawdown_pct: float,
    recovery_ratio: float,
    peak_volatility_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
) -> CarryTradeUnwindValidationResult:
    """Validate CarryTradeUnwind results against analysis-bases.md §6.

    Criteria
    --------
    1. Max FX drawdown     target [10%, 25%]  weight 0.35  (Brunnermeier et al. 2009)
    2. Recovery ratio      target [0.3, 0.7]  weight 0.25  (Rogoff 1996 PPP convergence)
    3. Peak volatility     target > 20%       weight 0.20  (BIS 2022; Menkhoff 2012)
    4. AC1 cascade         target > +0.2      weight 0.20  (Lo & MacKinlay 1988)
    """
    criteria = {}

    # --- Criterion 1: Max drawdown in [10%, 25%] ---
    if 10.0 <= max_drawdown_pct <= 25.0:
        dd_score = 1.0
    elif 5.0 <= max_drawdown_pct < 10.0:
        dd_score = 0.4 + (max_drawdown_pct - 5.0) / 5.0 * 0.6
    elif 25.0 < max_drawdown_pct <= 40.0:
        dd_score = 1.0 - (max_drawdown_pct - 25.0) / 15.0 * 0.5
    elif max_drawdown_pct > 40.0:
        dd_score = 0.1
    else:
        dd_score = max_drawdown_pct / 10.0 * 0.4

    criteria["max_drawdown"] = {
        "value": round(max_drawdown_pct, 3),
        "target": "10–25%",
        "score": round(dd_score, 3),
        "passed": 5.0 <= max_drawdown_pct <= 40.0,
    }

    # --- Criterion 2: Recovery ratio in [0.3, 0.7] ---
    if 0.3 <= recovery_ratio <= 0.7:
        rr_score = 1.0
    elif 0.1 <= recovery_ratio < 0.3:
        rr_score = 0.4 + (recovery_ratio - 0.1) / 0.2 * 0.6
    elif 0.7 < recovery_ratio <= 0.9:
        rr_score = 1.0 - (recovery_ratio - 0.7) / 0.2 * 0.4
    elif recovery_ratio > 0.9:
        rr_score = 0.3
    else:
        rr_score = recovery_ratio / 0.3 * 0.4

    criteria["recovery_ratio"] = {
        "value": round(recovery_ratio, 4),
        "target": "0.3–0.7",
        "score": round(rr_score, 3),
        "passed": 0.1 <= recovery_ratio <= 0.9,
    }

    # --- Criterion 3: Peak volatility > 20% (annualized-equivalent) ---
    # We use rolling vol in % per round; scale by sqrt(252) is scenario-specific.
    # Here we use raw peak rolling vol as proxy.
    if peak_volatility_pct >= 3.0:
        vol_score = min(1.0, 0.6 + (peak_volatility_pct - 3.0) / 5.0 * 0.4)
    elif peak_volatility_pct >= 1.5:
        vol_score = 0.3 + (peak_volatility_pct - 1.5) / 1.5 * 0.3
    else:
        vol_score = peak_volatility_pct / 1.5 * 0.3

    criteria["peak_volatility"] = {
        "value": round(peak_volatility_pct, 3),
        "target": ">3% per round (≈>20% annualized)",
        "score": round(vol_score, 3),
        "passed": peak_volatility_pct >= 1.5,
    }

    # --- Criterion 4: AC1 > +0.2 ---
    if autocorr_lag1 >= 0.20:
        ac_score = min(1.0, 0.6 + (autocorr_lag1 - 0.20) / 0.30 * 0.4)
    elif 0.10 <= autocorr_lag1 < 0.20:
        ac_score = 0.3 + (autocorr_lag1 - 0.10) / 0.10 * 0.3
    elif autocorr_lag1 < 0.0:
        ac_score = max(0.0, 0.1 + autocorr_lag1 * 0.5)
    else:
        ac_score = autocorr_lag1 / 0.20 * 0.3

    criteria["autocorrelation"] = {
        "value": round(autocorr_lag1, 4),
        "target": ">+0.2",
        "score": round(ac_score, 3),
        "passed": autocorr_lag1 >= 0.10,
    }

    overall_score = (
        dd_score * 0.35 + rr_score * 0.25 + vol_score * 0.20 + ac_score * 0.20
    )
    is_valid = overall_score > 0.50 and max_drawdown_pct >= 3.0

    interpretation = _build_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        max_drawdown_pct=max_drawdown_pct,
        recovery_ratio=recovery_ratio,
        peak_volatility_pct=peak_volatility_pct,
        autocorr_lag1=autocorr_lag1,
        total_rounds=total_rounds,
        dd_score=dd_score,
        rr_score=rr_score,
        vol_score=vol_score,
        ac_score=ac_score,
    )

    return CarryTradeUnwindValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def _build_interpretation(
    is_valid: bool,
    overall_score: float,
    max_drawdown_pct: float,
    recovery_ratio: float,
    peak_volatility_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
    dd_score: float,
    rr_score: float,
    vol_score: float,
    ac_score: float,
) -> str:
    """Build structured validation report following analysis-bases.md §6."""
    verdict = "VALID" if is_valid else "INVALID"
    lines = []
    lines.append(f"=== CARRY TRADE UNWIND SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Criterion 1
    if max_drawdown_pct >= 10.0:
        dd_assess = "PASS — FX drawdown consistent with carry-trade crisis literature."
    elif max_drawdown_pct >= 5.0:
        dd_assess = (
            "WEAK — Drawdown present but below calibration; increase LCF leverage."
        )
    else:
        dd_assess = "FAIL — Drawdown too shallow; LCF stop-loss not triggered."
    lines.append("[1] FX CASCADE DEPTH (MAX DRAWDOWN)")
    lines.append(f"    Observed: Max drawdown = {max_drawdown_pct:.2f}%")
    lines.append("    Expected: 10–25% (Brunnermeier, Nagel & Pedersen 2009)")
    lines.append(f"    Score: {dd_score:.1%}")
    lines.append(f"    Assessment: {dd_assess}")
    lines.append("")

    # Criterion 2
    if 0.3 <= recovery_ratio <= 0.7:
        rr_assess = "PASS — Partial recovery consistent with PPP convergence dynamics."
    elif recovery_ratio < 0.3:
        rr_assess = "WEAK — Recovery insufficient; increase γ or FCB position_size."
    else:
        rr_assess = "WEAK — Recovery too complete; crisis may be under-parameterized."
    lines.append("[2] RECOVERY DYNAMICS (RECOVERY RATIO)")
    lines.append(f"    Observed: Recovery ratio = {recovery_ratio:.3f}")
    lines.append("    Expected: 0.3–0.7 (Rogoff 1996 PPP convergence)")
    lines.append(f"    Score: {rr_score:.1%}")
    lines.append(f"    Assessment: {rr_assess}")
    lines.append("")

    # Criterion 3
    if peak_volatility_pct >= 3.0:
        vol_assess = (
            "PASS — Crisis-level volatility consistent with carry crash turbulence."
        )
    elif peak_volatility_pct >= 1.5:
        vol_assess = "WEAK — Moderate volatility; cascade partially active."
    else:
        vol_assess = "FAIL — Volatility too low; no crisis-level turbulence."
    lines.append("[3] CRISIS INTENSITY (PEAK ROLLING VOLATILITY)")
    lines.append(
        f"    Observed: Peak 10-round volatility = {peak_volatility_pct:.2f}% per round"
    )
    lines.append(
        "    Expected: >3% per round ≈ >20% annualized (BIS 2022; Menkhoff et al. 2012)"
    )
    lines.append(f"    Score: {vol_score:.1%}")
    lines.append(f"    Assessment: {vol_assess}")
    lines.append("")

    # Criterion 4
    if autocorr_lag1 >= 0.20:
        ac_assess = (
            "PASS — Positive momentum confirms carry-trade cascade self-reinforcement."
        )
    elif autocorr_lag1 >= 0.10:
        ac_assess = "WEAK — Mild momentum; cascade partially self-reinforcing."
    else:
        ac_assess = "FAIL — No momentum signature; cascade not self-reinforcing."
    lines.append("[4] CASCADE SELF-REINFORCEMENT (RETURN AUTOCORRELATION AC1)")
    lines.append(f"    Observed: Lag-1 autocorrelation = {autocorr_lag1:.3f}")
    lines.append("    Expected: >+0.2 (Lo & MacKinlay 1988 momentum detection)")
    lines.append(f"    Score: {ac_score:.1%}")
    lines.append(f"    Assessment: {ac_assess}")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            f"The simulation successfully reproduces carry-trade unwind cascade dynamics: "
            f"a {max_drawdown_pct:.1f}% drawdown with "
            f"recovery ratio {recovery_ratio:.2f}, "
            f"peak volatility {peak_volatility_pct:.1f}% per round, and AC1 {autocorr_lag1:.2f}. "
            f"Fit Score: {overall_score:.1%}."
        )
    else:
        lines.append(
            f"The simulation does not fully reproduce carry-trade unwind dynamics. "
            f"Overall Fit Score {overall_score:.1%} is below the 50% threshold. "
            f"Key issues: "
            + ("drawdown too low; " if max_drawdown_pct < 10.0 else "")
            + ("recovery insufficient; " if recovery_ratio < 0.3 else "")
            + ("volatility too low; " if peak_volatility_pct < 3.0 else "")
            + ("no momentum; " if autocorr_lag1 < 0.10 else "")
            + "Review analysis-bases.md §6 Validation Failure Diagnostics."
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
    cascade_onset_round: Optional[int],
    output_dir: str,
) -> None:
    """Create 4 analysis plots per analysis-bases.md §7."""
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
        "CarryTradeUnwind Rule \u2014 Investor Bidding Curves",
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
    fig.suptitle("CarryTradeUnwind — FX Rate Dynamics", fontsize=13, fontweight="bold")

    axes[0].plot(rounds_arr, prices_arr, label="FX Rate", color="red", linewidth=1.5)
    axes[0].plot(
        rounds_arr,
        fund_arr,
        label="Fundamental (PPP)",
        color="blue",
        linestyle="--",
        linewidth=1.2,
    )
    if cascade_onset_round:
        axes[0].axvline(
            x=cascade_onset_round,
            color="orange",
            linestyle=":",
            label=f"Cascade onset (r={cascade_onset_round})",
        )
    axes[0].set_xlabel("Round")
    axes[0].set_ylabel("FX Rate")
    axes[0].set_title("FX Rate vs. Fundamental")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(rounds_arr, deviation, color="purple", linewidth=1.2)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    for th in [-5, -10, -15]:
        axes[1].axhline(y=th, color="gray", linestyle=":", alpha=0.4)
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].set_title("FX Deviation from Fundamental")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "01_carrytradeunwind_dynamics.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 02: Cascade Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "CarryTradeUnwind — Cascade Intensity Dynamics", fontsize=13, fontweight="bold"
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
        axes[1].set_title("Per-Round FX Returns")
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "02_carrytradeunwind_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 03: Agent Summary ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "CarryTradeUnwind — Agent Activity Summary", fontsize=13, fontweight="bold"
    )

    agent_ids = sorted(investor_payloads.keys())
    if agent_ids:
        vwap_data = _compute_agent_vwap(investor_payloads, market_prices)
        vwaps = [vwap_data[a]["vwap"] for a in agent_ids]
        volumes = [vwap_data[a]["total_volume"] for a in agent_ids]
        x_pos = np.arange(len(agent_ids))
        axes[0].bar(x_pos, vwaps, color="steelblue", alpha=0.8)
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
        axes[0].set_ylabel("VWAP")
        axes[0].legend(fontsize=8)
        axes[0].grid(True, alpha=0.3)

        axes[1].bar(x_pos, volumes, color="coral", alpha=0.8)
        axes[1].set_xticks(x_pos)
        axes[1].set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=8)
        axes[1].set_title("Agent Total Trading Volume")
        axes[1].set_ylabel("Total Volume")
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "03_summary.png"), dpi=150, bbox_inches="tight"
    )
    plt.close()


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def analyze_carry_trade_unwind(
    data: Dict[str, Any],
    config: dict,
    output_dir: str,
) -> Dict[str, Any]:
    """Run full CarryTradeUnwind analysis pipeline."""
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
    unwind_velocity = _compute_unwind_velocity(prices_list)
    unwind_duration = _compute_unwind_duration(prices_list, fund_value)
    recovery_ratio = _compute_recovery_ratio(prices_list)
    cascade_onset_round = _compute_cascade_onset(
        prices_list, fund_value, threshold=-0.05
    )
    peak_volatility_pct = _compute_peak_rolling_volatility(prices_list)
    rolling_vols = _compute_rolling_volatility(prices_list)
    autocorr = _compute_autocorrelation(prices_list)

    # Agent VWAP
    vwap_data = _compute_agent_vwap(investor_payloads, market_prices)

    # Validation
    validation = _validate_carry_trade_unwind(
        max_drawdown_pct=max_drawdown_pct,
        recovery_ratio=recovery_ratio,
        peak_volatility_pct=peak_volatility_pct,
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
        cascade_onset_round=cascade_onset_round,
        output_dir=output_dir,
    )

    # Summary
    summary = {
        "scenario": "CarryTradeUnwind",
        "variant": "Rule",
        "total_rounds": total_rounds,
        "fundamental_value": round(fund_value, 4),
        "metrics": {
            "max_drawdown_pct": round(max_drawdown_pct, 4),
            "unwind_velocity": round(unwind_velocity, 4),
            "unwind_duration_rounds": unwind_duration,
            "recovery_ratio": round(recovery_ratio, 4),
            "cascade_onset_round": cascade_onset_round,
            "peak_rolling_vol_pct": round(peak_volatility_pct, 4),
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
    print("CARRY TRADE UNWIND ANALYSIS")
    print("=" * 50)
    print(f"Max drawdown: {max_drawdown_pct:.2f}%  (target: 10–25%)")
    print(f"Unwind velocity: {unwind_velocity:.4f}  (target: 0.10–0.40)")
    print(f"Unwind duration: {unwind_duration} rounds  (target: 5–30)")
    print(f"Recovery ratio: {recovery_ratio:.3f}  (target: 0.3–0.7)")
    print(f"Peak volatility: {peak_volatility_pct:.2f}% per round  (target: >3%)")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}  (target: >+0.2)")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run CarryTradeUnwind Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze CarryTradeUnwind simulation")
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
    summary = analyze_carry_trade_unwind(data, config, output_dir)
    # [polish-hook-9] universal baseline invocation
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'Rule'
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
        scenario='CarryTradeUnwind',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


if __name__ == "__main__":
    main()
