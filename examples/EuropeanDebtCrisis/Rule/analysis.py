#!/usr/bin/env python
"""EuropeanDebtCrisis Rule analysis — self-fulfilling sovereign-debt crisis.

Implements the seven analysis metrics declared in
``examples/EuropeanDebtCrisis/analysis-bases.md §2``:

1. Crisis Depth Index (CDI) — max negative deviation from fundamental.
2. Crisis Duration (CD) — rounds in which deviation < -10%.
3. Amplification Ratio (AR) — creditor sell volume / periphery sell volume.
4. Intervention Effectiveness Ratio (IER) — share of crisis rounds with ECB
   buys.
5. Spread Recovery Time (SRT) — rounds from trough to deviation > -5%.
6. Arbitrage Profit Rate (APR) — HedgedFund terminal return.
7. RAG Retrieval Quality (AQR) — re-exported from ``Rag/analysis.py``.

Academic references
-------------------
- De Grauwe (2011)    https://doi.org/10.2139/ssrn.1930063
- De Grauwe & Ji (2013)   https://doi.org/10.1016/j.jimonfin.2012.11.003
- Acharya, Drechsler, Schnabl (2014) https://doi.org/10.1111/jofi.12206
- Draghi (2012) "whatever it takes" ECB backstop
- Shleifer & Vishny (1997) https://doi.org/10.1111/j.1540-6261.1997.tb03807.x

Usage::

    python examples/EuropeanDebtCrisis/Rule/analysis.py \
        -c configs/EuropeanDebtCrisis/Rule/simulation.yml

Outputs (under ``EXPERIMENT/EuropeanDebtCrisis/Rule/analysis/``)::

    fig1_price_fundamental.png
    fig2_crisis_depth.png
    fig3_doom_loop.png
    fig4_intervention_timeline.png
    fig5_recovery.png
    fig6_phase_analysis.png
    fig7_agent_volume_attribution.png
    fig8_hedgedfund_pnl.png
    00_investor_bids.png           (alias of fig7 for standard contract)
    01_europeandebtcrisis_dynamics.png (alias of fig1)
    02_europeandebtcrisis_analysis.png (alias of fig2)
    03_summary.png                 (alias of fig5)
    summary.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.evaluation.finance import (
    calculate_max_drawdown,
    calculate_returns,
    save_figure,
)
from masim.evaluation.data_loader import load_data, market_players
from masim.utils import load_config, load_results


SCENARIO = "EuropeanDebtCrisis"
DEFAULT_CONFIG = "configs/EuropeanDebtCrisis/Rule/simulation.yml"

STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_europeandebtcrisis_dynamics.png",
    "02_europeandebtcrisis_analysis.png",
    "03_summary.png",
)

# Canonical class names for agent-type attribution.
_PERIPHERY_CLASS = "PeripheryBondSeller"
_CREDITOR_CLASSES = ("CreditorPanicker", "CreditorBankPanicker")
_CORE_CLASS = "CoreBondBuyer"
_ECB_CLASSES = ("ECBIntervenor", "ECBProxy")
_HEDGE_CLASS = "HedgedFund"

_AGENT_COLORS = {
    _PERIPHERY_CLASS: "#d1495b",   # deep red
    "CreditorPanicker": "#e07a5f",  # rust
    "CreditorBankPanicker": "#e07a5f",
    _CORE_CLASS: "#00798c",         # teal
    "ECBIntervenor": "#2a9d8f",     # ECB green
    "ECBProxy": "#2a9d8f",
    _HEDGE_CLASS: "#7b2cbf",        # purple
}


# ---------------------------------------------------------------------------
# Metric primitives (analysis-bases.md §2)
# ---------------------------------------------------------------------------


def crisis_depth_index(price_history: List[float], fundamental: float) -> float:
    """Maximum negative deviation of price from fundamental (as a positive number).

    Formula::

        CDI = max_t max(0, -(P(t) - F(t)) / F(t))

    Returns 0.0 when price never falls below fundamental.
    """
    if not price_history:
        raise ValueError("price_history is empty")
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    worst = 0.0
    for price in price_history:
        deviation = (float(price) - fundamental) / fundamental
        if deviation < 0.0 and -deviation > worst:
            worst = float(-deviation)
    return worst


def crisis_duration(
    price_history: List[float],
    fundamental: float,
    crisis_threshold: float = -0.10,
) -> int:
    """Count rounds in which (P(t) - F(t)) / F(t) < crisis_threshold."""
    if not price_history:
        raise ValueError("price_history is empty")
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    if crisis_threshold >= 0:
        raise ValueError("crisis_threshold must be negative")
    return int(
        sum(
            1
            for price in price_history
            if (float(price) - fundamental) / fundamental < crisis_threshold
        )
    )


def amplification_ratio(
    creditor_sell_volume: List[float],
    periphery_sell_volume: List[float],
) -> float:
    """Ratio of total creditor sell volume to total periphery sell volume.

    Returns 0.0 when periphery sell volume is zero (doom-loop attribution
    undefined without an initial shock).
    """
    total_creditor = float(sum(float(x) for x in creditor_sell_volume or []))
    total_periphery = float(sum(float(x) for x in periphery_sell_volume or []))
    if total_periphery <= 0.0:
        return 0.0
    return total_creditor / total_periphery


def intervention_effectiveness_ratio(
    ecb_buy_rounds: List[bool],
    crisis_rounds: List[bool],
) -> float:
    """Fraction of crisis rounds in which the ECB proxy is actively buying.

    Both arguments must be aligned per-round boolean lists.  Returns 0.0
    when no crisis rounds are present.
    """
    if len(ecb_buy_rounds) != len(crisis_rounds):
        raise ValueError(
            "ecb_buy_rounds and crisis_rounds must have the same length"
        )
    crisis_total = sum(1 for flag in crisis_rounds if bool(flag))
    if crisis_total == 0:
        return 0.0
    hits = sum(
        1
        for buy, crisis in zip(ecb_buy_rounds, crisis_rounds)
        if bool(crisis) and bool(buy)
    )
    return hits / crisis_total


def spread_recovery_time(
    price_history: List[float],
    fundamental: float,
    recovery_threshold: float = -0.05,
) -> int:
    """Rounds from crisis trough to first round with deviation > recovery_threshold.

    Returns -1 when no recovery is observed after the trough.  When the
    price never falls below fundamental, SRT is 0.
    """
    if not price_history:
        raise ValueError("price_history is empty")
    if fundamental <= 0:
        raise ValueError("fundamental must be positive")
    deviations = [
        (float(price) - fundamental) / fundamental for price in price_history
    ]
    trough_idx = int(np.argmin(deviations))
    if deviations[trough_idx] >= 0:
        return 0
    for idx in range(trough_idx + 1, len(deviations)):
        if deviations[idx] > recovery_threshold:
            return int(idx - trough_idx)
    return -1


def arbitrage_profit_rate(
    hf_terminal_wealth: float,
    hf_initial_wealth: float,
) -> float:
    """Terminal portfolio return for HedgedFund relative to initial wealth."""
    if hf_initial_wealth <= 0:
        raise ValueError("hf_initial_wealth must be positive")
    return (float(hf_terminal_wealth) - float(hf_initial_wealth)) / float(
        hf_initial_wealth
    )


# NOTE: ``analyze_rag_knowledge_effect`` is implemented in
# ``examples.EuropeanDebtCrisis.Rag.analysis`` (see analysis-bases.md §2.7).
# The Rule module exposes it via a thin lazy wrapper so callers can use a
# single import regardless of variant while keeping Rule ↔ Rag decoupled
# (Rag/analysis.py itself imports names from this module, so an eager
# import here would be a circular dependency).
def analyze_rag_knowledge_effect(
    rag_contexts: Dict[str, Dict[int, Any]],
) -> Dict[str, Any]:
    """Re-export of ``Rag/analysis.py::analyze_rag_knowledge_effect``.

    Imported lazily to keep the Rule and Rag modules decoupled.  See
    ``analysis-bases.md §2.7`` for the metric definition.
    """
    from examples.EuropeanDebtCrisis.Rag.analysis import (
        analyze_rag_knowledge_effect as _impl,
    )
    return _impl(rag_contexts)


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------


def _hf_extras(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return HedgedFund config extras (first matching entry)."""
    for entry in config["players"].values():
        pc = entry["config"]
        if pc["extras"].get("initial_cash") is None:
            continue
        cls_path = str(entry.get("class", ""))
        if cls_path.endswith(f":{_HEDGE_CLASS}"):
            return pc["extras"]
    return {}


