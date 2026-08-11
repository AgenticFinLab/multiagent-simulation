#!/usr/bin/env python
"""CurrencyCrisis Rule-Based Simulation Analysis

Analyzes self-fulfilling speculative currency attack dynamics including
attack intensity, peg defense, and expectation coordination channels.
Based on analysis-bases.md calibration targets (Obstfeld 1996 / Krugman 1979).

Usage:
    python examples/CurrencyCrisis/Rule/analysis.py \
        -c configs/CurrencyCrisis/Rule/simulation.yml
"""

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.data_loader import batch_to_rounds, load_data
from masim.evaluation.finance import (
    calculate_autocorrelation,
    calculate_max_drawdown,
)
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary

# ---------------------------------------------------------------------------
# Data loading (thin adapters over ``masim.evaluation``)
# ---------------------------------------------------------------------------



def _load_data(results) -> Dict[str, Any]:
    """Legacy alias. Delegates to ``masim.evaluation.data_loader.load_data``."""
    return load_data(results)


# ---------------------------------------------------------------------------
# Metrics  (analysis-bases.md §2)
# ---------------------------------------------------------------------------


def _compute_attack_intensity_index(
    prices_list: List[float], fundamental: float
) -> float:
    """AII — max negative deviation from peg (absolute fraction). analysis-bases.md §2.1."""
    if not prices_list or fundamental <= 0:
        return 0.0
    deviations = [(p - fundamental) / fundamental for p in prices_list]
    return float(abs(min(deviations)))


def _compute_peg_survival_duration(
    prices_list: List[float], fundamental: float, breach_threshold: float = -0.05
) -> int:
    """PSD — rounds until peg breach at δ < breach_threshold. analysis-bases.md §2.2."""
    if not prices_list or fundamental <= 0:
        return len(prices_list)
    for t, p in enumerate(prices_list):
        if (p - fundamental) / fundamental < breach_threshold:
            return t
    return len(prices_list)


def _compute_defense_exhaustion_rate(
    investor_payloads: Dict[str, Dict[int, dict]],
    prices_list: List[float],
    fundamental: float,
    crisis_threshold: float = -0.05,
) -> float:
    """DER — fraction of initial cash consumed per crisis round. analysis-bases.md §2.3."""
    if not prices_list or fundamental <= 0:
        return 0.0
    deviations = [(p - fundamental) / fundamental for p in prices_list]
    crisis_rounds = {i + 1 for i, d in enumerate(deviations) if d < crisis_threshold}
    if not crisis_rounds:
        return 0.0

    defender_types = {"CentralBankDefender", "RagLLMCentralBankDefender"}
    total_spent = 0.0
    initial_cash = 0.0

    for aid, rp in investor_payloads.items():
        if not any(t in aid for t in defender_types):
            continue
        # Estimate initial cash from first round's portfolio
        sorted_rounds = sorted(rp.keys())
        if not sorted_rounds:
            continue
        first_payload = rp[sorted_rounds[0]]
        cash_val = float(first_payload["cash"])
        qty_val = float(first_payload["quantity"])
        if cash_val > 0:
            initial_cash += cash_val
        for rnd, payload in rp.items():
            if rnd not in crisis_rounds:
                continue
            action = payload["action"]
            qty = float(payload["quantity"])
            price = prices_list[rnd - 1]
            if action == "buy":
                total_spent += qty * price

    if initial_cash < 1e-6 or len(crisis_rounds) == 0:
        return 0.0
    return float(total_spent / (initial_cash * len(crisis_rounds)))


