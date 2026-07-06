#!/usr/bin/env python
"""AnchoringEffect Rule-Based Simulation Analysis.

Driver for the AnchoringEffect Rule variant.  All metric mathematics live in
``examples.AnchoringEffect.metrics`` (registry-driven).  This file is responsible
for:

    1. Building the ``data`` dict from a record store (``_load_data``).
    2. Computing every registered metric (``REGISTRY.compute_all``).
    3. Validating against analysis-bases.md §6 calibration targets
       (``_validate_anchoring_effect``).
    4. Rendering the 11-panel dashboard set (``_create_visualizations``).
    5. Emitting ``summary.json`` plus printable interpretation.

LLM / RuleLLM / Rag variants delegate to :func:`analyze_anchoring` and override
the ``variant`` field — no metric maths are duplicated.

Usage::

    python examples/AnchoringEffect/Rule/analysis.py \
        -c configs/AnchoringEffect/Rule/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation.registry import MetricUnavailable
from masim.evaluation.data_loader import (
    batch_to_rounds as _batch_to_rounds,
    load_data as _load_data,
    market_data_from_payload as _market_data_from_payload,
    market_players as _market_players,
)
from examples.AnchoringEffect.metrics import REGISTRY


# ---------------------------------------------------------------------------
# Evaluation-first architecture (Pass 2 Migration Rule):
#   * Reusable helpers  → masim.evaluation.data_loader / registry
#   * Standard metrics  → masim.evaluation.finance.{timeseries,behavioral,microstructure}
#   * Scenario metrics  → examples.AnchoringEffect.metrics (registry-driven)
# See ``masim/evaluation/README.md`` for the authoritative catalogue and
# ``masim/skills/implement-simulation-skill/10-evaluation-architecture.md``
# for the migration rule.  Nothing in this file re-implements a function
# that already lives under ``masim.evaluation``.
# ---------------------------------------------------------------------------


def _get_adjustment_factor(config: dict) -> float:
    """Return the anchoring ``adjustment_factor`` from the first player
    config that exposes it under ``config.extras``.

    Scenario-specific config parsing — kept local because
    ``adjustment_factor`` is an AnchoringEffect-only field.  Raises if
    no player carries the field, mirroring the pre-refactor behaviour."""

    players = config["players"]
    for player_cfg in players.values():
        if "config" not in player_cfg:
            continue
        extras = player_cfg["config"].get("extras", {})
        if "adjustment_factor" in extras:
            return float(extras["adjustment_factor"])
    raise ValueError(
        "No adjustment_factor found in AnchoringEffect player configs."
    )


# ---------------------------------------------------------------------------
# Validation — analysis-bases.md §6 (Task 5: tightened gates)
# ---------------------------------------------------------------------------


@dataclass
class AnchoringValidationResult:
    """Result of AnchoringEffect simulation validation."""

    is_valid: bool
    score: float
    criteria: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    advisories: List[str] = field(default_factory=list)
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": round(self.score, 4),
            "criteria": self.criteria,
            "advisories": self.advisories,
            "interpretation": self.interpretation,
        }


def _score_band(value: float, lo: float, hi: float, soft: float = 0.5) -> float:
    """Triangular score: 1.0 inside [lo, hi]; linearly decays to ``soft`` at
    [lo/2, 2*hi] then to 0 at [lo/4, 4*hi]."""
    if lo <= value <= hi:
        return 1.0
    if value < lo:
        if value <= 0:
            return 0.0
        if value >= lo / 2.0:
            return soft + (1.0 - soft) * (value - lo / 2.0) / (lo / 2.0)
        if value >= lo / 4.0:
            return soft * (value - lo / 4.0) / (lo / 4.0)
        return 0.0
    # value > hi
    if value <= 2.0 * hi:
        return soft + (1.0 - soft) * (2.0 * hi - value) / hi
    if value <= 4.0 * hi:
        return soft * (4.0 * hi - value) / (2.0 * hi)
    return 0.0


def _validate_anchoring_effect(
    mad_pct: float,
    half_life: float,
    max_drawdown_pct: float,
    autocorr_lag1: float,
    total_rounds: int,
    silent_count: int = 0,
    under_revision_ratio: float = 1.0,
    signed_volume_autocorr: float = 0.0,
) -> AnchoringValidationResult:
    """Tightened gates per analysis-bases.md §6.

    Hard pass requires *all four*:
        mad_score          ≥ 0.5
        half_life_score    ≥ 0.5
        drawdown_score     ≥ 0.5
        weighted_overall   ≥ 0.6

    Target ranges (literature):
        MAD          ∈ [3, 10] %      (Campbell & Sharpe 2009)
        half-life    ∈ [20, 60]       (Campbell & Sharpe 2009)
        |drawdown|   ∈ [5, 20] %      (Northcraft & Neale 1987)

    Non-blocking advisories (do not affect ``is_valid``) are emitted when:
        * ``silent_count > 0``
        * ``under_revision_ratio < 0.7`` (correction starts too quickly)
        * ``|signed_volume_autocorr| > 0.5`` (book is degenerate / regime-locked)
    """
    criteria: Dict[str, Dict[str, Any]] = {}

    mad_score = _score_band(mad_pct, 3.0, 10.0)
    criteria["mad"] = {
        "value": round(mad_pct, 3),
        "target": "[3, 10] %",
        "score": round(mad_score, 3),
        "passed": mad_score >= 0.5,
    }

    hl_score = _score_band(half_life, 20.0, 60.0)
    criteria["half_life"] = {
        "value": round(half_life, 1),
        "target": "[20, 60] rounds",
        "score": round(hl_score, 3),
        "passed": hl_score >= 0.5,
    }

    abs_dd = abs(max_drawdown_pct)
    dd_score = _score_band(abs_dd, 5.0, 20.0)
    criteria["max_drawdown"] = {
        "value": round(max_drawdown_pct, 3),
        "target": "|drawdown| ∈ [5, 20] %",
        "score": round(dd_score, 3),
        "passed": dd_score >= 0.5,
    }

    overall = mad_score * 0.40 + hl_score * 0.40 + dd_score * 0.20
    is_valid = (
        mad_score >= 0.5
        and hl_score >= 0.5
        and dd_score >= 0.5
        and overall >= 0.6
    )

    advisories: List[str] = []
    if silent_count > 0:
        advisories.append(
            f"silent_agent_count={silent_count} (>0): some investors never traded."
        )
    if under_revision_ratio < 0.7:
        advisories.append(
            f"under_revision_ratio={under_revision_ratio:.2f} (<0.7): "
            "deviation flips sign too quickly — anchoring may be weak."
        )
    if abs(signed_volume_autocorr) > 0.5:
        advisories.append(
            f"signed_volume_autocorr={signed_volume_autocorr:.2f}: "
            "order flow is heavily auto-correlated — agents may be regime-locked."
        )

    interpretation = _build_interpretation(
        is_valid=is_valid,
        overall_score=overall,
        mad_pct=mad_pct,
        half_life=half_life,
        max_drawdown_pct=max_drawdown_pct,
        autocorr_lag1=autocorr_lag1,
        total_rounds=total_rounds,
        mad_score=mad_score,
        hl_score=hl_score,
        dd_score=dd_score,
        advisories=advisories,
    )

    return AnchoringValidationResult(
        is_valid=is_valid,
        score=overall,
        criteria=criteria,
        advisories=advisories,
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
    advisories: Optional[List[str]] = None,
) -> str:
    advisories = advisories or []
    lines: List[str] = []
    verdict = "VALID" if is_valid else "INVALID"
    lines.append(f"=== ANCHORING EFFECT SIMULATION VALIDATION: {verdict} ===")
    lines.append(
        f"Weighted Score: {overall_score:.1%}  (gate: ≥60% AND each component ≥50%)"
    )
    lines.append("")

    # [1] MAD
    lines.append("[1] MISPRICING MAGNITUDE (MAD)")
    lines.append(f"    Observed: {mad_pct:.2f}%   Target: [3, 10]%   Score: {mad_score:.1%}")
    lines.append("    Reference: Campbell & Sharpe (2009) — analyst forecast errors ~3–8%.")
    lines.append("")

    # [2] Half-life
    lines.append("[2] ANCHORING PERSISTENCE (HALF-LIFE)")
    lines.append(
        f"    Observed: {half_life:.1f} rounds   Target: [20, 60]   Score: {hl_score:.1%}"
    )
    lines.append("    Reference: Campbell & Sharpe (2009) — quarterly persistence.")
    lines.append("")

    # [3] Drawdown
    abs_dd = abs(max_drawdown_pct)
    lines.append("[3] CORRECTION DYNAMICS (MAX DRAWDOWN)")
    lines.append(
        f"    Observed: {max_drawdown_pct:.2f}%   Target |dd| ∈ [5, 20]%   Score: {dd_score:.1%}"
    )
    lines.append("    Reference: Northcraft & Neale (1987) — expert anchoring correction.")
    lines.append("")

    # [4] AC1
    lines.append("[4] RETURN AUTOCORRELATION (LAG 1)")
    lines.append(
        f"    Observed: {autocorr_lag1:.3f}   Reference: Lo & MacKinlay (1988) — random walk null."
    )
    lines.append("")

    # [5] Advisories
    if advisories:
        lines.append("[5] NON-BLOCKING ADVISORIES")
        for advisory in advisories:
            lines.append(f"    • {advisory}")
        lines.append("")

    # Summary
    lines.append("[SUMMARY]")
    if is_valid:
        lines.append(
            "Simulation reproduces anchoring-driven mispricing followed by mean reversion,"
        )
        lines.append(
            "consistent with Tversky & Kahneman (1974) and Campbell & Sharpe (2009)."
        )
    else:
        failed = []
        if mad_score < 0.5:
            failed.append("MAD outside calibration band")
        if hl_score < 0.5:
            failed.append("half-life outside calibration band")
        if dd_score < 0.5:
            failed.append("drawdown outside calibration band")
        if overall_score < 0.6:
            failed.append("weighted score below 60%")
        lines.append("Simulation does not satisfy analysis-bases.md §6 calibration:")
        for f in failed:
            lines.append(f"    – {f}")
        lines.append(
            "Tune adjustment_factor, mean_reversion (γ), and agent composition."
        )
    lines.append(f"Total rounds: {total_rounds}.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualization — registry-driven 9-panel dashboard set
# ---------------------------------------------------------------------------

_BID_COLORS = [
    "#3a86ff", "#ff006e", "#8338ec", "#06d6a0", "#fb5607",
    "#ff595e", "#1982c4", "#6a4c93", "#ffca3a", "#8ac926",
    "#e07a5f", "#3d405b", "#81b29a", "#f2cc8f", "#264653",
    "#e63946", "#457b9d", "#2a9d8f", "#e9c46a", "#f4a261",
]

_PHASE_COLORS = {
    "Anchor Establishment": "#bde0fe",
    "Persistent Mispricing": "#ffd6a5",
    "Slow Correction":       "#caffbf",
    "Convergence":           "#d0bdf4",
}


def _save(fig, output_dir: str, name: str) -> str:
    path = os.path.join(output_dir, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")
    return path


def _panel_investor_bids(data, computed, output_dir, variant):
    """Dashboard 00 — primary headline chart."""
    market_prices = data["market_prices"]
    investor_bids = data["investor_bids"]
    if not market_prices:
        return
    rounds_sorted = sorted(market_prices.keys())
    prices = [market_prices[r] for r in rounds_sorted]
    fund = sum(data["fundamentals"].values()) / max(1, len(data["fundamentals"]))
    fig, ax = plt.subplots(figsize=(16, 8))
    fig.suptitle(
        f"AnchoringEffect {variant} — Investor Bidding Curves",
        fontsize=14, fontweight="bold",
    )
    ax.plot(rounds_sorted, prices, color="#f0a500", linewidth=2.5,
            label="Market Price", zorder=10)
    ax.axhline(y=fund, color="darkgreen", linestyle="--", linewidth=1.2,
               label=f"Fundamental (F={fund:.2f})", alpha=0.8)
    for idx, (pid, bids_by_round) in enumerate(sorted(investor_bids.items())):
        bid_rounds = sorted(bids_by_round.keys())
        bid_vals = [float(bids_by_round[r]) for r in bid_rounds]
        ax.plot(bid_rounds, bid_vals, marker="o", markersize=2, linewidth=0.9,
                color=_BID_COLORS[idx % len(_BID_COLORS)], alpha=0.8,
                label=pid.replace("_", " ").title())
    ax.set_xlabel("Round"); ax.set_ylabel("Price")
    ax.set_title("Market Price & Individual Investor Bids")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06),
              ncol=min(5, len(investor_bids) + 2), fontsize=8,
              frameon=True, framealpha=0.7)
    _save(fig, output_dir, "00_investor_bids.png")


def _panel_price_dynamics(data, computed, output_dir, variant):
    """Dashboard 01 — Price/Fundamental, Deviation, Phase shading."""
    market_prices = data["market_prices"]
    if not market_prices:
        return
    rounds_sorted = sorted(market_prices.keys())
    prices = [market_prices[r] for r in rounds_sorted]
    fund = sum(data["fundamentals"].values()) / max(1, len(data["fundamentals"]))
    deviation_pct = [(p - fund) / fund * 100 for p in prices]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"AnchoringEffect {variant} — Price Dynamics",
                 fontsize=13, fontweight="bold")

    axes[0].plot(rounds_sorted, prices, color="steelblue", label="Market Price")
    axes[0].axhline(y=fund, color="darkgreen", linestyle="--",
                    label=f"Fundamental (F={fund:.1f})")
    # Phase shading from registry
    phase_block = computed.get("phase_assignment_ts", {})
    phases = phase_block.get("phases", [])
    phase_names = phase_block.get("phase_names", {})
    if phases:
        last_p = phases[0]; start = rounds_sorted[0]
        for i, p in enumerate(phases + [None]):
            if p != last_p:
                end = rounds_sorted[i - 1] if i - 1 < len(rounds_sorted) else rounds_sorted[-1]
                colour = _PHASE_COLORS.get(phase_names.get(str(last_p), ""), "#eeeeee")
                axes[0].axvspan(start, end, color=colour, alpha=0.35)
                if i < len(rounds_sorted):
                    start = rounds_sorted[i]
                last_p = p
    axes[0].set_title("Price vs. Fundamental (with phases)")
    axes[0].set_xlabel("Round"); axes[0].set_ylabel("Price")
    axes[0].legend(); axes[0].grid(True, alpha=0.3)

    axes[1].plot(rounds_sorted, deviation_pct, color="crimson",
                 label="Deviation (%)")
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].axhline(y=3, color="orange", linestyle=":", alpha=0.7, label="±3%")
    axes[1].axhline(y=10, color="red", linestyle=":", alpha=0.5, label="±10%")
    axes[1].axhline(y=-3, color="orange", linestyle=":", alpha=0.7)
    axes[1].axhline(y=-10, color="red", linestyle=":", alpha=0.5)
    hl_block = computed.get("half_life_fitted") or computed.get("half_life_threshold")
    if hl_block and hl_block.get("value_rounds") and \
            hl_block["value_rounds"] < len(prices):
        axes[1].axvline(x=rounds_sorted[int(hl_block["value_rounds"])],
                        color="purple", linestyle=":", alpha=0.7,
                        label=f"Half-life ≈ {hl_block['value_rounds']:.0f}")
    axes[1].set_title("Price Deviation from Fundamental (%)")
    axes[1].set_xlabel("Round"); axes[1].set_ylabel("Deviation (%)")
    axes[1].legend(fontsize=8); axes[1].grid(True, alpha=0.3)
    _save(fig, output_dir, "01_price_dynamics.png")


def _panel_volatility_returns(data, computed, output_dir, variant):
    """Dashboard 02 — Rolling vol + return distribution."""
    rolling = computed.get("rolling_volatility_ts", {})
    vols = rolling.get("rolling_vol_pct", [])
    market_prices = data["market_prices"]
    rounds_sorted = sorted(market_prices.keys())
    prices = [market_prices[r] for r in rounds_sorted]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"AnchoringEffect {variant} — Volatility & Returns",
                 fontsize=13, fontweight="bold")
    if vols:
        axes[0].plot(rounds_sorted[1: len(vols) + 1], vols, color="purple")
        axes[0].axhline(y=0.5, color="green", linestyle=":", alpha=0.7,
                        label="0.5%")
        axes[0].axhline(y=2.0, color="orange", linestyle=":", alpha=0.7,
                        label="2.0%")
        axes[0].set_title(f"Rolling Volatility (window={rolling.get('window', 10)})")
        axes[0].set_xlabel("Round"); axes[0].set_ylabel("Std (%)")
        axes[0].legend(fontsize=8); axes[0].grid(True, alpha=0.3)

    if len(prices) > 1:
        arr = np.array(prices)
        rets = np.diff(arr) / arr[:-1] * 100
        axes[1].hist(rets, bins=30, color="steelblue", alpha=0.7,
                     edgecolor="white")
        skew = computed.get("return_skewness", {}).get("value", float("nan"))
        kurt = computed.get("return_kurtosis", {}).get("value_excess", float("nan"))
        axes[1].set_title(f"Returns (skew={skew:.2f}, ex.kurt={kurt:.2f})")
        axes[1].set_xlabel("Return (%)"); axes[1].set_ylabel("Frequency")
        axes[1].grid(True, alpha=0.3)
    _save(fig, output_dir, "02_volatility_returns.png")


def _panel_autocorrelation(data, computed, output_dir, variant):
    """Dashboard 03 — Autocorrelation profile + variance ratio."""
    profile = computed.get("return_autocorr_profile", {})
    lags = profile.get("lags", [])
    acs = profile.get("ac_values", [])
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"AnchoringEffect {variant} — Serial Dependence",
        fontsize=13, fontweight="bold",
    )
    if lags:
        axes[0].bar(lags, acs, color="#4361ee", alpha=0.7)
        axes[0].axhline(y=0, color="black", linewidth=0.7)
        n = len(data["market_prices"]) - 1
        if n > 0:
            ci = 1.96 / np.sqrt(n)
            axes[0].axhline(y=ci, color="grey", linestyle=":", label="±95% CI")
            axes[0].axhline(y=-ci, color="grey", linestyle=":")
        axes[0].set_title("Return Autocorrelation (lags 1..10)")
        axes[0].set_xlabel("Lag"); axes[0].set_ylabel("AC")
        axes[0].legend(); axes[0].grid(True, alpha=0.3)

    vr = computed.get("variance_ratio_lo_mackinlay", {})
    if vr:
        periods = ["VR(2)", "VR(4)", "VR(8)"]
        vals = [vr.get("vr_q2", 1.0), vr.get("vr_q4", 1.0), vr.get("vr_q8", 1.0)]
        axes[1].bar(periods, vals, color="#7209b7", alpha=0.7)
        axes[1].axhline(y=1.0, color="black", linestyle="--",
                        label="Random walk (1.0)")
        axes[1].set_title("Lo & MacKinlay Variance Ratios")
        axes[1].set_ylabel("VR(q)"); axes[1].legend(); axes[1].grid(True, alpha=0.3)
    _save(fig, output_dir, "03_autocorrelation.png")


def _panel_anchoring(data, computed, output_dir, variant):
    """Dashboard 04 — bias / dispersion / under-revision."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"AnchoringEffect {variant} — Anchoring-Specific",
        fontsize=13, fontweight="bold",
    )

    bias = computed.get("bias_magnitude_pct", {})
    under = computed.get("under_revision_ratio", {})
    rt = computed.get("regime_transition_lag", {})
    cells = [
        ("MAD",               f"{computed.get('mad_pct', {}).get('value_pct', float('nan')):.2f}%"),
        ("Bias magnitude",    f"{bias.get('value_pct', float('nan')):.2f}%"),
        ("alpha (adj. factor)", f"{bias.get('alpha', float('nan')):.2f}"),
        ("Anchor price",      f"{bias.get('anchor_price', float('nan')):.2f}"),
        ("Fundamental",       f"{bias.get('fundamental_value', float('nan')):.2f}"),
        ("Under-revision",    f"{under.get('value', float('nan')):.2f}"),
        ("Regime trans. lag", f"{rt.get('value_rounds', float('nan'))}"),
    ]
    axes[0].axis("off")
    table = axes[0].table(
        cellText=[[k, v] for k, v in cells],
        colLabels=["Metric", "Value"],
        loc="center", cellLoc="left",
    )
    table.auto_set_font_size(False); table.set_fontsize(10)
    table.scale(1.0, 1.4)
    axes[0].set_title("Anchoring Magnitude Table")

    pad = computed.get("price_to_anchor_distance_ts", {})
    rounds = pad.get("rounds", [])
    dist = pad.get("distance_pct", [])
    if rounds:
        axes[1].plot(rounds, dist, color="darkred")
        axes[1].axhline(y=0, color="black", linestyle="--")
        axes[1].set_title(
            f"Price - Anchor (%)   anchor={pad.get('anchor_price', float('nan')):.2f}"
        )
        axes[1].set_xlabel("Round"); axes[1].set_ylabel("Distance (%)")
        axes[1].grid(True, alpha=0.3)
    _save(fig, output_dir, "04_anchoring_specific.png")


