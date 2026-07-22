#!/usr/bin/env python
"""AvailabilityBias Rule Simulation Analysis

Validate and analyse AvailabilityBias simulation results against
calibrated academic targets from analysis-bases.md §6.

Validation criteria (analysis-bases.md §6):
    [1] Peak deviation          [5%, 15%]    weight 0.30  Baker & Wurgler 2007
    [2] Bias persistence score  >= 0.10      weight 0.25  Tetlock 2007
    [3] AC1 (bias episode)      [0.20, 0.40] weight 0.25  De Bondt & Thaler 1985
    [4] Stabilization ratio     [0.40, 0.80] weight 0.20  Baker & Wurgler 2007

Usage:
    python examples/AvailabilityBias/Rule/analysis.py \\
        -c configs/AvailabilityBias/Rule/simulation.yml
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation.data_loader import batch_to_rounds, load_data
from masim.evaluation.finance import calculate_autocorrelation
from masim.evaluation import write_universal_summary

# ---------------------------------------------------------------------------
# Data loading (legacy underscore names preserved as thin adapters
# so non-Rule variants that import them keep working)
# ---------------------------------------------------------------------------


def _batch_to_rounds(values: list) -> Dict[int, float]:
    """Legacy adapter -> masim.evaluation.data_loader.batch_to_rounds."""
    return batch_to_rounds(values)


def _load_data(results) -> Dict[str, Any]:
    """Legacy adapter -> masim.evaluation.data_loader.load_data.

    Returns the canonical dict (which is a superset of the previous
    scenario-local shape: adds ``investor_quantities`` while preserving
    the keys this scenario reads: ``market_prices``, ``fundamentals``,
    ``investor_bids``, ``investor_payloads``).
    """
    return load_data(results)


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------


def _compute_peak_deviation(prices: np.ndarray, fundamentals: np.ndarray) -> float:
    """Compute max absolute deviation from fundamental (%)."""
    if len(prices) == 0 or len(fundamentals) == 0:
        return 0.0
    f_safe = np.where(fundamentals > 0, fundamentals, 1.0)
    deviation_pct = np.abs((prices - fundamentals) / f_safe) * 100.0
    return float(np.max(deviation_pct))


def _compute_bias_persistence(
    prices: np.ndarray,
    fundamentals: np.ndarray,
    window: int = 5,
    threshold: float = 5.0,
) -> float:
    """Compute fraction of rounds in sustained bias episode (|dev| > threshold for window rounds)."""
    if len(prices) < window:
        return 0.0
    f_safe = np.where(fundamentals > 0, fundamentals, 1.0)
    deviation_pct = np.abs((prices - fundamentals) / f_safe) * 100.0
    count = 0
    for t in range(window - 1, len(prices)):
        if all(deviation_pct[t - j] > threshold for j in range(window)):
            count += 1
    denom = len(prices) - (window - 1)
    return float(count / denom) if denom > 0 else 0.0


def _compute_rolling_ac1(returns: np.ndarray, window: int = 10) -> float:
    """Compute maximum rolling lag-1 autocorrelation over any window.

    Thin wrapper around ``masim.evaluation.finance.calculate_autocorrelation``
    applied to each sliding window of length ``window`` in the returns
    series; the maximum lag-1 value is returned. Falls back to a single
    full-series lag-1 autocorrelation when the series is shorter than
    ``window + 1``.
    """
    arr = np.asarray(returns, dtype=float)
    if len(arr) < window + 1:
        if len(arr) > 2:
            acf = calculate_autocorrelation(list(arr), max_lag=1)
            return float(acf[0]) if acf else 0.0
        return 0.0
    best = 0.0
    for start in range(len(arr) - window):
        seg = arr[start : start + window]
        acf = calculate_autocorrelation(list(seg), max_lag=1)
        if not acf:
            continue
        val = float(acf[0])
        if not np.isnan(val) and val > best:
            best = val
    return best


def _compute_stabilization_ratio(
    investor_payloads: Dict[str, Dict[int, dict]],
    prices: np.ndarray,
    fundamentals: np.ndarray,
    threshold_pct: float = 5.0,
) -> float:
    """Compute stabilization ratio: rational volume / biased volume during bias episodes.

    Stabilizing agents: names containing 'systematic', 'value', 'analyst'
    Biased agents: names containing 'recent', 'media', 'overweight', 'influenced'
    """
    if len(prices) == 0 or len(fundamentals) == 0:
        return 0.0
    f_safe = np.where(fundamentals > 0, fundamentals, 1.0)
    deviation_pct = np.abs((prices - fundamentals) / f_safe) * 100.0

    stabilizing_vol = 0.0
    biased_vol = 0.0

    stabilizing_kw = {"systematic", "value", "analyst"}
    biased_kw = {"recent", "media", "overweight", "influenced"}

    for agent_id, round_payloads in investor_payloads.items():
        lower_id = agent_id.lower()
        is_stabilizing = any(kw in lower_id for kw in stabilizing_kw)
        is_biased = any(kw in lower_id for kw in biased_kw)
        if not is_stabilizing and not is_biased:
            continue
        for rnd, payload in round_payloads.items():
            # Only count rounds in bias episode
            idx = rnd - 1
            if 0 <= idx < len(deviation_pct) and deviation_pct[idx] > threshold_pct:
                qty = abs(payload["quantity"])
                if is_stabilizing:
                    stabilizing_vol += qty
                elif is_biased:
                    biased_vol += qty

    if biased_vol == 0:
        return 0.0
    return float(stabilizing_vol / biased_vol)


# ---------------------------------------------------------------------------
# Validation dataclass
# ---------------------------------------------------------------------------


@dataclass
class AvailabilityBiasValidationResult:
    """Structured validation result for an AvailabilityBias simulation run."""

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


def _validate_availability_bias(
    peak_deviation_pct: float,
    bias_persistence: float,
    ac1_bias_episode: float,
    stabilization_ratio: float,
    total_rounds: int,
) -> AvailabilityBiasValidationResult:
    """Validate simulation output against analysis-bases.md §6 calibration targets.

    Scoring (each criterion 0-1, linear interpolation):
        [1] Peak deviation [5%, 15%]    weight 0.30  Baker & Wurgler 2007
        [2] Persistence >= 0.10         weight 0.25  Tetlock 2007
        [3] AC1 [0.20, 0.40]            weight 0.25  De Bondt & Thaler 1985
        [4] Stabilization [0.40, 0.80]  weight 0.20  Baker & Wurgler 2007

    Returns:
        AvailabilityBiasValidationResult with weighted Fit Score.
    """
    # --- [1] Peak deviation target [5%, 15%], weight 0.30 ---
    dev_lo, dev_hi = 5.0, 15.0
    if dev_lo <= peak_deviation_pct <= dev_hi:
        dev_score = 1.0
    elif peak_deviation_pct < dev_lo:
        dev_score = max(0.0, peak_deviation_pct / dev_lo)
    else:
        dev_score = max(0.0, 1.0 - (peak_deviation_pct - dev_hi) / dev_hi)

    # --- [2] Bias persistence >= 0.10, weight 0.25 ---
    pers_target = 0.10
    if bias_persistence >= pers_target:
        pers_score = 1.0
    else:
        pers_score = (
            max(0.0, bias_persistence / pers_target) if pers_target > 0 else 0.0
        )

    # --- [3] AC1 (bias episode) [0.20, 0.40], weight 0.25 ---
    ac_lo, ac_hi = 0.20, 0.40
    if ac_lo <= ac1_bias_episode <= ac_hi:
        ac_score = 1.0
    elif ac1_bias_episode < ac_lo:
        ac_score = max(0.0, ac1_bias_episode / ac_lo) if ac_lo > 0 else 0.0
    else:
        ac_score = max(0.0, 1.0 - (ac1_bias_episode - ac_hi) / ac_hi)

    # --- [4] Stabilization ratio [0.40, 0.80], weight 0.20 ---
    stab_lo, stab_hi = 0.40, 0.80
    if stab_lo <= stabilization_ratio <= stab_hi:
        stab_score = 1.0
    elif stabilization_ratio < stab_lo:
        stab_score = max(0.0, stabilization_ratio / stab_lo) if stab_lo > 0 else 0.0
    else:
        stab_score = max(0.0, 1.0 - (stabilization_ratio - stab_hi) / stab_hi)

    overall_score = (
        dev_score * 0.30 + pers_score * 0.25 + ac_score * 0.25 + stab_score * 0.20
    )
    is_valid = overall_score > 0.50 and peak_deviation_pct >= 3.0

    criteria = {
        "peak_deviation": {
            "observed": round(peak_deviation_pct, 2),
            "target_range": "[5%, 15%]",
            "score": round(dev_score, 3),
            "weight": 0.30,
            "citation": "Baker & Wurgler 2007",
        },
        "bias_persistence": {
            "observed": round(bias_persistence, 4),
            "target_range": ">= 0.10 (10%+ rounds)",
            "score": round(pers_score, 3),
            "weight": 0.25,
            "citation": "Tetlock 2007",
        },
        "ac1_bias_episode": {
            "observed": round(ac1_bias_episode, 4),
            "target_range": "[0.20, 0.40]",
            "score": round(ac_score, 3),
            "weight": 0.25,
            "citation": "De Bondt & Thaler 1985",
        },
        "stabilization_ratio": {
            "observed": round(stabilization_ratio, 4),
            "target_range": "[0.40, 0.80]",
            "score": round(stab_score, 3),
            "weight": 0.20,
            "citation": "Baker & Wurgler 2007; Shleifer & Vishny 1997",
        },
    }

    return AvailabilityBiasValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
    )


# ---------------------------------------------------------------------------
# Interpretation builder
# ---------------------------------------------------------------------------


def _build_interpretation(
    result: AvailabilityBiasValidationResult,
    peak_deviation_pct: float,
    bias_persistence: float,
    ac1_bias_episode: float,
    stabilization_ratio: float,
    total_rounds: int,
) -> str:
    """Build human-readable validation interpretation string."""
    status = "VALID" if result.is_valid else "INVALID"
    lines: List[str] = [
        f"=== AVAILABILITY BIAS SIMULATION VALIDATION: {status} ===",
        f"Overall Fit Score: {result.score:.1%} (threshold: 50%)",
        "",
    ]

    # [1] Peak deviation
    dev = result.criteria["peak_deviation"]
    if peak_deviation_pct >= 5.0:
        dev_assess = (
            "PASS — deviation within calibrated range (Baker & Wurgler 2007: 5–15%)"
        )
    elif peak_deviation_pct >= 3.0:
        dev_assess = "MARGINAL — bias effect present but below target"
    else:
        dev_assess = (
            "FAIL — bias effect too weak; check recency_weight and media_weight"
        )
    lines += [
        "[1] BIAS EPISODE DEPTH (PEAK DEVIATION)",
        f"    Observed: {peak_deviation_pct:.1f}%   Expected: 5–15% (Baker & Wurgler 2007)",
        f"    Score: {dev['score']:.3f}   Assessment: {dev_assess}",
        "",
    ]

    # [2] Persistence
    per = result.criteria["bias_persistence"]
    if bias_persistence >= 0.10:
        per_assess = (
            "PASS — sustained bias episodes detected (Tetlock 2007: ≥ 10% of rounds)"
        )
    else:
        per_assess = "FAIL — bias episodes too transient; increase recency_weight"
    lines += [
        "[2] BIAS PERSISTENCE (SUSTAINED EPISODE FRACTION)",
        f"    Observed: {bias_persistence:.2%}   Expected: >= 10% (Tetlock 2007)",
        f"    Score: {per['score']:.3f}   Assessment: {per_assess}",
        "",
    ]

    # [3] AC1
    ac = result.criteria["ac1_bias_episode"]
    if ac1_bias_episode >= 0.20:
        ac_assess = "PASS — overreaction momentum detected (De Bondt & Thaler 1985)"
    else:
        ac_assess = "FAIL — no momentum pattern; bias not creating persistent trends"
    lines += [
        "[3] OVERREACTION MOMENTUM (AC1 DURING BIAS EPISODE)",
        f"    Observed: {ac1_bias_episode:.4f}   Expected: 0.20–0.40 (De Bondt & Thaler 1985)",
        f"    Score: {ac['score']:.3f}   Assessment: {ac_assess}",
        "",
    ]

    # [4] Stabilization ratio
    stab = result.criteria["stabilization_ratio"]
    if 0.40 <= stabilization_ratio <= 0.80:
        stab_assess = "PASS — partial correction consistent with limits-of-arbitrage"
    elif stabilization_ratio < 0.40:
        stab_assess = "FAIL — stabilizing agents insufficient; increase SystematicAnalyst position"
    else:
        stab_assess = "MARGINAL — rational agents may be over-correcting bias"
    lines += [
        "[4] STABILIZATION RATIO (RATIONAL / BIASED VOLUME)",
        f"    Observed: {stabilization_ratio:.4f}   Expected: 0.40–0.80 (Baker & Wurgler 2007)",
        f"    Score: {stab['score']:.3f}   Assessment: {stab_assess}",
        "",
    ]

    # [SUMMARY]
    lines += [
        "[SUMMARY]",
        f"    Peak Deviation Score:     {result.criteria['peak_deviation']['score']:.3f} × 0.30",
        f"    Bias Persistence Score:   {result.criteria['bias_persistence']['score']:.3f} × 0.25",
        f"    AC1 Score:                {result.criteria['ac1_bias_episode']['score']:.3f} × 0.25",
        f"    Stabilization Score:      {result.criteria['stabilization_ratio']['score']:.3f} × 0.20",
        f"    Fit Score: {result.score:.1%}",
        f"    Status: {'VALID — simulation reproduces availability bias dynamics' if result.is_valid else 'INVALID — calibration targets not met'}",
    ]

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
    result: AvailabilityBiasValidationResult,
    output_dir: str,
) -> List[str]:
    """Generate four analysis plots.

    Plot 00: Investor Bid Curves (headline chart)
    Plot 01: Price vs Fundamental + Deviation % with \u00b15%, \u00b110%, \u00b115% thresholds
    Plot 02: Agent Volume by Type + Stabilization Ratio
    Plot 03: Rolling AC1 + Validation Criteria Summary

    Returns:
        List of output file paths.
    """
    if not market_prices:
        return []

    rounds_sorted = sorted(market_prices.keys())
    prices = np.array([market_prices[r] for r in rounds_sorted])
    rounds = np.array(rounds_sorted)

    if not fundamentals:
        raise ValueError("No fundamental data recorded - simulation data is incomplete")
    fund_arr = np.array([fundamentals[r] for r in rounds_sorted])

    f_safe = np.where(fund_arr > 0, fund_arr, 1.0)
    deviation_pct = (prices - fund_arr) / f_safe * 100.0
    returns = np.diff(prices) / np.where(prices[:-1] > 0, prices[:-1], 1.0) * 100.0

    paths: List[str] = []

    # --- Plot 0: Investor Bid Curves (PRIMARY headline chart) ---
    _fv = float(np.mean(fund_arr))
    fig0, ax0 = plt.subplots(figsize=(16, 8))
    fig0.suptitle(
        "AvailabilityBias Rule \u2014 Investor Bidding Curves",
        fontsize=14,
        fontweight="bold",
    )
    ax0.plot(
        rounds, prices, color="#f0a500", linewidth=2.5, label="Market Price", zorder=10
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
    paths.append(_p0)
    print(f"Saved: {_p0}")

    # --- Plot 01: Price Dynamics ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle("AvailabilityBias — Price Dynamics", fontsize=13, fontweight="bold")

    ax1.plot(rounds, prices, color="steelblue", linewidth=1.8, label="Market Price")
    ax1.plot(
        rounds,
        fund_arr,
        color="darkgreen",
        linestyle="--",
        linewidth=1.2,
        label="Fundamental",
    )
    ax1.set_ylabel("Price")
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    ax2.plot(rounds, deviation_pct, color="crimson", linewidth=1.5)
    ax2.axhline(y=0.0, color="black", linestyle="--", alpha=0.5)
    for thr, color, label in [
        (5.0, "gold", "±5%"),
        (10.0, "orange", "±10%"),
        (15.0, "red", "±15%"),
    ]:
        ax2.axhline(
            y=thr, color=color, linestyle=":", alpha=0.7, linewidth=1, label=label
        )
        ax2.axhline(y=-thr, color=color, linestyle=":", alpha=0.7, linewidth=1)
    ax2.set_ylabel("Deviation from Fundamental (%)")
    ax2.set_xlabel("Round")
    ax2.legend(fontsize=8, ncol=3)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    p01 = os.path.join(output_dir, "01_availability_bias_dynamics.png")
    plt.savefig(p01, dpi=150, bbox_inches="tight")
    plt.close()
    paths.append(p01)

    # --- Plot 02: Bias Dynamics (Agent Volume + Stabilization) ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("AvailabilityBias — Bias Dynamics", fontsize=13, fontweight="bold")

    if investor_payloads:
        agent_ids = sorted(investor_payloads.keys())
        buy_vols = []
        sell_vols = []
        for aid in agent_ids:
            b = sum(
                p["quantity"]
                for p in investor_payloads[aid].values()
                if p["quantity"] > 0
            )
            s = sum(
                abs(p["quantity"])
                for p in investor_payloads[aid].values()
                if p["quantity"] < 0
            )
            buy_vols.append(b)
            sell_vols.append(s)
        x_pos = np.arange(len(agent_ids))
        ax1.bar(x_pos - 0.2, buy_vols, 0.4, label="Buy", color="steelblue", alpha=0.8)
        ax1.bar(x_pos + 0.2, sell_vols, 0.4, label="Sell", color="firebrick", alpha=0.8)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(agent_ids, rotation=30, ha="right", fontsize=7)
        ax1.set_title("Agent Volume by Type")
        ax1.set_ylabel("Total Quantity")
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
    else:
        ax1.text(
            0.5, 0.5, "No agent data", ha="center", va="center", transform=ax1.transAxes
        )

    # Rolling AC1
    if len(returns) >= 5:
        window = min(10, len(returns))
        rolling_ac1 = []
        for i in range(len(returns)):
            seg_start = max(0, i - window + 1)
            seg = returns[seg_start : i + 1]
            if len(seg) > 2:
                ac = np.corrcoef(seg[:-1], seg[1:])[0, 1]
                rolling_ac1.append(ac if not np.isnan(ac) else 0.0)
            else:
                rolling_ac1.append(0.0)
        ret_rounds = rounds[1:]
        ax2.plot(
            ret_rounds,
            rolling_ac1,
            color="purple",
            linewidth=1.5,
            label=f"Rolling AC1 ({window}-round)",
        )
        ax2.axhline(y=0.0, color="black", linestyle="--", alpha=0.5)
        ax2.axhline(
            y=0.20,
            color="green",
            linestyle=":",
            alpha=0.8,
            linewidth=1.2,
            label="+0.20 target",
        )
        ax2.axhline(
            y=-0.10,
            color="red",
            linestyle=":",
            alpha=0.7,
            linewidth=1.0,
            label="−0.10 reversal",
        )
        ax2.set_title("Rolling Return Autocorrelation")
        ax2.set_xlabel("Round")
        ax2.set_ylabel("AC1")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    p02 = os.path.join(output_dir, "02_availability_bias_analysis.png")
    plt.savefig(p02, dpi=150, bbox_inches="tight")
    plt.close()
    paths.append(p02)

    # --- Plot 03: Summary ---
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("AvailabilityBias — Summary", fontsize=13, fontweight="bold")

    # Sub-plot A: Validation scores
    crit_names = [
        "Peak Dev\n[5%,15%]",
        "Persistence\n≥10%",
        "AC1 Bias\n[0.20,0.40]",
        "Stabilization\n[0.40,0.80]",
    ]
    crit_scores = [
        result.criteria["peak_deviation"]["score"],
        result.criteria["bias_persistence"]["score"],
        result.criteria["ac1_bias_episode"]["score"],
        result.criteria["stabilization_ratio"]["score"],
    ]
    crit_colors = [
        "green" if s >= 0.7 else "orange" if s >= 0.4 else "red" for s in crit_scores
    ]
    axes[0].bar(range(len(crit_names)), crit_scores, color=crit_colors, alpha=0.8)
    axes[0].axhline(
        y=0.7, color="black", linestyle="--", linewidth=1.2, label="Pass (0.7)"
    )
    axes[0].set_xticks(range(len(crit_names)))
    axes[0].set_xticklabels(crit_names, fontsize=8)
    axes[0].set_ylim(0, 1.1)
    axes[0].set_title(f"Validation Criteria\n(Fit Score: {result.score:.1%})")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    # Sub-plot B: Return distribution (fat tails from bias)
    if len(returns) > 5:
        axes[1].hist(returns, bins=30, color="steelblue", alpha=0.7, edgecolor="white")
        axes[1].axvline(x=0, color="black", linestyle="--", alpha=0.5)
        axes[1].set_title("Return Distribution (Bias-Driven Tails)")
        axes[1].set_xlabel("Return (%)")
        axes[1].set_ylabel("Frequency")
        axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    p03 = os.path.join(output_dir, "03_summary.png")
    plt.savefig(p03, dpi=150, bbox_inches="tight")
    plt.close()
    paths.append(p03)

    return paths


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def analyze_availability_bias(
    data: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Orchestrate full AvailabilityBias analysis pipeline.

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
    fundamentals_map = data["fundamentals"]
    investor_payloads = data["investor_payloads"]

    if not market_prices:
        print("No simulation data found. Run simulation first.")
        return {}

    rounds_sorted = sorted(market_prices.keys())
    prices = np.array([market_prices[r] for r in rounds_sorted])
    if not fundamentals_map:
        raise ValueError("No fundamental data recorded - simulation data is incomplete")
    fund_arr = np.array([fundamentals_map[r] for r in rounds_sorted])

    total_rounds = len(rounds_sorted)

    peak_deviation_pct = _compute_peak_deviation(prices, fund_arr)
    bias_persistence = _compute_bias_persistence(prices, fund_arr)

    returns = np.diff(prices) / np.where(prices[:-1] > 0, prices[:-1], 1.0)
    ac1_bias = _compute_rolling_ac1(returns, window=10)

    stab_ratio = _compute_stabilization_ratio(investor_payloads, prices, fund_arr)

    result = _validate_availability_bias(
        peak_deviation_pct=peak_deviation_pct,
        bias_persistence=bias_persistence,
        ac1_bias_episode=ac1_bias,
        stabilization_ratio=stab_ratio,
        total_rounds=total_rounds,
    )

    interpretation = _build_interpretation(
        result=result,
        peak_deviation_pct=peak_deviation_pct,
        bias_persistence=bias_persistence,
        ac1_bias_episode=ac1_bias,
        stabilization_ratio=stab_ratio,
        total_rounds=total_rounds,
    )
    result.interpretation = interpretation
    print(interpretation)

    _create_visualizations(
        market_prices=market_prices,
        fundamentals=fundamentals_map,
        investor_bids=data["investor_bids"],
        investor_payloads=investor_payloads,
        result=result,
        output_dir=output_dir,
    )

    summary = {"validation": result.to_dict()}
    summary["metrics"] = {
        "peak_deviation_pct": round(peak_deviation_pct, 3),
        "bias_persistence": round(bias_persistence, 4),
        "ac1_bias_episode": round(ac1_bias, 4),
        "stabilization_ratio": round(stab_ratio, 4),
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
    """Run AvailabilityBias Rule analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Analyze AvailabilityBias Rule simulation results"
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
    summary = analyze_availability_bias(data, config, output_dir)
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
        scenario='AvailabilityBias',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "_validate_availability_bias",
    "_build_interpretation",
    "analyze_availability_bias",
]

if __name__ == "__main__":
    main()
