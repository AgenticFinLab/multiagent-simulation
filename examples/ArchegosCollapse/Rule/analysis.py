#!/usr/bin/env python
"""ArchegosCollapse Rule-Based Simulation Analysis

Analyzes simulation results for forced-liquidation cascade dynamics and
prime-broker first-mover advantage.
Based on analysis-bases.md calibration targets (Archegos 2021 / FSB 2022).

Usage:
    python examples/ArchegosCollapse/Rule/analysis.py \
        -c configs/ArchegosCollapse/Rule/simulation.yml
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results
from examples.standard_rule_analysis import _market_data_from_payload, _market_players

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

    for player in _market_players(results).values():
        if "price" in player.batch_store_names:
            market_prices.update(_batch_to_rounds(player.batch("price").all()))
        if "fundamental" in player.batch_store_names:
            fundamentals.update(_batch_to_rounds(player.batch("fundamental").all()))
        for round_num, payload in player.turns.payloads().items():
            market_data = _market_data_from_payload(payload)
            if round_num not in market_prices and "price" in market_data:
                market_prices[round_num] = float(market_data["price"])
            if round_num not in fundamentals:
                if "fundamental" in market_data:
                    fundamentals[round_num] = float(market_data["fundamental"])
                elif "fundamental_value" in market_data:
                    fundamentals[round_num] = float(market_data["fundamental_value"])

    investor_bids: Dict[str, Dict[int, float]] = {}
    investor_payloads: Dict[str, Dict[int, dict]] = {}
    for pid, player in results.players_by_role("player").items():
        bid = player.turns.field("bid_price")
        if bid:
            investor_bids[pid] = bid
        payloads = player.turns.payloads()
        if payloads:
            investor_payloads[pid] = payloads

    return {
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "investor_bids": investor_bids,
        "investor_payloads": investor_payloads,
    }


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


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


def _compute_cascade_onset(
    prices_list: List[float], fundamental: float, threshold: float = -0.10
) -> Optional[int]:
    """First round where deviation crosses threshold (default -10%)."""
    for i, p in enumerate(prices_list):
        if fundamental > 0 and (p - fundamental) / fundamental < threshold:
            return i + 1  # 1-based round number
    return None


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
    """Compute VWAP and total volume by agent.

    Returns dict: {agent_id: {"vwap": float, "total_volume": float, "total_buy": float, "total_sell": float}}
    """
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
            action = payload["action"]
            if action == "buy":
                total_buy += abs_qty
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
class ArchegosCollapseValidationResult:
    """Result of ArchegosCollapse simulation validation."""

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


def _validate_archegos_collapse(
    max_drawdown_pct: float,
    cascade_onset_round: Optional[int],
    peak_volatility_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
) -> ArchegosCollapseValidationResult:
    """Validate ArchegosCollapse results against analysis-bases.md §6 calibration targets.

    Criteria
    --------
    1. Max drawdown    target [20%, 60%]    weight 0.35  (Archegos ViacomCBS −60%; FSB 2022)
    2. Cascade onset   target [10, 30]      weight 0.30  (Brunnermeier 2009 leverage cascade)
    3. Peak volatility target [3%, 8%]      weight 0.20  (Andersen et al. 2003; Archegos stocks)
    4. AC1 cascade     target [0.20, 0.50]  weight 0.15  (Brunnermeier & Pedersen 2009)
    """
    criteria = {}

    # --- Criterion 1: Max drawdown in [20%, 60%] ---
    if 20.0 <= max_drawdown_pct <= 60.0:
        dd_score = 1.0
    elif 10.0 <= max_drawdown_pct < 20.0:
        dd_score = 0.4 + (max_drawdown_pct - 10.0) / 10.0 * 0.6
    elif 60.0 < max_drawdown_pct <= 80.0:
        dd_score = 1.0 - (max_drawdown_pct - 60.0) / 20.0 * 0.5
    elif max_drawdown_pct > 80.0:
        dd_score = 0.1
    else:
        dd_score = max_drawdown_pct / 20.0 * 0.4

    criteria["max_drawdown"] = {
        "value": round(max_drawdown_pct, 3),
        "target": "20–60%",
        "score": round(dd_score, 3),
        "passed": 10.0 <= max_drawdown_pct <= 80.0,
    }

    # --- Criterion 2: Cascade onset round in [10, 30] ---
    if cascade_onset_round is None:
        onset_score = 0.0
    elif 10 <= cascade_onset_round <= 30:
        onset_score = 1.0
    elif 5 <= cascade_onset_round < 10:
        onset_score = 0.4 + (cascade_onset_round - 5) / 5.0 * 0.6
    elif 30 < cascade_onset_round <= 45:
        onset_score = 1.0 - (cascade_onset_round - 30) / 15.0 * 0.5
    else:
        onset_score = 0.1

    criteria["cascade_onset"] = {
        "value": cascade_onset_round,
        "target": "rounds 10–30",
        "score": round(onset_score, 3),
        "passed": cascade_onset_round is not None and 5 <= cascade_onset_round <= 45,
    }

    # --- Criterion 3: Peak rolling volatility in [3%, 8%] ---
    if 3.0 <= peak_volatility_pct <= 8.0:
        vol_score = 1.0
    elif 1.5 <= peak_volatility_pct < 3.0:
        vol_score = 0.4 + (peak_volatility_pct - 1.5) / 1.5 * 0.6
    elif 8.0 < peak_volatility_pct <= 15.0:
        vol_score = 1.0 - (peak_volatility_pct - 8.0) / 7.0 * 0.5
    elif peak_volatility_pct > 15.0:
        vol_score = 0.1
    else:
        vol_score = peak_volatility_pct / 3.0 * 0.4

    criteria["peak_volatility"] = {
        "value": round(peak_volatility_pct, 3),
        "target": "3–8% per round",
        "score": round(vol_score, 3),
        "passed": 1.5 <= peak_volatility_pct <= 15.0,
    }

    # --- Criterion 4: AC1 in [0.20, 0.50] ---
    if 0.20 <= autocorr_lag1 <= 0.50:
        ac_score = 1.0
    elif 0.10 <= autocorr_lag1 < 0.20:
        ac_score = 0.4 + (autocorr_lag1 - 0.10) / 0.10 * 0.6
    elif 0.50 < autocorr_lag1 <= 0.70:
        ac_score = 1.0 - (autocorr_lag1 - 0.50) / 0.20 * 0.4
    elif autocorr_lag1 < 0.0:
        ac_score = max(0.0, 0.2 + autocorr_lag1 * 0.5)
    else:
        ac_score = autocorr_lag1 / 0.20 * 0.4

    criteria["autocorrelation"] = {
        "value": round(autocorr_lag1, 4),
        "target": "0.20–0.50",
        "score": round(ac_score, 3),
        "passed": 0.10 <= autocorr_lag1 <= 0.70,
    }

    overall_score = (
        dd_score * 0.35 + onset_score * 0.30 + vol_score * 0.20 + ac_score * 0.15
    )
    is_valid = overall_score > 0.50 and max_drawdown_pct >= 5.0

    interpretation = _build_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        max_drawdown_pct=max_drawdown_pct,
        cascade_onset_round=cascade_onset_round,
        peak_volatility_pct=peak_volatility_pct,
        autocorr_lag1=autocorr_lag1,
        total_rounds=total_rounds,
        dd_score=dd_score,
        onset_score=onset_score,
        vol_score=vol_score,
        ac_score=ac_score,
    )

    return ArchegosCollapseValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def _build_interpretation(
    is_valid: bool,
    overall_score: float,
    max_drawdown_pct: float,
    cascade_onset_round: Optional[int],
    peak_volatility_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
    dd_score: float,
    onset_score: float,
    vol_score: float,
    ac_score: float,
) -> str:
    """Build structured validation report following analysis-bases.md §6."""
    verdict = "VALID" if is_valid else "INVALID"
    lines = []
    lines.append(f"=== ARCHEGOS COLLAPSE SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Criterion 1: Max Drawdown
    if max_drawdown_pct >= 20.0:
        dd_assess = (
            "PASS — Cascade depth consistent with Archegos prime-broker liquidation."
        )
    elif max_drawdown_pct >= 10.0:
        dd_assess = "WEAK — Cascade present but below calibration target; increase price_impact (λ)."
    else:
        dd_assess = "FAIL — Cascade too shallow; liquidation not producing significant sell-off."
    lines.append("[1] FORCED-LIQUIDATION CASCADE DEPTH (MAX DRAWDOWN)")
    lines.append(f"    Observed: Max drawdown = {max_drawdown_pct:.2f}%")
    lines.append(
        f"    Expected: 20–60% (Archegos ViacomCBS −60%, Morgan Stanley −25–40%; FSB 2022, pp. 47–51)"
    )
    lines.append(f"    Score: {dd_score:.1%}")
    lines.append(f"    Assessment: {dd_assess}")
    lines.append("")

    # Criterion 2: Cascade Onset Round
    onset_str = (
        str(cascade_onset_round) if cascade_onset_round else "N/A (never reached −10%)"
    )
    if cascade_onset_round and 10 <= cascade_onset_round <= 30:
        onset_assess = "PASS — Cascade onset timing matches Archegos 3–5 trading day unfold pattern."
    elif cascade_onset_round and cascade_onset_round < 10:
        onset_assess = "EARLY — Cascade starts before agents fully deploy capital; check initial position."
    elif cascade_onset_round:
        onset_assess = (
            "LATE — Position building too slow; check leverage_trigger threshold."
        )
    else:
        onset_assess = (
            "FAIL — Cascade never started; ConcentratedFund not triggering margin call."
        )
    lines.append("[2] CASCADE TIMING (ONSET ROUND)")
    lines.append(f"    Observed: Cascade onset round = {onset_str}")
    lines.append(
        f"    Expected: Rounds 10–30 (Brunnermeier 2009: leverage cascades unfold 1–3 trading days)"
    )
    lines.append(f"    Score: {onset_score:.1%}")
    lines.append(f"    Assessment: {onset_assess}")
    lines.append("")

    # Criterion 3: Peak Volatility
    if peak_volatility_pct >= 3.0:
        vol_assess = "PASS — Cascade volatility consistent with Archegos-affected stocks intraday activity."
    elif peak_volatility_pct >= 1.5:
        vol_assess = "WEAK — Cascade active but low turbulence; consider increasing price_impact (λ)."
    else:
        vol_assess = "FAIL — No significant volatility spike; forced selling not impacting prices."
    lines.append("[3] CASCADE INTENSITY (PEAK ROLLING VOLATILITY)")
    lines.append(
        f"    Observed: Peak 10-round volatility = {peak_volatility_pct:.2f}% per round"
    )
    lines.append(
        f"    Expected: 3–8% per round (Archegos stocks 5–8% intraday; Andersen et al. 2003)"
    )
    lines.append(f"    Score: {vol_score:.1%}")
    lines.append(f"    Assessment: {vol_assess}")
    lines.append("")

    # Criterion 4: Autocorrelation
    if autocorr_lag1 >= 0.20:
        ac_assess = "PASS — Positive momentum confirms funding-liquidity spiral self-reinforcement."
    elif autocorr_lag1 >= 0.10:
        ac_assess = "WEAK — Mild momentum; cascade partially self-reinforcing."
    else:
        ac_assess = "FAIL — No momentum signature; cascade not self-reinforcing via margin calls."
    lines.append("[4] CASCADE SELF-REINFORCEMENT (RETURN AUTOCORRELATION AC1)")
    lines.append(f"    Observed: Lag-1 autocorrelation = {autocorr_lag1:.3f}")
    lines.append(
        f"    Expected: 0.20–0.50 (Brunnermeier & Pedersen 2009: funding-liquidity spiral signature)"
    )
    lines.append(f"    Score: {ac_score:.1%}")
    lines.append(f"    Assessment: {ac_assess}")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            f"The simulation successfully reproduces Archegos-style forced-liquidation cascade dynamics: "
            f"a {max_drawdown_pct:.1f}% drawdown with "
            + (
                f"cascade onset at round {cascade_onset_round}"
                if cascade_onset_round
                else "no cascade onset"
            )
            + f", peak volatility {peak_volatility_pct:.1f}% per round, and lag-1 AC1 {autocorr_lag1:.2f}. "
            f"The cascade self-reinforcement mechanism (selling → price fall → more margin calls) is "
            f"operating as designed. Fit Score: {overall_score:.1%}."
        )
    else:
        lines.append(
            f"The simulation does not fully reproduce Archegos-style cascade dynamics. "
            f"Overall Fit Score {overall_score:.1%} is below the 50% threshold. "
            f"Key issues: "
            + ("drawdown too low; " if max_drawdown_pct < 20.0 else "")
            + ("cascade never started; " if cascade_onset_round is None else "")
            + ("volatility insufficient; " if peak_volatility_pct < 3.0 else "")
            + ("no momentum; " if autocorr_lag1 < 0.10 else "")
            + "Review analysis-bases.md §6 Validation Failure Signs for parameter fixes."
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
    """Create 4 analysis plots per analysis-bases.md §7.

    Plots
    -----
    00_investor_bids.png   : Investor Bidding Curves (headline chart)
    01_archegoscollapse_dynamics.png: Price vs Fundamental + Deviation %
    02_archegoscollapse_analysis.png : Rolling Volatility + Return Autocorrelation
    03_summary.png         : Agent VWAP comparison + Cascade onset annotation
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
        "ArchegosCollapse Rule \u2014 Investor Bidding Curves",
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
        "ArchegosCollapse — Price Cascade Dynamics", fontsize=13, fontweight="bold"
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
    if cascade_onset_round:
        axes[0].axvline(
            x=cascade_onset_round,
            color="orange",
            linestyle=":",
            alpha=0.8,
            label=f"Cascade onset (r{cascade_onset_round})",
        )
    axes[0].set_title("Price vs Fundamental")
    axes[0].set_xlabel("Round")
    axes[0].set_ylabel("Price")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(rounds_arr, deviation, color="darkred", linewidth=1.5)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].axhline(
        y=-10, color="orange", linestyle=":", alpha=0.7, label="−10% (PB1 trigger)"
    )
    axes[1].axhline(
        y=-15, color="red", linestyle=":", alpha=0.7, label="−15% (PB2 trigger)"
    )
    axes[1].axhline(
        y=-20, color="darkred", linestyle=":", alpha=0.7, label="−20% (deep cascade)"
    )
    axes[1].set_title("Price Deviation from Fundamental (%)")
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "01_archegoscollapse_dynamics.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 02: Cascade Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "ArchegosCollapse — Cascade Intensity Analysis", fontsize=13, fontweight="bold"
    )

    if rolling_vols and len(prices_list) > 1:
        vol_rounds = rounds_arr[1:]
        axes[0].plot(vol_rounds, rolling_vols, color="purple", linewidth=1.5)
        axes[0].axhline(
            y=3.0,
            color="orange",
            linestyle=":",
            alpha=0.7,
            label="3% cascade threshold",
        )
        axes[0].axhline(
            y=8.0, color="red", linestyle=":", alpha=0.7, label="8% extreme threshold"
        )
        axes[0].set_title("Rolling Volatility (10-round window, %)")
        axes[0].set_xlabel("Round")
        axes[0].set_ylabel("Volatility (%)")
        axes[0].legend(fontsize=8)
        axes[0].grid(True, alpha=0.3)

    if len(prices_list) > 2:
        returns_arr = np.diff(prices_arr) / prices_arr[:-1] * 100
        window = 10
        rolling_ac = []
        for i in range(window, len(returns_arr)):
            seg = returns_arr[max(0, i - window) : i]
            if len(seg) > 2:
                try:
                    ac = float(np.corrcoef(seg[:-1], seg[1:])[0, 1])
                except Exception:
                    ac = 0.0
            else:
                ac = 0.0
            rolling_ac.append(ac)
        ac_rounds = rounds_arr[window + 1 :]
        if len(ac_rounds) == len(rolling_ac):
            axes[1].plot(ac_rounds, rolling_ac, color="steelblue", linewidth=1.5)
            axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
            axes[1].axhline(
                y=0.2,
                color="green",
                linestyle=":",
                alpha=0.7,
                label="AC1=0.20 (momentum)",
            )
            axes[1].axhline(
                y=-0.2,
                color="red",
                linestyle=":",
                alpha=0.7,
                label="AC1=−0.20 (mean revert)",
            )
        axes[1].set_title("Rolling Return Autocorrelation (AC1)")
        axes[1].set_xlabel("Round")
        axes[1].set_ylabel("AC1")
        axes[1].legend(fontsize=8)
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "02_archegoscollapse_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 03: Agent Summary ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "ArchegosCollapse — Agent Activity Summary", fontsize=13, fontweight="bold"
    )

    # VWAP comparison
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
        axes[0].set_title("Agent VWAP (First-Mover Advantage)")
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


