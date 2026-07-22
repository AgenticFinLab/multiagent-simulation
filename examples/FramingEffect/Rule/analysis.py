#!/usr/bin/env python
"""FramingEffect Rule-Based Simulation Analysis (rich dashboard driver).

This module implements the full analysis contract declared in
``examples/FramingEffect/analysis-bases.md``. It is the single source of
truth for the metric mathematics; the LLM / RuleLLM / Rag variants are
thin wrappers that delegate to :func:`analyze_framingeffect` with a
different ``variant`` label.

Responsibilities:

    1. Pure metric functions (`framing_deviation_index`,
       `framing_asymmetry_ratio`, `framing_volume_impact`,
       `rational_correction_efficiency`,
       `volatility_amplification_factor`,
       `wealth_distribution_index`) — see analysis-bases.md §2.
    2. Load raw record data via ``masim.evaluation.data_loader``.
    3. Compute the six scenario-specific metrics plus standard structural
       metrics (drawdown, volatility, autocorrelation).
    4. Render the 9-panel dashboard specified by analysis-bases.md §7 and
       §3 (Dimensions 1–4).
    5. Validate against §6.2 calibration targets.
    6. Emit ``summary.json`` and a printable interpretation.

Usage::

    python examples/FramingEffect/Rule/analysis.py \
        -c configs/FramingEffect/Rule/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation.data_loader import (
    aligned_market_series as _aligned_market_series,
    batch_to_rounds as _batch_to_rounds,
    load_data as _load_data,
    market_data_from_payload as _market_data_from_payload,
    market_players as _market_players,
)
from masim.evaluation import write_universal_summary

# ---------------------------------------------------------------------------
# Evaluation-first architecture:
#   * Data loading  → masim.evaluation.data_loader (shared)
#   * Scenario metrics (framing_*, wealth_distribution_index) — kept
#     local because they are FramingEffect-specific per analysis-bases.md §2
# ---------------------------------------------------------------------------


# =========================================================================
# §1 — Pure metric functions (analysis-bases.md §2)
# =========================================================================


def framing_deviation_index(price_history: list[float], fundamental: float) -> float:
    """Mean absolute deviation from fundamental. See analysis-bases.md §2.1."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if not price_history:
        raise ValueError("price_history must not be empty")
    return float(np.mean([abs(price - fundamental) / fundamental for price in price_history]))


def framing_asymmetry_ratio(price_history: list[float], fundamental: float) -> float:
    """Positive-vs-negative deviation magnitude ratio. See analysis-bases.md §2.2."""
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if not price_history:
        raise ValueError("price_history must not be empty")
    deviations = [(price - fundamental) / fundamental for price in price_history]
    positives = [abs(dev) for dev in deviations if dev > 0]
    negatives = [abs(dev) for dev in deviations if dev < 0]
    if not positives or not negatives:
        raise ValueError("price_history must contain both positive and negative deviations")
    return float(np.mean(positives) / np.mean(negatives))


def framing_volume_impact(
    net_demand_history: list[float],
    dev_history: list[float],
    threshold: float = 0.02,
) -> float:
    """Average absolute net demand in framing-active rounds. See analysis-bases.md §2.3."""
    if len(net_demand_history) != len(dev_history):
        raise ValueError("net_demand_history and dev_history lengths must match")
    active = [
        abs(demand)
        for demand, deviation in zip(net_demand_history, dev_history)
        if abs(deviation) > threshold
    ]
    if not active:
        raise ValueError("no framing-active rounds found")
    return float(np.mean(active))


def rational_correction_efficiency(
    dev_history: list[float],
    lookahead: int = 5,
    threshold: float = 0.05,
) -> float:
    """Fraction of large deviations that halve within a lookahead window. See analysis-bases.md §2.4."""
    if lookahead <= 0:
        raise ValueError("lookahead must be positive")
    if len(dev_history) <= lookahead:
        raise ValueError("dev_history is shorter than lookahead window")
    candidates = [
        idx
        for idx in range(len(dev_history) - lookahead)
        if abs(dev_history[idx]) > threshold
    ]
    if not candidates:
        raise ValueError("no large deviations found for correction-efficiency calculation")
    corrected = [
        idx
        for idx in candidates
        if abs(dev_history[idx + lookahead]) < abs(dev_history[idx]) * 0.5
    ]
    return float(len(corrected) / len(candidates))


def volatility_amplification_factor(
    price_history: list[float],
    dev_history: list[float],
    threshold: float = 0.02,
) -> float:
    """Volatility ratio of framing-active rounds to quiet rounds. See analysis-bases.md §2.5."""
    if len(price_history) != len(dev_history):
        raise ValueError("price_history and dev_history lengths must match")
    if len(price_history) < 3:
        raise ValueError("price_history must contain at least three points")
    returns = np.diff(np.array(price_history, dtype=float)) / np.array(price_history[:-1], dtype=float)
    active = [ret for ret, dev in zip(returns, dev_history[1:]) if abs(dev) > threshold]
    quiet = [ret for ret, dev in zip(returns, dev_history[1:]) if abs(dev) <= threshold]
    if len(active) < 2 or len(quiet) < 2:
        raise ValueError("both active and quiet return groups need at least two observations")
    quiet_vol = float(np.std(quiet))
    if quiet_vol == 0:
        raise ValueError("quiet-round volatility is zero")
    return float(np.std(active) / quiet_vol)


