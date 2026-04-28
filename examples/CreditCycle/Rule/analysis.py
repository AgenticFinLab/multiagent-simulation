#!/usr/bin/env python
"""CreditCycle Rule-Based Simulation Analysis

Analyzes credit boom-bust cycle dynamics driven by pro-cyclical lending,
Minsky fragility, and counter-cyclical stabilization.
Based on analysis-bases.md calibration targets (Geanakoplos 2010 / Minsky 1986).

Usage:
    python examples/CreditCycle/Rule/analysis.py \
        -c configs/CreditCycle/Rule/simulation.yml
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
    """Convert batch store list to {round_num: value}, round_num is 1-based."""
    return {i + 1: v for i, v in enumerate(values)}


def _load_data(results) -> Dict[str, Any]:
    """Load price/fundamental batch stores and investor turn payloads.

    Returns
    -------
    dict with keys:
        market_prices       : {round_num: float}
        fundamentals        : {round_num: float}
        investor_payloads   : {player_id: {round_num: dict}}
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
# Metrics  (analysis-bases.md §2)
# ---------------------------------------------------------------------------


def _compute_peak_deviation(
    prices_list: List[float], fundamental: float
) -> Tuple[float, float]:
    """Peak positive and trough negative deviation from fundamental (fraction).

    Returns (peak_positive, trough_negative) as absolute fractions.
    """
    if not prices_list or fundamental <= 0:
        return (0.0, 0.0)
    deviations = [(p - fundamental) / fundamental for p in prices_list]
    peak = max(deviations) if deviations else 0.0
    trough = min(deviations) if deviations else 0.0
    return (float(peak), float(trough))


def _compute_leverage_amplitude_index(peak: float, trough: float) -> float:
    """LAI = |peak_positive_deviation| / |trough_negative_deviation|.

    analysis-bases.md §2.1 — Geanakoplos (2010).
    """
    if abs(trough) < 1e-12:
        return float("inf") if peak > 0 else 0.0
    return abs(peak) / abs(trough)


def _compute_minsky_fragility_score(
    investor_payloads: Dict[str, Dict[int, dict]],
    prices_list: List[float],
    fundamental: float,
    crisis_threshold: float = -0.05,
) -> float:
    """MFS — average stable_rounds before bust events. analysis-bases.md §2.2.

    Approximation: count consecutive rounds where |δ|<0.02 before each bust onset.
    """
    if not prices_list or fundamental <= 0:
        return 0.0
    deviations = [(p - fundamental) / fundamental for p in prices_list]
    # Find bust onsets: first round crossing crisis_threshold after stable
    bust_onsets: List[int] = []
    in_crisis = False
    for i, d in enumerate(deviations):
        if d < crisis_threshold and not in_crisis:
            bust_onsets.append(i)
            in_crisis = True
        elif d >= crisis_threshold * 0.5:
            in_crisis = False

    if not bust_onsets:
        return 0.0

    scores: List[float] = []
    for onset in bust_onsets:
        stable = 0
        for j in range(onset - 1, -1, -1):
            if abs(deviations[j]) < 0.02:
                stable += 1
            else:
                break
        scores.append(float(stable))
    return float(np.mean(scores)) if scores else 0.0


def _compute_credit_contraction_speed(prices_list: List[float]) -> float:
    """CCS — price units per round from peak to trough. analysis-bases.md §2.3."""
    if len(prices_list) < 2:
        return 0.0
    peak_val = max(prices_list)
    peak_idx = prices_list.index(peak_val)
    post_peak = prices_list[peak_idx:]
    trough_val = min(post_peak)
    trough_idx = peak_idx + post_peak.index(trough_val)
    if trough_idx == peak_idx:
        return 0.0
    return float((peak_val - trough_val) / (trough_idx - peak_idx))