def analyze_archegos_collapse(
    data: Dict[str, Any],
    config: dict,
    output_dir: str,
) -> Dict[str, Any]:
    """Run full ArchegosCollapse analysis pipeline.

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
    cascade_onset_round = _compute_cascade_onset(
        prices_list, fund_value, threshold=-0.10
    )
    peak_volatility_pct = _compute_peak_rolling_volatility(prices_list)
    rolling_vols = _compute_rolling_volatility(prices_list)
    autocorr = _compute_autocorrelation(prices_list)

    # Agent VWAP
    vwap_data = _compute_agent_vwap(investor_payloads, market_prices)

    # Validation
    validation = _validate_archegos_collapse(
        max_drawdown_pct=max_drawdown_pct,
        cascade_onset_round=cascade_onset_round,
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
        "scenario": "ArchegosCollapse",
        "variant": "Rule",
        "total_rounds": total_rounds,
        "fundamental_value": round(fund_value, 4),
        "metrics": {
            "max_drawdown_pct": round(max_drawdown_pct, 4),
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
    print("ARCHEGOS COLLAPSE ANALYSIS")
    print("=" * 50)
    print(f"Max drawdown: {max_drawdown_pct:.2f}%  (target: 20–60%)")
    onset_str = str(cascade_onset_round) if cascade_onset_round else "N/A"
    print(f"Cascade onset: round {onset_str}  (target: 10–30)")
    print(f"Peak volatility: {peak_volatility_pct:.2f}% per round  (target: 3–8%)")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}  (target: 0.20–0.50)")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run ArchegosCollapse Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze ArchegosCollapse simulation")
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
    summary = analyze_archegos_collapse(data, config, output_dir)
    return summary


if __name__ == "__main__":
    main()