def _fundamental_from_config(config: Dict[str, Any]) -> float:
    """Return the fundamental price declared by the Market coordinator."""
    for entry in config["players"].values():
        pc = entry["config"]
        if pc.get("role") == "coordinator" and "fundamental_value" in pc["extras"]:
            return float(pc["extras"]["fundamental_value"])
    raise ValueError("configs missing coordinator fundamental_value")


def _classify_agent(agent_type: str) -> str:
    """Bucket an ``agent_type`` string into a canonical class family."""
    if agent_type == _PERIPHERY_CLASS:
        return _PERIPHERY_CLASS
    if agent_type in _CREDITOR_CLASSES:
        return _CREDITOR_CLASSES[0]
    if agent_type == _CORE_CLASS:
        return _CORE_CLASS
    if agent_type in _ECB_CLASSES:
        return _ECB_CLASSES[0]
    if agent_type == _HEDGE_CLASS:
        return _HEDGE_CLASS
    return agent_type or "Unknown"


def _extract_price_fundamental(
    results: Any,
    config: Dict[str, Any],
) -> Tuple[List[int], List[float], List[float]]:
    """Return aligned (rounds, prices, fundamentals) as plain lists."""
    price_map: Dict[int, float] = {}
    fund_map: Dict[int, float] = {}

    for player in market_players(results).values():
        # HistoryBuffer flushes into batch_store_names on write; fall back to
        # turn payloads when batch stores are unavailable.
        try:
            names = set(player.batch_store_names or [])
        except Exception:
            names = set()
        if "price" in names:
            for i, value in enumerate(player.batch("price").all()):
                price_map[i + 1] = float(value)
        if "fundamental" in names:
            for i, value in enumerate(player.batch("fundamental").all()):
                fund_map[i + 1] = float(value)
        for round_num, payload in player.turns.payloads().items():
            market_data = payload
            if isinstance(payload, dict) and "market_data" in payload:
                inner = payload.get("market_data")
                if isinstance(inner, dict):
                    market_data = inner
            if isinstance(market_data, dict):
                if round_num not in price_map and "price" in market_data:
                    price_map[round_num] = float(market_data["price"])
                if round_num not in fund_map:
                    if "fundamental" in market_data:
                        fund_map[round_num] = float(market_data["fundamental"])
                    elif "fundamental_value" in market_data:
                        fund_map[round_num] = float(
                            market_data["fundamental_value"]
                        )

    if not price_map:
        raise ValueError("No market price data recorded — check Market player")

    if not fund_map:
        constant = _fundamental_from_config(config)
        fund_map = {r: constant for r in price_map}

    rounds = sorted(set(price_map) & set(fund_map))
    if not rounds:
        raise ValueError("price and fundamental series share no rounds")
    prices = [price_map[r] for r in rounds]
    fundamentals = [fund_map[r] for r in rounds]
    return rounds, prices, fundamentals


def _extract_agent_volumes(
    results: Any,
    rounds: List[int],
) -> Dict[str, Dict[str, Dict[int, float]]]:
    """Aggregate per-round buy/sell volumes for each canonical agent class.

    Returns::

        {
            class_name: {
                "buy":  {round_num: quantity},
                "sell": {round_num: quantity},
                "hold_rounds": {round_num: 1},  # marker
                "player_ids": set(...),
            },
            ...
        }
    """
    buckets: Dict[str, Dict[str, Any]] = {}

    for pid, player in results.players_by_role("player").items():
        for round_num, payload in player.turns.payloads().items():
            if not isinstance(payload, dict):
                continue
            action = payload.get("action")
            if action not in ("buy", "sell", "hold"):
                continue
            quantity = float(payload.get("quantity", 0.0) or 0.0)
            agent_type = str(
                payload.get("agent_type") or payload.get("strategy") or ""
            )
            cls = _classify_agent(agent_type)
            bucket = buckets.setdefault(
                cls,
                {"buy": {}, "sell": {}, "player_ids": set()},
            )
            bucket["player_ids"].add(pid)
            side = bucket[action] if action in ("buy", "sell") else None
            if side is not None:
                side[round_num] = side.get(round_num, 0.0) + max(0.0, quantity)

    # Ensure keys exist for the canonical scenario classes even when the
    # variant did not observe orders for one of them.
    for canonical in (
        _PERIPHERY_CLASS,
        _CREDITOR_CLASSES[0],
        _CORE_CLASS,
        _ECB_CLASSES[0],
        _HEDGE_CLASS,
    ):
        buckets.setdefault(
            canonical, {"buy": {}, "sell": {}, "player_ids": set()}
        )
    return buckets