def _compute_counter_cyclical_offset_ratio(
    investor_payloads: Dict[str, Dict[int, dict]],
    prices_list: List[float],
    fundamental: float,
    bust_threshold: float = -0.05,
) -> float:
    """CCOR — stabilizer buy / destabilizer sell during bust. analysis-bases.md §2.4."""
    if not prices_list or fundamental <= 0:
        return 0.0
    deviations = [(p - fundamental) / fundamental for p in prices_list]
    bust_rounds = {i + 1 for i, d in enumerate(deviations) if d < bust_threshold}
    if not bust_rounds:
        return 0.0

    stabilizer_buy = 0.0
    destabilizer_sell = 0.0
    stabilizer_types = {
        "CounterCyclicalLender",
        "ValueInvestor",
        "RagLLMCounterCyclicalLender",
        "RagLLMValueInvestor",
    }
    destabilizer_types = {
        "ProCyclicalLender",
        "MinskyBorrower",
        "RagLLMProCyclicalLender",
        "RagLLMMinskyBorrower",
    }

    for aid, rp in investor_payloads.items():
        agent_type = aid.split("_")[0] if "_" in aid else aid
        for rnd, payload in rp.items():
            if rnd not in bust_rounds:
                continue
            action = payload.get("action", "hold")
            qty = float(payload.get("quantity", 0))
            if any(t in aid for t in stabilizer_types):
                if action == "buy":
                    stabilizer_buy += qty
            if any(t in aid for t in destabilizer_types):
                if action == "sell":
                    destabilizer_sell += qty

    if destabilizer_sell < 1e-6:
        return float("inf") if stabilizer_buy > 0 else 0.0
    return float(stabilizer_buy / destabilizer_sell)


def _compute_phase_duration_ratio(
    prices_list: List[float], fundamental: float, threshold: float = 0.02
) -> float:
    """PDR — expansion rounds / contraction rounds. analysis-bases.md §2.5."""
    if not prices_list or fundamental <= 0:
        return 0.0
    deviations = [(p - fundamental) / fundamental for p in prices_list]
    expansion = sum(1 for d in deviations if d > threshold)
    contraction = sum(1 for d in deviations if d < -threshold)
    if contraction == 0:
        return float("inf") if expansion > 0 else 1.0
    return float(expansion / contraction)


def _compute_max_drawdown(prices_list: List[float]) -> float:
    """Maximum peak-to-trough drawdown (%, positive value)."""
    arr = np.array(prices_list)
    if len(arr) < 2:
        return 0.0
    peak = arr[0]
    max_dd = 0.0
    for price in arr:
        if price > peak:
            peak = price
        dd = (peak - price) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
    return float(max_dd * 100)


def _compute_peak_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> float:
    """Peak rolling volatility of returns (std dev per window, %)."""
    arr = np.array(prices_list)
    if len(arr) < 2:
        return 0.0
    returns = np.diff(arr) / arr[:-1] * 100
    peak_vol = 0.0
    for i in range(len(returns)):
        start = max(0, i - window + 1)
        vol = float(np.std(returns[start : i + 1]))
        if vol > peak_vol:
            peak_vol = vol
    return peak_vol


def _compute_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> List[float]:
    """Rolling volatility time series."""
    arr = np.array(prices_list)
    if len(arr) < 2:
        return []
    returns = np.diff(arr) / arr[:-1] * 100
    vols = []
    for i in range(len(returns)):
        start = max(0, i - window + 1)
        vols.append(float(np.std(returns[start : i + 1])))
    return vols


def _compute_autocorrelation(prices_list: List[float], lag: int = 1) -> float:
    """Lag-1 autocorrelation of returns."""
    arr = np.array(prices_list)
    if len(arr) < lag + 2:
        return 0.0
    returns = np.diff(arr) / arr[:-1]
    n = len(returns)
    if n <= lag:
        return 0.0
    mu = np.mean(returns)
    centered = returns - mu
    autocov = np.mean(centered[: n - lag] * centered[lag:])
    var = np.var(centered)
    if var < 1e-12:
        return 0.0
    return float(autocov / var)


def _compute_agent_vwap(
    investor_payloads: Dict[str, Dict[int, dict]],
    market_prices: Dict[int, float],
) -> Dict[str, Dict[str, float]]:
    """Compute VWAP and total volume by agent."""
    vwap_data: Dict[str, Dict[str, float]] = {}
    for aid, round_payloads in investor_payloads.items():
        pv_sum = 0.0
        total_vol = 0.0
        total_buy = 0.0
        total_sell = 0.0
        for rnd, payload in round_payloads.items():
            qty = float(payload.get("quantity", 0))
            price = market_prices.get(rnd, 0.0)
            abs_qty = abs(qty)
            pv_sum += abs_qty * price
            total_vol += abs_qty
            action = payload.get("action", "hold")
            if action == "buy":
                total_buy += qty
            elif action == "sell":
                total_sell += qty
        vwap_data[aid] = {
            "vwap": pv_sum / total_vol if total_vol > 0 else 0.0,
            "total_volume": total_vol,
            "total_buy": total_buy,
            "total_sell": total_sell,
        }
    return vwap_data