def wealth_distribution_index(agent_wealth: list[float]) -> float:
    """Gini-style wealth dispersion index. See analysis-bases.md §2.6."""
    if not agent_wealth:
        raise ValueError("agent_wealth must not be empty")
    wealth = np.array(agent_wealth, dtype=float)
    if np.any(wealth < 0):
        raise ValueError("agent_wealth must be non-negative")
    if np.sum(wealth) == 0:
        raise ValueError("agent_wealth sum must be positive")
    sorted_wealth = np.sort(wealth)
    n = len(sorted_wealth)
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * sorted_wealth)) / (n * np.sum(sorted_wealth)) - (n + 1) / n)


# =========================================================================
# §2 — Legacy JSON loader / calculate_metrics / create_visualizations
# =========================================================================
# Kept for ad-hoc callers and unit tests. The main pipeline uses
# `_load_data(results)` from `masim.evaluation.data_loader` instead.


def load_simulation_data(record_path: str | Path) -> Dict[str, Any]:
    """Load a JSON simulation result file from a record directory (ad-hoc)."""
    root = Path(record_path)
    if not root.exists():
        raise FileNotFoundError(f"record_path does not exist: {root}")
    candidates = sorted(root.rglob("*.json"))
    if not candidates:
        raise FileNotFoundError(f"no JSON records found under {root}")
    with candidates[-1].open("r", encoding="utf-8") as handle:
        return json.load(handle)


def calculate_metrics(data: Dict[str, Any]) -> Dict[str, float]:
    """Calculate core FramingEffect metrics from structured JSON data (ad-hoc)."""
    prices: List[float] = data["price_history"]
    fundamental = float(data["fundamental"])
    dev_history = [(price - fundamental) / fundamental for price in prices]
    metrics = {
        "framing_deviation_index": framing_deviation_index(prices, fundamental),
        "framing_asymmetry_ratio": framing_asymmetry_ratio(prices, fundamental),
    }
    if "net_demand_history" in data:
        metrics["framing_volume_impact"] = framing_volume_impact(
            data["net_demand_history"], dev_history
        )
    if "agent_wealth" in data:
        metrics["wealth_distribution_index"] = wealth_distribution_index(data["agent_wealth"])
    return metrics


def create_visualizations(data: Dict[str, Any], output_dir: str | Path) -> None:
    """Create the legacy single price/deviation plot (ad-hoc)."""
    prices = data["price_history"]
    if not prices:
        raise ValueError("data['price_history'] must not be empty")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    fundamental = float(data["fundamental"])
    rounds = list(range(1, len(prices) + 1))
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, prices, label="price")
    plt.axhline(fundamental, color="black", linestyle="--", label="fundamental")
    plt.xlabel("Round")
    plt.ylabel("Price")
    plt.title("FramingEffect Price Dynamics")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output / "framingeffect_price_dynamics.png")
    plt.close()


# =========================================================================
# §3 — Derived series helpers (build inputs for scenario metrics)
# =========================================================================


def _fundamental_value_from_config(config: Dict[str, Any]) -> float:
    """Extract the constant fundamental_value from a coordinator player config."""
    players = config.get("players", {})
    for player_cfg in players.values():
        cfg = player_cfg.get("config", {}) if isinstance(player_cfg, dict) else {}
        extras = cfg.get("extras", {})
        if "fundamental_value" in extras:
            return float(extras["fundamental_value"])
    return 100.0  # analysis-bases.md §6.2 normalization


def _net_demand_series(
    investor_quantities: Dict[str, Dict[int, float]],
    rounds: List[int],
) -> List[float]:
    """Sum signed investor quantities per round → net_demand series."""
    series: List[float] = []
    for round_num in rounds:
        total = 0.0
        for pid_quantities in investor_quantities.values():
            if round_num in pid_quantities:
                total += float(pid_quantities[round_num])
        series.append(total)
    return series


def _investor_role_from_id(pid: str) -> str:
    """Infer agent-type role from a player_id like ``gainframefollower_0``."""
    stem = pid.rsplit("_", 1)[0].lower()
    if "gainframe" in stem:
        return "GainFrameFollower"
    if "lossframe" in stem:
        return "LossFrameReactor"
    if "frameinvariant" in stem:
        return "FrameInvariantTrader"
    if "arbitrage" in stem:
        return "ArbitrageFramer"
    if "noise" in stem:
        return "NoiseTrader"
    return stem or pid


