#!/usr/bin/env python
"""Flash Crash Rule Simulation Analysis.

Implements the six scenario metrics catalogued in
``examples/FlashCrash/analysis-bases.md §2`` and produces the eight
diagnostic PNGs required by ``analysis-bases.md §7``, in addition to the
standardized artefacts required by the ``implement-simulation-skill``
output contract (``summary.json`` + ``00_investor_bids.png``,
``01_flashcrash_dynamics.png``, ``02_flashcrash_analysis.png``,
``03_summary.png``).

Metrics (all from ``analysis-bases.md §2``):

    - ``crash_depth(price_history, fundamental)``
    - ``liquidity_vacuum_duration(liquidity_history, low_threshold=50.0)``
    - ``stop_loss_cascade_volume(orders_history)``
    - ``recovery_speed(price_history, trough_round, fundamental,
        recovery_threshold=0.02)``
    - ``liquidity_provider_withdrawal_fraction(provides_liquidity_history,
        crash_start, crash_end)``
    - ``price_amplification_ratio(observed_max_drop, baseline_max_drop)``

Reusable time-series primitives are imported from ``masim.evaluation.finance``
so scenario code owns only scenario-specific orchestration
(see ``masim/skills/implement-simulation-skill/09-step5-to-10-review.md §7.1``).

Usage:
    python examples/FlashCrash/Rule/analysis.py \
        -c configs/FlashCrash/Rule/simulation.yml
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.data_loader import (
    load_data as _load_shared_market_data,
    market_players,
)
from masim.evaluation.finance import (
    calculate_max_drawdown,
    calculate_returns,
    calculate_rolling_volatility,
    save_figure,
)
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary


# ---------------------------------------------------------------------------
# Constants (§4 phase table + §6 target ranges)
# ---------------------------------------------------------------------------

PHASE_COLORS = {
    "Normal": "#a8dadc",
    "Trigger": "#f4a261",
    "Cascade": "#e76f51",
    "Trough": "#9d0208",
    "Recovery": "#2a9d8f",
}

STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_flashcrash_dynamics.png",
    "02_flashcrash_analysis.png",
    "03_summary.png",
)

# Agent-type keywords used for classification. We prefer ``payload["agent_type"]``
# when present, then fall back to strategy substring matching against the
# ``__class__.__name__`` recorded by every FlashCrash investor.
_STOPLOSS_KEYS = ("stoploss", "stop_loss", "stop-loss")
_HFT_KEYS = ("highfrequency", "hft")
_FUNDAMENTAL_KEYS = ("fundamental",)
_MARKETMAKER_KEYS = ("marketmaker", "market_maker", "market-maker", "flashmarketmaker")
_ALGO_KEYS = ("algorithmic", "algo")
_NOISE_KEYS = ("retail", "noise")


def _classify_agent_type(payload: Dict[str, Any]) -> str:
    """Return coarse agent-type label from a payload.

    Preference order matches the analysis-bases.md §2 contract for
    ``stop_loss_cascade_volume``: ``agent_type`` field first, then
    ``strategy`` (class name).
    """
    label = str(payload.get("agent_type") or payload.get("strategy") or "").lower()
    if any(key in label for key in _STOPLOSS_KEYS):
        return "stoploss"
    if any(key in label for key in _HFT_KEYS):
        return "hft"
    if any(key in label for key in _FUNDAMENTAL_KEYS):
        return "fundamental"
    if any(key in label for key in _MARKETMAKER_KEYS):
        return "marketmaker"
    if any(key in label for key in _ALGO_KEYS):
        return "algorithmic"
    if any(key in label for key in _NOISE_KEYS):
        return "noise"
    return "other"


# ---------------------------------------------------------------------------
# Metric functions (analysis-bases.md §2)
# ---------------------------------------------------------------------------


def crash_depth(price_history: List[float], fundamental: float) -> float:
    """Max downward deviation below ``fundamental`` as a fraction.

    Returns a non-negative float — ``0.09`` means the trough fell 9%
    below the fundamental value. Reference: analysis-bases.md §2.
    """
    if not price_history or fundamental == 0:
        return 0.0
    deviations = [(float(p) - fundamental) / fundamental for p in price_history]
    return abs(min(deviations))


def liquidity_vacuum_duration(
    liquidity_history: List[float], low_threshold: float = 50.0
) -> int:
    """Number of rounds with ``total_liquidity <= low_threshold``.

    Measures how long the market operates in the amplified-impact regime
    (analysis-bases.md §2).
    """
    return int(sum(1 for liq in liquidity_history if float(liq) <= low_threshold))


def stop_loss_cascade_volume(orders_history: List[List[Dict[str, Any]]]) -> float:
    """Total sell volume from StopLossTrader agents across all rounds.

    Uses ``agent_type == 'stoploss'`` when present, otherwise falls back
    to ``strategy`` (class-name substring). Only counts sell orders
    (``quantity < 0``). Reference: analysis-bases.md §2.
    """
    total = 0.0
    for round_orders in orders_history:
        for order in round_orders:
            if _classify_agent_type(order) != "stoploss":
                continue
            qty = float(order.get("quantity", 0.0))
            if qty < 0:
                total += abs(qty)
    return float(total)


def recovery_speed(
    price_history: List[float],
    trough_round: int,
    fundamental: float,
    recovery_threshold: float = 0.02,
) -> int:
    """Rounds from ``trough_round`` until price returns to within
    ``recovery_threshold`` of ``fundamental``.

    ``trough_round`` is 0-indexed into ``price_history``. Returns -1
    if the run ends before recovery (analysis-bases.md §2).
    """
    if fundamental == 0 or not price_history:
        return -1
    if trough_round < 0 or trough_round >= len(price_history):
        return -1
    for i in range(trough_round, len(price_history)):
        if abs(price_history[i] - fundamental) / fundamental <= recovery_threshold:
            return i - trough_round
    return -1


def liquidity_provider_withdrawal_fraction(
    provides_liquidity_history: List[Dict[str, bool]],
    crash_start: int,
    crash_end: int,
) -> float:
    """Fraction of liquidity-eligible agents WITHDRAWN during the crash
    window ``[crash_start, crash_end)`` (analysis-bases.md §2).

    ``provides_liquidity_history[r]`` is a mapping of agent-id → bool.
    """
    if crash_start < 0:
        crash_start = 0
    crash_end = min(crash_end, len(provides_liquidity_history))
    if crash_start >= crash_end:
        return 0.0
    window = provides_liquidity_history[crash_start:crash_end]
    if not window:
        return 0.0
    total_withdrawn = sum(sum(1 for v in r.values() if not v) for r in window)
    denominator = sum(len(r) for r in window)
    if denominator <= 0:
        return 0.0
    return float(total_withdrawn / denominator)


def price_amplification_ratio(
    observed_max_drop: float, baseline_max_drop: float
) -> float:
    """Ratio of observed crash depth to a rolling baseline crash depth.

    Values > 1 indicate liquidity-driven amplification
    (analysis-bases.md §2).
    """
    return float(observed_max_drop / max(baseline_max_drop, 1e-6))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def _extract_extras(config: Dict[str, Any], role: str) -> Dict[str, Any]:
    """Return the ``extras`` block for the first player with a matching role."""
    for entry in config["players"].values():
        pcfg = entry.get("config", {})
        if pcfg.get("role") == role:
            return pcfg.get("extras", {})
    return {}


def _series_from_history(hist_dict: Dict[int, float]) -> List[float]:
    return [float(hist_dict[r]) for r in sorted(hist_dict)]


def _coordinator_series(
    coord_player: Any, name: str
) -> Dict[int, float]:
    """Read a batch store from the coordinator, indexed 0..N-1 → 1..N."""
    if name not in coord_player.batch_store_names:
        return {}
    values = coord_player.batch(name).all()
    return {i + 1: float(v) for i, v in enumerate(values)}


def _coordinator_from_payloads(
    coord_player: Any, field: str
) -> Dict[int, float]:
    """Recover a scalar field from the coordinator turn payloads."""
    out: Dict[int, float] = {}
    for round_num, payload in coord_player.turns.payloads().items():
        md = payload.get("market_data") if isinstance(payload, dict) else None
        source = md if isinstance(md, dict) else payload
        if isinstance(source, dict) and field in source:
            out[round_num] = float(source[field])
    return out


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract all data needed by ``calculate_metrics`` and plotting.

    Returns
    -------
    dict with keys:
        rounds                   : sorted list of round numbers
        prices                   : List[float] aligned with ``rounds``
        fundamental              : float — from coordinator config extras
        liquidity                : List[float] aligned with ``rounds``
        volume                   : List[float] aligned with ``rounds``
        net_demand               : List[float] aligned with ``rounds``
        orders_history           : List[List[dict]] — orders per round
        provides_liquidity_history : List[Dict[str, bool]] — per round
        investor_quantities      : {pid: {round: qty}}
        investor_bids            : {pid: {round: bid_price}}
        investor_payloads        : {pid: {round: payload}}
        market_prices            : {round: price}   (dict form for plots)
        fundamentals             : {round: fundamental}
        volumes                  : {round: volume}
        agent_ids_by_type        : {agent_type: [pid, ...]}
    """
    results = load_results(config)

    coordinators = market_players(results)
    if not coordinators:
        raise ValueError("No coordinator player found in results")
    coord_player = next(iter(coordinators.values()))

    # Fundamental value from config (Rule variant persists this in extras).
    market_extras = _extract_extras(config, "coordinator")
    fundamental = float(market_extras.get("fundamental_value", 100.0))

    # Coordinator batch stores.
    market_prices = _coordinator_series(coord_player, "price")
    volumes = _coordinator_series(coord_player, "volume")
    liquidity = _coordinator_series(coord_player, "liquidity")

    # Fill from turn payloads if any store missing.
    if not market_prices:
        market_prices = _coordinator_from_payloads(coord_player, "price")
    if not volumes:
        volumes = _coordinator_from_payloads(coord_player, "volume")
    if not liquidity:
        liquidity = _coordinator_from_payloads(coord_player, "liquidity")
    net_demand = _coordinator_from_payloads(coord_player, "net_demand")
    fundamentals = _coordinator_from_payloads(coord_player, "fundamental")

    if not market_prices:
        raise ValueError("No market price data recorded")

    # Ensure fundamentals populated.
    if not fundamentals:
        fundamentals = {r: fundamental for r in market_prices}

    # Investor payloads / order reconstruction.
    investor_quantities: Dict[str, Dict[int, float]] = {}
    investor_bids: Dict[str, Dict[int, float]] = {}
    investor_payloads: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for pid, player in results.players_by_role("player").items():
        payloads = player.turns.payloads()
        if payloads:
            investor_payloads[pid] = payloads
        qty = player.turns.field("quantity")
        if qty:
            investor_quantities[pid] = qty
        bid = player.turns.field("bid_price")
        if bid:
            investor_bids[pid] = bid

    rounds = sorted(market_prices)

    # Reconstruct orders_history[round-1] = list of investor payloads for that round.
    orders_history: List[List[Dict[str, Any]]] = []
    provides_liquidity_history: List[Dict[str, bool]] = []
    for r in rounds:
        round_orders: List[Dict[str, Any]] = []
        provides_round: Dict[str, bool] = {}
        for pid, payloads in investor_payloads.items():
            payload = payloads.get(r)
            if not isinstance(payload, dict):
                continue
            round_orders.append(payload)
            # Only track liquidity-eligible agents (HFT + MarketMaker + Fundamental
            # produce liquidity records; RuleLLM/LLM/Rag investors may omit the
            # field entirely — treat missing as "not liquidity provider").
            if "provides_liquidity" in payload:
                provides_round[pid] = bool(payload["provides_liquidity"])
        orders_history.append(round_orders)
        provides_liquidity_history.append(provides_round)

    # Group investors by coarse agent type for plotting.
    agent_ids_by_type: Dict[str, List[str]] = {}
    for pid, payloads in investor_payloads.items():
        # Use the first payload seen to classify.
        first = next(iter(payloads.values())) if payloads else {}
        agent_type = _classify_agent_type(first if isinstance(first, dict) else {})
        agent_ids_by_type.setdefault(agent_type, []).append(pid)

    prices_list = [market_prices[r] for r in rounds]
    liquidity_list = [float(liquidity.get(r, 0.0)) for r in rounds]
    volume_list = [float(volumes.get(r, 0.0)) for r in rounds]
    net_demand_list = [float(net_demand.get(r, 0.0)) for r in rounds]

    return {
        "rounds": rounds,
        "prices": prices_list,
        "fundamental": fundamental,
        "liquidity": liquidity_list,
        "volume": volume_list,
        "net_demand": net_demand_list,
        "orders_history": orders_history,
        "provides_liquidity_history": provides_liquidity_history,
        "investor_quantities": investor_quantities,
        "investor_bids": investor_bids,
        "investor_payloads": investor_payloads,
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "volumes": volumes,
        "agent_ids_by_type": agent_ids_by_type,
    }