def _extract_hedgedfund_state(
    results: Any,
    rounds: List[int],
    prices: List[float],
    hf_extras: Dict[str, Any],
) -> Dict[str, Any]:
    """Reconstruct the HedgedFund cash/position/wealth trajectory.

    Uses turn payloads to replay orders using bid_price and quantity so that
    reconstructed wealth is independent of the coordinator clearing.
    """
    initial_cash = float(hf_extras.get("initial_cash", 0.0))
    initial_position = float(hf_extras.get("initial_position", 0.0))

    price_by_round = {r: p for r, p in zip(rounds, prices)}
    trades_by_pid: Dict[str, List[Dict[str, Any]]] = {}
    for pid, player in results.players_by_role("player").items():
        for round_num, payload in player.turns.payloads().items():
            if not isinstance(payload, dict):
                continue
            if _classify_agent(str(payload.get("agent_type", ""))) != _HEDGE_CLASS:
                continue
            trades_by_pid.setdefault(pid, []).append(
                {
                    "round": int(round_num),
                    "action": str(payload.get("action", "hold")),
                    "quantity": float(payload.get("quantity", 0.0) or 0.0),
                    "bid_price": float(payload.get("bid_price", 0.0) or 0.0),
                }
            )

    if not trades_by_pid:
        # No HedgedFund observed — return zeros so downstream metrics
        # remain finite but flagged as unavailable.
        return {
            "initial_wealth": initial_cash + initial_position * (prices[0] if prices else 0.0),
            "terminal_wealth": initial_cash + initial_position * (prices[-1] if prices else 0.0),
            "wealth_by_round": {r: initial_cash for r in rounds},
            "cash_by_round": {r: initial_cash for r in rounds},
            "position_by_round": {r: initial_position for r in rounds},
            "player_count": 0,
        }

    wealth_series: Dict[int, float] = {r: 0.0 for r in rounds}
    cash_series: Dict[int, float] = {r: 0.0 for r in rounds}
    position_series: Dict[int, float] = {r: 0.0 for r in rounds}

    initial_wealth_total = 0.0
    terminal_wealth_total = 0.0

    for pid, trades in trades_by_pid.items():
        cash = initial_cash
        position = initial_position
        initial_wealth_total += cash + position * (prices[0] if prices else 0.0)

        trade_by_round = {t["round"]: t for t in trades}
        for r, market_price in zip(rounds, prices):
            trade = trade_by_round.get(r)
            if trade is not None:
                qty = max(0.0, trade["quantity"])
                bid = trade["bid_price"] if trade["bid_price"] > 0 else market_price
                if trade["action"] == "buy" and qty > 0:
                    cash -= qty * bid
                    position += qty
                elif trade["action"] == "sell" and qty > 0:
                    cash += qty * bid
                    position -= qty
            wealth_series[r] += cash + position * market_price
            cash_series[r] += cash
            position_series[r] += position
        terminal_wealth_total += cash + position * (prices[-1] if prices else 0.0)

    return {
        "initial_wealth": initial_wealth_total,
        "terminal_wealth": terminal_wealth_total,
        "wealth_by_round": wealth_series,
        "cash_by_round": cash_series,
        "position_by_round": position_series,
        "player_count": len(trades_by_pid),
    }


def load_simulation_data(
    config: Dict[str, Any],
    results: Optional[Any] = None,
) -> Dict[str, Any]:
    """Load market and agent data for the EuropeanDebtCrisis scenario.

    Parameters
    ----------
    config : dict
        Resolved simulation configuration (from ``load_config``).
    results : optional
        A previously-loaded ``SimulationResults`` instance.  When omitted the
        function calls ``masim.utils.load_results(config)`` itself.

    Returns
    -------
    dict with the following keys::

        rounds                       list[int]
        prices                       list[float]
        fundamentals                 list[float]
        fundamental                  float (assumed-constant reference)
        deviations                   list[float]  (P-F)/F
        agent_volumes                dict[class_name, dict]
        periphery_sell_volume_by_round dict[int, float]
        creditor_sell_volume_by_round  dict[int, float]
        ecb_buy_rounds               list[bool]
        crisis_rounds                list[bool]
        hf_initial_wealth            float
        hf_terminal_wealth           float
        hf_state                     dict (wealth/cash/position by round)
        investor_bids                dict[player_id, dict[int, float]]
    """
    if results is None:
        results = load_results(config)

    rounds, prices, fundamentals = _extract_price_fundamental(results, config)
    fundamental = _fundamental_from_config(config)
    deviations = [(p - f) / f for p, f in zip(prices, fundamentals)]
    crisis_rounds = [dev < -0.10 for dev in deviations]

    agent_volumes = _extract_agent_volumes(results, rounds)

    periphery_sell = {
        r: float(agent_volumes[_PERIPHERY_CLASS]["sell"].get(r, 0.0))
        for r in rounds
    }
    creditor_sell = {
        r: float(agent_volumes[_CREDITOR_CLASSES[0]]["sell"].get(r, 0.0))
        for r in rounds
    }
    ecb_buy_rounds = [
        float(agent_volumes[_ECB_CLASSES[0]]["buy"].get(r, 0.0)) > 0.0
        for r in rounds
    ]

    hf_state = _extract_hedgedfund_state(
        results, rounds, prices, _hf_extras(config)
    )

    # Investor bids for the 00 plot alias.
    standard = load_data(results)
    investor_bids = standard.get("investor_bids", {})
    investor_quantities = standard.get("investor_quantities", {})

    return {
        "scenario": SCENARIO,
        "rounds": rounds,
        "prices": prices,
        "fundamentals": fundamentals,
        "fundamental": fundamental,
        "deviations": deviations,
        "agent_volumes": agent_volumes,
        "periphery_sell_volume_by_round": periphery_sell,
        "creditor_sell_volume_by_round": creditor_sell,
        "ecb_buy_rounds": ecb_buy_rounds,
        "crisis_rounds": crisis_rounds,
        "hf_initial_wealth": float(hf_state["initial_wealth"]),
        "hf_terminal_wealth": float(hf_state["terminal_wealth"]),
        "hf_state": hf_state,
        "investor_bids": investor_bids,
        "investor_quantities": investor_quantities,
    }