def _compute_self_fulfilling_amplification_factor(
    investor_payloads: Dict[str, Dict[int, dict]],
    prices_list: List[float],
    fundamental: float,
    attack_threshold: float = -0.03,
) -> float:
    """SFAF — SelfFulfillingTrader sell / SpeculativeAttacker sell during attack.

    analysis-bases.md §2.4 — Obstfeld (1996).
    """
    if not prices_list or fundamental <= 0:
        return 0.0
    deviations = [(p - fundamental) / fundamental for p in prices_list]
    attack_rounds = {i + 1 for i, d in enumerate(deviations) if d < attack_threshold}
    if not attack_rounds:
        return 0.0

    attacker_sell = 0.0
    sft_sell = 0.0
    attacker_types = {"SpeculativeAttacker", "RagLLMSpeculativeAttacker"}
    sft_types = {"SelfFulfillingTrader", "RagLLMSelfFulfillingTrader"}

    for aid, rp in investor_payloads.items():
        for rnd, payload in rp.items():
            if rnd not in attack_rounds:
                continue
            action = payload["action"]
            qty = float(payload["quantity"])
            if action == "sell":
                if any(t in aid for t in attacker_types):
                    attacker_sell += qty
                if any(t in aid for t in sft_types):
                    sft_sell += qty

    if attacker_sell < 1e-6:
        return 0.0
    return float(sft_sell / attacker_sell)


def _compute_fundamental_anchor_strength(
    investor_payloads: Dict[str, Dict[int, dict]],
    prices_list: List[float],
    fundamental: float,
    attack_threshold: float = -0.03,
) -> float:
    """FAS — fraction of attack rounds where FundamentalHedger buys. analysis-bases.md §2.5."""
    if not prices_list or fundamental <= 0:
        return 0.0
    deviations = [(p - fundamental) / fundamental for p in prices_list]
    attack_rounds = sorted(
        i + 1 for i, d in enumerate(deviations) if d < attack_threshold
    )
    if not attack_rounds:
        return 0.0

    hedger_types = {"FundamentalHedger", "RagLLMFundamentalHedger"}
    active_rounds = 0

    for aid, rp in investor_payloads.items():
        if not any(t in aid for t in hedger_types):
            continue
        for rnd in attack_rounds:
            if rnd in rp:
                payload = rp[rnd]
                if payload["action"] == "buy":
                    active_rounds += 1

    # Normalize by number of hedger agents * attack rounds
    hedger_count = sum(
        1 for aid in investor_payloads if any(t in aid for t in hedger_types)
    )
    total_possible = hedger_count * len(attack_rounds) if hedger_count > 0 else 1
    return float(active_rounds / total_possible)


def _compute_recovery_speed(
    prices_list: List[float], fundamental: float, recovery_threshold: float = 0.03
) -> int:
    """RS — rounds from trough back to within ±threshold of peg. analysis-bases.md §2.6."""
    if not prices_list or fundamental <= 0:
        return len(prices_list)
    trough_idx = prices_list.index(min(prices_list))
    for t in range(trough_idx, len(prices_list)):
        if abs((prices_list[t] - fundamental) / fundamental) < recovery_threshold:
            return t - trough_idx
    return len(prices_list) - trough_idx


def _compute_max_drawdown(prices_list: List[float]) -> float:
    """Maximum peak-to-trough drawdown (%, positive value).

    Thin adapter over ``masim.evaluation.finance.calculate_max_drawdown`` —
    ``abs()`` restores the historical positive-magnitude convention.
    """
    if len(prices_list) < 2:
        return 0.0
    return float(abs(calculate_max_drawdown(list(prices_list))[0]))


def _compute_peak_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> float:
    """Peak rolling volatility of returns (std dev per window, %)."""
    vols = _compute_rolling_volatility(prices_list, window=window)
    return max(vols) if vols else 0.0