# ---------------------------------------------------------------------------
# Metric orchestration
# ---------------------------------------------------------------------------


def _detect_crash_window(
    prices: List[float], fundamental: float
) -> Tuple[int, int, int]:
    """Return ``(crash_start, trough_round, crash_end_exclusive)``.

    Uses ``calculate_max_drawdown`` to find the peak → trough interval and
    extends ``crash_end`` to include the recovery zone (bounded by the run).
    All indices are 0-based into ``prices``.
    """
    if len(prices) < 2:
        return 0, 0, len(prices)
    _, peak_idx, trough_idx = calculate_max_drawdown(prices)
    if trough_idx <= peak_idx:
        trough_idx = int(np.argmin(prices))
        peak_idx = max(0, trough_idx - 1)
    # Extend crash_end to the first round that recovers within ±2% of
    # fundamental after the trough, or the end of the run.
    recovery_offset = recovery_speed(prices, trough_idx, fundamental, 0.02)
    if recovery_offset >= 0:
        crash_end = min(len(prices), trough_idx + recovery_offset + 1)
    else:
        crash_end = len(prices)
    return peak_idx, trough_idx, crash_end


def _rolling_baseline_max_drop(
    prices: List[float], fundamental: float, window: int = 10
) -> float:
    """Baseline crash depth measured on the first ``window`` rounds.

    Rationale: analysis-bases.md §2 baseline is the crash depth in a
    healthy-liquidity regime. The first 10 rounds correspond to the
    "Normal" phase from analysis-bases.md §4, so their max deviation
    represents baseline noise-driven pullbacks. Falls back to 1% of
    fundamental if the window is degenerate.
    """
    baseline_slice = prices[: max(2, window)]
    baseline = crash_depth(baseline_slice, fundamental)
    if baseline <= 0:
        baseline = 0.01
    return float(baseline)