def _agent_type_volume(
    investor_quantities: Dict[str, Dict[int, float]],
    rounds: List[int],
) -> Dict[str, Dict[int, Tuple[float, float]]]:
    """Return {agent_type: {round: (buy_qty, sell_qty)}} across all rounds."""
    per_type: Dict[str, Dict[int, Tuple[float, float]]] = {}
    for pid, quantities in investor_quantities.items():
        role = _investor_role_from_id(pid)
        bucket = per_type.setdefault(role, {r: (0.0, 0.0) for r in rounds})
        for round_num in rounds:
            qty = float(quantities.get(round_num, 0.0))
            buy, sell = bucket[round_num]
            if qty > 0:
                bucket[round_num] = (buy + qty, sell)
            elif qty < 0:
                bucket[round_num] = (buy, sell + abs(qty))
    return per_type


def _agent_wealth_from_payloads(
    investor_payloads: Dict[str, Dict[int, dict]],
    investor_quantities: Dict[str, Dict[int, float]],
    final_price: float,
) -> Dict[str, float]:
    """Approximate final wealth per agent from turn payloads.

    Wealth is: cash + position × final_price, where cash and position are
    recovered from any payload that reports ``cash``/``position``. If no
    such fields are recorded, wealth is approximated as
    ``|cumulative_signed_quantity| × final_price``, which preserves
    ranking across agents even though the absolute value is a proxy.
    """
    wealth: Dict[str, float] = {}
    for pid, payloads in investor_payloads.items():
        cash: float | None = None
        position: float | None = None
        for round_num in sorted(payloads):
            payload = payloads[round_num]
            if not isinstance(payload, dict):
                continue
            if "cash" in payload:
                cash = float(payload["cash"])
            if "position" in payload:
                position = float(payload["position"])
        if cash is not None and position is not None:
            wealth[pid] = cash + position * final_price
        else:
            cum = sum(float(v) for v in investor_quantities.get(pid, {}).values())
            wealth[pid] = abs(cum) * final_price + 10000.0  # +baseline cash proxy
    return wealth


# =========================================================================
# §4 — Validation (analysis-bases.md §6)
# =========================================================================


@dataclass
class FramingValidationResult:
    """Structural validation result for a FramingEffect run."""

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


def _score_range(value: float, lower: float, upper: float) -> float:
    """Score a scalar against a target interval (1.0 if inside)."""
    if not np.isfinite(value):
        return 0.0
    if lower <= value <= upper:
        return 1.0
    if value < lower:
        return max(0.0, value / lower) if lower > 0 else 0.0
    return max(0.0, 1.0 - (value - upper) / max(upper, 1.0))


def _validate_framing_effect(
    fdi: float,
    far: float,
    rce: float,
    vaf: float,
    total_rounds: int,
) -> FramingValidationResult:
    """Validate against analysis-bases.md §6.1 stylised facts + §6.2 targets."""
    fdi_score = _score_range(fdi, 0.03, 0.10)
    far_score = _score_range(far, 0.8, 2.5)
    rce_score = _score_range(rce, 0.35, 0.65)
    vaf_score = _score_range(vaf, 1.5, 3.5)
    rounds_score = _score_range(float(total_rounds), 150.0, 100000.0)

    criteria = {
        "Framing Deviation Index (FDI)": {
            "value": round(fdi, 4),
            "target": "0.03 – 0.10 (Kuhberger 1998, LeBaron 2006)",
            "score": round(fdi_score, 3),
            "passed": fdi_score >= 0.5,
        },
        "Framing Asymmetry Ratio (FAR)": {
            "value": round(far, 4),
            "target": "0.8 – 2.5 (Tversky & Kahneman 1992)",
            "score": round(far_score, 3),
            "passed": far_score >= 0.5,
        },
        "Rational Correction Efficiency (RCE)": {
            "value": round(rce, 4),
            "target": "0.35 – 0.65 (Shleifer & Vishny 1997)",
            "score": round(rce_score, 3),
            "passed": rce_score >= 0.5,
        },
        "Volatility Amplification Factor (VAF)": {
            "value": round(vaf, 4),
            "target": "1.5 – 3.5 (Bollerslev 2009)",
            "score": round(vaf_score, 3),
            "passed": vaf_score >= 0.5,
        },
        "Full-Round Completion": {
            "value": int(total_rounds),
            "target": ">= 150 recorded rounds",
            "score": round(rounds_score, 3),
            "passed": rounds_score >= 0.99,
        },
    }
    weights = {
        "Framing Deviation Index (FDI)": 0.25,
        "Framing Asymmetry Ratio (FAR)": 0.20,
        "Rational Correction Efficiency (RCE)": 0.20,
        "Volatility Amplification Factor (VAF)": 0.15,
        "Full-Round Completion": 0.20,
    }
    score = sum(criteria[name]["score"] * w for name, w in weights.items())
    is_valid = score >= 0.5 and rounds_score >= 0.99

    interpretation = "\n".join(
        [
            f"=== FRAMINGEFFECT VALIDATION: {'VALID' if is_valid else 'INVALID'} ===",
            f"Overall Fit Score: {score:.1%} (threshold 50%)",
            "",
            f"[FDI]  {fdi:.4f}  target 0.03–0.10   score {fdi_score:.1%}",
            f"[FAR]  {far:.4f}  target 0.8–2.5     score {far_score:.1%}",
            f"[RCE]  {rce:.4f}  target 0.35–0.65   score {rce_score:.1%}",
            f"[VAF]  {vaf:.4f}  target 1.5–3.5     score {vaf_score:.1%}",
            f"[Rounds] {total_rounds}",
            "",
            "Rule variant is the calibration anchor for LLM/RuleLLM/Rag comparison.",
        ]
    )
    return FramingValidationResult(is_valid, score, criteria, interpretation)