def _panel_agent_volume(data, computed, output_dir, variant):
    """Dashboard 05 — Per-agent buy/sell + action frequency."""
    avb = computed.get("agent_volume_buy_sell", {}).get("per_agent", {})
    aaf = computed.get("agent_action_frequency", {}).get("per_agent", {})
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f"AnchoringEffect {variant} — Agent Trading Volume",
        fontsize=13, fontweight="bold",
    )
    if avb:
        agents = list(avb.keys())
        buys = [avb[a]["total_buy"] for a in agents]
        sells = [avb[a]["total_sell"] for a in agents]
        x = np.arange(len(agents))
        axes[0].bar(x - 0.2, buys, 0.4, label="Buy", color="green", alpha=0.7)
        axes[0].bar(x + 0.2, sells, 0.4, label="Sell", color="red", alpha=0.7)
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(agents, rotation=35, ha="right", fontsize=7)
        axes[0].set_title("Buy vs Sell Volume per Agent")
        axes[0].set_ylabel("Total quantity"); axes[0].legend()
        axes[0].grid(True, alpha=0.3)
    if aaf:
        agents = list(aaf.keys())
        buys = [aaf[a]["buy"] for a in agents]
        sells = [aaf[a]["sell"] for a in agents]
        holds = [aaf[a]["hold"] for a in agents]
        x = np.arange(len(agents))
        axes[1].bar(x, buys, label="Buy", color="green", alpha=0.7)
        axes[1].bar(x, sells, bottom=buys, label="Sell",
                    color="red", alpha=0.7)
        bottom_hold = [b + s for b, s in zip(buys, sells)]
        axes[1].bar(x, holds, bottom=bottom_hold, label="Hold",
                    color="grey", alpha=0.7)
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(agents, rotation=35, ha="right", fontsize=7)
        axes[1].set_title("Action Frequency per Agent")
        axes[1].set_ylabel("Round count"); axes[1].legend()
        axes[1].grid(True, alpha=0.3)
    _save(fig, output_dir, "05_agent_volume.png")


