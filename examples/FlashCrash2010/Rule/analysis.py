#!/usr/bin/env python
"""2010 Flash Crash Rule Simulation Analysis.

Implements ``analysis-bases.md`` for the ``Rule`` variant of the 2010 Flash
Crash scenario. Produces the standardised output set required by the
``implement-simulation-skill``:

    summary.json
    00_investor_bids.png  (alias of fig7_stop_loss_cascade.png)
    01_flashcrash2010_dynamics.png  (alias of fig1_price_dynamics.png)
    02_flashcrash2010_analysis.png  (alias of fig3_drawdown.png)
    03_summary.png  (alias of fig8_recovery.png)

Metric functions correspond one-to-one with ``analysis-bases.md §2``:

    * ``max_drawdown``
    * ``depth_collapse_ratio``
    * ``spread_widening_factor``
    * ``hft_withdrawal_rounds``
    * ``cascade_trigger_rounds``
    * ``recovery_time``

Usage
-----
    python examples/FlashCrash2010/Rule/analysis.py \
        -c configs/FlashCrash2010/Rule/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.finance import (
    calculate_max_drawdown,
    calculate_returns,
    calculate_rolling_volatility,
    save_figure,
    validate_flash_crash,
)
from masim.evaluation.data_loader import market_players
from masim.utils import load_config, load_results


# ===========================================================================
# Standard output naming (mandated by implement-simulation-skill)
# ===========================================================================


STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_flashcrash2010_dynamics.png",
    "02_flashcrash2010_analysis.png",
    "03_summary.png",
)


def _write_standard_named_outputs(output_dir: str) -> None:
    """Create fixed-name aliases required by the standard output contract.

    Copies the analytically-named source figures to their standardised
    ``00_/01_/02_/03_`` alias names so downstream tooling can rely on a
    stable file layout regardless of scenario.
    """
    aliases = {
        "fig7_stop_loss_cascade.png": "00_investor_bids.png",
        "fig1_price_dynamics.png": "01_flashcrash2010_dynamics.png",
        "fig3_drawdown.png": "02_flashcrash2010_analysis.png",
        "fig8_recovery.png": "03_summary.png",
    }
    for source, target in aliases.items():
        source_path = os.path.join(output_dir, source)
        if not os.path.exists(source_path):
            raise FileNotFoundError(
                f"missing FlashCrash2010 analysis figure: {source_path}"
            )
        shutil.copyfile(source_path, os.path.join(output_dir, target))


# ===========================================================================
# Core metric functions (analysis-bases.md §2)
# ===========================================================================


def max_drawdown(price_history: List[float]) -> float:
    """Peak-to-trough price decline as a fraction of the running peak.

    Returns a non-negative number (``0.09`` = 9 % drawdown). ``analysis-bases.md §2``.
    """
    if not price_history:
        return 0.0
    peak = price_history[0]
    max_dd = 0.0
    for p in price_history:
        if p > peak:
            peak = p
        if peak > 0:
            dd = (peak - p) / peak
            if dd > max_dd:
                max_dd = dd
    return float(max_dd)


def depth_collapse_ratio(depth_history: List[float], base_depth: float) -> float:
    """Minimum observed depth divided by the configured ``base_depth``.

    ``0.1`` means depth fell to 10 % of baseline (a 90 % collapse).
    Returns NaN when the metric is undefined (empty history / non-positive
    base). 1.0 was previously used as a fallback, but that is the exact
    "no collapse / normal liquidity" null and silently made missing data
    look like a real negative result.
    """
    if not depth_history or base_depth <= 0:
        return float("nan")
    return float(min(depth_history) / base_depth)


def spread_widening_factor(
    spread_history: List[float], normal_spread: float = 0.0001
) -> float:
    """Maximum spread reached divided by ``normal_spread`` (baseline).

    Returns NaN when the metric is undefined (empty history or invalid
    baseline). Previously returned 1.0 (the "no widening" null) on empty
    input, which conflated a missing measurement with a real negative
    result. Also removed the max(normal_spread, 1e-8) denominator floor,
    which turned intended NaN divisions into artificially-large finite
    numbers.
    """
    if not spread_history or normal_spread <= 0:
        return float("nan")
    return float(max(spread_history) / normal_spread)


def hft_withdrawal_rounds(
    hft_orders_by_round: List[List[Dict[str, Any]]],
    withdrawal_threshold: int = 0,
) -> int:
    """Number of rounds in which total HFT order quantity equals zero.

    ``withdrawal_threshold`` permits a small residual HFT flow (default 0).
    """
    count = 0
    for round_orders in hft_orders_by_round:
        hft_qty = sum(
            abs(o.get("quantity", 0))
            for o in round_orders
            if o.get("agent_type") == "hft"
        )
        if hft_qty <= withdrawal_threshold:
            count += 1
    return int(count)


def cascade_trigger_rounds(
    stoploss_orders_by_round: List[List[Dict[str, Any]]],
) -> List[int]:
    """Rounds in which at least one ``StopLossTrader`` fires a sell.

    Returned indices are 0-based positions into ``stoploss_orders_by_round``.
    """
    return [
        i
        for i, round_orders in enumerate(stoploss_orders_by_round)
        if any(
            o.get("agent_type") == "stoploss" and o.get("quantity", 0) < 0
            for o in round_orders
        )
    ]


def recovery_time(
    price_history: List[float],
    trough_round: int,
    fundamental: float,
    threshold: float = 0.02,
) -> int:
    """Rounds from ``trough_round`` back to within ``threshold`` of ``fundamental``.

    Returns ``-1`` when the market never recovers within the observed window.
    """
    if fundamental <= 0 or not price_history:
        return -1
    trough_round = max(0, min(int(trough_round), len(price_history) - 1))
    for i in range(trough_round, len(price_history)):
        if abs(price_history[i] - fundamental) / fundamental <= threshold:
            return i - trough_round
    return -1


# ===========================================================================
# Cascade wave counting (used by validation §6)
# ===========================================================================


def count_cascade_waves(cascade_rounds: List[int], gap: int = 3) -> int:
    """Cluster consecutive ``cascade_trigger_rounds`` into distinct waves.

    Two triggers separated by more than ``gap`` rounds are treated as
    belonging to different waves. Used by ``validate_flashcrash2010()``
    to score the "2–5 distinct waves" band described in
    ``analysis-bases.md §6``.
    """
    if not cascade_rounds:
        return 0
    sorted_rounds = sorted(cascade_rounds)
    waves = 1
    prev = sorted_rounds[0]
    for r in sorted_rounds[1:]:
        if r - prev > gap:
            waves += 1
        prev = r
    return int(waves)


# ===========================================================================
# Data loading
# ===========================================================================


def _extract_series_from_market(
    coordinator: Any,
) -> Tuple[List[float], List[float], List[float], List[float], List[int]]:
    """Extract per-round price, spread, depth, volume series from Market payloads.

    The ``Market.decide()`` step returns
    ``{"market_data": {...}, "outbound_messages": [...]}`` and this payload
    is what MASim persists per round in ``turns.payloads()``. We normalise
    to plain Python lists ordered by round number.
    """
    payloads = coordinator.turns.payloads()
    price: List[float] = []
    spread: List[float] = []
    depth: List[float] = []
    volume: List[float] = []
    rounds: List[int] = []

    for rn in sorted(payloads.keys()):
        payload = payloads[rn]
        md = payload.get("market_data") if isinstance(payload, dict) else None
        if not isinstance(md, dict):
            continue
        if "price" not in md:
            continue
        price.append(float(md["price"]))
        spread.append(float(md["spread"]) if "spread" in md else float("nan"))
        depth.append(float(md["depth"]) if "depth" in md else float("nan"))
        volume.append(float(md["volume"]) if "volume" in md else float("nan"))
        rounds.append(int(rn))
    return price, spread, depth, volume, rounds


def _collect_orders_by_round(
    results: Any,
    rounds: List[int],
) -> Tuple[
    Dict[int, List[Dict[str, Any]]],
    Dict[int, List[Dict[str, Any]]],
    Dict[str, Dict[int, Dict[str, Any]]],
]:
    """Return ``(hft_by_round, stoploss_by_round, per_agent_payloads)``.

    Each round is a list of order dicts (matching the payload shape produced
    by the investor ``decide()`` methods in ``players.py``).
    ``per_agent_payloads[agent_id][round] = payload`` is also returned so
    LLM/Rag variants can add their own diagnostics on top of the same
    extraction.
    """
    hft_by_round: Dict[int, List[Dict[str, Any]]] = {r: [] for r in rounds}
    stop_by_round: Dict[int, List[Dict[str, Any]]] = {r: [] for r in rounds}
    per_agent: Dict[str, Dict[int, Dict[str, Any]]] = {}

    for pid, player in results.players_by_role("player").items():
        agent_payloads: Dict[int, Dict[str, Any]] = {}
        for rn, payload in player.turns.payloads().items():
            if not isinstance(payload, dict):
                continue
            agent_payloads[int(rn)] = payload
            agent_type = payload.get("agent_type")
            if agent_type == "hft" and int(rn) in hft_by_round:
                hft_by_round[int(rn)].append(payload)
            if agent_type == "stoploss" and int(rn) in stop_by_round:
                stop_by_round[int(rn)].append(payload)
        if agent_payloads:
            per_agent[pid] = agent_payloads

    return hft_by_round, stop_by_round, per_agent


def load_simulation_data(config: Dict[str, Any], results: Any) -> Dict[str, Any]:
    """Load all per-round series required by ``calculate_metrics``.

    Parameters
    ----------
    config : dict
        Parsed simulation config (from ``load_config``).
    results : MASim Results
        Already-loaded record store (from ``load_results``).

    Returns
    -------
    dict with keys:
        rounds, price_history, spread_history, depth_history, volume_history,
        fundamental, base_depth, normal_spread,
        hft_orders_by_round, stoploss_orders_by_round,
        per_agent_payloads.
    """
    coordinators = market_players(results)
    if not coordinators:
        raise ValueError("No coordinator/market player found in results")
    coordinator = next(iter(coordinators.values()))

    price, spread, depth, volume, rounds = _extract_series_from_market(coordinator)
    if not price:
        raise ValueError("No market price payloads found in coordinator turns")

    hft_by_round, stop_by_round, per_agent = _collect_orders_by_round(
        results, rounds
    )
    hft_orders_by_round = [hft_by_round[r] for r in rounds]
    stoploss_orders_by_round = [stop_by_round[r] for r in rounds]

    market_extras = config["players"]["market"]["config"]["extras"]
    fundamental = float(market_extras["fundamental_value"])
    base_depth_val = float(market_extras["base_depth"])

    # Locate a canonical normal_spread (falls back to 1e-4 per analysis-bases §2)
    normal_spread = 0.0001
    for entry in config["players"].values():
        extras = entry.get("config", {}).get("extras", {}) or {}
        if "normal_spread" in extras:
            normal_spread = float(extras["normal_spread"])
            break

    return {
        "rounds": rounds,
        "price_history": price,
        "spread_history": spread,
        "depth_history": depth,
        "volume_history": volume,
        "fundamental": fundamental,
        "base_depth": base_depth_val,
        "normal_spread": normal_spread,
        "hft_orders_by_round": hft_orders_by_round,
        "stoploss_orders_by_round": stoploss_orders_by_round,
        "per_agent_payloads": per_agent,
    }


# ===========================================================================
# Metric aggregation
# ===========================================================================


def calculate_metrics(
    data: Dict[str, Any], config: Dict[str, Any]
) -> Dict[str, Any]:
    """Assemble the metric dict consumed by ``validate_flashcrash2010``.

    Uses ``masim.evaluation.finance.calculate_max_drawdown`` for the
    peak/trough indices in addition to the analysis-bases ``max_drawdown``
    function so downstream plots can shade the correct phase bands.
    """
    price = data["price_history"]
    spread = data["spread_history"]
    depth = data["depth_history"]
    volume = data["volume_history"]
    fundamental = data["fundamental"]
    base_depth_val = data["base_depth"]
    normal_spread = data["normal_spread"]

    # Peak/trough via evaluation-first helper (dd_pct is signed, negative)
    dd_pct, peak_idx, trough_idx = calculate_max_drawdown(price)
    dd_fraction = max_drawdown(price)  # analysis-bases §2 unsigned form

    depth_ratio = depth_collapse_ratio(depth, base_depth_val)
    spread_factor = spread_widening_factor(spread, normal_spread)
    hft_wd = hft_withdrawal_rounds(data["hft_orders_by_round"])
    cascade_rounds = cascade_trigger_rounds(data["stoploss_orders_by_round"])
    wave_count = count_cascade_waves(cascade_rounds)
    rec_time = recovery_time(price, trough_idx, fundamental)

    # Returns / rolling volatility (evaluation-first)
    returns = calculate_returns(price)
    rolling_vol = calculate_rolling_volatility(price, window=10)
    mean_vol = float(np.mean(rolling_vol)) if len(rolling_vol) else 0.0
    max_vol = float(np.max(rolling_vol)) if len(rolling_vol) else 0.0

    return {
        # Core §2 metrics ----------------------------------------------------
        "max_drawdown": float(dd_fraction),
        "max_drawdown_pct": float(dd_pct),
        "peak_round": int(peak_idx),
        "trough_round": int(trough_idx),
        "depth_collapse_ratio": float(depth_ratio),
        "spread_widening_factor": float(spread_factor),
        "hft_withdrawal_rounds": int(hft_wd),
        "cascade_trigger_rounds": cascade_rounds,
        "cascade_wave_count": int(wave_count),
        "recovery_time": int(rec_time),
        # Generic price / return summary ------------------------------------
        "total_rounds": len(price),
        "initial_price": float(price[0]) if price else None,
        "final_price": float(price[-1]) if price else None,
        "min_price": float(min(price)) if price else None,
        "max_price": float(max(price)) if price else None,
        "mean_return": float(np.mean(returns)) if len(returns) else 0.0,
        "return_std": float(np.std(returns)) if len(returns) else 0.0,
        "mean_rolling_volatility": mean_vol,
        "max_rolling_volatility": max_vol,
        "total_volume": float(sum(volume)),
        "fundamental_value": float(fundamental),
        "base_depth": float(base_depth_val),
        "normal_spread": float(normal_spread),
    }


# ===========================================================================
# Validation (analysis-bases.md §6 targets)
# ===========================================================================


def _in_range(value: float, lo: float, hi: float) -> bool:
    return lo <= value <= hi


def validate_flashcrash2010(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Score core metrics against the ``analysis-bases.md §6`` bands.

    Also runs the shared ``validate_flash_crash`` from
    ``masim.evaluation.finance.validation`` so we retain compatibility with
    the family-wide validation surface.
    """
    checks: Dict[str, Dict[str, Any]] = {}

    mdd = metrics["max_drawdown"]
    checks["max_drawdown"] = {
        "value": mdd,
        "target": "0.05 – 0.12",
        "passed": _in_range(mdd, 0.05, 0.12),
    }
    dcr = metrics["depth_collapse_ratio"]
    checks["depth_collapse_ratio"] = {
        "value": dcr,
        "target": "0.05 – 0.20",
        "passed": _in_range(dcr, 0.05, 0.20),
    }
    swf = metrics["spread_widening_factor"]
    checks["spread_widening_factor"] = {
        "value": swf,
        "target": "5 – 50",
        "passed": _in_range(swf, 5.0, 50.0),
    }
    hwr = metrics["hft_withdrawal_rounds"]
    checks["hft_withdrawal_rounds"] = {
        "value": hwr,
        "target": "5 – 20",
        "passed": _in_range(hwr, 5, 20),
    }
    waves = metrics["cascade_wave_count"]
    checks["cascade_wave_count"] = {
        "value": waves,
        "target": "2 – 5",
        "passed": _in_range(waves, 2, 5),
    }
    rec = metrics["recovery_time"]
    checks["recovery_time"] = {
        "value": rec,
        "target": "10 – 25",
        "passed": rec >= 0 and _in_range(rec, 10, 25),
    }

    passed = sum(1 for c in checks.values() if c["passed"])
    total = len(checks)
    score = passed / total if total else 0.0

    # Cross-check against the family-wide FlashCrash validator
    total_rounds = metrics["total_rounds"]
    crash_duration = max(0, metrics["trough_round"] - metrics["peak_round"])
    recovery_detected = rec >= 0
    finance_val = validate_flash_crash(
        max_drawdown=metrics["max_drawdown_pct"],
        crash_duration=crash_duration,
        recovery_detected=recovery_detected,
        total_rounds=total_rounds,
    ).to_dict()

    return {
        "checks": checks,
        "passed_count": passed,
        "total_checks": total,
        "score": score,
        "finance_validation": finance_val,
        "interpretation": _interpret_validation(checks, score),
    }