# ---------------------------------------------------------------------------
# Validation  (analysis-bases.md §6)
# ---------------------------------------------------------------------------


@dataclass
class CreditCycleValidationResult:
    """Result of CreditCycle simulation validation."""

    is_valid: bool
    score: float  # 0-1 overall fit score
    criteria: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": round(self.score, 4),
            "criteria": self.criteria,
            "interpretation": self.interpretation,
        }


def _validate_credit_cycle(
    peak_deviation_pct: float,
    ccor: float,
    lai: float,
    mfs: float,
    total_rounds: int,
) -> CreditCycleValidationResult:
    """Validate CreditCycle results against analysis-bases.md §6 calibration targets.

    Criteria
    --------
    1. Peak boom deviation target [8%, 15%]   weight 0.30  (Geanakoplos 2010)
    2. CCOR              target [0.4, 0.6]    weight 0.25  (Basel III CCyB)
    3. LAI               target [1.0, 2.0]    weight 0.25  (Geanakoplos 2010 §4)
    4. MFS               target [4, 8] rounds weight 0.20  (Minsky 1986)
    """
    criteria = {}

    # --- Criterion 1: Peak boom deviation in [8%, 15%] ---
    if 8.0 <= peak_deviation_pct <= 15.0:
        dev_score = 1.0
    elif 4.0 <= peak_deviation_pct < 8.0:
        dev_score = 0.4 + (peak_deviation_pct - 4.0) / 4.0 * 0.6
    elif 15.0 < peak_deviation_pct <= 25.0:
        dev_score = 1.0 - (peak_deviation_pct - 15.0) / 10.0 * 0.5
    elif peak_deviation_pct > 25.0:
        dev_score = 0.1
    else:
        dev_score = peak_deviation_pct / 8.0 * 0.4

    criteria["peak_deviation"] = {
        "value": round(peak_deviation_pct, 3),
        "target": "8–15%",
        "score": round(dev_score, 3),
        "passed": 4.0 <= peak_deviation_pct <= 25.0,
    }

    # --- Criterion 2: CCOR in [0.4, 0.6] ---
    if 0.4 <= ccor <= 0.6:
        ccor_score = 1.0
    elif 0.2 <= ccor < 0.4:
        ccor_score = 0.4 + (ccor - 0.2) / 0.2 * 0.6
    elif 0.6 < ccor <= 0.9:
        ccor_score = 1.0 - (ccor - 0.6) / 0.3 * 0.5
    elif ccor > 0.9:
        ccor_score = 0.2
    else:
        ccor_score = ccor / 0.4 * 0.4

    criteria["ccor"] = {
        "value": round(ccor, 4),
        "target": "0.4–0.6",
        "score": round(ccor_score, 3),
        "passed": 0.2 <= ccor <= 0.9,
    }

    # --- Criterion 3: LAI in [1.0, 2.0] ---
    if 1.0 <= lai <= 2.0:
        lai_score = 1.0
    elif 0.5 <= lai < 1.0:
        lai_score = 0.4 + (lai - 0.5) / 0.5 * 0.6
    elif 2.0 < lai <= 3.5:
        lai_score = 1.0 - (lai - 2.0) / 1.5 * 0.5
    elif lai > 3.5:
        lai_score = 0.1
    else:
        lai_score = lai / 1.0 * 0.4

    criteria["lai"] = {
        "value": round(lai, 4),
        "target": "1.0–2.0",
        "score": round(lai_score, 3),
        "passed": 0.5 <= lai <= 3.5,
    }

    # --- Criterion 4: MFS in [4, 8] rounds ---
    if 4.0 <= mfs <= 8.0:
        mfs_score = 1.0
    elif 2.0 <= mfs < 4.0:
        mfs_score = 0.4 + (mfs - 2.0) / 2.0 * 0.6
    elif 8.0 < mfs <= 15.0:
        mfs_score = 1.0 - (mfs - 8.0) / 7.0 * 0.5
    elif mfs > 15.0:
        mfs_score = 0.1
    else:
        mfs_score = mfs / 4.0 * 0.4

    criteria["mfs"] = {
        "value": round(mfs, 3),
        "target": "4–8 rounds",
        "score": round(mfs_score, 3),
        "passed": 2.0 <= mfs <= 15.0,
    }

    overall_score = (
        dev_score * 0.30 + ccor_score * 0.25 + lai_score * 0.25 + mfs_score * 0.20
    )
    is_valid = overall_score > 0.50 and peak_deviation_pct >= 3.0

    interpretation = _build_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        peak_deviation_pct=peak_deviation_pct,
        ccor=ccor,
        lai=lai,
        mfs=mfs,
        total_rounds=total_rounds,
        dev_score=dev_score,
        ccor_score=ccor_score,
        lai_score=lai_score,
        mfs_score=mfs_score,
    )

    return CreditCycleValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def _build_interpretation(
    is_valid: bool,
    overall_score: float,
    peak_deviation_pct: float,
    ccor: float,
    lai: float,
    mfs: float,
    total_rounds: int,
    dev_score: float,
    ccor_score: float,
    lai_score: float,
    mfs_score: float,
) -> str:
    """Build structured validation report following analysis-bases.md §6."""
    verdict = "VALID" if is_valid else "INVALID"
    lines = []
    lines.append(f"=== CREDIT CYCLE SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Criterion 1: Peak Boom Deviation
    if peak_deviation_pct >= 8.0:
        dev_assess = "PASS — Boom amplitude consistent with Geanakoplos leverage cycle calibration."
    elif peak_deviation_pct >= 4.0:
        dev_assess = "WEAK — Boom present but below target; increase credit_multiplier or reduce mean_reversion."
    else:
        dev_assess = (
            "FAIL — Boom too weak; ProCyclicalLender not amplifying sufficiently."
        )
    lines.append("[1] CREDIT BOOM AMPLITUDE (PEAK DEVIATION)")
    lines.append(f"    Observed: Peak positive deviation = {peak_deviation_pct:.2f}%")
    lines.append(
        f"    Expected: 8–15% (Geanakoplos 2010: leverage cycle peak; Reinhart & Rogoff 2009)"
    )
    lines.append(f"    Score: {dev_score:.1%}")
    lines.append(f"    Assessment: {dev_assess}")
    lines.append("")

    # Criterion 2: CCOR
    if 0.4 <= ccor <= 0.6:
        ccor_assess = "PASS — Counter-cyclical offset balanced; stabilizers absorb 40–60% of bust selling."
    elif ccor < 0.3:
        ccor_assess = (
            "WEAK — Stabilizers too weak; increase CounterCyclicalLender order_size."
        )
    else:
        ccor_assess = "HIGH — Stabilizers dominate; cycle may be over-dampened."
    lines.append("[2] COUNTER-CYCLICAL OFFSET (CCOR)")
    lines.append(f"    Observed: CCOR = {ccor:.3f}")
    lines.append(
        f"    Expected: 0.4–0.6 (Basel III CCyB: counter-cyclical buffers absorb ~50% bust pressure)"
    )
    lines.append(f"    Score: {ccor_score:.1%}")
    lines.append(f"    Assessment: {ccor_assess}")
    lines.append("")

    # Criterion 3: LAI
    if 1.0 <= lai <= 2.0:
        lai_assess = "PASS — Leverage amplitude asymmetry consistent with historical credit cycles."
    elif lai < 1.0:
        lai_assess = "LOW — Booms shorter than busts; atypical cycle shape."
    else:
        lai_assess = (
            "HIGH — Extreme boom-bust asymmetry; check ProCyclicalLender parameters."
        )
    lines.append("[3] LEVERAGE ASYMMETRY (LAI)")
    lines.append(f"    Observed: LAI = {lai:.3f}")
    lines.append(
        f"    Expected: 1.0–2.0 (Geanakoplos 2010 §4: booms somewhat longer than busts)"
    )
    lines.append(f"    Score: {lai_score:.1%}")
    lines.append(f"    Assessment: {lai_assess}")
    lines.append("")

    # Criterion 4: MFS
    if 4.0 <= mfs <= 8.0:
        mfs_assess = (
            "PASS — Minsky fragility accumulates over 4–8 stable rounds before bust."
        )
    elif mfs < 2.0:
        mfs_assess = "LOW — Insufficient stability before bust; system too volatile for Minsky build-up."
    else:
        mfs_assess = "HIGH — Extended stability breeds deep fragility; bust may be unusually severe."
    lines.append("[4] MINSKY FRAGILITY (MFS)")
    lines.append(f"    Observed: MFS = {mfs:.1f} rounds")
    lines.append(
        f"    Expected: 4–8 rounds (Minsky 1986: hedge→speculative→Ponzi transition period)"
    )
    lines.append(f"    Score: {mfs_score:.1%}")
    lines.append(f"    Assessment: {mfs_assess}")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            f"The simulation successfully reproduces credit cycle boom-bust dynamics: "
            f"peak boom deviation {peak_deviation_pct:.1f}%, "
            f"CCOR {ccor:.2f}, LAI {lai:.2f}, MFS {mfs:.1f} rounds. "
            f"The Geanakoplos leverage cycle mechanism (pro-cyclical lending → boom → "
            f"Minsky fragility → bust → counter-cyclical offset) is operating as designed. "
            f"Fit Score: {overall_score:.1%}."
        )
    else:
        lines.append(
            f"The simulation does not fully reproduce credit cycle dynamics. "
            f"Overall Fit Score {overall_score:.1%} is below the 50% threshold. "
            f"Key issues: "
            + ("boom too weak; " if peak_deviation_pct < 8.0 else "")
            + ("CCOR out of range; " if not (0.2 <= ccor <= 0.9) else "")
            + ("LAI out of range; " if not (0.5 <= lai <= 3.5) else "")
            + ("MFS too low; " if mfs < 2.0 else "")
            + "Review analysis-bases.md §6 for parameter fixes."
        )
    lines.append(f"Fit Score: {overall_score:.1%}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualizations  (analysis-bases.md §7)
# ---------------------------------------------------------------------------


def _create_visualizations(
    market_prices: Dict[int, float],
    fundamentals: Dict[int, float],
    investor_payloads: Dict[str, Dict[int, dict]],
    rolling_vols: List[float],
    output_dir: str,
) -> None:
    """Create 3 analysis plots per analysis-bases.md §7.

    Plots
    -----
    01_price_dynamics.png   : Price vs Fundamental + Deviation %
    02_cycle_dynamics.png   : Rolling Volatility + Phase attribution
    03_summary.png          : Agent VWAP comparison + Volume
    """
    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    fund_value = float(np.mean(list(fundamentals.values()))) if fundamentals else 100.0
    fund_list = [fundamentals.get(r, fund_value) for r in rounds_sorted]
    rounds_arr = np.array(rounds_sorted)
    prices_arr = np.array(prices_list)
    fund_arr = np.array(fund_list)
    deviation = (prices_arr - fund_arr) / fund_arr * 100

    # ---- Plot 01: Price Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "CreditCycle — Price & Credit Dynamics", fontsize=13, fontweight="bold"
    )

    axes[0].plot(
        rounds_arr, prices_arr, label="Market Price", color="darkblue", linewidth=1.5
    )
    axes[0].plot(
        rounds_arr,
        fund_arr,
        label="Fundamental",
        color="green",
        linestyle="--",
        linewidth=1.2,
    )
    axes[0].set_title("Price vs Fundamental")
    axes[0].set_xlabel("Round")
    axes[0].set_ylabel("Price")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(rounds_arr, deviation, color="darkred", linewidth=1.5)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].axhline(
        y=8, color="orange", linestyle=":", alpha=0.7, label="+8% boom floor"
    )
    axes[1].axhline(
        y=15, color="red", linestyle=":", alpha=0.7, label="+15% boom ceiling"
    )
    axes[1].axhline(
        y=-5, color="blue", linestyle=":", alpha=0.7, label="−5% bust threshold"
    )
    axes[1].set_title("Price Deviation from Fundamental (%)")
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "01_price_dynamics.png"), dpi=150, bbox_inches="tight"
    )
    plt.close()

    # ---- Plot 02: Cycle Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "CreditCycle — Cycle Intensity Analysis", fontsize=13, fontweight="bold"
    )

    if rolling_vols and len(prices_list) > 1:
        vol_rounds = rounds_arr[1:]
        axes[0].plot(vol_rounds, rolling_vols, color="purple", linewidth=1.5)
        axes[0].axhline(
            y=2.0,
            color="orange",
            linestyle=":",
            alpha=0.7,
            label="2% cycle threshold",
        )
        axes[0].set_title("Rolling Volatility (10-round window, %)")
        axes[0].set_xlabel("Round")
        axes[0].set_ylabel("Volatility (%)")
        axes[0].legend(fontsize=8)
        axes[0].grid(True, alpha=0.3)

    # Phase classification
    expansion = deviation > 2.0
    contraction = deviation < -2.0
    axes[1].fill_between(
        rounds_arr,
        0,
        deviation,
        where=expansion,
        color="lightcoral",
        alpha=0.4,
        label="Expansion (δ>2%)",
    )
    axes[1].fill_between(
        rounds_arr,
        0,
        deviation,
        where=contraction,
        color="lightblue",
        alpha=0.4,
        label="Contraction (δ<-2%)",
    )
    axes[1].plot(rounds_arr, deviation, color="black", linewidth=0.8)
    axes[1].axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    axes[1].set_title("Phase Classification")
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "02_cycle_dynamics.png"), dpi=150, bbox_inches="tight"
    )
    plt.close()

    # ---- Plot 03: Agent Summary ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("CreditCycle — Agent Activity Summary", fontsize=13, fontweight="bold")

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
                y=fund_value,
                color="green",
                linestyle="--",
                alpha=0.7,
                label=f"Fundamental={fund_value:.1f}",
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