def _panel_agent_positions(data, computed, output_dir, variant):
    """Dashboard 06 — Net position over time + terminal PnL/Sharpe."""
    nets = computed.get("agent_net_position_ts", {}).get("per_agent", {})
    pnls = computed.get("agent_pnl_terminal", {}).get("per_agent", {})
    sharpes = computed.get("agent_sharpe_terminal", {}).get("per_agent", {})
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f"AnchoringEffect {variant} — Agent Positions & Performance",
        fontsize=13, fontweight="bold",
    )
    if nets:
        for idx, (aid, block) in enumerate(sorted(nets.items())):
            rs = block.get("rounds", [])
            ps = block.get("positions", [])
            axes[0].plot(rs, ps, linewidth=1.0,
                         color=_BID_COLORS[idx % len(_BID_COLORS)],
                         label=aid.replace("_", " ").title())
        axes[0].set_title("Net position over time")
        axes[0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        axes[0].set_xlabel("Round"); axes[0].set_ylabel("Net quantity")
        axes[0].legend(loc="upper left", fontsize=6, ncol=2)
        axes[0].grid(True, alpha=0.3)
    if pnls:
        agents = list(pnls.keys())
        pnl_vals = [pnls[a].get("pnl", 0.0) for a in agents]
        sharpe_vals = [sharpes.get(a, {}).get("sharpe", 0.0) for a in agents]
        x = np.arange(len(agents))
        ax2 = axes[1]
        ax2.bar(x - 0.2, pnl_vals, 0.4, label="Terminal PnL",
                color="#4361ee", alpha=0.7)
        ax2.set_xticks(x)
        ax2.set_xticklabels(agents, rotation=35, ha="right", fontsize=7)
        ax2.set_ylabel("PnL"); ax2.legend(loc="upper left")
        ax2.grid(True, alpha=0.3)
        ax3 = ax2.twinx()
        ax3.bar(x + 0.2, sharpe_vals, 0.4, label="Sharpe",
                color="#fb8500", alpha=0.7)
        ax3.set_ylabel("Sharpe"); ax3.legend(loc="upper right")
        ax2.set_title("Terminal PnL & Sharpe per Agent")
    _save(fig, output_dir, "06_agent_performance.png")


def _panel_microstructure(data, computed, output_dir, variant):
    """Dashboard 07 — Order imbalance, signed-vol AC, RU/AT ratio,
    momentum/anchoring coupling."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"AnchoringEffect {variant} — Microstructure",
        fontsize=13, fontweight="bold",
    )
    oib = computed.get("order_imbalance_ts", {})
    rounds = oib.get("rounds", [])
    imb = oib.get("imbalance", [])
    if rounds:
        axes[0].plot(rounds, imb, color="teal")
        axes[0].axhline(y=0, color="black", linestyle="--", alpha=0.5)
        mean_imb = oib.get("mean_imbalance", 0.0)
        axes[0].axhline(y=mean_imb, color="red", linestyle=":",
                        label=f"mean={mean_imb:.2f}")
        axes[0].set_title("Order Imbalance per Round")
        axes[0].set_xlabel("Round"); axes[0].set_ylabel("net / gross")
        axes[0].legend(); axes[0].grid(True, alpha=0.3)

    signed_ac = computed.get("signed_volume_autocorr", {}).get(
        "value", float("nan")
    )
    ru_at = computed.get("corrective_to_biased_volume_ratio", {})
    coup = computed.get("momentum_anchoring_coupling", {})
    cells = [
        ("Signed-volume AC(1)", f"{signed_ac:.3f}"),
        ("RU / (AT+HA) volume", f"{ru_at.get('value', float('nan')):.3f}"),
        ("MT vs AT corr",       f"{coup.get('value', float('nan')):.3f}"),
        ("Biased volume",       f"{ru_at.get('biased_volume', float('nan')):.0f}"),
        ("Corrective volume",   f"{ru_at.get('corrective_volume', float('nan')):.0f}"),
    ]
    axes[1].axis("off")
    table = axes[1].table(
        cellText=[[k, v] for k, v in cells],
        colLabels=["Microstructure", "Value"],
        loc="center", cellLoc="left",
    )
    table.auto_set_font_size(False); table.set_fontsize(10); table.scale(1.0, 1.4)
    axes[1].set_title("Microstructure Diagnostics")
    _save(fig, output_dir, "07_microstructure.png")


def _panel_inference(data, computed, output_dir, variant):
    """Dashboard 08 — Block-bootstrap CIs + ADF/Ljung-Box."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"AnchoringEffect {variant} — Statistical Inference",
        fontsize=13, fontweight="bold",
    )

    mad_ci = computed.get("mad_block_bootstrap_ci_95", {})
    hl_ci = computed.get("half_life_block_bootstrap_ci_95", {})

    labels: List[str] = []
    means: List[float] = []
    los: List[float] = []
    his: List[float] = []
    if mad_ci:
        labels.append("MAD (%)")
        means.append(mad_ci.get("mean_pct", 0.0))
        los.append(mad_ci.get("ci95_low_pct", 0.0))
        his.append(mad_ci.get("ci95_high_pct", 0.0))
    if hl_ci:
        labels.append("Half-life (rds)")
        means.append(hl_ci.get("mean_rounds", 0.0))
        los.append(hl_ci.get("ci95_low_rounds", 0.0))
        his.append(hl_ci.get("ci95_high_rounds", 0.0))
    if labels:
        x = np.arange(len(labels))
        err = [
            [m - lo for m, lo in zip(means, los)],
            [hi - m for m, hi in zip(means, his)],
        ]
        axes[0].errorbar(x, means, yerr=err, fmt="o", color="#4361ee",
                         capsize=8, markersize=8)
        axes[0].set_xticks(x); axes[0].set_xticklabels(labels)
        axes[0].set_title("Block-Bootstrap 95% CIs")
        axes[0].grid(True, alpha=0.3)

    lb = computed.get("ljung_box_returns_pvalue", {})
    adf = computed.get("adf_unit_root_pvalue", {})
    cells = [
        ("Ljung-Box Q",   f"{lb.get('q_statistic', float('nan')):.2f}"),
        ("LB p-value",    f"{lb.get('p_value', float('nan')):.3f}"),
        ("LB max lag",    f"{lb.get('max_lag', '')}"),
        ("ADF t-stat",    f"{adf.get('t_statistic', float('nan')):.2f}"),
        ("ADF p-value",   f"{adf.get('approx_p_value', float('nan')):.3f}"),
    ]
    axes[1].axis("off")
    table = axes[1].table(
        cellText=[[k, v] for k, v in cells],
        colLabels=["Test", "Value"],
        loc="center", cellLoc="left",
    )
    table.auto_set_font_size(False); table.set_fontsize(10); table.scale(1.0, 1.4)
    axes[1].set_title("Hypothesis Tests")
    _save(fig, output_dir, "08_inference.png")