# =========================================================================
# §5 — Dashboard panels (9-panel set, analysis-bases.md §7 + §3)
# =========================================================================


_AGENT_COLORS = {
    "GainFrameFollower": "#e63946",   # red — gain framing
    "LossFrameReactor": "#f4a261",    # orange — loss framing
    "FrameInvariantTrader": "#2a9d8f",  # teal — rational
    "ArbitrageFramer": "#264653",     # dark — rational arbitrage
    "NoiseTrader": "#a8a8a8",         # gray — noise baseline
}


def _save(fig, output_dir: str, name: str) -> None:
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, name), dpi=150, bbox_inches="tight")
    plt.close(fig)


def _panel_investor_bids(data, computed, output_dir, variant):
    """Panel 00 — investor bidding curves overlaid on price+fundamental."""
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    investor_bids = data["investor_bids"]
    rounds = sorted(market_prices)
    prices = [market_prices[r] for r in rounds]
    fund_vals = [fundamentals[r] for r in rounds]

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(rounds, prices, color="#f0a500", linewidth=2.5, label="Market Price", zorder=10)
    ax.plot(rounds, fund_vals, color="darkgreen", linestyle="--", label="Fundamental")
    bid_colors = ["#3a86ff", "#ff006e", "#8338ec", "#06d6a0", "#fb5607",
                   "#ff595e", "#1982c4", "#6a4c93", "#ffca3a", "#8ac926"]
    for i, (pid, bids) in enumerate(sorted(investor_bids.items())):
        b_rounds = sorted(bids)
        b_vals = [float(bids[r]) for r in b_rounds]
        ax.plot(b_rounds, b_vals, marker="o", markersize=2, linewidth=0.9,
                color=bid_colors[i % len(bid_colors)], alpha=0.8, label=pid)
    ax.set_title(f"FramingEffect ({variant}) — Investor Bidding Curves")
    ax.set_xlabel("Round"); ax.set_ylabel("Price")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4, fontsize=8)
    _save(fig, output_dir, "00_investor_bids.png")


def _panel_price_dynamics(data, computed, output_dir, variant):
    """Panel 01 — price vs fundamental with ±2%, ±5% deviation bands."""
    market_prices = data["market_prices"]; fundamentals = data["fundamentals"]
    rounds = sorted(market_prices)
    prices = np.array([market_prices[r] for r in rounds])
    fund_vals = np.array([fundamentals[r] for r in rounds])
    upper2, lower2 = fund_vals * 1.02, fund_vals * 0.98
    upper5, lower5 = fund_vals * 1.05, fund_vals * 0.95

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.fill_between(rounds, lower5, upper5, color="#ffb703", alpha=0.15, label="±5% band")
    ax.fill_between(rounds, lower2, upper2, color="#8ecae6", alpha=0.30, label="±2% band")
    ax.plot(rounds, fund_vals, color="darkgreen", linestyle="--", linewidth=1.5, label="Fundamental")
    ax.plot(rounds, prices, color="#d62828", linewidth=2, label="Price")
    ax.set_title(f"FramingEffect ({variant}) — Price vs. Fundamental")
    ax.set_xlabel("Round"); ax.set_ylabel("Price")
    ax.grid(True, alpha=0.3); ax.legend(loc="best", fontsize=9)
    _save(fig, output_dir, "01_price_dynamics.png")


def _panel_deviation_timeseries(data, computed, output_dir, variant):
    """Panel 02 — deviation(t) time-series with phase annotations."""
    market_prices = data["market_prices"]; fundamentals = data["fundamentals"]
    rounds, prices, fund_vals = _aligned_market_series(market_prices, fundamentals)
    dev = [(p - f) / f for p, f in zip(prices, fund_vals)]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(rounds, [d * 100 for d in dev], color="#6a4c93", linewidth=1.6)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="-")
    ax.axhline(2, color="#ffb703", linewidth=0.8, linestyle="--", label="±2% threshold")
    ax.axhline(-2, color="#ffb703", linewidth=0.8, linestyle="--")
    ax.axhline(5, color="#d62828", linewidth=0.8, linestyle="--", label="±5% threshold")
    ax.axhline(-5, color="#d62828", linewidth=0.8, linestyle="--")

    fdi = computed.get("framing_deviation_index", float("nan"))
    far = computed.get("framing_asymmetry_ratio", float("nan"))
    ax.text(
        0.02, 0.95,
        f"FDI = {fdi:.4f}   FAR = {far:.3f}",
        transform=ax.transAxes, fontsize=10, va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.75),
    )
    ax.set_title(f"FramingEffect ({variant}) — Deviation Time-Series")
    ax.set_xlabel("Round"); ax.set_ylabel("Deviation (%)")
    ax.grid(True, alpha=0.3); ax.legend(loc="upper right", fontsize=9)
    _save(fig, output_dir, "02_deviation_timeseries.png")