def _interpret_validation(checks: Dict[str, Dict[str, Any]], score: float) -> str:
    """Human-readable one-liner summarising validation status."""
    failed = [name for name, c in checks.items() if not c["passed"]]
    if score == 1.0:
        return "All FlashCrash2010 §6 targets met — full flash-crash profile reproduced."
    if score >= 0.5:
        return f"Partial reproduction (score={score:.0%}). Off-target: {', '.join(failed)}."
    return (
        f"FlashCrash2010 profile NOT reproduced (score={score:.0%}). "
        f"Off-target: {', '.join(failed)}."
    )


# ===========================================================================
# Visualisations
# ===========================================================================


_PHASE_COLORS = {
    "Normal": "#D5E8D4",
    "Trigger": "#FFF2CC",
    "Cascade": "#F8CECC",
    "Trough": "#E1D5E7",
    "Recovery": "#DAE8FC",
}


def _phase_bands(metrics: Dict[str, Any], total_rounds: int) -> List[Tuple[str, int, int]]:
    """Approximate phase boundaries used by ``fig2_phase_shading``.

    Uses the typical rounds table from ``analysis-bases.md §4`` while
    snapping ``Cascade``/``Trough`` to the detected peak/trough indices
    when available so the shading matches the actual simulation trace.
    """
    peak = metrics.get("peak_round", 0)
    trough = metrics.get("trough_round", total_rounds - 1)
    normal_end = max(min(10, peak), 1)
    trigger_end = max(normal_end + 1, min(peak, normal_end + 5))
    cascade_end = max(trigger_end + 1, trough)
    trough_end = min(total_rounds - 1, cascade_end + 3)
    return [
        ("Normal", 0, normal_end),
        ("Trigger", normal_end, trigger_end),
        ("Cascade", trigger_end, cascade_end),
        ("Trough", cascade_end, trough_end),
        ("Recovery", trough_end, total_rounds - 1),
    ]