def _compute_rolling_volatility(
    prices_list: List[float], window: int = 10
) -> List[float]:
    """Rolling volatility of returns (percent).

    Kept local because ``masim.evaluation.finance.calculate_rolling_volatility``
    operates on prices (not returns) and does not multiply by 100.
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

    Thin adapter over ``masim.evaluation.finance.calculate_autocorrelation``.
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
        pv_sum = 0.0
        total_vol = 0.0
        total_buy = 0.0
        total_sell = 0.0
        for rnd, payload in round_payloads.items():
            qty = float(payload["quantity"])
            price = market_prices[rnd]
            abs_qty = abs(qty)
            pv_sum += abs_qty * price
            total_vol += abs_qty
            action = payload["action"]
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
class CurrencyCrisisValidationResult:
    """Result of CurrencyCrisis simulation validation."""

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


def _validate_currency_crisis(
    aii: float,
    psd: int,
    sfaf: float,
    fas: float,
    total_rounds: int,
) -> CurrencyCrisisValidationResult:
    """Validate CurrencyCrisis results against analysis-bases.md §6 calibration targets.

    Criteria
    --------
    1. AII   target [0.10, 0.25]   weight 0.30  (Eichengreen et al. 1995)
    2. PSD   target [15, 30]       weight 0.25  (Obstfeld 1996)
    3. SFAF  target [0.5, 1.5]     weight 0.25  (Obstfeld 1996 self-fulfilling)
    4. FAS   target [0.5, 0.8]     weight 0.20  (Morris & Shin 1998)
    """
    criteria = {}

    # --- Criterion 1: AII in [0.10, 0.25] ---
    if 0.10 <= aii <= 0.25:
        aii_score = 1.0
    elif 0.05 <= aii < 0.10:
        aii_score = 0.4 + (aii - 0.05) / 0.05 * 0.6
    elif 0.25 < aii <= 0.40:
        aii_score = 1.0 - (aii - 0.25) / 0.15 * 0.5
    elif aii > 0.40:
        aii_score = 0.1
    else:
        aii_score = aii / 0.10 * 0.4

    criteria["aii"] = {
        "value": round(aii, 4),
        "target": "0.10–0.25",
        "score": round(aii_score, 3),
        "passed": 0.05 <= aii <= 0.40,
    }

    # --- Criterion 2: PSD in [15, 30] rounds ---
    if 15 <= psd <= 30:
        psd_score = 1.0
    elif 8 <= psd < 15:
        psd_score = 0.4 + (psd - 8) / 7.0 * 0.6
    elif 30 < psd <= 50:
        psd_score = 1.0 - (psd - 30) / 20.0 * 0.5
    elif psd > 50:
        psd_score = 0.2
    else:
        psd_score = psd / 15.0 * 0.4

    criteria["psd"] = {
        "value": psd,
        "target": "15–30 rounds",
        "score": round(psd_score, 3),
        "passed": 8 <= psd <= 50,
    }

    # --- Criterion 3: SFAF in [0.5, 1.5] ---
    if 0.5 <= sfaf <= 1.5:
        sfaf_score = 1.0
    elif 0.2 <= sfaf < 0.5:
        sfaf_score = 0.4 + (sfaf - 0.2) / 0.3 * 0.6
    elif 1.5 < sfaf <= 2.5:
        sfaf_score = 1.0 - (sfaf - 1.5) / 1.0 * 0.5
    elif sfaf > 2.5:
        sfaf_score = 0.1
    else:
        sfaf_score = sfaf / 0.5 * 0.4

    criteria["sfaf"] = {
        "value": round(sfaf, 4),
        "target": "0.5–1.5",
        "score": round(sfaf_score, 3),
        "passed": 0.2 <= sfaf <= 2.5,
    }

    # --- Criterion 4: FAS in [0.5, 0.8] ---
    if 0.5 <= fas <= 0.8:
        fas_score = 1.0
    elif 0.3 <= fas < 0.5:
        fas_score = 0.4 + (fas - 0.3) / 0.2 * 0.6
    elif 0.8 < fas <= 1.0:
        fas_score = 1.0 - (fas - 0.8) / 0.2 * 0.3
    elif fas < 0.1:
        fas_score = 0.1
    else:
        fas_score = fas / 0.5 * 0.4

    criteria["fas"] = {
        "value": round(fas, 4),
        "target": "0.5–0.8",
        "score": round(fas_score, 3),
        "passed": 0.3 <= fas <= 1.0,
    }

    overall_score = (
        aii_score * 0.30 + psd_score * 0.25 + sfaf_score * 0.25 + fas_score * 0.20
    )
    is_valid = overall_score > 0.50 and aii >= 0.03

    interpretation = _build_interpretation(
        is_valid=is_valid,
        overall_score=overall_score,
        aii=aii,
        psd=psd,
        sfaf=sfaf,
        fas=fas,
        total_rounds=total_rounds,
        aii_score=aii_score,
        psd_score=psd_score,
        sfaf_score=sfaf_score,
        fas_score=fas_score,
    )

    return CurrencyCrisisValidationResult(
        is_valid=is_valid,
        score=overall_score,
        criteria=criteria,
        interpretation=interpretation,
    )


def _build_interpretation(
    is_valid: bool,
    overall_score: float,
    aii: float,
    psd: int,
    sfaf: float,
    fas: float,
    total_rounds: int,
    aii_score: float,
    psd_score: float,
    sfaf_score: float,
    fas_score: float,
) -> str:
    """Build structured validation report following analysis-bases.md §6."""
    verdict = "VALID" if is_valid else "INVALID"
    lines = []
    lines.append(f"=== CURRENCY CRISIS SIMULATION VALIDATION: {verdict} ===")
    lines.append(f"Overall Fit Score: {overall_score:.1%} (threshold: 50%)")
    lines.append("")

    # Criterion 1: AII
    if aii >= 0.12:
        aii_assess = "PASS — Attack depth consistent with Eichengreen et al. (1995) EMP severity."
    elif aii >= 0.05:
        aii_assess = (
            "WEAK — Attack present but mild; increase SpeculativeAttacker order_size."
        )
    else:
        aii_assess = "FAIL — No significant attack; speculative pressure insufficient."
    lines.append("[1] ATTACK INTENSITY (AII)")
    lines.append(f"    Observed: AII = {aii:.4f} (max |deviation| = {aii*100:.1f}%)")
    lines.append(
        f"    Expected: 0.10–0.25 (Eichengreen et al. 1995: −12% to −25% from peg)"
    )
    lines.append(f"    Score: {aii_score:.1%}")
    lines.append(f"    Assessment: {aii_assess}")
    lines.append("")

    # Criterion 2: PSD
    if 15 <= psd <= 30:
        psd_assess = "PASS — Peg defended for 15–30 rounds before breach; realistic defense duration."
    elif psd < 8:
        psd_assess = (
            "EARLY — Peg breached too quickly; increase CentralBankDefender reserves."
        )
    elif psd > total_rounds * 0.9:
        psd_assess = "NO BREACH — Peg held; attack repelled or insufficient."
    else:
        psd_assess = (
            "LATE — Defense lasted longer than expected; check attack parameters."
        )
    lines.append("[2] PEG SURVIVAL DURATION (PSD)")
    lines.append(f"    Observed: PSD = {psd} rounds")
    lines.append(
        f"    Expected: 15–30 rounds (Obstfeld 1996: reserves sustain peg for limited period)"
    )
    lines.append(f"    Score: {psd_score:.1%}")
    lines.append(f"    Assessment: {psd_assess}")
    lines.append("")

    # Criterion 3: SFAF
    if 0.6 <= sfaf <= 0.9:
        sfaf_assess = (
            "PASS — Self-fulfilling amplification at Obstfeld (1996) expected range."
        )
    elif sfaf > 1.0:
        sfaf_assess = (
            "HIGH — Self-fulfilling channel dominates; crisis is coordination-driven."
        )
    elif sfaf < 0.3:
        sfaf_assess = "LOW — Minimal self-fulfilling amplification; crisis is attacker-driven only."
    else:
        sfaf_assess = (
            "MODERATE — Amplification present but below expected coordination level."
        )
    lines.append("[3] SELF-FULFILLING AMPLIFICATION (SFAF)")
    lines.append(f"    Observed: SFAF = {sfaf:.3f}")
    lines.append(
        f"    Expected: 0.5–1.5 (Obstfeld 1996: SelfFulfillingTrader adds but doesn't dominate)"
    )
    lines.append(f"    Score: {sfaf_score:.1%}")
    lines.append(f"    Assessment: {sfaf_assess}")
    lines.append("")

    # Criterion 4: FAS
    if 0.5 <= fas <= 0.8:
        fas_assess = "PASS — FundamentalHedger active during most attack rounds; anchor operational."
    elif fas < 0.3:
        fas_assess = (
            "WEAK — Fundamental anchor too weak; hedger rarely buying during attacks."
        )
    else:
        fas_assess = "HIGH — Fundamental anchor strong; may limit crisis depth."
    lines.append("[4] FUNDAMENTAL ANCHOR STRENGTH (FAS)")
    lines.append(f"    Observed: FAS = {fas:.3f}")
    lines.append(
        f"    Expected: 0.5–0.8 (Morris & Shin 1998: fundamentals anchor against self-fulfilling crises)"
    )
    lines.append(f"    Score: {fas_score:.1%}")
    lines.append(f"    Assessment: {fas_assess}")
    lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            f"The simulation successfully reproduces self-fulfilling currency crisis dynamics: "
            f"AII {aii:.3f} ({aii*100:.1f}% max deviation from peg), "
            f"peg survived {psd} rounds, SFAF {sfaf:.2f}, FAS {fas:.2f}. "
            f"The Obstfeld self-fulfilling mechanism (expectation coordination → selling → "
            f"peg breach) is operating as designed. Fit Score: {overall_score:.1%}."
        )
    else:
        lines.append(
            f"The simulation does not fully reproduce currency crisis dynamics. "
            f"Overall Fit Score {overall_score:.1%} is below the 50% threshold. "
            f"Key issues: "
            + ("attack too weak; " if aii < 0.10 else "")
            + ("peg breached too early; " if psd < 8 else "")
            + ("peg never breached; " if psd > total_rounds * 0.9 else "")
            + ("SFAF out of range; " if not (0.2 <= sfaf <= 2.5) else "")
            + ("FAS too low; " if fas < 0.3 else "")
            + "Review analysis-bases.md §6 for parameter fixes."
        )
    lines.append(f"Fit Score: {overall_score:.1%}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualizations  (analysis-bases.md §7)
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
    psd: int,
    output_dir: str,
) -> None:
    """Create 4 analysis plots per analysis-bases.md §7.

    Plots
    -----
    00_investor_bids.png     : Investor Bidding Curves (headline chart)
    01_currencycrisis_dynamics.png    : Exchange rate vs Peg + Deviation %
    02_currencycrisis_analysis.png    : Rolling Volatility + Attack phase attribution
    03_summary.png           : Agent VWAP comparison + Volume
    """
    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    if not fundamentals:
        raise ValueError("No fundamental data recorded - simulation data is incomplete")
    fund_value = float(np.mean(list(fundamentals.values())))
    fund_list = [fundamentals[r] for r in rounds_sorted]
    rounds_arr = np.array(rounds_sorted)
    prices_arr = np.array(prices_list)
    fund_arr = np.array(fund_list)
    deviation = (prices_arr - fund_arr) / fund_arr * 100

    # --- Plot 0: Investor Bid Curves (PRIMARY headline chart) ---
    fig0, ax0 = plt.subplots(figsize=(16, 8))
    fig0.suptitle(
        "CurrencyCrisis Rule \u2014 Investor Bidding Curves",
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
        y=fund_value,
        color="darkgreen",
        linestyle="--",
        linewidth=1.2,
        label=f"Fundamental (F={fund_value:.2f})",
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
        "CurrencyCrisis — Exchange Rate & Peg Defense", fontsize=13, fontweight="bold"
    )

    axes[0].plot(
        rounds_arr, prices_arr, label="Exchange Rate", color="darkblue", linewidth=1.5
    )
    axes[0].plot(
        rounds_arr,
        fund_arr,
        label="Peg (Fundamental)",
        color="green",
        linestyle="--",
        linewidth=1.2,
    )
    if psd < len(rounds_sorted):
        axes[0].axvline(
            x=rounds_sorted[psd] if psd < len(rounds_sorted) else rounds_sorted[-1],
            color="red",
            linestyle=":",
            alpha=0.8,
            label=f"Peg breach (r{psd})",
        )
    axes[0].set_title("Exchange Rate vs Peg")
    axes[0].set_xlabel("Round")
    axes[0].set_ylabel("Price")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(rounds_arr, deviation, color="darkred", linewidth=1.5)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].axhline(
        y=-5, color="orange", linestyle=":", alpha=0.7, label="−5% peg breach"
    )
    axes[1].axhline(y=-10, color="red", linestyle=":", alpha=0.7, label="−10% crisis")
    axes[1].axhline(
        y=-20, color="darkred", linestyle=":", alpha=0.7, label="−20% severe"
    )
    axes[1].set_title("Deviation from Peg (%)")
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "01_currencycrisis_dynamics.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 02: Crisis Dynamics ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "CurrencyCrisis — Crisis Intensity Analysis", fontsize=13, fontweight="bold"
    )

    if rolling_vols and len(prices_list) > 1:
        vol_rounds = rounds_arr[1:]
        axes[0].plot(vol_rounds, rolling_vols, color="purple", linewidth=1.5)
        axes[0].axhline(
            y=2.0,
            color="orange",
            linestyle=":",
            alpha=0.7,
            label="2% volatility threshold",
        )
        axes[0].set_title("Rolling Volatility (10-round window, %)")
        axes[0].set_xlabel("Round")
        axes[0].set_ylabel("Volatility (%)")
        axes[0].legend(fontsize=8)
        axes[0].grid(True, alpha=0.3)

    # Attack vs defense phase
    attack_phase = deviation < -3.0
    axes[1].fill_between(
        rounds_arr,
        0,
        deviation,
        where=attack_phase,
        color="salmon",
        alpha=0.4,
        label="Attack phase (δ<-3%)",
    )
    axes[1].plot(rounds_arr, deviation, color="black", linewidth=0.8)
    axes[1].axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    axes[1].set_title("Attack Phase Identification")
    axes[1].set_xlabel("Round")
    axes[1].set_ylabel("Deviation (%)")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "02_currencycrisis_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # ---- Plot 03: Agent Summary ----
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        "CurrencyCrisis — Agent Activity Summary", fontsize=13, fontweight="bold"
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
                y=fund_value,
                color="green",
                linestyle="--",
                alpha=0.7,
                label=f"Peg={fund_value:.4f}",
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


def analyze_currency_crisis(
    data: Dict[str, Any],
    config: dict,
    output_dir: str,
) -> Dict[str, Any]:
    """Run full CurrencyCrisis analysis pipeline.

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
    aii = _compute_attack_intensity_index(prices_list, fund_value)
    psd = _compute_peg_survival_duration(prices_list, fund_value)
    der = _compute_defense_exhaustion_rate(investor_payloads, prices_list, fund_value)
    sfaf = _compute_self_fulfilling_amplification_factor(
        investor_payloads, prices_list, fund_value
    )
    fas = _compute_fundamental_anchor_strength(
        investor_payloads, prices_list, fund_value
    )
    rs = _compute_recovery_speed(prices_list, fund_value)
    max_dd = _compute_max_drawdown(prices_list)
    peak_vol = _compute_peak_rolling_volatility(prices_list)
    rolling_vols = _compute_rolling_volatility(prices_list)
    autocorr = _compute_autocorrelation(prices_list)

    # Agent VWAP
    vwap_data = _compute_agent_vwap(investor_payloads, market_prices)

    # Validation
    validation = _validate_currency_crisis(
        aii=aii,
        psd=psd,
        sfaf=sfaf,
        fas=fas,
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
        psd=psd,
        output_dir=output_dir,
    )

    # Summary
    variant = os.path.basename(os.path.dirname(config["setting"]["record_path"]))
    summary = {
        "scenario": "CurrencyCrisis",
        "variant": variant,
        "total_rounds": total_rounds,
        "fundamental_value": round(fund_value, 4),
        "metrics": {
            "attack_intensity_index": round(aii, 4),
            "peg_survival_duration": psd,
            "defense_exhaustion_rate": round(der, 4),
            "self_fulfilling_amplification_factor": round(sfaf, 4),
            "fundamental_anchor_strength": round(fas, 4),
            "recovery_speed_rounds": rs,
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
    print("CURRENCY CRISIS ANALYSIS")
    print("=" * 50)
    print(f"AII: {aii:.4f} ({aii*100:.1f}% max deviation)  (target: 0.10–0.25)")
    print(f"PSD: {psd} rounds  (target: 15–30)")
    print(f"DER: {der:.4f} per crisis round  (target: <0.3)")
    print(f"SFAF: {sfaf:.3f}  (target: 0.5–1.5)")
    print(f"FAS: {fas:.3f}  (target: 0.5–0.8)")
    print(f"Recovery speed: {rs} rounds  (target: 10–25)")
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run CurrencyCrisis Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze CurrencyCrisis simulation")
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
    summary = analyze_currency_crisis(data, config, output_dir)
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
        scenario='CurrencyCrisis',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


__all__ = [
    "_load_data",
    "_validate_currency_crisis",
    "_build_interpretation",
    "analyze_currency_crisis",
]

if __name__ == "__main__":
    main()