def _panel_volatility_regime(data, computed, output_dir, variant):
    """Panel 03 — return volatility split into framing-active vs quiet regimes."""
    market_prices = data["market_prices"]; fundamentals = data["fundamentals"]
    rounds, prices, fund_vals = _aligned_market_series(market_prices, fundamentals)
    if len(prices) < 3:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.text(0.5, 0.5, "Insufficient data for volatility regime", ha="center")
        _save(fig, output_dir, "03_volatility_regime.png")
        return
    dev = np.array([(p - f) / f for p, f in zip(prices, fund_vals)])
    returns = np.diff(prices) / prices[:-1] * 100
    active_mask = np.abs(dev[1:]) > 0.02
    active_returns = returns[active_mask]
    quiet_returns = returns[~active_mask]
    vaf = computed.get("volatility_amplification_factor", float("nan"))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(rounds[1:], returns, color="#457b9d", linewidth=1.0)
    for r, mask in zip(rounds[1:], active_mask):
        if mask:
            axes[0].axvspan(r - 0.5, r + 0.5, color="#e76f51", alpha=0.15)
    axes[0].axhline(0, color="black", linewidth=0.8, linestyle="--")
    axes[0].set_title("Returns (framing-active regions shaded)")
    axes[0].set_xlabel("Round"); axes[0].set_ylabel("Return (%)")
    axes[0].grid(True, alpha=0.3)

    if len(active_returns) >= 2 and len(quiet_returns) >= 2:
        axes[1].hist([quiet_returns, active_returns], bins=25, stacked=False,
                      label=[f"Quiet σ={np.std(quiet_returns):.2f}%",
                             f"Active σ={np.std(active_returns):.2f}%"],
                      color=["#8ecae6", "#e76f51"], alpha=0.75)
        axes[1].legend(fontsize=9)
    else:
        axes[1].text(0.5, 0.5, "Insufficient regime data", ha="center",
                     transform=axes[1].transAxes)
    axes[1].set_title(f"Return Distribution by Regime  (VAF = {vaf:.3f})")
    axes[1].set_xlabel("Return (%)"); axes[1].grid(True, alpha=0.3)
    _save(fig, output_dir, "03_volatility_regime.png")


def _panel_framing_metrics(data, computed, output_dir, variant):
    """Panel 04 — bar chart of core metrics with calibration target bands."""
    metrics = {
        "FDI": (computed.get("framing_deviation_index", float("nan")), 0.03, 0.10),
        "FAR": (computed.get("framing_asymmetry_ratio", float("nan")), 0.8, 2.5),
        "RCE": (computed.get("rational_correction_efficiency", float("nan")), 0.35, 0.65),
        "VAF": (computed.get("volatility_amplification_factor", float("nan")), 1.5, 3.5),
        "WDI": (computed.get("wealth_distribution_index", float("nan")), 0.15, 0.35),
    }
    labels = list(metrics.keys())
    values = [metrics[k][0] for k in labels]
    lows = [metrics[k][1] for k in labels]
    highs = [metrics[k][2] for k in labels]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(labels))
    ax.bar(x, values, color="#264653", alpha=0.85, label="Observed", zorder=3)
    for i, (lo, hi) in enumerate(zip(lows, highs)):
        ax.plot([i - 0.35, i + 0.35], [lo, lo], color="#2a9d8f", linewidth=2, zorder=4)
        ax.plot([i - 0.35, i + 0.35], [hi, hi], color="#2a9d8f", linewidth=2, zorder=4)
        ax.fill_between([i - 0.35, i + 0.35], lo, hi, color="#2a9d8f", alpha=0.20, zorder=2)
    for i, v in enumerate(values):
        if np.isfinite(v):
            ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_title(f"FramingEffect ({variant}) — Core Metrics vs. Calibration Targets")
    ax.set_ylabel("Metric value")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(["Observed", "Target band"], loc="upper right", fontsize=9)
    _save(fig, output_dir, "04_framing_metrics.png")