def _panel_wealth_dynamics(data, computed, output_dir, variant):
    """Dashboard 09 — Terminal wealth bars + Gini + wealth transfer."""
    wealth_block = computed.get("agent_wealth_terminal", {})
    gini_block = computed.get("gini_coefficient", {})
    transfer_block = computed.get("wealth_transfer_direction", {})
    per_agent = wealth_block.get("per_agent", {})
    if not per_agent:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f"AnchoringEffect {variant} \u2014 Wealth Dynamics",
        fontsize=13, fontweight="bold",
    )
    # Left: terminal wealth bars grouped by strategy
    strategy_wealth: Dict[str, List[float]] = {}
    for pid, info in per_agent.items():
        # Infer strategy from payloads
        payloads = data["investor_payloads"].get(pid, {})
        strategy = "Unknown"
        for payload in payloads.values():
            strategy = payload.get("strategy", "Unknown")
            break
        strategy_wealth.setdefault(strategy, []).append(info.get("wealth", 0.0))
    strategies = sorted(strategy_wealth)
    means = [float(np.mean(strategy_wealth[s])) for s in strategies]
    x = np.arange(len(strategies))
    colors = [_BID_COLORS[i % len(_BID_COLORS)] for i in range(len(strategies))]
    axes[0].bar(x, means, color=colors, alpha=0.8)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(strategies, rotation=35, ha="right", fontsize=8)
    axes[0].set_title("Mean Terminal Wealth by Strategy")
    axes[0].set_ylabel("Wealth ($)")
    axes[0].grid(True, alpha=0.3)
    gini = gini_block.get("value", float("nan"))
    axes[0].annotate(
        f"Gini = {gini:.3f}",
        xy=(0.95, 0.95), xycoords="axes fraction",
        ha="right", va="top", fontsize=11,
        bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.8),
    )
    # Right: wealth transfer direction
    biased_change = transfer_block.get("biased_net_change", 0.0)
    corrective_change = transfer_block.get("corrective_net_change", 0.0)
    labels = ["Biased\n(AT+HA+DT)", "Corrective\n(RU+FA+CT)"]
    values = [biased_change, corrective_change]
    bar_colors = ["#ff6b6b" if v < 0 else "#51cf66" for v in values]
    axes[1].bar(labels, values, color=bar_colors, alpha=0.8, width=0.5)
    axes[1].axhline(y=0, color="black", linestyle="--", alpha=0.5)
    axes[1].set_title("Net Wealth Change by Group")
    axes[1].set_ylabel("\u0394 Wealth ($)")
    axes[1].grid(True, alpha=0.3)
    transfer = transfer_block.get("transfer_to_corrective", 0.0)
    axes[1].annotate(
        f"Transfer \u2192 Corrective: ${transfer:,.0f}",
        xy=(0.5, 0.95), xycoords="axes fraction",
        ha="center", va="top", fontsize=10,
        bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.8),
    )
    _save(fig, output_dir, "09_wealth_dynamics.png")