def plot_fig1_price_dynamics(data: Dict[str, Any], output_dir: str) -> None:
    """4-panel: price+fundamental / depth / spread / volume."""
    rounds = list(range(len(data["price_history"])))
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))

    ax = axes[0, 0]
    ax.plot(rounds, data["price_history"], color="#2E86AB", lw=1.5, label="Price")
    ax.axhline(data["fundamental"], color="#E63946", ls="--", lw=1, label="Fundamental")
    ax.set_title("Price vs Fundamental")
    ax.set_xlabel("Round")
    ax.set_ylabel("Price")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.plot(rounds, data["depth_history"], color="#8D5A99", lw=1.5)
    ax.axhline(data["base_depth"], color="#264653", ls="--", lw=1, label="base_depth")
    ax.set_title("Order-Book Depth")
    ax.set_xlabel("Round")
    ax.set_ylabel("Depth")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)

    ax = axes[1, 0]
    ax.plot(rounds, data["spread_history"], color="#E76F51", lw=1.5)
    ax.axhline(
        data["normal_spread"], color="#264653", ls="--", lw=1, label="normal_spread"
    )
    ax.set_title("Bid–Ask Spread")
    ax.set_xlabel("Round")
    ax.set_ylabel("Spread")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)

    ax = axes[1, 1]
    ax.bar(rounds, data["volume_history"], color="#2A9D8F", alpha=0.7)
    ax.set_title("Aggregate Volume")
    ax.set_xlabel("Round")
    ax.set_ylabel("Volume")
    ax.grid(alpha=0.3)

    fig.suptitle("Fig 1 — Price/Depth/Spread/Volume Dynamics", fontsize=13)
    fig.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig1_price_dynamics.png"))