def _panel_agent_volume_breakdown(data, computed, output_dir, variant):
    """Panel 05 — stacked bar of buy/sell volume by agent type per round-window."""
    market_prices = data["market_prices"]
    rounds = sorted(market_prices)
    per_type = _agent_type_volume(data["investor_quantities"], rounds)
    if not per_type:
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.text(0.5, 0.5, "No investor quantity records", ha="center")
        _save(fig, output_dir, "05_agent_volume_breakdown.png")
        return
    # Bin into ~20 windows for readability
    n_bins = max(4, min(20, len(rounds) // 10))
    bin_edges = np.linspace(min(rounds), max(rounds) + 1, n_bins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    for ax, side_idx, side_label in [(axes[0], 0, "Buy"), (axes[1], 1, "Sell")]:
        bottom = np.zeros(n_bins)
        for role, bucket in per_type.items():
            binned = np.zeros(n_bins)
            for r, (buy, sell) in bucket.items():
                bin_i = min(np.searchsorted(bin_edges, r, side="right") - 1, n_bins - 1)
                binned[bin_i] += (buy if side_idx == 0 else sell)
            ax.bar(bin_centers, binned, bottom=bottom, width=(bin_edges[1] - bin_edges[0]) * 0.85,
                    color=_AGENT_COLORS.get(role, "#888"), label=role if side_idx == 0 else None, alpha=0.9)
            bottom += binned
        ax.set_title(f"{side_label} volume by agent type (binned)")
        ax.set_ylabel("Quantity")
        ax.grid(True, alpha=0.3, axis="y")
    axes[0].legend(loc="upper right", fontsize=8, ncol=3)
    axes[1].set_xlabel("Round")
    _save(fig, output_dir, "05_agent_volume_breakdown.png")


def _panel_correction_efficiency(data, computed, output_dir, variant):
    """Panel 06 — RCE visualization: large-dev events + correction outcomes."""
    market_prices = data["market_prices"]; fundamentals = data["fundamentals"]
    rounds, prices, fund_vals = _aligned_market_series(market_prices, fundamentals)
    dev = [(p - f) / f for p, f in zip(prices, fund_vals)]
    lookahead, threshold = 5, 0.05
    large_idx = [i for i in range(len(dev) - lookahead) if abs(dev[i]) > threshold]
    corrected_idx = [i for i in large_idx
                      if abs(dev[i + lookahead]) < abs(dev[i]) * 0.5]
    uncorrected_idx = [i for i in large_idx if i not in corrected_idx]
    rce = computed.get("rational_correction_efficiency", float("nan"))

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(rounds, [d * 100 for d in dev], color="#6a4c93", linewidth=1.4, label="Deviation (%)", zorder=3)
    ax.axhline(5, color="#d62828", linewidth=0.8, linestyle="--")
    ax.axhline(-5, color="#d62828", linewidth=0.8, linestyle="--", label="±5% activation threshold")
    if corrected_idx:
        ax.scatter([rounds[i] for i in corrected_idx],
                    [dev[i] * 100 for i in corrected_idx],
                    color="#2a9d8f", s=60, label=f"Corrected ({len(corrected_idx)})",
                    zorder=5, edgecolors="white", linewidth=1)
    if uncorrected_idx:
        ax.scatter([rounds[i] for i in uncorrected_idx],
                    [dev[i] * 100 for i in uncorrected_idx],
                    color="#e76f51", s=60, label=f"Uncorrected ({len(uncorrected_idx)})",
                    zorder=5, edgecolors="white", linewidth=1, marker="X")
    ax.text(0.02, 0.95, f"RCE = {rce:.3f}   (lookahead = {lookahead} rounds)",
             transform=ax.transAxes, fontsize=10, va="top",
             bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
    ax.set_title(f"FramingEffect ({variant}) — Rational Correction Efficiency")
    ax.set_xlabel("Round"); ax.set_ylabel("Deviation (%)")
    ax.grid(True, alpha=0.3); ax.legend(loc="lower right", fontsize=9)
    _save(fig, output_dir, "06_correction_efficiency.png")


def _panel_wealth_by_agent(data, computed, output_dir, variant):
    """Panel 07 — final wealth bar chart grouped by agent type, with Gini annotation."""
    market_prices = data["market_prices"]
    if not market_prices:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No price data", ha="center")
        _save(fig, output_dir, "07_wealth_by_agent.png")
        return
    final_price = float(market_prices[max(market_prices)])
    wealth_by_pid = _agent_wealth_from_payloads(
        data["investor_payloads"], data["investor_quantities"], final_price
    )
    if not wealth_by_pid:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, "No investor payloads", ha="center")
        _save(fig, output_dir, "07_wealth_by_agent.png")
        return

    # Group by agent type
    type_wealth: Dict[str, List[Tuple[str, float]]] = {}
    for pid, w in sorted(wealth_by_pid.items()):
        role = _investor_role_from_id(pid)
        type_wealth.setdefault(role, []).append((pid, w))
    wdi = computed.get("wealth_distribution_index", float("nan"))

    fig, ax = plt.subplots(figsize=(14, 6))
    labels: List[str] = []
    values: List[float] = []
    colors: List[str] = []
    for role, pairs in type_wealth.items():
        for pid, w in pairs:
            labels.append(pid); values.append(w); colors.append(_AGENT_COLORS.get(role, "#888"))
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, alpha=0.9)
    mean_w = float(np.mean(values)) if values else 0.0
    ax.axhline(mean_w, color="black", linestyle="--", linewidth=1, label=f"Mean {mean_w:.0f}")
    for i, v in enumerate(values):
        ax.text(i, v, f"{v:.0f}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_title(f"FramingEffect ({variant}) — Final Wealth by Agent   (WDI = {wdi:.3f})")
    ax.set_ylabel("Final wealth (proxy)")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(loc="upper right", fontsize=9)
    _save(fig, output_dir, "07_wealth_by_agent.png")


def _panel_summary(data, computed, output_dir, variant):
    """Panel 08 — combined summary: residual + returns histogram + net demand overlay."""
    market_prices = data["market_prices"]; fundamentals = data["fundamentals"]
    rounds, prices, fund_vals = _aligned_market_series(market_prices, fundamentals)
    prices_arr = np.array(prices); fund_arr = np.array(fund_vals)
    residual = prices_arr - fund_arr
    returns = np.diff(prices_arr) / prices_arr[:-1] * 100 if len(prices_arr) > 1 else np.array([])
    net_demand = _net_demand_series(data["investor_quantities"], rounds)
    fvi = computed.get("framing_volume_impact", float("nan"))

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    axes[0, 0].plot(rounds, residual, color="#e76f51", linewidth=1.4)
    axes[0, 0].axhline(0, color="black", linewidth=0.8, linestyle="--")
    axes[0, 0].set_title("Price − Fundamental (residual)")
    axes[0, 0].set_xlabel("Round"); axes[0, 0].set_ylabel("Residual")
    axes[0, 0].grid(True, alpha=0.3)

    if len(returns):
        axes[0, 1].hist(returns, bins=25, color="#457b9d", alpha=0.75)
        axes[0, 1].axvline(0, color="black", linewidth=0.8, linestyle="--")
    axes[0, 1].set_title("Return Distribution")
    axes[0, 1].set_xlabel("Return (%)"); axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].bar(rounds, net_demand, color="#6a4c93", alpha=0.7)
    axes[1, 0].axhline(0, color="black", linewidth=0.8, linestyle="--")
    axes[1, 0].set_title(f"Net Demand per Round   (FVI = {fvi:.2f})")
    axes[1, 0].set_xlabel("Round"); axes[1, 0].set_ylabel("Buy − Sell")
    axes[1, 0].grid(True, alpha=0.3, axis="y")

    # Metrics text summary in axes[1,1]
    axes[1, 1].axis("off")
    lines = [f"Scenario: FramingEffect ({variant})",
              f"Rounds: {len(rounds)}",
              "",
              "Core Metrics (analysis-bases.md §2)",
              f"  FDI = {computed.get('framing_deviation_index', float('nan')):.4f}",
              f"  FAR = {computed.get('framing_asymmetry_ratio', float('nan')):.3f}",
              f"  FVI = {computed.get('framing_volume_impact', float('nan')):.2f}",
              f"  RCE = {computed.get('rational_correction_efficiency', float('nan')):.3f}",
              f"  VAF = {computed.get('volatility_amplification_factor', float('nan')):.3f}",
              f"  WDI = {computed.get('wealth_distribution_index', float('nan')):.4f}",
              "",
              f"Price:  init {prices_arr[0]:.2f}   final {prices_arr[-1]:.2f}",
              f"        min  {prices_arr.min():.2f}  max   {prices_arr.max():.2f}",
              ]
    axes[1, 1].text(0.02, 0.98, "\n".join(lines), va="top", ha="left",
                    family="monospace", fontsize=10, transform=axes[1, 1].transAxes)
    fig.suptitle(f"FramingEffect ({variant}) — Summary")
    _save(fig, output_dir, "08_summary.png")


_DASHBOARDS = [
    _panel_investor_bids,
    _panel_price_dynamics,
    _panel_deviation_timeseries,
    _panel_volatility_regime,
    _panel_framing_metrics,
    _panel_agent_volume_breakdown,
    _panel_correction_efficiency,
    _panel_wealth_by_agent,
    _panel_summary,
]


def _create_visualizations(data, computed, output_dir, variant="Rule") -> None:
    """Render every panel, never abort the whole pipeline on a single failure."""
    if not data["market_prices"]:
        return
    os.makedirs(output_dir, exist_ok=True)
    for panel in _DASHBOARDS:
        try:
            panel(data, computed, output_dir, variant)
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] dashboard {panel.__name__} failed: {exc}")


# =========================================================================
# §6 — Compute all metrics
# =========================================================================


def compute_all_metrics(data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, float]:
    """Compute every scenario metric from raw data + config.

    Uses fundamental_value from config when the recorded fundamentals dict
    is empty. Returns a flat ``{metric_name: value}`` dict. Failed
    computations are stored as ``float('nan')`` rather than raising, so a
    single missing series doesn't abort the whole run.
    """
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    if not market_prices:
        raise ValueError("No market price data recorded")

    fund_value = _fundamental_value_from_config(config)
    if not fundamentals:
        fundamentals = {r: fund_value for r in market_prices}
        data["fundamentals"] = fundamentals

    rounds, prices, fund_vals = _aligned_market_series(market_prices, fundamentals)
    dev_history = [(p - f) / f for p, f in zip(prices, fund_vals)]
    net_demand = _net_demand_series(data["investor_quantities"], rounds)
    final_price = float(prices[-1])
    wealth_by_pid = _agent_wealth_from_payloads(
        data["investor_payloads"], data["investor_quantities"], final_price
    )
    agent_wealth = list(wealth_by_pid.values())

    def _safe(fn, *args, **kwargs) -> float:
        try:
            return float(fn(*args, **kwargs))
        except (ValueError, ZeroDivisionError) as exc:
            print(f"[warn] {fn.__name__}: {exc}")
            return float("nan")

    return {
        "framing_deviation_index": _safe(framing_deviation_index, prices, fund_value),
        "framing_asymmetry_ratio": _safe(framing_asymmetry_ratio, prices, fund_value),
        "framing_volume_impact": _safe(framing_volume_impact, net_demand, dev_history),
        "rational_correction_efficiency": _safe(rational_correction_efficiency, dev_history),
        "volatility_amplification_factor": _safe(volatility_amplification_factor, prices, dev_history),
        "wealth_distribution_index": _safe(wealth_distribution_index, agent_wealth) if agent_wealth else float("nan"),
    }


# =========================================================================
# §7 — Analyze pipeline (top-level driver)
# =========================================================================


def analyze_framingeffect(
    data: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str,
    variant: str = "Rule",
) -> Dict[str, Any]:
    """Run FramingEffect analysis: metrics → validation → dashboards → summary."""
    os.makedirs(output_dir, exist_ok=True)
    computed = compute_all_metrics(data, config)
    total_rounds = len(data["market_prices"])

    validation = _validate_framing_effect(
        fdi=computed.get("framing_deviation_index", float("nan")),
        far=computed.get("framing_asymmetry_ratio", float("nan")),
        rce=computed.get("rational_correction_efficiency", float("nan")),
        vaf=computed.get("volatility_amplification_factor", float("nan")),
        total_rounds=total_rounds,
    )

    print(f"Generating {len(_DASHBOARDS)} FramingEffect dashboards in {output_dir}/")
    _create_visualizations(data, computed, output_dir, variant=variant)

    prices_list = [float(v) for _, v in sorted(data["market_prices"].items())]
    summary = {
        "scenario": "FramingEffect",
        "variant": variant,
        "total_rounds": total_rounds,
        "fundamental_value": _fundamental_value_from_config(config),
        "metrics": computed,
        "price": {
            "initial": round(prices_list[0], 4) if prices_list else 0.0,
            "final": round(prices_list[-1], 4) if prices_list else 0.0,
            "min": round(min(prices_list), 4) if prices_list else 0.0,
            "max": round(max(prices_list), 4) if prices_list else 0.0,
        },
        "validation": validation.to_dict(),
    }
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)

    print("\n" + "=" * 50)
    print(f"FRAMING EFFECT ANALYSIS — {variant}")
    print("=" * 50)
    print(f"Total Rounds: {total_rounds}")
    print(f"FDI: {computed.get('framing_deviation_index', float('nan')):.4f}  (target 0.03–0.10)")
    print(f"FAR: {computed.get('framing_asymmetry_ratio', float('nan')):.3f}  (target 0.8–2.5)")
    print(f"RCE: {computed.get('rational_correction_efficiency', float('nan')):.3f}  (target 0.35–0.65)")
    print(f"VAF: {computed.get('volatility_amplification_factor', float('nan')):.3f}  (target 1.5–3.5)")
    print(f"\n{validation.interpretation}")
    print(f"\nFit Score: {validation.score:.1%}  VALID={validation.is_valid}")
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
        scenario='FramingEffect',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


