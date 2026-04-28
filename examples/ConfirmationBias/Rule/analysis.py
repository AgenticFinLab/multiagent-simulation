#!/usr/bin/env python
"""ConfirmationBias Rule-Based Simulation Analysis

Analyzes simulation results for confirmation-bias-driven price distortion.
Based on analysis-bases.md §6 calibration targets
(Nickerson 1998; Lord et al. 1979; Rabin & Schrag 1999; Hong & Stein 1999).

Usage:
    python examples/ConfirmationBias/Rule/analysis.py \
        -c configs/ConfirmationBias/Rule/simulation.yml
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results

__all__ = [
    "_batch_to_rounds",
    "_load_data",
    "_validate_confirmation_bias",
    "_build_interpretation",
    "analyze_confirmation_bias",
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _batch_to_rounds(values: list) -> Dict[int, float]:
    """Convert batch store list to {round_num: value}, round_num is 1-based."""
    return {i + 1: v for i, v in enumerate(values)}


def _load_data(results) -> Dict[str, Any]:
    """Load price/fundamental batch stores and investor turn payloads."""
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
# Metrics
# ---------------------------------------------------------------------------


def _compute_bias_amplitude(prices_list: List[float], fundamental: float) -> float:
    """Peak absolute deviation from fundamental (%)."""
    if not prices_list or fundamental <= 0:
        return 0.0
    deviations = [(p - fundamental) / fundamental * 100 for p in prices_list]
    return float(max(abs(d) for d in deviations))


def _compute_bias_persistence(
    prices_list: List[float], fundamental: float, threshold: float = 0.02
) -> int:
    """Number of rounds where |deviation| > threshold."""
    if not prices_list or fundamental <= 0:
        return 0
    count = 0
    for p in prices_list:
        if abs((p - fundamental) / fundamental) > threshold:
            count += 1
    return count


def _compute_correction_ratio(prices_list: List[float], fundamental: float) -> float:
    """Fraction of rounds where price moved toward fundamental vs. away."""
    if len(prices_list) < 2 or fundamental <= 0:
        return 0.0
    toward = 0
    total = 0
    for i in range(1, len(prices_list)):
        prev_dev = abs(prices_list[i - 1] - fundamental)
        curr_dev = abs(prices_list[i] - fundamental)
        total += 1
        if curr_dev < prev_dev:
            toward += 1
    return float(toward / total) if total > 0 else 0.0


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
            qty = float(payload.get("quantity", 0))
            price = market_prices.get(rnd, 0.0)
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
class ConfirmationBiasValidationResult:
    """Result of ConfirmationBias simulation validation."""

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


def _validate_confirmation_bias(
    bias_amplitude_pct: float,
    bias_persistence: int,
    correction_ratio: float,
    autocorr_lag1: float,
    total_rounds: int,
) -> ConfirmationBiasValidationResult:
    """Validate ConfirmationBias results against analysis-bases.md §6.

    Criteria
    --------
    1. Bias amplitude   target [2%, 8%]    weight 0.25  (Nickerson 1998; Rabin & Schrag 1999)
    2. Bias persistence target [30, 70]    weight 0.25  (Rabin & Schrag 1999 high-q regime)
    3. Correction ratio target [0.2, 0.5]  weight 0.25  (Hong & Stein 1999; Fama 1970)
    4. AC1              target [0.05, 0.20] weight 0.25 (Jegadeesh & Titman 1993)
    """
    criteria = {}

    # --- Criterion 1: Bias amplitude in [2%, 8%] ---
    if 2.0 <= bias_amplitude_pct <= 8.0:
        amp_score = 1.0
    elif 1.0 <= bias_amplitude_pct < 2.0:
        amp_score = 0.4 + (bias_amplitude_pct - 1.0) / 1.0 * 0.6
    elif 8.0 < bias_amplitude_pct <= 12.0:
        amp_score = 1.0 - (bias_amplitude_pct - 8.0) / 4.0 * 0.5
    elif bias_amplitude_pct > 12.0:
        amp_score = 0.1
    else:
        amp_score = bias_amplitude_pct / 2.0 * 0.4

    criteria["bias_amplitude"] = {
        "value": round(bias_amplitude_pct, 3),
        "target": "2–8%",
        "score": round(amp_score, 3),
        "passed": 1.0 <= bias_amplitude_pct <= 12.0,
    }

    # --- Criterion 2: Bias persistence in [30, 70] (out of 100) ---
    persistence_frac = bias_persistence / total_rounds if total_rounds > 0 else 0
    target_lo = int(total_rounds * 0.30)
    target_hi = int(total_rounds * 0.70)
    if target_lo <= bias_persistence <= target_hi:
        pers_score = 1.0
    elif bias_persistence < target_lo:
        pers_score = max(0.1, bias_persistence / target_lo) if target_lo > 0 else 0.1
    else:
        over = bias_persistence - target_hi
        pers_score = (
            max(0.2, 1.0 - over / (total_rounds - target_hi) * 0.6)
            if total_rounds > target_hi
            else 0.2
        )

    criteria["bias_persistence"] = {
        "value": bias_persistence,
        "target": f"{target_lo}–{target_hi} rounds (30–70% of {total_rounds})",
        "score": round(pers_score, 3),
        "passed": bias_persistence >= int(total_rounds * 0.15),
    }

    # --- Criterion 3: Correction ratio in [0.2, 0.5] ---
    if 0.2 <= correction_ratio <= 0.5:
        cr_score = 1.0
    elif 0.1 <= correction_ratio < 0.2:
        cr_score = 0.4 + (correction_ratio - 0.1) / 0.1 * 0.6
    elif 0.5 < correction_ratio <= 0.7:
        cr_score = 1.0 - (correction_ratio - 0.5) / 0.2 * 0.4
    elif correction_ratio > 0.7:
        cr_score = 0.2
    else:
        cr_score = correction_ratio / 0.2 * 0.4

    criteria["correction_ratio"] = {
        "value": round(correction_ratio, 4),
        "target": "0.2–0.5",
        "score": round(cr_score, 3),
        "passed": 0.1 <= correction_ratio <= 0.7,
    }

    # --- Criterion 4: AC1 in [0.05, 0.20] ---
    if 0.05 <= autocorr_lag1 <= 0.20:
        ac_score = 1.0
    elif 0.0 <= autocorr_lag1 < 0.05:
        ac_score = 0.4 + autocorr_lag1 / 0.05 * 0.6
    elif 0.20 < autocorr_lag1 <= 0.35:
        ac_score = 1.0 - (autocorr_lag1 - 0.20) / 0.15 * 0.4
    elif autocorr_lag1 < 0.0:
        ac_score = max(0.0, 0.2 + autocorr_lag1 * 2.0)
    else:
        ac_score = 0.2

    criteria["autocorrelation"] = {
        "value": round(autocorr_lag1, 4),
        "target": "0.05–0.20",
        "score": round(ac_score, 3),
        "passed": -0.05 <= autocorr_lag1 <= 0.35,
    }

    overall_score = (
        amp_score * 0.25 + pers_score * 0.25 + cr_score * 0.25 + ac_score * 0.25
    )
    is_valid = overall_score > 0.50 and bias_amplitude_pct >= 1.0

    interpretation = _build_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        bias_amplitude_pct=bias_amplitude_pct,
        bias_persistence=bias_persistence,
        correction_ratio=correction_ratio,
        autocorr_lag1=autocorr_lag1,
        total_rounds=total_rounds,
        amp_score=amp_score,
        pers_score=pers_score,
        cr_score=cr_score,
        ac_score=ac_score,
    )

    return ConfirmationBiasValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def _build_interpretation(
    is_valid: bool,
    overall_score: float,
    bias_amplitude_pct: float,
    bias_persistence: int,
    correction_ratio: float,
    autocorr_lag1: float,
    total_rounds: int,
    amp_score: float,
    pers_score: float,
    cr_score: float,
    ac_score: float,
) -> str:
    """Build structured validation report following analysis-bases.md §6."""
    verdict = "VALID" if is_valid else "INVALID"
    lines = []
    lines.append(f"=== CONFIRMATION BIAS SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Criterion 1
    if bias_amplitude_pct >= 2.0:
        amp_assess = (
            "PASS — Bias amplitude consistent with confirmation bias literature."
        )
    elif bias_amplitude_pct >= 1.0:
        amp_assess = (
            "WEAK — Bias present but below calibration; increase confirmation_strength."
        )
    else:
        amp_assess = "FAIL — Bias too small; belief not compounding."
    lines.append("[1] BIAS AMPLITUDE (PEAK DEVIATION)")
    lines.append(f"    Observed: Peak bias amplitude = {bias_amplitude_pct:.2f}%")
    lines.append(
        "    Expected: 2–8% (Nickerson 1998; Lord et al. 1979; Rabin & Schrag 1999)"
    )
    lines.append(f"    Score: {amp_score:.1%}")
    lines.append(f"    Assessment: {amp_assess}")
    lines.append("")

    # Criterion 2
    if bias_persistence >= int(total_rounds * 0.30):
        pers_assess = "PASS — Bias persists across sufficient rounds."
    elif bias_persistence >= int(total_rounds * 0.15):
        pers_assess = "WEAK — Moderate persistence; noise may dominate."
    else:
        pers_assess = (
            "FAIL — Bias too transient; check confirmation_strength and noise."
        )
    lines.append("[2] BIAS PERSISTENCE (ROUNDS ABOVE THRESHOLD)")
    lines.append(
        f"    Observed: Bias persistent for {bias_persistence} of {total_rounds} rounds"
    )
    lines.append(
        f"    Expected: {int(total_rounds * 0.30)}–{int(total_rounds * 0.70)} rounds "
        f"(Rabin & Schrag 1999 high-q persistence regime)"
    )
    lines.append(f"    Score: {pers_score:.1%}")
    lines.append(f"    Assessment: {pers_assess}")
    lines.append("")

    # Criterion 3
    if 0.2 <= correction_ratio <= 0.5:
        cr_assess = "PASS — Stabilizers partially correct bias without eliminating it."
    elif correction_ratio < 0.2:
        cr_assess = "WEAK — Stabilizers too weak; bias dominates unchecked."
    else:
        cr_assess = "WEAK — Stabilizers too effective; bias corrected too quickly."
    lines.append("[3] CORRECTION DYNAMICS (CORRECTION RATIO)")
    lines.append(f"    Observed: Correction ratio = {correction_ratio:.3f}")
    lines.append("    Expected: 0.2–0.5 (Hong & Stein 1999; Fama 1970)")
    lines.append(f"    Score: {cr_score:.1%}")
    lines.append(f"    Assessment: {cr_assess}")
    lines.append("")

    # Criterion 4
    if autocorr_lag1 >= 0.05:
        ac_assess = (
            "PASS — Positive momentum confirms belief-compounding-driven persistence."
        )
    elif autocorr_lag1 >= 0.0:
        ac_assess = "WEAK — Near-zero momentum; bias may not compound reliably."
    else:
        ac_assess = "FAIL — Negative autocorrelation; mean-reversion dominates."
    lines.append("[4] MOMENTUM SIGNATURE (RETURN AUTOCORRELATION AC1)")
    lines.append(f"    Observed: Lag-1 autocorrelation = {autocorr_lag1:.3f}")
    lines.append("    Expected: 0.05–0.20 (Jegadeesh & Titman 1993)")
    lines.append(f"    Score: {ac_score:.1%}")
    lines.append(f"    Assessment: {ac_assess}")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            f"The simulation successfully reproduces confirmation bias dynamics: "
            f"peak amplitude {bias_amplitude_pct:.1f}%, persistent for {bias_persistence} rounds, "
            f"correction ratio {correction_ratio:.2f}, AC1 {autocorr_lag1:.2f}. "
            f"Fit Score: {overall_score:.1%}."
        )
    else:
        lines.append(
            f"The simulation does not fully reproduce confirmation bias dynamics. "
            f"Overall Fit Score {overall_score:.1%} is below the 50% threshold. "
            f"Key issues: "
            + ("amplitude too low; " if bias_amplitude_pct < 2.0 else "")
            + (
                "persistence too low; "
                if bias_persistence < int(total_rounds * 0.15)
                else ""
            )
            + ("correction too strong; " if correction_ratio > 0.7 else "")
            + ("no momentum; " if autocorr_lag1 < 0.0 else "")
            + "Review analysis-bases.md §6 for parameter adjustments."
        )
    lines.append(f"Fit Score: {overall_score:.1%}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------------


def _create_visualizations(
    market_prices: Dict[int, float],
    fundamentals: Dict[int, float],
    investor_payloads: Dict[str, Dict[int, dict]],
    rolling_vols: List[float],
    output_dir: str,
) -> None:
    """Create 3 analysis plots per analysis-bases.md §7."""
    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    fund_list = [fundamentals.get(r, 100.0) for r in rounds_sorted]
    rounds_arr = np.array(rounds_sorted)
    prices_arr = np.array(prices_list)
    fund_arr = np.array(fund_list)
    deviation = (prices_arr - fund_arr) / fund_arr * 100

    # ---- Plot 01: Price Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("ConfirmationBias — Price Dynamics", fontsize=13, fontweight="bold")

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
    axes[0].set_xlabel("Round")
    axes[0].set_ylabel("Price")
    axes[0].set_title("Price vs. Fundamental")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(rounds_arr, deviation, color="purple", linewidth=1.2)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    for th in [-2, 2, -5, 5, -8, 8]:
        axes[1].axhline(y=th, color="gray", linestyle=":", alpha=0.3)
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].set_title("Bias Deviation from Fundamental")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "01_price_dynamics.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 02: Bias Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "ConfirmationBias — Bias Intensity Dynamics", fontsize=13, fontweight="bold"
    )

    if rolling_vols:
        vol_rounds = rounds_arr[1:] if len(rounds_arr) > 1 else rounds_arr
        if len(vol_rounds) == len(rolling_vols):
            axes[0].plot(vol_rounds, rolling_vols, color="darkorange", linewidth=1.2)
        else:
            axes[0].plot(rolling_vols, color="darkorange", linewidth=1.2)
        axes[0].set_xlabel("Round")
        axes[0].set_ylabel("Rolling Volatility (%)")
        axes[0].set_title("10-Round Rolling Volatility")
        axes[0].grid(True, alpha=0.3)

    # Cumulative deviation (bias accumulation)
    cum_dev = np.cumsum(deviation)
    axes[1].plot(rounds_arr, cum_dev, color="teal", linewidth=1.2)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Cumulative Deviation (%)")
    axes[1].set_title("Cumulative Bias Accumulation")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "02_bias_dynamics.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 03: Agent Summary ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "ConfirmationBias — Agent Activity Summary", fontsize=13, fontweight="bold"
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


def analyze_confirmation_bias(
    data: Dict[str, Any],
    config: dict,
    output_dir: str,
) -> Dict[str, Any]:
    """Run full ConfirmationBias analysis pipeline."""
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    investor_payloads = data["investor_payloads"]

    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    fund_value = float(np.mean(list(fundamentals.values()))) if fundamentals else 100.0
    total_rounds = len(rounds_sorted)

    # Metrics
    bias_amplitude_pct = _compute_bias_amplitude(prices_list, fund_value)
    bias_persistence = _compute_bias_persistence(
        prices_list, fund_value, threshold=0.02
    )
    correction_ratio = _compute_correction_ratio(prices_list, fund_value)
    rolling_vols = _compute_rolling_volatility(prices_list)
    autocorr = _compute_autocorrelation(prices_list)
    vwap_data = _compute_agent_vwap(investor_payloads, market_prices)

    # Validation
    validation = _validate_confirmation_bias(
        bias_amplitude_pct=bias_amplitude_pct,
        bias_persistence=bias_persistence,
        correction_ratio=correction_ratio,
        autocorr_lag1=autocorr,
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
        "scenario": "ConfirmationBias",
        "variant": "Rule",
        "total_rounds": total_rounds,
        "fundamental_value": round(fund_value, 4),
        "metrics": {
            "bias_amplitude_pct": round(bias_amplitude_pct, 4),
            "bias_persistence": bias_persistence,
            "correction_ratio": round(correction_ratio, 4),
            "return_autocorr_lag1": round(autocorr, 4),
        },
        "price": {
            "initial": round(prices_list[0], 4) if prices_list else None,
            "final": round(prices_list[-1], 4) if prices_list else None,
            "min": round(min(prices_list), 4) if prices_list else None,
            "max": round(max(prices_list), 4) if prices_list else None,
        },
        "agent_vwap": {
            k: {sk: round(sv, 4) for sk, sv in v.items()} for k, v in vwap_data.items()
        },
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 50)
    print("CONFIRMATION BIAS ANALYSIS")
    print("=" * 50)
    print(f"Bias amplitude: {bias_amplitude_pct:.2f}%  (target: 2–8%)")
    print(
        f"Bias persistence: {bias_persistence} rounds  (target: 30–70% of {total_rounds})"
    )
    print(f"Correction ratio: {correction_ratio:.3f}  (target: 0.2–0.5)")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}  (target: 0.05–0.20)")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run ConfirmationBias Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze ConfirmationBias simulation")
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
    summary = analyze_confirmation_bias(data, config, output_dir)
    return summary


if __name__ == "__main__":
    main()