def calculate_metrics(
    data: Dict[str, Any], config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Compute all six scenario metrics + generic price/return summary.

    Returns a dict ready to be JSON-serialised.
    """
    prices = data["prices"]
    fundamental = data["fundamental"]
    liquidity_list = data["liquidity"]
    orders_history = data["orders_history"]
    provides_history = data["provides_liquidity_history"]

    if not prices:
        raise ValueError("Cannot compute metrics: empty price history")

    # Crash window detection.
    peak_idx, trough_idx, crash_end = _detect_crash_window(prices, fundamental)

    # Six scenario metrics.
    depth = crash_depth(prices, fundamental)
    vacuum = liquidity_vacuum_duration(liquidity_list, low_threshold=50.0)
    cascade_volume = stop_loss_cascade_volume(orders_history)
    recovery = recovery_speed(prices, trough_idx, fundamental, recovery_threshold=0.02)
    withdrawal_fraction = liquidity_provider_withdrawal_fraction(
        provides_history, crash_start=peak_idx, crash_end=crash_end
    )
    baseline_drop = _rolling_baseline_max_drop(prices, fundamental, window=10)
    amp_ratio = price_amplification_ratio(depth, baseline_drop)

    # Generic price/return metrics via masim.evaluation.finance.
    prices_arr = np.asarray(prices, dtype=float)
    returns = calculate_returns(prices_arr.tolist())
    if isinstance(returns, np.ndarray) and returns.size:
        volatility_pct = float(np.std(returns) * 100)
        mean_return_pct = float(np.mean(returns) * 100)
        max_return_pct = float(np.max(returns) * 100)
        min_return_pct = float(np.min(returns) * 100)
    else:
        volatility_pct = mean_return_pct = 0.0
        max_return_pct = min_return_pct = 0.0

    max_dd, _, _ = calculate_max_drawdown(prices)
    deviations = [(p - fundamental) / fundamental for p in prices]

    scenario_metrics = {
        "crash_depth": float(depth),
        "liquidity_vacuum_duration": int(vacuum),
        "stop_loss_cascade_volume": float(cascade_volume),
        "recovery_speed": int(recovery),
        "liquidity_provider_withdrawal_fraction": float(withdrawal_fraction),
        "price_amplification_ratio": float(amp_ratio),
        "baseline_max_drop": float(baseline_drop),
        "peak_round": int(peak_idx + 1),
        "trough_round": int(trough_idx + 1),
        "crash_end_round": int(crash_end),
    }

    price_metrics = {
        "initial": float(prices_arr[0]),
        "final": float(prices_arr[-1]),
        "min": float(prices_arr.min()),
        "max": float(prices_arr.max()),
        "mean": float(prices_arr.mean()),
        "total_rounds": int(len(prices_arr)),
    }
    return_metrics = {
        "mean_return_pct": mean_return_pct,
        "volatility_pct": volatility_pct,
        "max_return_pct": max_return_pct,
        "min_return_pct": min_return_pct,
        "max_drawdown_pct": float(max_dd),
    }
    deviation_metrics = {
        "max_abs_deviation_pct": float(max(abs(d) for d in deviations) * 100)
        if deviations
        else 0.0,
        "final_deviation_pct": float(deviations[-1] * 100) if deviations else 0.0,
    }

    return {
        "scenario_metrics": scenario_metrics,
        "price_metrics": price_metrics,
        "return_metrics": return_metrics,
        "deviation_metrics": deviation_metrics,
    }


# ---------------------------------------------------------------------------
# Validation (analysis-bases.md §6 target ranges)
# ---------------------------------------------------------------------------


def _score_range(value: float, lower: float, upper: float) -> float:
    """Score a scalar against a bounded acceptable interval."""
    if value <= 0 and lower > 0:
        return 0.0
    if lower <= value <= upper:
        return 1.0
    if value < lower:
        return max(0.0, value / lower) if lower > 0 else 0.0
    return max(0.0, 1.0 - (value - upper) / max(upper, 1.0))


def validate_flash_crash(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Validate scenario metrics against analysis-bases.md §6 target ranges.

    Returns a dict with per-criterion scores and an aggregate score/verdict.
    """
    sm = metrics["scenario_metrics"]

    depth = sm["crash_depth"]
    vacuum = sm["liquidity_vacuum_duration"]
    cascade = sm["stop_loss_cascade_volume"]
    recovery = sm["recovery_speed"]
    withdrawal = sm["liquidity_provider_withdrawal_fraction"]
    amp_ratio = sm["price_amplification_ratio"]

    criteria = {
        "crash_depth": {
            "value": round(depth, 4),
            "target": "0.05–0.12 (analysis-bases.md §6)",
            "score": round(_score_range(depth, 0.05, 0.12), 3),
        },
        "liquidity_vacuum_duration": {
            "value": int(vacuum),
            "target": "5–20 rounds",
            "score": round(_score_range(float(vacuum), 5.0, 20.0), 3),
        },
        "stop_loss_cascade_volume": {
            "value": round(cascade, 2),
            "target": "500–3000 shares",
            "score": round(_score_range(cascade, 500.0, 3000.0), 3),
        },
        "recovery_speed": {
            "value": int(recovery),
            "target": "10–30 rounds (positive)",
            "score": round(
                _score_range(float(recovery), 10.0, 30.0) if recovery >= 0 else 0.0,
                3,
            ),
        },
        "liquidity_provider_withdrawal_fraction": {
            "value": round(withdrawal, 4),
            "target": "0.6–1.0 during crash window",
            "score": round(_score_range(withdrawal, 0.6, 1.0), 3),
        },
        "price_amplification_ratio": {
            "value": round(amp_ratio, 4),
            "target": "1.5–4.0",
            "score": round(_score_range(amp_ratio, 1.5, 4.0), 3),
        },
    }

    weights = {
        "crash_depth": 0.25,
        "liquidity_vacuum_duration": 0.15,
        "stop_loss_cascade_volume": 0.15,
        "recovery_speed": 0.15,
        "liquidity_provider_withdrawal_fraction": 0.15,
        "price_amplification_ratio": 0.15,
    }
    aggregate = sum(criteria[k]["score"] * w for k, w in weights.items())
    is_valid = aggregate >= 0.5

    interpretation_lines = [
        "=== FLASH CRASH VALIDATION: "
        f"{'VALID' if is_valid else 'INVALID'} ===",
        f"Aggregate Score: {aggregate:.1%}",
        "",
    ]
    for name, entry in criteria.items():
        interpretation_lines.append(
            f"  {name:42s} value={entry['value']} target={entry['target']} "
            f"score={entry['score']}"
        )
    interpretation = "\n".join(interpretation_lines)

    return {
        "is_valid": bool(is_valid),
        "score": round(aggregate, 4),
        "criteria": criteria,
        "interpretation": interpretation,
    }


# ---------------------------------------------------------------------------
# Visualization (8 diagnostic PNGs)
# ---------------------------------------------------------------------------


def _phase_ranges(metrics: Dict[str, Any], total_rounds: int) -> Dict[str, Tuple[int, int]]:
    """Derive phase ranges from detected crash window + §4 defaults.

    All ranges are 1-based (inclusive-lower, exclusive-upper) round
    numbers, matching the ``rounds`` axis on plots.
    """
    sm = metrics["scenario_metrics"]
    peak_round = sm["peak_round"]
    trough_round = sm["trough_round"]
    crash_end = sm["crash_end_round"]

    normal_end = max(1, min(peak_round, 11))
    trigger_end = max(normal_end + 1, min(peak_round + 1, 16))
    cascade_end = max(trigger_end + 1, trough_round)
    trough_end = min(total_rounds + 1, max(cascade_end + 1, trough_round + 5))
    recovery_end = max(trough_end + 1, crash_end + 1)
    recovery_end = min(total_rounds + 1, recovery_end)

    return {
        "Normal": (1, normal_end),
        "Trigger": (normal_end, trigger_end),
        "Cascade": (trigger_end, cascade_end),
        "Trough": (cascade_end, trough_end),
        "Recovery": (trough_end, recovery_end),
    }


def plot_fig1_price_liquidity_dynamics(
    data: Dict[str, Any], output_dir: str
) -> None:
    """Fig 1: 3-panel — price+fundamental / liquidity / volume."""
    rounds = data["rounds"]
    fundamental = data["fundamental"]

    fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    fig.suptitle("Fig 1: FlashCrash Price / Liquidity / Volume Dynamics",
                 fontsize=13, fontweight="bold")

    ax = axes[0]
    ax.plot(rounds, data["prices"], color="#d1495b", linewidth=1.6,
            label="Market Price")
    ax.axhline(fundamental, color="#00798c", linestyle="--", linewidth=1.2,
               label=f"Fundamental ({fundamental:g})")
    ax.set_ylabel("Price")
    ax.set_title("A. Price vs Fundamental")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(rounds, data["liquidity"], color="#3a86ff", linewidth=1.5)
    ax.axhline(50.0, color="#e63946", linestyle=":", linewidth=1.1,
               label="low_liquidity_threshold=50")
    ax.set_ylabel("Total Liquidity")
    ax.set_title("B. Aggregate Liquidity")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[2]
    ax.bar(rounds, data["volume"], color="#457b9d", alpha=0.85, width=0.9)
    ax.plot(rounds, data["net_demand"], color="#e76f51", linewidth=1.2,
            label="Net Demand")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Round")
    ax.set_ylabel("Volume / Net Demand")
    ax.set_title("C. Volume and Net Demand")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig1_price_liquidity_dynamics.png")
    save_figure(fig, path)
    plt.close(fig)


def plot_fig2_phase_overlay(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Fig 2: Price path with phase-band shading (§4)."""
    rounds = data["rounds"]
    prices = data["prices"]
    fundamental = data["fundamental"]
    phases = _phase_ranges(metrics, len(rounds))

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.suptitle("Fig 2: Phase Overlay — Normal → Trigger → Cascade → Trough → Recovery",
                 fontsize=13, fontweight="bold")

    for phase_name, (lo, hi) in phases.items():
        if hi <= lo:
            continue
        ax.axvspan(lo, hi, color=PHASE_COLORS[phase_name], alpha=0.25,
                   label=phase_name)

    ax.plot(rounds, prices, color="#000000", linewidth=1.8, label="Price")
    ax.axhline(fundamental, color="#00798c", linestyle="--", linewidth=1.1,
               label="Fundamental")

    sm = metrics["scenario_metrics"]
    ax.axvline(sm["peak_round"], color="#f4a261", linestyle=":", linewidth=1.1)
    ax.axvline(sm["trough_round"], color="#9d0208", linestyle=":", linewidth=1.1)

    ax.set_xlabel("Round")
    ax.set_ylabel("Price")
    handles, labels = ax.get_legend_handles_labels()
    dedup: Dict[str, Any] = {}
    for h, l in zip(handles, labels):
        dedup.setdefault(l, h)
    ax.legend(dedup.values(), dedup.keys(), fontsize=8, loc="lower left", ncol=3)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig2_phase_overlay.png")
    save_figure(fig, path)
    plt.close(fig)


def plot_fig3_crash_depth_analysis(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Fig 3: Deviation-from-fundamental with crash_depth annotation."""
    rounds = data["rounds"]
    prices = np.array(data["prices"], dtype=float)
    fundamental = data["fundamental"]
    deviations_pct = (prices - fundamental) / fundamental * 100

    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    fig.suptitle("Fig 3: Crash Depth Diagnostic", fontsize=13, fontweight="bold")

    sm = metrics["scenario_metrics"]
    depth_pct = sm["crash_depth"] * 100

    ax = axes[0]
    ax.plot(rounds, deviations_pct, color="#7b2cbf", linewidth=1.6)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axhline(-depth_pct, color="#e63946", linestyle="--", linewidth=1.2,
               label=f"crash_depth = {depth_pct:.2f}%")
    ax.fill_between(rounds, deviations_pct, 0, where=(deviations_pct < 0),
                    color="#e63946", alpha=0.15)
    ax.set_ylabel("Deviation (%)")
    ax.set_title("A. (Price − Fundamental) / Fundamental")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(rounds, prices, color="#d1495b", linewidth=1.6, label="Price")
    ax.axhline(fundamental, color="#00798c", linestyle="--", linewidth=1.1,
               label="Fundamental")
    ax.axvline(sm["trough_round"], color="#9d0208", linestyle=":",
               linewidth=1.1, label=f"Trough @ R{sm['trough_round']}")
    ax.set_xlabel("Round")
    ax.set_ylabel("Price")
    ax.set_title("B. Price Path with Trough Marker")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig3_crash_depth_analysis.png")
    save_figure(fig, path)
    plt.close(fig)


def plot_fig4_liquidity_vacuum(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Fig 4: Liquidity path with low_threshold and vacuum shading."""
    rounds = data["rounds"]
    liquidity = np.array(data["liquidity"], dtype=float)
    low_threshold = 50.0

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.suptitle("Fig 4: Liquidity Vacuum Detection", fontsize=13,
                 fontweight="bold")

    ax.plot(rounds, liquidity, color="#3a86ff", linewidth=1.6, label="Liquidity")
    ax.axhline(low_threshold, color="#e63946", linestyle="--", linewidth=1.2,
               label=f"low_threshold = {low_threshold:g}")
    below_mask = liquidity <= low_threshold
    ax.fill_between(rounds, liquidity, low_threshold, where=below_mask,
                    color="#e63946", alpha=0.20,
                    label="Vacuum window")

    sm = metrics["scenario_metrics"]
    ax.text(
        0.02, 0.95,
        f"liquidity_vacuum_duration = {sm['liquidity_vacuum_duration']} rounds",
        transform=ax.transAxes, fontsize=11,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="#ffe5e5", alpha=0.85),
    )
    ax.set_xlabel("Round")
    ax.set_ylabel("Total Liquidity")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig4_liquidity_vacuum.png")
    save_figure(fig, path)
    plt.close(fig)


def plot_fig5_stop_loss_cascade(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Fig 5: Stop-loss sell volume per round."""
    rounds = data["rounds"]
    sl_volume = []
    for round_orders in data["orders_history"]:
        vol = 0.0
        for o in round_orders:
            if _classify_agent_type(o) == "stoploss":
                q = float(o.get("quantity", 0.0))
                if q < 0:
                    vol += abs(q)
        sl_volume.append(vol)

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.suptitle("Fig 5: Stop-Loss Cascade Volume by Round", fontsize=13,
                 fontweight="bold")

    bars = ax.bar(rounds, sl_volume, color="#e63946", alpha=0.85, width=0.9,
                  label="Stop-Loss sell volume")
    ax.set_xlabel("Round")
    ax.set_ylabel("Absolute Sell Volume (shares)")

    sm = metrics["scenario_metrics"]
    ax.text(
        0.02, 0.95,
        f"total stop_loss_cascade_volume = {sm['stop_loss_cascade_volume']:.1f}",
        transform=ax.transAxes, fontsize=11,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="#ffe5e5", alpha=0.85),
    )
    ax.axvline(sm["peak_round"], color="#f4a261", linestyle=":", linewidth=1.1,
               label=f"Peak @ R{sm['peak_round']}")
    ax.axvline(sm["trough_round"], color="#9d0208", linestyle=":", linewidth=1.1,
               label=f"Trough @ R{sm['trough_round']}")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    _ = bars  # ensure reference retained for style consistency
    plt.tight_layout()
    path = os.path.join(output_dir, "fig5_stop_loss_cascade.png")
    save_figure(fig, path)
    plt.close(fig)


def plot_fig6_hft_withdrawal(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Fig 6: HFT (and MarketMaker) participation per round."""
    rounds = data["rounds"]
    provides_history = data["provides_liquidity_history"]

    hft_or_mm_ids = set(
        data["agent_ids_by_type"].get("hft", [])
        + data["agent_ids_by_type"].get("marketmaker", [])
        + data["agent_ids_by_type"].get("fundamental", [])
    )

    # Per-round fraction of liquidity providers still active.
    fractions_active: List[float] = []
    for round_provides in provides_history:
        eligible = [
            v for pid, v in round_provides.items() if pid in hft_or_mm_ids
        ]
        if not eligible:
            eligible = list(round_provides.values())
        fractions_active.append(
            float(sum(1 for v in eligible if v) / len(eligible))
            if eligible else 0.0
        )

    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)
    fig.suptitle("Fig 6: HFT / MarketMaker Withdrawal Dynamics", fontsize=13,
                 fontweight="bold")

    ax = axes[0]
    ax.plot(rounds, fractions_active, color="#2a9d8f", linewidth=1.6,
            label="Fraction actively providing liquidity")
    ax.axhline(1.0, color="#00798c", linestyle=":", linewidth=1.0)
    ax.set_ylabel("Fraction providing")
    ax.set_ylim(-0.05, 1.10)
    ax.set_title("A. Liquidity Provision Fraction Over Time")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    sm = metrics["scenario_metrics"]
    crash_start = sm["peak_round"]
    crash_end = sm["crash_end_round"]
    bars = ax.bar(
        ["Withdrawal Fraction (crash window)"],
        [sm["liquidity_provider_withdrawal_fraction"]],
        color="#e63946", alpha=0.85, width=0.5,
    )
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.02,
                f"{h:.3f}", ha="center", va="bottom", fontsize=11)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Withdrawal fraction")
    ax.set_title(
        f"B. Crash-Window Withdrawal Fraction (rounds {crash_start}..{crash_end - 1})"
    )
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(output_dir, "fig6_hft_withdrawal.png")
    save_figure(fig, path)
    plt.close(fig)


def plot_fig7_agent_contribution(
    data: Dict[str, Any], output_dir: str
) -> None:
    """Fig 7: Net volume per agent type."""
    agent_totals: Dict[str, float] = {}
    agent_signed: Dict[str, float] = {}
    for round_orders in data["orders_history"]:
        for o in round_orders:
            atype = _classify_agent_type(o)
            q = float(o.get("quantity", 0.0))
            agent_totals[atype] = agent_totals.get(atype, 0.0) + abs(q)
            agent_signed[atype] = agent_signed.get(atype, 0.0) + q

    types = sorted(agent_totals.keys())
    colors = {
        "hft": "#3a86ff",
        "marketmaker": "#06d6a0",
        "stoploss": "#e63946",
        "fundamental": "#2a9d8f",
        "algorithmic": "#f4a261",
        "noise": "#adb5bd",
        "other": "#8d99ae",
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Fig 7: Agent-Type Contribution to Order Flow", fontsize=13,
                 fontweight="bold")

    ax = axes[0]
    totals = [agent_totals[t] for t in types]
    bar_colors = [colors.get(t, "#7F8C8D") for t in types]
    bars = ax.bar(types, totals, color=bar_colors, alpha=0.85, edgecolor="white")
    for bar, v in zip(bars, totals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(totals + [1]) * 0.01,
                f"{v:.0f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Total |quantity|")
    ax.set_title("A. Absolute Volume by Agent Type")
    ax.tick_params(axis="x", labelrotation=30)
    ax.grid(True, alpha=0.3, axis="y")

    ax = axes[1]
    signed = [agent_signed[t] for t in types]
    ax.bar(types, signed,
           color=[colors.get(t, "#7F8C8D") for t in types],
           alpha=0.85, edgecolor="white")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Signed net quantity")
    ax.set_title("B. Signed Net Quantity by Agent Type (buys−sells)")
    ax.tick_params(axis="x", labelrotation=30)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    path = os.path.join(output_dir, "fig7_agent_contribution.png")
    save_figure(fig, path)
    plt.close(fig)


def plot_fig8_recovery_dynamics(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Fig 8: Post-trough price path with recovery threshold band."""
    rounds = data["rounds"]
    prices = np.array(data["prices"], dtype=float)
    fundamental = data["fundamental"]
    sm = metrics["scenario_metrics"]
    trough_round = sm["trough_round"]
    trough_idx = max(0, trough_round - 1)

    post = rounds[trough_idx:]
    post_prices = prices[trough_idx:]

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.suptitle("Fig 8: Recovery Dynamics", fontsize=13, fontweight="bold")

    ax.plot(rounds, prices, color="#adb5bd", linewidth=1.0, alpha=0.6,
            label="Full price path")
    ax.plot(post, post_prices, color="#2a9d8f", linewidth=2.0,
            label="Post-trough")

    upper = fundamental * 1.02
    lower = fundamental * 0.98
    ax.axhspan(lower, upper, color="#a8dadc", alpha=0.35,
               label="±2% of fundamental (recovery zone)")
    ax.axhline(fundamental, color="#00798c", linestyle="--", linewidth=1.1)
    ax.axvline(trough_round, color="#9d0208", linestyle=":", linewidth=1.1,
               label=f"Trough @ R{trough_round}")

    recovery = sm["recovery_speed"]
    if recovery >= 0:
        recovery_round = trough_round + recovery
        ax.axvline(recovery_round, color="#2a9d8f", linestyle=":", linewidth=1.1,
                   label=f"Recovery @ R{recovery_round} (Δ={recovery})")
    else:
        ax.text(0.98, 0.05, "Did not recover within run",
                transform=ax.transAxes, fontsize=11, ha="right",
                bbox=dict(boxstyle="round", facecolor="#ffe5e5", alpha=0.85))

    ax.set_xlabel("Round")
    ax.set_ylabel("Price")
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(output_dir, "fig8_recovery_dynamics.png")
    save_figure(fig, path)
    plt.close(fig)


def create_visualizations(
    data: Dict[str, Any], metrics: Dict[str, Any], output_dir: str
) -> None:
    """Emit all eight diagnostic figures (analysis-bases.md §7)."""
    os.makedirs(output_dir, exist_ok=True)
    plot_fig1_price_liquidity_dynamics(data, output_dir)
    plot_fig2_phase_overlay(data, metrics, output_dir)
    plot_fig3_crash_depth_analysis(data, metrics, output_dir)
    plot_fig4_liquidity_vacuum(data, metrics, output_dir)
    plot_fig5_stop_loss_cascade(data, metrics, output_dir)
    plot_fig6_hft_withdrawal(data, metrics, output_dir)
    plot_fig7_agent_contribution(data, output_dir)
    plot_fig8_recovery_dynamics(data, metrics, output_dir)


def _write_standard_named_outputs(output_dir: str) -> None:
    """Copy the fig{N}_*.png outputs to the standardized filenames.

    Ordered mapping (implement-simulation-skill §7.1):
        fig1 → 01_flashcrash_dynamics.png
        fig3 → 02_flashcrash_analysis.png
        fig5 → 00_investor_bids.png  (best in-scope proxy for the
                                     "investor order/quantity traces" plot;
                                     agent-type volume bars fulfil the
                                     analysis-bases.md §7 contract for
                                     that slot)
        fig8 → 03_summary.png
    """
    aliases = {
        "fig1_price_liquidity_dynamics.png": "01_flashcrash_dynamics.png",
        "fig3_crash_depth_analysis.png": "02_flashcrash_analysis.png",
        "fig5_stop_loss_cascade.png": "00_investor_bids.png",
        "fig8_recovery_dynamics.png": "03_summary.png",
    }
    for source, target in aliases.items():
        source_path = os.path.join(output_dir, source)
        if not os.path.exists(source_path):
            raise FileNotFoundError(
                f"missing FlashCrash analysis figure: {source_path}"
            )
        shutil.copyfile(source_path, os.path.join(output_dir, target))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> Dict[str, Any]:
    """Run the full FlashCrash Rule analysis pipeline."""
    parser = argparse.ArgumentParser(description="Analyze FlashCrash Rule simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/FlashCrash/Rule/simulation.yml",
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    record_dir = config["setting"]["record_path"]
    base_dir = os.path.dirname(record_dir)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("FlashCrash Rule Analysis — analysis-bases.md §2 metrics")
    print("=" * 70)

    print("\n[1] Loading simulation data...")
    data = load_simulation_data(config)
    print(f"    Loaded {len(data['prices'])} price points")
    print(f"    Loaded orders from {len(data['investor_payloads'])} investors")

    print("\n[2] Computing scenario metrics...")
    metrics = calculate_metrics(data, config)
    sm = metrics["scenario_metrics"]
    print(f"    crash_depth                             = {sm['crash_depth']:.4f}")
    print(f"    liquidity_vacuum_duration               = {sm['liquidity_vacuum_duration']}")
    print(f"    stop_loss_cascade_volume                = {sm['stop_loss_cascade_volume']:.1f}")
    print(f"    recovery_speed                          = {sm['recovery_speed']}")
    print(f"    liquidity_provider_withdrawal_fraction  = {sm['liquidity_provider_withdrawal_fraction']:.4f}")
    print(f"    price_amplification_ratio               = {sm['price_amplification_ratio']:.4f}")

    print("\n[3] Validating against analysis-bases.md §6 target ranges...")
    validation = validate_flash_crash(metrics)
    print(f"    Aggregate score: {validation['score']:.1%} — "
          f"{'VALID' if validation['is_valid'] else 'INVALID'}")

    print("\n[4] Generating figures (8 plots)...")
    create_visualizations(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)
    print(f"    All figures saved to: {output_dir}/")

    summary = {
        "scenario": "FlashCrash",
        "variant": "Rule",
        "record_path": record_dir,
        "total_rounds": int(len(data["prices"])),
        "metrics": metrics,
        "validation": validation,
    }
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[5] summary.json written to {summary_path}")

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    print(validation["interpretation"])
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
        scenario='FlashCrash',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


if __name__ == "__main__":
    main()


__all__ = [
    # Metric functions (analysis-bases.md §2)
    "crash_depth",
    "liquidity_vacuum_duration",
    "stop_loss_cascade_volume",
    "recovery_speed",
    "liquidity_provider_withdrawal_fraction",
    "price_amplification_ratio",
    # Orchestration
    "load_simulation_data",
    "calculate_metrics",
    "validate_flash_crash",
    "create_visualizations",
    # Plotting primitives
    "plot_fig1_price_liquidity_dynamics",
    "plot_fig2_phase_overlay",
    "plot_fig3_crash_depth_analysis",
    "plot_fig4_liquidity_vacuum",
    "plot_fig5_stop_loss_cascade",
    "plot_fig6_hft_withdrawal",
    "plot_fig7_agent_contribution",
    "plot_fig8_recovery_dynamics",
    # Contract
    "STANDARD_OUTPUT_FILES",
    "_write_standard_named_outputs",
    # Entry point
    "main",
]