# Legacy shim kept for callers that still reference this symbol.
def analyze_framingeffect_standard(
    data: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Legacy alias — now routes to the rich pipeline."""
    return analyze_framingeffect(data, config, output_dir, variant="Rule")


STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_price_dynamics.png",
    "02_deviation_timeseries.png",
    "03_volatility_regime.png",
    "04_framing_metrics.png",
    "05_agent_volume_breakdown.png",
    "06_correction_efficiency.png",
    "07_wealth_by_agent.png",
    "08_summary.png",
)


def main() -> Dict[str, Any]:
    """Run FramingEffect Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze FramingEffect simulation")
    parser.add_argument(
        "-c", "--config", type=str,
        default="configs/FramingEffect/Rule/simulation.yml",
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    return analyze_framingeffect(data, config, output_dir, variant="Rule")


__all__ = [
    # Pure metrics (analysis-bases.md §2)
    "framing_deviation_index",
    "framing_asymmetry_ratio",
    "framing_volume_impact",
    "rational_correction_efficiency",
    "volatility_amplification_factor",
    "wealth_distribution_index",
    # Legacy ad-hoc helpers
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    # Rich pipeline
    "compute_all_metrics",
    "analyze_framingeffect",
    "analyze_framingeffect_standard",
    "FramingValidationResult",
    "STANDARD_OUTPUT_FILES",
    "_load_data",
    "_batch_to_rounds",
    "main",
]


if __name__ == "__main__":
    main()