def _panel_information_tail_risk(data, computed, output_dir, variant):
    """Dashboard 10 — Efficiency ratio + tail risk + HHI + correlation heatmap."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        f"AnchoringEffect {variant} \u2014 Information Efficiency & Tail Risk",
        fontsize=13, fontweight="bold",
    )
    # [0,0] Price efficiency ratio as a single-value annotation + decay slope
    per = computed.get("price_efficiency_ratio", {})
    decay = computed.get("deviation_decay_slope", {})
    persist = computed.get("forecast_error_persistence", {})
    cells = [
        ("Price Efficiency Ratio", f"{per.get('value', float('nan')):.3f}"),
        ("Deviation Decay Slope", f"{decay.get('slope_per_round', float('nan')):.5f}"),
        ("Forecast Error Persist.", f"{persist.get('value', float('nan')):.3f}"),
    ]
    info_share = computed.get("information_share_by_strategy", {})
    shares = info_share.get("shares", {})
    for strategy, share in sorted(shares.items(), key=lambda x: -x[1])[:4]:
        cells.append((f"Info share: {strategy}", f"{share:.1%}"))
    axes[0, 0].axis("off")
    table = axes[0, 0].table(
        cellText=[[k, v] for k, v in cells],
        colLabels=["Metric", "Value"],
        loc="center", cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.3)
    axes[0, 0].set_title("Information Efficiency")

    # [0,1] VaR / CVaR tail histogram
    market_prices = data["market_prices"]
    rounds_sorted = sorted(market_prices.keys())
    prices = np.array([market_prices[r] for r in rounds_sorted], dtype=float)
    if prices.size > 1:
        rets = np.diff(prices) / prices[:-1] * 100
        axes[0, 1].hist(rets, bins=30, color="steelblue", alpha=0.7,
                        edgecolor="white")
        var_block = computed.get("value_at_risk_95", {})
        cvar_block = computed.get("conditional_var_95", {})
        var_val = var_block.get("value_pct", float("nan"))
        cvar_val = cvar_block.get("value_pct", float("nan"))
        if np.isfinite(var_val):
            axes[0, 1].axvline(x=var_val, color="red", linestyle="--",
                               label=f"VaR\u2089\u2085={var_val:.2f}%")
        if np.isfinite(cvar_val):
            axes[0, 1].axvline(x=cvar_val, color="darkred", linestyle=":",
                               label=f"CVaR\u2089\u2085={cvar_val:.2f}%")
        axes[0, 1].set_title("Return Distribution + Tail Risk")
        axes[0, 1].set_xlabel("Return (%)")
        axes[0, 1].set_ylabel("Frequency")
        axes[0, 1].legend(fontsize=9)
        axes[0, 1].grid(True, alpha=0.3)

    # [1,0] HHI concentration
    hhi_block = computed.get("herfindahl_volume_concentration", {})
    hhi = hhi_block.get("value", float("nan"))
    n_agents = hhi_block.get("n_agents", 14)
    ideal = 1.0 / max(n_agents, 1)
    axes[1, 0].bar(["HHI", "Ideal (1/N)"], [hhi, ideal],
                   color=["#e63946", "#2a9d8f"], alpha=0.8, width=0.4)
    axes[1, 0].set_title(f"Volume Concentration (N={n_agents})")
    axes[1, 0].set_ylabel("HHI")
    axes[1, 0].set_ylim(0, max(0.5, hhi * 1.5) if np.isfinite(hhi) else 0.5)
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].annotate(
        f"HHI = {hhi:.3f}",
        xy=(0.5, 0.9), xycoords="axes fraction",
        ha="center", fontsize=11,
        bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.8),
    )

    # [1,1] Strategy correlation heatmap
    corr_block = computed.get("strategy_correlation_matrix", {})
    matrix = corr_block.get("matrix", {})
    strategies = corr_block.get("strategies", [])
    if matrix and len(strategies) >= 2:
        arr = np.array([[matrix[s1].get(s2, 0.0) for s2 in strategies]
                        for s1 in strategies])
        im = axes[1, 1].imshow(arr, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        axes[1, 1].set_xticks(range(len(strategies)))
        axes[1, 1].set_yticks(range(len(strategies)))
        short_names = [s[:8] for s in strategies]
        axes[1, 1].set_xticklabels(short_names, rotation=45, ha="right", fontsize=7)
        axes[1, 1].set_yticklabels(short_names, fontsize=7)
        axes[1, 1].set_title("Strategy Demand Correlation")
        fig.colorbar(im, ax=axes[1, 1], fraction=0.046, pad=0.04)
    else:
        axes[1, 1].axis("off")
        axes[1, 1].set_title("Strategy Correlation (insufficient data)")
    _save(fig, output_dir, "10_information_tail_risk.png")


_DASHBOARDS = [
    _panel_investor_bids,
    _panel_price_dynamics,
    _panel_volatility_returns,
    _panel_autocorrelation,
    _panel_anchoring,
    _panel_agent_volume,
    _panel_agent_positions,
    _panel_microstructure,
    _panel_inference,
    _panel_wealth_dynamics,
    _panel_information_tail_risk,
]


def _create_visualizations(
    data: Dict[str, Any],
    computed: Dict[str, Any],
    output_dir: str,
    variant: str = "Rule",
) -> None:
    """Render all 11 dashboards from the registry-computed metric blocks."""
    if not data["market_prices"]:
        return
    os.makedirs(output_dir, exist_ok=True)
    for panel in _DASHBOARDS:
        try:
            panel(data, computed, output_dir, variant)
        except Exception as exc:  # noqa: BLE001 — never fail whole pipeline
            print(f"[warn] dashboard {panel.__name__} failed: {exc}")


# ---------------------------------------------------------------------------
# Public analysis contract
# ---------------------------------------------------------------------------


def load_simulation_data(config: dict) -> Dict[str, Any]:
    """Load persisted simulation records into the standard analysis data dict."""
    return _load_data(load_results(config))


def calculate_metrics(data: Dict[str, Any], config: dict) -> Dict[str, Any]:
    """Compute every registered metric and return a flat scalar summary.

    The flat dict only contains scalar fields (output keys ending in
    ``_value``, ``_pct``, ``value``, ``value_pct``, ``mean``, ``ratio``, etc.).
    For the full nested registry payload, call :func:`compute_all_metrics`.
    """
    computed = compute_all_metrics(data, config)
    flat = {k: v for k, v in computed.items() if k != "_unavailable"}
    return flat


def compute_all_metrics(data: Dict[str, Any], config: dict) -> Dict[str, Any]:
    """Run every registered metric and return a flat ``{name: outputs}`` dict.

    The evaluation-first ``MetricsRegistry.compute_all`` returns::

        {"metrics": {name: outputs, ...},
         "unavailable": [name, ...],
         "errors": {name: message, ...}}

    We flatten the ``metrics`` payload here so callers can index by metric
    name directly, and we preserve the unavailable / error lists under
    reserved ``_unavailable`` / ``_errors`` keys.
    """
    result = REGISTRY.compute_all(data, config)
    flat: Dict[str, Any] = dict(result.get("metrics", {}))
    if result.get("unavailable"):
        flat["_unavailable"] = list(result["unavailable"])
    if result.get("errors"):
        flat["_errors"] = dict(result["errors"])
    return flat


def create_visualizations(
    data: Dict[str, Any],
    config: dict,
    output_dir: str,
) -> None:
    """Compute metrics and render all dashboards."""
    computed = compute_all_metrics(data, config)
    _create_visualizations(data, computed, output_dir, variant="Rule")


def analyze_anchoring(
    data: Dict[str, Any], config: dict, output_dir: str,
    variant: str = "Rule",
) -> Dict[str, Any]:
    """Run full anchoring analysis pipeline (metrics + validation + plots).

    Parameters
    ----------
    variant
        Label to embed in the summary and plot titles. Override from
        LLM/RuleLLM/Rag wrappers.
    """
    os.makedirs(output_dir, exist_ok=True)

    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]

    if not market_prices:
        raise ValueError("No market price data found. Run simulation first.")
    if not fundamentals:
        raise ValueError("No fundamental value data found in market records.")

    rounds_sorted = sorted(market_prices.keys())
    prices_list = [market_prices[r] for r in rounds_sorted]
    total_rounds = len(prices_list)
    fund_value = sum(fundamentals.values()) / len(fundamentals)
    adjustment_factor = _get_adjustment_factor(config)

    # --- All metrics via registry ---
    computed = compute_all_metrics(data, config)

    # Pull the headline scalars used by validation.
    mad_pct = computed.get("mad_pct", {}).get("value_pct", float("nan"))
    hl_block = computed.get("half_life_fitted") or computed.get("half_life_threshold", {})
    half_life = float(hl_block.get("value_rounds", float("nan")))
    max_dd = computed.get("max_drawdown_pct", {}).get("value_pct", float("nan"))
    autocorr = computed.get("return_autocorr_lag1", {}).get("value", float("nan"))
    silent_count = int(
        computed.get("silent_agent_count", {}).get("silent_count", 0)
    )
    under_rev = float(
        computed.get("under_revision_ratio", {}).get("value", 1.0)
    )
    sv_ac = float(
        computed.get("signed_volume_autocorr", {}).get("value", 0.0)
    )

    validation = _validate_anchoring_effect(
        mad_pct=mad_pct,
        half_life=half_life,
        max_drawdown_pct=max_dd,
        autocorr_lag1=autocorr,
        total_rounds=total_rounds,
        silent_count=silent_count,
        under_revision_ratio=under_rev,
        signed_volume_autocorr=sv_ac,
    )

    # --- Plots ---
    print(f"Generating {len(_DASHBOARDS)} analysis dashboards in {output_dir}/")
    _create_visualizations(data, computed, output_dir, variant=variant)

    # --- Summary ---
    summary = {
        "scenario": "AnchoringEffect",
        "variant": variant,
        "total_rounds": total_rounds,
        "fundamental_value": fund_value,
        "adjustment_factor": adjustment_factor,
        "metrics_by_category": {
            cat: {m.name: computed.get(m.name) for m in REGISTRY.metrics_in_category(cat)
                  if computed.get(m.name) is not None}
            for cat in REGISTRY.categories()
        },
        "metrics_unavailable": computed.get("_unavailable", {}),
        "metrics_flat": {k: v for k, v in computed.items()
                         if k != "_unavailable"},
        "price": {
            "initial": round(prices_list[0], 4),
            "final": round(prices_list[-1], 4),
            "min": round(min(prices_list), 4),
            "max": round(max(prices_list), 4),
            "mean": round(sum(prices_list) / len(prices_list), 4),
        },
        "validation": validation.to_dict(),
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    # --- Console output ---
    print("\n" + "=" * 50)
    print(f"ANCHORING EFFECT ANALYSIS — {variant}")
    print("=" * 50)
    print(f"MAD: {mad_pct:.2f}%  (target: 3–10%)")
    print(f"Half-life: {half_life:.1f} rounds  (target: 20–60)")
    print(f"Max drawdown: {max_dd:.2f}%  (target: −5% to −20%)")
    print(f"Lag-1 autocorrelation: {autocorr:.3f}")
    print(f"Silent agents: {silent_count}")
    print(f"\n{validation.interpretation}")
    print(f"\nFit Score: {validation.score:.1%}  "
          f"VALID={validation.is_valid}")

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Run AnchoringEffect Rule analysis."""
    parser = argparse.ArgumentParser(description="Analyze AnchoringEffect simulation")
    parser.add_argument(
        "-c", "--config", type=str, required=True,
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    return analyze_anchoring(data, config, output_dir)


if __name__ == "__main__":
    main()


__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "compute_all_metrics",
    "create_visualizations",
    "analyze_anchoring",
    "_validate_anchoring_effect",
    "_build_interpretation",
    "_load_data",
    "_batch_to_rounds",
    "AnchoringValidationResult",
    "REGISTRY",
]