# ---------------------------------------------------------------------------
# Metric calculation & validation
# ---------------------------------------------------------------------------


def calculate_metrics(
    data: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compute all seven scenario metrics plus a generic price summary.

    ``config`` is accepted for signature parity with the other scenarios but
    is not currently required — all inputs come from ``data``.
    """
    prices = list(data["prices"])
    fundamentals = list(data["fundamentals"])
    fundamental = float(data.get("fundamental", fundamentals[0] if fundamentals else 0.0))
    deviations = list(data["deviations"])

    cdi = crisis_depth_index(prices, fundamental)
    cd = crisis_duration(prices, fundamental)

    creditor_sell = list(data["creditor_sell_volume_by_round"].values())
    periphery_sell = list(data["periphery_sell_volume_by_round"].values())
    ar = amplification_ratio(creditor_sell, periphery_sell)

    ier = intervention_effectiveness_ratio(
        data["ecb_buy_rounds"], data["crisis_rounds"]
    )
    srt = spread_recovery_time(prices, fundamental)
    apr = arbitrage_profit_rate(
        data["hf_terminal_wealth"], data["hf_initial_wealth"]
    )

    # Generic price/return summary — reuses evaluation-first helpers.
    returns = calculate_returns(prices)
    if isinstance(returns, dict):
        returns_arr = np.asarray(list(returns.values()), dtype=float)
    else:
        returns_arr = np.asarray(returns, dtype=float)
    max_dd_pct, peak_idx, trough_idx = calculate_max_drawdown(prices)

    price_summary = {
        "initial": float(prices[0]),
        "final": float(prices[-1]),
        "min": float(np.min(prices)),
        "max": float(np.max(prices)),
        "mean": float(np.mean(prices)),
        "total_rounds": int(len(prices)),
    }
    deviation_summary = {
        "max_abs_deviation_pct": float(np.max(np.abs(deviations)) * 100.0),
        "mean_abs_deviation_pct": float(np.mean(np.abs(deviations)) * 100.0),
        "final_deviation_pct": float(deviations[-1] * 100.0),
        "min_deviation_pct": float(np.min(deviations) * 100.0),
    }
    return_summary = {
        "max_drawdown_pct": float(max_dd_pct),
        "peak_round": int(peak_idx + 1),
        "trough_round": int(trough_idx + 1),
        "volatility_pct": (
            float(np.std(returns_arr) * 100.0) if returns_arr.size else 0.0
        ),
        "annualized_volatility_pct": (
            float(np.std(returns_arr) * np.sqrt(252) * 100.0)
            if returns_arr.size
            else 0.0
        ),
    }

    return {
        "scenario": SCENARIO,
        "crisis_depth_index": cdi,
        "crisis_duration": cd,
        "amplification_ratio": ar,
        "intervention_effectiveness_ratio": ier,
        "spread_recovery_time": srt,
        "arbitrage_profit_rate": apr,
        "hf_initial_wealth": float(data["hf_initial_wealth"]),
        "hf_terminal_wealth": float(data["hf_terminal_wealth"]),
        "price_metrics": price_summary,
        "deviation_metrics": deviation_summary,
        "return_metrics": return_summary,
        "aggregate_volumes": {
            _PERIPHERY_CLASS: {
                "buy": float(sum(data["agent_volumes"][_PERIPHERY_CLASS]["buy"].values())),
                "sell": float(sum(data["agent_volumes"][_PERIPHERY_CLASS]["sell"].values())),
            },
            _CREDITOR_CLASSES[0]: {
                "buy": float(sum(data["agent_volumes"][_CREDITOR_CLASSES[0]]["buy"].values())),
                "sell": float(sum(data["agent_volumes"][_CREDITOR_CLASSES[0]]["sell"].values())),
            },
            _CORE_CLASS: {
                "buy": float(sum(data["agent_volumes"][_CORE_CLASS]["buy"].values())),
                "sell": float(sum(data["agent_volumes"][_CORE_CLASS]["sell"].values())),
            },
            _ECB_CLASSES[0]: {
                "buy": float(sum(data["agent_volumes"][_ECB_CLASSES[0]]["buy"].values())),
                "sell": float(sum(data["agent_volumes"][_ECB_CLASSES[0]]["sell"].values())),
            },
            _HEDGE_CLASS: {
                "buy": float(sum(data["agent_volumes"][_HEDGE_CLASS]["buy"].values())),
                "sell": float(sum(data["agent_volumes"][_HEDGE_CLASS]["sell"].values())),
            },
        },
    }


def _score_range(value: float, lower: float, upper: float) -> float:
    if value != value:  # NaN
        return 0.0
    if lower <= value <= upper:
        return 1.0
    if value < lower:
        return max(0.0, value / lower) if lower > 0 else 0.0
    return max(0.0, 1.0 - (value - upper) / max(upper, 1.0))


def validate_european_debt_crisis(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Score scenario metrics against the §6.2 calibration targets.

    Returns
    -------
    dict with keys ``is_valid``, ``score``, ``criteria``, ``interpretation``.
    """
    cdi = float(metrics["crisis_depth_index"])
    cd = int(metrics["crisis_duration"])
    ar = float(metrics["amplification_ratio"])
    ier = float(metrics["intervention_effectiveness_ratio"])
    srt = int(metrics["spread_recovery_time"])
    apr = float(metrics["arbitrage_profit_rate"])

    cdi_score = _score_range(cdi, 0.10, 0.30)
    cd_score = _score_range(float(cd), 5.0, 30.0)
    ar_score = _score_range(ar, 0.5, 1.5)
    # IER: nonzero during crisis is the calibration target.  If there is no
    # crisis (crisis_duration == 0) IER cannot be measured — treat as pass.
    if cd == 0:
        ier_score = 1.0
        ier_target = "no crisis observed — IER not applicable"
    else:
        ier_score = 1.0 if ier > 0.0 else 0.0
        ier_target = ">0 during crisis rounds"
    srt_score = 1.0 if srt >= 0 else 0.0  # -1 sentinel = no recovery
    apr_score = 1.0 if np.isfinite(apr) else 0.0

    criteria = {
        "Crisis Depth Index (CDI)": {
            "value": round(cdi, 4),
            "target": "0.10 to 0.30 preferred",
            "score": round(cdi_score, 3),
            "passed": cdi_score >= 0.5,
        },
        "Crisis Duration (CD)": {
            "value": cd,
            "target": "5 to 30 rounds preferred",
            "score": round(cd_score, 3),
            "passed": cd_score >= 0.5,
        },
        "Amplification Ratio (AR)": {
            "value": round(ar, 4),
            "target": "0.5 to 1.5 preferred",
            "score": round(ar_score, 3),
            "passed": ar_score >= 0.5,
        },
        "Intervention Effectiveness (IER)": {
            "value": round(ier, 4),
            "target": ier_target,
            "score": round(ier_score, 3),
            "passed": ier_score >= 0.5,
        },
        "Spread Recovery Time (SRT)": {
            "value": srt,
            "target": "finite within 200 rounds",
            "score": round(srt_score, 3),
            "passed": srt_score >= 0.5,
        },
        "Arbitrage Profit Rate (APR)": {
            "value": round(apr, 4),
            "target": "finite; diagnostic",
            "score": round(apr_score, 3),
            "passed": apr_score >= 0.5,
        },
    }
    weights = {
        "Crisis Depth Index (CDI)": 0.25,
        "Crisis Duration (CD)": 0.20,
        "Amplification Ratio (AR)": 0.15,
        "Intervention Effectiveness (IER)": 0.15,
        "Spread Recovery Time (SRT)": 0.15,
        "Arbitrage Profit Rate (APR)": 0.10,
    }
    score = sum(criteria[name]["score"] * weight for name, weight in weights.items())
    is_valid = score >= 0.5
    verdict = "VALID" if is_valid else "INVALID"

    lines = [
        f"=== {SCENARIO} SIMULATION VALIDATION: {verdict} ===",
        f"Overall Fit Score: {score:.1%} (threshold: 50%)",
        "",
    ]
    for idx, (name, entry) in enumerate(criteria.items(), start=1):
        lines.extend(
            [
                f"[{idx}] {name}",
                f"    Observed: {entry['value']}",
                f"    Target:   {entry['target']}",
                f"    Score:    {entry['score']:.1%}",
                f"    Passed:   {entry['passed']}",
                "",
            ]
        )
    lines.append("[SUMMARY]")
    lines.append(
        f"CDI={cdi:.3f}  CD={cd}  AR={ar:.3f}  IER={ier:.3f}  "
        f"SRT={srt}  APR={apr:.3f}"
    )
    interpretation = "\n".join(lines)

    return {
        "is_valid": bool(is_valid),
        "score": round(float(score), 4),
        "criteria": criteria,
        "interpretation": interpretation,
    }


# ---------------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------------


def _phase_labels(deviations: List[float]) -> List[str]:
    """Return one-of five phase labels for each round.

    Phases (analysis-bases.md §4)::

        Pre-crisis | Onset | Doom-loop | Intervention | Recovery
    """
    if not deviations:
        return []
    trough_idx = int(np.argmin(deviations))
    phases: List[str] = []
    for idx, dev in enumerate(deviations):
        if idx < trough_idx and dev >= -0.05:
            phases.append("Pre-crisis")
        elif idx < trough_idx and dev >= -0.10:
            phases.append("Onset")
        elif idx < trough_idx and dev >= -0.20:
            phases.append("Doom-loop")
        elif idx == trough_idx or (idx < len(deviations) - 1 and dev < -0.15):
            phases.append("Intervention")
        else:
            phases.append("Recovery")
    return phases


def plot_fig1_price_fundamental(
    data: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 1: Peripheral price vs fundamental with above/below shading."""
    rounds = data["rounds"]
    prices = np.asarray(data["prices"], dtype=float)
    fundamentals = np.asarray(data["fundamentals"], dtype=float)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(rounds, prices, color="#d1495b", linewidth=2.0, label="Periphery Price P(t)")
    ax.plot(
        rounds,
        fundamentals,
        color="#00798c",
        linewidth=1.5,
        linestyle="--",
        label="Fundamental F(t)",
    )
    ax.fill_between(
        rounds,
        prices,
        fundamentals,
        where=prices < fundamentals,
        alpha=0.15,
        color="#d1495b",
        label="P < F (stress)",
    )
    ax.fill_between(
        rounds,
        prices,
        fundamentals,
        where=prices >= fundamentals,
        alpha=0.10,
        color="#2a9d8f",
        label="P ≥ F",
    )
    ax.set_xlabel("Round")
    ax.set_ylabel("Peripheral Sovereign Bond Price")
    ax.set_title(
        "Fig 1: Peripheral Price vs Fundamental — De Grauwe (2011) Setup",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", fontsize=9)
    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig1_price_fundamental.png"))


def plot_fig2_crisis_depth(
    data: Dict[str, Any],
    metrics: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 2: deviation series with crisis threshold band and CDI annotation."""
    rounds = data["rounds"]
    deviations_pct = np.asarray(data["deviations"], dtype=float) * 100.0
    cdi = float(metrics["crisis_depth_index"])
    cd = int(metrics["crisis_duration"])

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(rounds, deviations_pct, color="#7b2cbf", linewidth=1.8, label="Deviation (%)")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.axhline(-10, color="#e07a5f", linewidth=1.2, linestyle=":", label="Crisis threshold (-10%)")
    ax.axhline(-20, color="#c1121f", linewidth=1.2, linestyle=":", label="Severe threshold (-20%)")
    ax.fill_between(
        rounds,
        deviations_pct,
        -10,
        where=deviations_pct < -10,
        alpha=0.25,
        color="#c1121f",
        label="Crisis rounds",
    )
    if len(rounds):
        trough_idx = int(np.argmin(deviations_pct))
        ax.annotate(
            f"CDI = {cdi:.3f}\ntrough @ round {rounds[trough_idx]}\nCD = {cd} rounds",
            xy=(rounds[trough_idx], deviations_pct[trough_idx]),
            xytext=(rounds[trough_idx] + max(5, len(rounds) // 20), deviations_pct[trough_idx] - 3),
            fontsize=10,
            arrowprops=dict(arrowstyle="->", color="black"),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8edeb", alpha=0.9),
        )
    ax.set_xlabel("Round")
    ax.set_ylabel("Deviation (P - F) / F (%)")
    ax.set_title(
        "Fig 2: Crisis Depth Index & Crisis Duration",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=9)
    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig2_crisis_depth.png"))


def plot_fig3_doom_loop(
    data: Dict[str, Any],
    metrics: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 3: doom-loop analysis — periphery vs creditor sell volume + AR series."""
    rounds = data["rounds"]
    periphery_sell = [
        float(data["periphery_sell_volume_by_round"].get(r, 0.0)) for r in rounds
    ]
    creditor_sell = [
        float(data["creditor_sell_volume_by_round"].get(r, 0.0)) for r in rounds
    ]

    # Rolling amplification ratio (windowed sums to keep denominator stable).
    window = max(5, len(rounds) // 20)
    ar_series: List[float] = []
    for i in range(len(rounds)):
        lo = max(0, i - window + 1)
        p_sum = sum(periphery_sell[lo : i + 1])
        c_sum = sum(creditor_sell[lo : i + 1])
        ar_series.append(c_sum / p_sum if p_sum > 0 else 0.0)

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    fig.suptitle(
        "Fig 3: Sovereign-Bank Doom Loop (Acharya, Drechsler, Schnabl 2014)",
        fontsize=13,
        fontweight="bold",
    )

    ax = axes[0]
    ax.bar(
        rounds,
        periphery_sell,
        color=_AGENT_COLORS[_PERIPHERY_CLASS],
        alpha=0.7,
        label=f"{_PERIPHERY_CLASS} sell volume",
    )
    ax.bar(
        rounds,
        creditor_sell,
        bottom=periphery_sell,
        color=_AGENT_COLORS[_CREDITOR_CLASSES[0]],
        alpha=0.7,
        label=f"{_CREDITOR_CLASSES[0]} sell volume",
    )
    ax.set_ylabel("Sell Volume (units)")
    ax.set_title("A. Stacked Sell Volume — Initial Shock vs Creditor Amplification")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.plot(rounds, ar_series, color="#e07a5f", linewidth=1.8, label=f"AR (window={window})")
    ax.axhline(
        float(metrics["amplification_ratio"]),
        color="#c1121f",
        linestyle="--",
        linewidth=1.0,
        label=f"AR (cumulative)={metrics['amplification_ratio']:.3f}",
    )
    ax.axhline(1.0, color="black", linestyle=":", linewidth=0.8, label="AR = 1")
    ax.set_ylabel("Amplification Ratio")
    ax.set_xlabel("Round")
    ax.set_title("B. Rolling Amplification Ratio (creditor / periphery sell)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig3_doom_loop.png"))


def plot_fig4_intervention_timeline(
    data: Dict[str, Any],
    metrics: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 4: ECB buy actions overlaid on crisis-round window."""
    rounds = data["rounds"]
    deviations_pct = np.asarray(data["deviations"], dtype=float) * 100.0
    crisis_flags = data["crisis_rounds"]
    ecb_flags = data["ecb_buy_rounds"]
    ecb_buy_volume = [
        float(data["agent_volumes"][_ECB_CLASSES[0]]["buy"].get(r, 0.0)) for r in rounds
    ]
    ier = float(metrics["intervention_effectiveness_ratio"])

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.plot(
        rounds,
        deviations_pct,
        color="#7b2cbf",
        linewidth=1.6,
        label="Deviation (%)",
        zorder=3,
    )
    ax1.axhline(-10, color="#c1121f", linestyle=":", linewidth=1.0)
    ax1.fill_between(
        rounds,
        min(deviations_pct.min(), -25.0),
        deviations_pct.max(),
        where=np.asarray(crisis_flags, dtype=bool),
        alpha=0.10,
        color="#c1121f",
        label="Crisis rounds (dev < -10%)",
    )
    ax1.set_xlabel("Round")
    ax1.set_ylabel("Deviation (%)", color="#7b2cbf")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.bar(
        rounds,
        ecb_buy_volume,
        color=_AGENT_COLORS[_ECB_CLASSES[0]],
        alpha=0.55,
        label="ECB buy volume",
        zorder=1,
    )
    ax2.set_ylabel("ECB Buy Volume", color=_AGENT_COLORS[_ECB_CLASSES[0]])

    hits = sum(1 for buy, crisis in zip(ecb_flags, crisis_flags) if buy and crisis)
    total_crisis = sum(1 for crisis in crisis_flags if crisis)
    ax1.set_title(
        f"Fig 4: ECB Intervention Timeline — IER = {ier:.3f}"
        f"  ({hits}/{total_crisis} crisis rounds covered)",
        fontsize=13,
        fontweight="bold",
    )
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="lower left", fontsize=9)
    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig4_intervention_timeline.png"))


def plot_fig5_recovery(
    data: Dict[str, Any],
    metrics: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 5: post-trough price recovery with -5% recovery band."""
    rounds = data["rounds"]
    deviations_pct = np.asarray(data["deviations"], dtype=float) * 100.0
    srt = int(metrics["spread_recovery_time"])

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(rounds, deviations_pct, color="#264653", linewidth=1.8, label="Deviation (%)")
    ax.axhline(-5, color="#2a9d8f", linewidth=1.2, linestyle="--", label="Recovery threshold (-5%)")
    ax.axhline(-10, color="#c1121f", linewidth=1.0, linestyle=":", label="Crisis threshold (-10%)")
    ax.axhline(0, color="black", linewidth=0.6)

    if len(rounds):
        trough_idx = int(np.argmin(deviations_pct))
        ax.axvline(
            rounds[trough_idx],
            color="#e07a5f",
            linewidth=1.2,
            linestyle="--",
            label=f"Trough (round {rounds[trough_idx]})",
        )
        if srt > 0 and trough_idx + srt < len(rounds):
            recovery_round = rounds[trough_idx + srt]
            ax.axvline(
                recovery_round,
                color="#2a9d8f",
                linewidth=1.2,
                linestyle="--",
                label=f"Recovery (round {recovery_round})",
            )
            ax.fill_betweenx(
                [deviations_pct.min(), 5],
                rounds[trough_idx],
                recovery_round,
                color="#2a9d8f",
                alpha=0.12,
            )
        srt_text = f"SRT = {srt}" if srt >= 0 else "SRT = no recovery"
        ax.text(
            0.02,
            0.05,
            srt_text,
            transform=ax.transAxes,
            fontsize=11,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8edeb", alpha=0.9),
        )
    ax.set_xlabel("Round")
    ax.set_ylabel("Deviation (%)")
    ax.set_title(
        "Fig 5: Spread Recovery Time — Post-Trough Path",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=9)
    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig5_recovery.png"))


def plot_fig6_phase_analysis(data: Dict[str, Any], output_dir: str) -> None:
    """Fig 6: Pre-crisis/Onset/Doom-loop/Intervention/Recovery over price."""
    rounds = data["rounds"]
    prices = np.asarray(data["prices"], dtype=float)
    deviations = list(data["deviations"])
    phases = _phase_labels(deviations)

    phase_colors = {
        "Pre-crisis": "#e9ecef",
        "Onset": "#ffe0b2",
        "Doom-loop": "#f4a261",
        "Intervention": "#c1121f",
        "Recovery": "#a8dadc",
    }

    fig, ax = plt.subplots(figsize=(14, 6))
    if phases:
        current = phases[0]
        start = rounds[0]
        for idx, label in enumerate(phases + [None]):
            if label != current or idx == len(phases):
                end = rounds[idx - 1] if idx > 0 else rounds[0]
                ax.axvspan(start, end + 0.5, alpha=0.35, color=phase_colors.get(current, "#dee2e6"))
                if idx < len(phases):
                    start = rounds[idx]
                    current = label
    ax.plot(rounds, prices, color="#264653", linewidth=2.0, label="Price")
    ax.axhline(
        float(data["fundamental"]),
        color="#00798c",
        linewidth=1.5,
        linestyle="--",
        label="Fundamental",
    )
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.35) for c in phase_colors.values()
    ]
    labels = list(phase_colors.keys())
    handles.append(plt.Line2D([], [], color="#264653", linewidth=2.0))
    labels.append("Price")
    ax.legend(handles, labels, loc="lower left", fontsize=9, ncol=3)
    ax.set_xlabel("Round")
    ax.set_ylabel("Peripheral Bond Price")
    ax.set_title(
        "Fig 6: Crisis Phase Decomposition (analysis-bases.md §4)",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig6_phase_analysis.png"))


def plot_fig7_agent_volume_attribution(
    data: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 7: stacked bar of per-round net volume for each canonical agent class."""
    rounds = data["rounds"]
    agent_volumes = data["agent_volumes"]

    canonical_order = [
        _PERIPHERY_CLASS,
        _CREDITOR_CLASSES[0],
        _CORE_CLASS,
        _ECB_CLASSES[0],
        _HEDGE_CLASS,
    ]

    # Net volume per round = buy - sell (positive = net buying pressure).
    series: Dict[str, List[float]] = {}
    for cls in canonical_order:
        vol = agent_volumes.get(cls, {"buy": {}, "sell": {}})
        series[cls] = [
            float(vol["buy"].get(r, 0.0)) - float(vol["sell"].get(r, 0.0))
            for r in rounds
        ]

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    fig.suptitle(
        "Fig 7: Agent-Level Volume Attribution",
        fontsize=13,
        fontweight="bold",
    )

    ax = axes[0]
    pos_base = np.zeros(len(rounds), dtype=float)
    neg_base = np.zeros(len(rounds), dtype=float)
    for cls in canonical_order:
        values = np.asarray(series[cls], dtype=float)
        pos = np.where(values > 0, values, 0.0)
        neg = np.where(values < 0, values, 0.0)
        ax.bar(
            rounds,
            pos,
            bottom=pos_base,
            color=_AGENT_COLORS.get(cls, "#7F8C8D"),
            alpha=0.85,
            label=f"{cls} (buy)",
        )
        ax.bar(
            rounds,
            neg,
            bottom=neg_base,
            color=_AGENT_COLORS.get(cls, "#7F8C8D"),
            alpha=0.55,
            hatch="//",
            label=f"{cls} (sell)",
        )
        pos_base += pos
        neg_base += neg
    ax.axhline(0, color="black", linewidth=0.7)
    ax.set_ylabel("Net Volume per Round")
    ax.set_title("A. Stacked Buy (positive) and Sell (negative, hatched) Volume")
    ax.legend(fontsize=7, ncol=3, loc="upper right")
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    totals = {
        cls: (
            float(sum(agent_volumes[cls]["buy"].values())),
            float(sum(agent_volumes[cls]["sell"].values())),
        )
        for cls in canonical_order
    }
    x = np.arange(len(canonical_order))
    width = 0.4
    buy_totals = [totals[c][0] for c in canonical_order]
    sell_totals = [totals[c][1] for c in canonical_order]
    ax.bar(
        x - width / 2,
        buy_totals,
        width,
        color="#2a9d8f",
        alpha=0.85,
        label="Total buy",
    )
    ax.bar(
        x + width / 2,
        sell_totals,
        width,
        color="#c1121f",
        alpha=0.85,
        label="Total sell",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(canonical_order, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("Cumulative Volume")
    ax.set_title("B. Cumulative Buy vs Sell Volume by Agent Class")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig7_agent_volume_attribution.png"))


def plot_fig8_hedgedfund_pnl(
    data: Dict[str, Any],
    metrics: Dict[str, Any],
    output_dir: str,
) -> None:
    """Fig 8: HedgedFund wealth (cash + position*price) evolution."""
    hf_state = data["hf_state"]
    rounds = data["rounds"]
    apr = float(metrics["arbitrage_profit_rate"])

    wealth = [float(hf_state["wealth_by_round"].get(r, 0.0)) for r in rounds]
    cash = [float(hf_state["cash_by_round"].get(r, 0.0)) for r in rounds]
    position = [float(hf_state["position_by_round"].get(r, 0.0)) for r in rounds]

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True)
    fig.suptitle(
        f"Fig 8: HedgedFund Wealth Evolution — APR = {apr:+.2%}"
        f"  ({hf_state.get('player_count', 0)} instances)",
        fontsize=13,
        fontweight="bold",
    )

    ax = axes[0]
    ax.plot(rounds, wealth, color="#7b2cbf", linewidth=2.0, label="Total wealth")
    ax.plot(rounds, cash, color="#00798c", linewidth=1.4, linestyle="--", label="Cash")
    ax.axhline(
        float(data["hf_initial_wealth"]),
        color="black",
        linewidth=0.8,
        linestyle=":",
        label=f"Initial ({data['hf_initial_wealth']:.0f})",
    )
    ax.set_ylabel("Wealth")
    ax.set_title("A. Cash + Position × Price")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)

    ax = axes[1]
    ax.plot(rounds, position, color="#d1495b", linewidth=1.8, label="Position (units)")
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_xlabel("Round")
    ax.set_ylabel("Position (units)")
    ax.set_title("B. HedgedFund Position Trajectory")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    plt.tight_layout()
    save_figure(fig, os.path.join(output_dir, "fig8_hedgedfund_pnl.png"))


def _write_standard_named_outputs(output_dir: str) -> None:
    """Alias variant-specific PNGs onto the fixed standard-contract names.

    The standard 4-plot contract (``examples/standard_rule_analysis.py``)
    demands these four filenames.  We map the closest scenario figure to
    each so downstream tooling continues to work.
    """
    aliases = {
        "fig7_agent_volume_attribution.png": "00_investor_bids.png",
        "fig1_price_fundamental.png": "01_europeandebtcrisis_dynamics.png",
        "fig2_crisis_depth.png": "02_europeandebtcrisis_analysis.png",
        "fig5_recovery.png": "03_summary.png",
    }
    for source, target in aliases.items():
        source_path = os.path.join(output_dir, source)
        if not os.path.exists(source_path):
            raise FileNotFoundError(
                f"missing EuropeanDebtCrisis analysis figure: {source_path}"
            )
        shutil.copyfile(source_path, os.path.join(output_dir, target))


def create_visualizations(
    data: Dict[str, Any],
    metrics: Dict[str, Any],
    output_dir: str,
) -> None:
    """Emit all eight scenario figures plus the four standard aliases."""
    os.makedirs(output_dir, exist_ok=True)
    plot_fig1_price_fundamental(data, output_dir)
    plot_fig2_crisis_depth(data, metrics, output_dir)
    plot_fig3_doom_loop(data, metrics, output_dir)
    plot_fig4_intervention_timeline(data, metrics, output_dir)
    plot_fig5_recovery(data, metrics, output_dir)
    plot_fig6_phase_analysis(data, output_dir)
    plot_fig7_agent_volume_attribution(data, output_dir)
    plot_fig8_hedgedfund_pnl(data, metrics, output_dir)
    _write_standard_named_outputs(output_dir)


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------


def analyze_europeandebtcrisis(
    config: Dict[str, Any],
    output_dir: str,
    results: Optional[Any] = None,
) -> Dict[str, Any]:
    """Run the full analysis pipeline and return the summary dict."""
    if results is None:
        results = load_results(config)
    data = load_simulation_data(config, results)
    metrics = calculate_metrics(data, config)
    validation = validate_european_debt_crisis(metrics)
    create_visualizations(data, metrics, output_dir)

    summary = {
        "scenario": SCENARIO,
        "record_path": config["setting"]["record_path"],
        "total_rounds": int(metrics["price_metrics"]["total_rounds"]),
        "metrics": metrics,
        "validation": validation,
    }
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    _print_console_report(metrics, validation)
    return summary


def _print_console_report(
    metrics: Dict[str, Any], validation: Dict[str, Any]
) -> None:
    print("\n" + "=" * 60)
    print(f"{SCENARIO.upper()} ANALYSIS")
    print("=" * 60)
    print(f"CDI = {metrics['crisis_depth_index']:.4f}")
    print(f"CD  = {metrics['crisis_duration']} rounds")
    print(f"AR  = {metrics['amplification_ratio']:.4f}")
    print(f"IER = {metrics['intervention_effectiveness_ratio']:.4f}")
    print(f"SRT = {metrics['spread_recovery_time']} rounds")
    print(f"APR = {metrics['arbitrage_profit_rate']:+.4f}")
    print(
        f"HF wealth: {metrics['hf_initial_wealth']:.2f} -> "
        f"{metrics['hf_terminal_wealth']:.2f}"
    )
    print("\nVALIDATION:")
    print(validation["interpretation"])
    print(f"Fit Score: {validation['score']:.1%}")


def main() -> Dict[str, Any]:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze EuropeanDebtCrisis Rule results"
    )
    parser.add_argument("-c", "--config", type=str, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)
    return analyze_europeandebtcrisis(config, output_dir)


__all__ = [
    "SCENARIO",
    "DEFAULT_CONFIG",
    "STANDARD_OUTPUT_FILES",
    # metric primitives
    "crisis_depth_index",
    "crisis_duration",
    "amplification_ratio",
    "intervention_effectiveness_ratio",
    "spread_recovery_time",
    "arbitrage_profit_rate",
    "analyze_rag_knowledge_effect",
    # pipeline
    "load_simulation_data",
    "calculate_metrics",
    "validate_european_debt_crisis",
    "create_visualizations",
    "analyze_europeandebtcrisis",
    "main",
]


if __name__ == "__main__":
    main()