def plot_fig2_phase_shading(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Price series with Normal/Trigger/Cascade/Trough/Recovery phase bands."""
    rounds = list(range(len(data["price_history"])))
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(rounds, data["price_history"], color="#1D3557", lw=1.6, zorder=5)
    ax.axhline(data["fundamental"], color="#E63946", ls="--", lw=1, label="Fundamental")

    for label, lo, hi in _phase_bands(metrics, len(rounds)):
        if hi <= lo:
            continue
        ax.axvspan(lo, hi, color=_PHASE_COLORS.get(label, "#EEEEEE"), alpha=0.5, label=label)

    handles, labels = ax.get_legend_handles_labels()
    seen = set()
    unique = [(h, l) for h, l in zip(handles, labels) if not (l in seen or seen.add(l))]
    ax.legend(*zip(*unique), loc="best", fontsize=9)
    ax.set_title("Fig 2 — Price with Phase Shading (analysis-bases §4)")
    ax.set_xlabel("Round")
    ax.set_ylabel("Price")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig2_phase_shading.png"))


def plot_fig3_drawdown(data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str) -> None:
    """Running peak-to-trough drawdown curve."""
    price = np.asarray(data["price_history"], dtype=float)
    if len(price) == 0:
        return
    running_max = np.maximum.accumulate(price)
    dd = (price - running_max) / np.where(running_max > 0, running_max, 1.0)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(range(len(dd)), dd * 100.0, 0, color="#E63946", alpha=0.4)
    ax.plot(dd * 100.0, color="#7A1F2B", lw=1.4)
    ax.axhline(0, color="black", lw=0.6)
    ax.axvline(
        metrics["trough_round"], color="#264653", ls=":", lw=1, label="trough"
    )
    ax.set_title(
        f"Fig 3 — Running Drawdown (max_drawdown={metrics['max_drawdown']:.2%})"
    )
    ax.set_xlabel("Round")
    ax.set_ylabel("Drawdown (%)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig3_drawdown.png"))


def plot_fig4_depth_collapse(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Depth vs base_depth ratio; annotate the collapse minimum."""
    depth = np.asarray(data["depth_history"], dtype=float)
    base = max(data["base_depth"], 1e-9)
    ratio = depth / base
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(ratio, color="#8D5A99", lw=1.5)
    ax.axhline(1.0, color="#264653", ls="--", lw=1, label="base_depth")
    ax.axhline(
        metrics["depth_collapse_ratio"],
        color="#E63946",
        ls=":",
        lw=1,
        label=f"min ratio = {metrics['depth_collapse_ratio']:.3f}",
    )
    min_idx = int(np.argmin(ratio)) if len(ratio) else 0
    if len(ratio):
        ax.annotate(
            f"collapse @ round {min_idx}\nratio={ratio[min_idx]:.3f}",
            xy=(min_idx, ratio[min_idx]),
            xytext=(min_idx + max(len(ratio) // 20, 1), ratio[min_idx] + 0.2),
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#333333"),
        )
    ax.set_title("Fig 4 — Depth Collapse (depth / base_depth)")
    ax.set_xlabel("Round")
    ax.set_ylabel("Ratio")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig4_depth_collapse.png"))


def plot_fig5_spread_widening(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Spread series with baseline; annotate max widening factor."""
    spread = np.asarray(data["spread_history"], dtype=float)
    normal = max(data["normal_spread"], 1e-8)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(spread, color="#E76F51", lw=1.5, label="spread")
    ax.axhline(normal, color="#264653", ls="--", lw=1, label="normal_spread")
    if len(spread):
        max_idx = int(np.argmax(spread))
        ax.annotate(
            f"max = {spread[max_idx]:.4f}\nfactor = {metrics['spread_widening_factor']:.1f}×",
            xy=(max_idx, spread[max_idx]),
            xytext=(max_idx + max(len(spread) // 20, 1), spread[max_idx]),
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#333333"),
        )
    ax.set_title("Fig 5 — Spread Widening")
    ax.set_xlabel("Round")
    ax.set_ylabel("Spread")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig5_spread_widening.png"))


def plot_fig6_hft_withdrawal(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """HFT participation bar per round + total withdrawal-round count."""
    hft_qty = [
        sum(abs(o.get("quantity", 0)) for o in round_orders)
        for round_orders in data["hft_orders_by_round"]
    ]
    withdrawn = [1 if q == 0 else 0 for q in hft_qty]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    ax1.bar(range(len(hft_qty)), hft_qty, color="#2E86AB", alpha=0.8)
    ax1.set_title(
        f"Fig 6 — HFT Participation "
        f"(withdrawal_rounds = {metrics['hft_withdrawal_rounds']})"
    )
    ax1.set_ylabel("Total |HFT Qty|")
    ax1.grid(alpha=0.3)

    ax2.bar(range(len(withdrawn)), withdrawn, color="#E63946", alpha=0.8)
    ax2.set_ylabel("Withdrawn (1=yes)")
    ax2.set_xlabel("Round")
    ax2.set_ylim(-0.05, 1.15)
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig6_hft_withdrawal.png"))


def plot_fig7_stop_loss_cascade(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Stop-loss volume per round; mark cascade rounds; count waves."""
    volumes = [
        sum(
            abs(o.get("quantity", 0))
            for o in round_orders
            if o.get("agent_type") == "stoploss" and o.get("quantity", 0) < 0
        )
        for round_orders in data["stoploss_orders_by_round"]
    ]
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(len(volumes)), volumes, color="#7A1F2B", alpha=0.8)
    for r in metrics.get("cascade_trigger_rounds", []):
        ax.axvline(r, color="#F4A261", ls=":", lw=1, alpha=0.7)
    ax.set_title(
        f"Fig 7 — Stop-Loss Cascade "
        f"(waves={metrics['cascade_wave_count']}, "
        f"triggers={len(metrics.get('cascade_trigger_rounds', []))})"
    )
    ax.set_xlabel("Round")
    ax.set_ylabel("Stop-Loss Sell Volume")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig7_stop_loss_cascade.png"))


def plot_fig8_recovery(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Post-trough price with fundamental ±2 % recovery band."""
    price = np.asarray(data["price_history"], dtype=float)
    fund = data["fundamental"]
    trough = max(0, min(metrics["trough_round"], len(price) - 1))
    xs = np.arange(trough, len(price))
    if len(xs) == 0:
        return
    ys = price[trough:]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(xs, ys, color="#1D3557", lw=1.6, label="Post-trough price")
    ax.axhline(fund, color="#E63946", ls="--", lw=1, label="Fundamental")
    ax.fill_between(
        xs,
        fund * 0.98,
        fund * 1.02,
        color="#DAE8FC",
        alpha=0.6,
        label="Recovery band (±2%)",
    )
    if metrics["recovery_time"] >= 0:
        rr = trough + metrics["recovery_time"]
        ax.axvline(rr, color="#2A9D8F", ls=":", lw=1.2, label=f"Recovered @ R{rr}")
    ax.set_title(
        f"Fig 8 — Recovery (recovery_time = {metrics['recovery_time']} rounds)"
    )
    ax.set_xlabel("Round")
    ax.set_ylabel("Price")
    ax.legend(loc="best", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig8_recovery.png"))


def create_visualizations(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Emit all eight analysis figures for the FlashCrash2010 scenario."""
    os.makedirs(output_dir, exist_ok=True)
    plot_fig1_price_dynamics(data, output_dir)
    plot_fig2_phase_shading(data, metrics, output_dir)
    plot_fig3_drawdown(data, metrics, output_dir)
    plot_fig4_depth_collapse(data, metrics, output_dir)
    plot_fig5_spread_widening(data, metrics, output_dir)
    plot_fig6_hft_withdrawal(data, metrics, output_dir)
    plot_fig7_stop_loss_cascade(data, metrics, output_dir)
    plot_fig8_recovery(data, metrics, output_dir)


# ===========================================================================
# Pipeline
# ===========================================================================


def analyze_flash_crash(config_path: str) -> Dict[str, Any]:
    """Run the full FlashCrash2010 Rule analysis pipeline.

    Loads the config, replays records, computes metrics, produces figures,
    writes ``summary.json`` (metrics + validation) and returns the summary.
    """
    config = load_config(config_path)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = load_simulation_data(config, results)
    metrics = calculate_metrics(data, config)
    validation = validate_flashcrash2010(metrics)

    create_visualizations(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)

    summary: Dict[str, Any] = {
        "scenario": "FlashCrash2010",
        "variant": "Rule",
        "config_path": config_path,
        **metrics,
        "validation": validation,
    }

    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    return summary


def main() -> Dict[str, Any]:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze FlashCrash2010 Rule simulation"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash2010/Rule/simulation.yml",
    )
    args = parser.parse_args()

    print("=" * 72)
    print("FlashCrash2010 Rule Analysis")
    print("=" * 72)
    summary = analyze_flash_crash(args.config)
    print(f"max_drawdown          = {summary['max_drawdown']:.4f}")
    print(f"depth_collapse_ratio  = {summary['depth_collapse_ratio']:.4f}")
    print(f"spread_widening_factor= {summary['spread_widening_factor']:.2f}×")
    print(f"hft_withdrawal_rounds = {summary['hft_withdrawal_rounds']}")
    print(f"cascade_wave_count    = {summary['cascade_wave_count']}")
    print(f"recovery_time         = {summary['recovery_time']}")
    print()
    print(summary["validation"]["interpretation"])
    return summary


__all__ = [
    # Metric functions (analysis-bases §2)
    "max_drawdown",
    "depth_collapse_ratio",
    "spread_widening_factor",
    "hft_withdrawal_rounds",
    "cascade_trigger_rounds",
    "recovery_time",
    "count_cascade_waves",
    # Pipeline
    "load_simulation_data",
    "calculate_metrics",
    "validate_flashcrash2010",
    "create_visualizations",
    "analyze_flash_crash",
    # Standard outputs
    "STANDARD_OUTPUT_FILES",
    "_write_standard_named_outputs",
    # Plot helpers
    "plot_fig1_price_dynamics",
    "plot_fig2_phase_shading",
    "plot_fig3_drawdown",
    "plot_fig4_depth_collapse",
    "plot_fig5_spread_widening",
    "plot_fig6_hft_withdrawal",
    "plot_fig7_stop_loss_cascade",
    "plot_fig8_recovery",
    "main",
]


if __name__ == "__main__":
    main()