def analyze_credit_cycle(
    data: Dict[str, Any],
    config: dict,
    output_dir: str,
) -> Dict[str, Any]:
    """Run full CreditCycle analysis pipeline.

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
    fund_value = float(np.mean(list(fundamentals.values()))) if fundamentals else 100.0
    total_rounds = len(rounds_sorted)

    # Metrics
    peak_dev, trough_dev = _compute_peak_deviation(prices_list, fund_value)
    peak_deviation_pct = peak_dev * 100
    lai = _compute_leverage_amplitude_index(peak_dev, trough_dev)
    mfs = _compute_minsky_fragility_score(investor_payloads, prices_list, fund_value)
    ccs = _compute_credit_contraction_speed(prices_list)
    ccor = _compute_counter_cyclical_offset_ratio(
        investor_payloads, prices_list, fund_value
    )
    pdr = _compute_phase_duration_ratio(prices_list, fund_value)
    max_dd = _compute_max_drawdown(prices_list)
    peak_vol = _compute_peak_rolling_volatility(prices_list)
    rolling_vols = _compute_rolling_volatility(prices_list)
    autocorr = _compute_autocorrelation(prices_list)

    # Agent VWAP
    vwap_data = _compute_agent_vwap(investor_payloads, market_prices)

    # Validation
    validation = _validate_credit_cycle(
        peak_deviation_pct=peak_deviation_pct,
        ccor=ccor,
        lai=lai,
        mfs=mfs,
        total_rounds=total_rounds,
    )

    # Plots
    print(f"Generating analysis plots in {output_dir}/")
    _create_visualizations(
        market_prices=market_prices,
        fundamentals=fundamentals,
        investor_payloads=investor_payloads,
        rolling_vols=rolling_vols,
        output_dir=output_dir,
    )

    # Summary
    summary = {
        "scenario": "CreditCycle",
        "variant": "Rule",
        "total_rounds": total_rounds,
        "fundamental_value": round(fund_value, 4),
        "metrics": {
            "peak_deviation_pct": round(peak_deviation_pct, 4),
            "trough_deviation_pct": round(trough_dev * 100, 4),
            "leverage_amplitude_index": round(lai, 4),
            "minsky_fragility_score": round(mfs, 4),
            "credit_contraction_speed": round(ccs, 4),
            "counter_cyclical_offset_ratio": round(ccor, 4),
            "phase_duration_ratio": round(pdr, 4),
            "max_drawdown_pct": round(max_dd, 4),
            "peak_rolling_vol_pct": round(peak_vol, 4),
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
    print("CREDIT CYCLE ANALYSIS")
    print("=" * 50)
    print(f"Peak boom deviation: {peak_deviation_pct:.2f}%  (target: 8–15%)")
    print(f"CCOR: {ccor:.3f}  (target: 0.4–0.6)")
    print(f"LAI: {lai:.3f}  (target: 1.0–2.0)")
    print(f"MFS: {mfs:.1f} rounds  (target: 4–8)")
    print(f"CCS: {ccs:.2f} price units/round")
    print(f"PDR: {pdr:.2f}  (target: 1.5–3.0)")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run CreditCycle Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze CreditCycle simulation")
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
    summary = analyze_credit_cycle(data, config, output_dir)
    return summary


__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "_validate_credit_cycle",
    "_build_interpretation",
    "analyze_credit_cycle",
]

if __name__ == "__main__":
    main()
