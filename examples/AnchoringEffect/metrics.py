"""AnchoringEffect — Metric Catalogue.

Authoritative reference: ``masim/evaluation/README.md`` (see also
``masim/skills/implement-simulation-skill/10-evaluation-architecture.md``).
This scenario-root module MUST NOT re-implement any function that is already
provided by ``masim.evaluation``; it may only import + register standard
metrics and add scenario-specific ones.

This module assembles the complete metric registry for the AnchoringEffect
scenario by combining:

  1. **36 standard metrics** from ``masim.evaluation.finance`` (distributed
     across ``timeseries.py`` [23], ``behavioral.py`` [8], and
     ``microstructure.py`` [5] — covering price dynamics, information
     efficiency, statistical inference, tail risk, agent behaviour, and
     microstructure).  These are reusable across every finance scenario;
     registered via ``register_standard_metrics(REGISTRY)`` below.

  2. **8 scenario-specific metrics** defined below — these require
     AnchoringEffect-specific config parsing (initial anchor, adjustment
     factor, hardcoded strategy names, phase detection) and cannot be
     abstracted into the shared catalogue.

The shared helper ``_returns`` is re-imported from
``masim.evaluation.finance.timeseries`` to preserve a single-source
implementation for arithmetic-return computation.

Data contract (built by ``examples.AnchoringEffect.Rule.analysis._load_data``)::

    data = {
        "market_prices":       {round: float},
        "fundamentals":        {round: float},
        "investor_quantities": {player_id: {round: float}},
        "investor_bids":       {player_id: {round: float}},
        "investor_payloads":   {player_id: {round: dict}},
    }

Categories (per analysis-bases.md):

    price_dynamics, anchoring_specific, agent_behaviour, microstructure,
    statistical_inference, phase_decomposition,
    information_efficiency, tail_risk.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from masim.evaluation.registry import (
    Metric,
    MetricsRegistry,
    MetricUnavailable,
)
from masim.evaluation.finance import register_standard_metrics
from masim.evaluation.data_loader import (
    aligned_prices_and_fundamentals as _aligned_prices_and_fundamentals,
    payload_buy_sell as _payload_buy_sell,
)
from masim.evaluation.finance.timeseries import _returns


# ---------------------------------------------------------------------------
# Archetype ids used to filter payloads by `strategy`.
#
# The wire-format contract stamps every InvestorOrder with
# ``strategy=self.STRATEGY`` — and every canonical AnchoringEffect class
# (Rule / LLM / RuleLLM / Rag) declares ``STRATEGY`` as the kebab-case
# archetype id (e.g. ``anchored-trader``).  Grouping metrics below must
# match on that same identifier — the previous PascalCase spellings
# (``AnchoredTrader`` etc.) silently failed to match any payload and
# turned all four grouping metrics into permanent ``MetricUnavailable``.
# ---------------------------------------------------------------------------

ANCHORED_TRADER = "anchored-trader"
HISTORICAL_ANCHOR = "historical-anchor"
RATIONAL_UPDATER = "rational-updater"
MOMENTUM_TRADER = "momentum-trader"
DISPOSITION_TRADER = "disposition-trader"
CONTRARIAN_TRADER = "contrarian-trader"
FUNDAMENTAL_ANALYST = "fundamental-analyst"

BIASED_STRATEGIES = frozenset({
    ANCHORED_TRADER, HISTORICAL_ANCHOR, DISPOSITION_TRADER,
})
CORRECTIVE_STRATEGIES = frozenset({
    RATIONAL_UPDATER, FUNDAMENTAL_ANALYST, CONTRARIAN_TRADER,
})


# ---------------------------------------------------------------------------
# Scenario-specific helpers (AnchoringEffect only)
# ---------------------------------------------------------------------------


def _coordinator_extras(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return the market coordinator's `extras` dict."""
    for player in config["players"].values():
        player_config = player["config"]
        if player_config["role"] == "coordinator":
            return player_config["extras"]
    raise MetricUnavailable("no coordinator player found in config")


def _anchored_adjustment_factor(config: Dict[str, Any]) -> float:
    """Return the AnchoredTrader's adjustment_factor (alpha)."""
    for player in config["players"].values():
        extras = player["config"]["extras"]
        if "adjustment_factor" in extras:
            return float(extras["adjustment_factor"])
    raise MetricUnavailable("no adjustment_factor present in any player extras")


def _initial_anchor(config: Dict[str, Any]) -> float:
    """Return the simulation's initial price (the canonical anchor)."""
    extras = _coordinator_extras(config)
    if "initial_price" not in extras:
        raise MetricUnavailable("coordinator extras lacks initial_price")
    return float(extras["initial_price"])


def _strategy_demand(payloads: Dict[str, Dict[int, dict]], strategies) -> Dict[int, float]:
    """Net signed demand summed across the named strategies."""
    targets = set(strategies)
    demand: Dict[int, float] = {}
    for round_payloads in payloads.values():
        for round_num, payload in round_payloads.items():
            if payload.get("strategy") not in targets:
                continue
            buy, sell = _payload_buy_sell(payload)
            demand[round_num] = demand.get(round_num, 0.0) + (buy - sell)
    return demand


def _detect_phases(deviations_pct: np.ndarray) -> List[Dict[str, Any]]:
    """Heuristic phase classification matching analysis-bases.md §4.

    Phases:
      1 Anchor Establishment   — first 10 rounds (or until |dev| stable < 0.5%)
      2 Persistent Mispricing  — |dev| above 2% threshold
      3 Slow Correction        — |dev| declining for 5+ consecutive rounds
      4 Convergence            — |dev| below 1% sustained 5 rounds
    """
    n = deviations_pct.size
    abs_dev = np.abs(deviations_pct)
    phases: List[Dict[str, Any]] = []
    cur_phase = 1
    cur_start = 0
    persist_thresh = 2.0
    converge_thresh = 1.0
    decline_window = 5

    def declining(end: int) -> bool:
        if end < decline_window:
            return False
        window = abs_dev[end - decline_window + 1 : end + 1]
        return bool(np.all(np.diff(window) < 0))

    def converged_run(end: int) -> bool:
        if end < decline_window - 1:
            return False
        window = abs_dev[end - decline_window + 1 : end + 1]
        return bool(np.all(window < converge_thresh))

    for i in range(n):
        if cur_phase == 1 and i >= 10 and abs_dev[i] >= persist_thresh:
            phases.append({"phase": 1, "start": cur_start, "end": i - 1})
            cur_phase = 2
            cur_start = i
        elif cur_phase == 2 and declining(i):
            phases.append({"phase": 2, "start": cur_start, "end": i - 1})
            cur_phase = 3
            cur_start = i
        elif cur_phase == 3 and converged_run(i):
            phases.append({"phase": 3, "start": cur_start, "end": i - 1})
            cur_phase = 4
            cur_start = i
    phases.append({"phase": cur_phase, "start": cur_start, "end": n - 1})
    return phases


# ---------------------------------------------------------------------------
# Scenario-specific metric functions
# ---------------------------------------------------------------------------


def m_bias_magnitude_pct(data, config):
    """(1 - alpha) * |anchor - F| / F using config initial_price as anchor."""
    rounds, prices, funds = _aligned_prices_and_fundamentals(data)
    alpha = _anchored_adjustment_factor(config)
    anchor = _initial_anchor(config)
    fundamental = float(funds.mean())
    bias = (1.0 - alpha) * abs(anchor - fundamental) / fundamental
    return {
        "value_pct": float(bias * 100),
        "alpha": alpha,
        "anchor_price": anchor,
        "fundamental_value": fundamental,
    }


def m_anchor_dispersion(data, config):
    """Std of perceived_target across AnchoredTrader instances."""
    payloads = data["investor_payloads"]
    targets_per_round: Dict[int, List[float]] = {}
    for pid, round_payloads in payloads.items():
        for round_num, payload in round_payloads.items():
            if payload.get("strategy") != ANCHORED_TRADER:
                continue
            if "perceived_target" not in payload:
                continue
            targets_per_round.setdefault(round_num, []).append(
                float(payload["perceived_target"])
            )
    if not targets_per_round:
        raise MetricUnavailable(
            f"no {ANCHORED_TRADER!r} payload contained `perceived_target`"
        )
    rounds_sorted = sorted(targets_per_round)
    dispersions = [float(np.std(targets_per_round[r])) for r in rounds_sorted]
    return {
        "rounds": rounds_sorted,
        "dispersion_per_round": dispersions,
        "mean_dispersion": float(np.mean(dispersions)),
        "max_dispersion": float(np.max(dispersions)),
    }


def m_price_to_anchor_distance_ts(data, config):
    """Percent distance of market price from canonical anchor (initial price)."""
    rounds, prices, _ = _aligned_prices_and_fundamentals(data)
    anchor = _initial_anchor(config)
    distance_pct = ((prices - anchor) / anchor * 100).tolist()
    return {
        "rounds": rounds,
        "anchor_price": anchor,
        "distance_pct": distance_pct,
        "mean_abs_distance_pct": float(np.mean(np.abs(distance_pct))),
    }


def m_corrective_to_biased_volume_ratio(data, config):
    """RationalUpdater volume / (AnchoredTrader + HistoricalAnchor) volume."""
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    biased_total = 0.0
    corrective_total = 0.0
    biased_ids = {ANCHORED_TRADER, HISTORICAL_ANCHOR}
    for round_payloads in payloads.values():
        for payload in round_payloads.values():
            strategy = payload.get("strategy")
            buy, sell = _payload_buy_sell(payload)
            volume = buy + sell
            if strategy in biased_ids:
                biased_total += volume
            elif strategy == RATIONAL_UPDATER:
                corrective_total += volume
    if biased_total <= 0:
        raise MetricUnavailable("no biased agent volume recorded")
    return {
        "value": corrective_total / biased_total,
        "biased_volume": biased_total,
        "corrective_volume": corrective_total,
    }


def m_momentum_anchoring_coupling(data, config):
    """Pearson correlation between AnchoredTrader and MomentumTrader net demand."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    at_demand = _strategy_demand(payloads, {ANCHORED_TRADER})
    mt_demand = _strategy_demand(payloads, {MOMENTUM_TRADER})
    if not at_demand or not mt_demand:
        raise MetricUnavailable("need both AT and MT trades for coupling")
    common = sorted(set(at_demand) & set(mt_demand))
    if len(common) < 5:
        raise MetricUnavailable("need >=5 shared rounds for coupling")
    at_series = np.asarray([at_demand[r] for r in common], dtype=float)
    mt_series = np.asarray([mt_demand[r] for r in common], dtype=float)
    if np.std(at_series) < 1e-12 or np.std(mt_series) < 1e-12:
        raise MetricUnavailable("zero variance in AT or MT demand")
    corr = float(np.corrcoef(at_series, mt_series)[0, 1])
    return {"value": corr}


def m_phase_assignment_ts(data, config):
    """Round-by-round assignment to anchoring phase 1..4."""
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    deviations_pct = (prices - funds) / funds * 100
    phases = _detect_phases(deviations_pct)
    return {
        "phases": phases,
        "phase_names": {
            1: "Anchor Establishment",
            2: "Persistent Mispricing",
            3: "Slow Correction",
            4: "Convergence",
        },
        "total_rounds": int(prices.size),
    }


def m_per_phase_metrics_table(data, config):
    """MAD, vol, return per detected anchoring phase."""
    rounds, prices, funds = _aligned_prices_and_fundamentals(data)
    deviations_pct = (prices - funds) / funds * 100
    phases = _detect_phases(deviations_pct)
    returns = _returns(prices)
    table: List[Dict[str, Any]] = []
    for phase_info in phases:
        phase_id = phase_info["phase"]
        start = phase_info["start"]
        end = phase_info["end"]
        rounds_phase = rounds[start : end + 1]
        if not rounds_phase:
            continue
        slice_dev = deviations_pct[start : end + 1]
        ret_start = max(0, start)
        ret_end = max(ret_start, end)
        slice_ret = returns[ret_start:ret_end] if ret_end > ret_start else np.array([])
        entry = {
            "phase": phase_id,
            "round_start": rounds_phase[0],
            "round_end": rounds_phase[-1],
            "n_rounds": len(rounds_phase),
            "mad_pct": float(np.mean(np.abs(slice_dev))),
            "mean_signed_dev_pct": float(np.mean(slice_dev)),
            "max_abs_dev_pct": float(np.max(np.abs(slice_dev))),
        }
        if slice_ret.size >= 2:
            entry["mean_return_pct"] = float(np.mean(slice_ret) * 100)
            entry["volatility_pct"] = float(np.std(slice_ret) * 100)
        else:
            entry["mean_return_pct"] = 0.0
            entry["volatility_pct"] = 0.0
        table.append(entry)
    return {"table": table}


def m_wealth_transfer_direction(data, config):
    """Net wealth flow from biased to corrective agents.

    Scenario-specific: hardcodes AnchoringEffect strategy group classification
    (biased = anchored-trader / historical-anchor / disposition-trader,
     corrective = rational-updater / fundamental-analyst / contrarian-trader).
    """
    payloads = data.get("investor_payloads")
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    final_price = float(prices[-1])
    # Use data_loader for standard config extraction
    from masim.evaluation.data_loader import per_agent_initial_cash, per_agent_initial_position
    initial_cash = per_agent_initial_cash(config)
    initial_positions = per_agent_initial_position(config)
    biased_wealth_change = 0.0
    corrective_wealth_change = 0.0
    for pid, round_payloads in payloads.items():
        if pid not in initial_cash or pid not in initial_positions:
            # Fail loudly rather than silently endow an unknown agent with
            # cash=0/position=0.  A default zero endowment silently zeroes
            # initial_wealth and turns the entire terminal-vs-initial delta
            # into a fabricated "profit" equal to the mark-to-market value —
            # exactly the class of null-hypothesis-coincident mock the audit
            # is eliminating.
            raise MetricUnavailable(
                f"agent {pid!r} appears in payloads but has no config entry "
                "(initial_cash / initial_position missing)"
            )
        cash = initial_cash[pid]
        position = initial_positions[pid]
        initial_wealth = cash + position * final_price
        strategy = None
        for payload in round_payloads.values():
            if strategy is None:
                strategy = payload.get("strategy")
            buy, sell = _payload_buy_sell(payload)
            # HOLD / skipped / clipped-to-zero records contribute nothing to
            # wealth arithmetic; skip them explicitly rather than dereferencing
            # a potentially absent bid_price with a silent final_price fallback.
            if buy == 0 and sell == 0:
                continue
            # Wire-format contract (masim.format.order.validate_order) requires
            # every non-hold order to carry bid_price > 0. A missing or
            # non-positive value here is a broken record; surface it as
            # MetricUnavailable rather than laundering it into wealth deltas.
            if "bid_price" not in payload:
                raise MetricUnavailable(
                    f"agent {pid!r} record has action-implied trade "
                    f"(buy={buy}, sell={sell}) but no bid_price — "
                    "wire-format contract violated"
                )
            bid = float(payload["bid_price"])
            if bid <= 0:
                raise MetricUnavailable(
                    f"agent {pid!r} record has action-implied trade "
                    f"(buy={buy}, sell={sell}) but bid_price={bid!r} "
                    "(must be strictly positive) — wire-format contract violated"
                )
            cash -= buy * bid
            cash += sell * bid
            position = position + buy - sell
        terminal_wealth = cash + position * final_price
        change = terminal_wealth - initial_wealth
        if strategy in BIASED_STRATEGIES:
            biased_wealth_change += change
        elif strategy in CORRECTIVE_STRATEGIES:
            corrective_wealth_change += change
    return {
        "biased_net_change": biased_wealth_change,
        "corrective_net_change": corrective_wealth_change,
        "transfer_to_corrective": corrective_wealth_change - biased_wealth_change,
    }


# ---------------------------------------------------------------------------
# REGISTRY — standard metrics first, then scenario-specific
# ---------------------------------------------------------------------------


REGISTRY = MetricsRegistry()

# Register all 36 standard metrics (price_dynamics, information_efficiency,
# statistical_inference, tail_risk, agent_behaviour, microstructure)
register_standard_metrics(REGISTRY)

# Scenario-specific: anchoring_specific (3)
REGISTRY.register(Metric(
    name="bias_magnitude_pct", category="anchoring_specific", fn=m_bias_magnitude_pct,
    output_keys=("value_pct", "alpha", "anchor_price", "fundamental_value"),
    references=("Tversky & Kahneman (1974)",),
    description="(1-alpha) * |anchor - F|/F using config initial_price.",
))
REGISTRY.register(Metric(
    name="anchor_dispersion", category="anchoring_specific", fn=m_anchor_dispersion,
    output_keys=("rounds", "dispersion_per_round", "mean_dispersion", "max_dispersion"),
    references=("Tversky & Kahneman (1974)",),
    description="Std of perceived_target across AnchoredTrader instances.",
))
REGISTRY.register(Metric(
    name="price_to_anchor_distance_ts", category="anchoring_specific", fn=m_price_to_anchor_distance_ts,
    output_keys=("rounds", "anchor_price", "distance_pct", "mean_abs_distance_pct"),
    references=("Tversky & Kahneman (1974)",),
    description="Percent distance of price from canonical anchor.",
))

# Scenario-specific: microstructure (2)
REGISTRY.register(Metric(
    name="corrective_to_biased_volume_ratio", category="microstructure",
    fn=m_corrective_to_biased_volume_ratio,
    output_keys=("value", "biased_volume", "corrective_volume"),
    references=("Shleifer & Vishny (1997)",),
    description="RU volume / (AT + HA) volume — limits to arbitrage proxy.",
))
REGISTRY.register(Metric(
    name="momentum_anchoring_coupling", category="microstructure",
    fn=m_momentum_anchoring_coupling,
    output_keys=("value",), references=("Hong & Stein (1999)",),
    description="Pearson corr between AT and MT net demand.",
))

# Scenario-specific: phase_decomposition (2)
REGISTRY.register(Metric(
    name="phase_assignment_ts", category="phase_decomposition", fn=m_phase_assignment_ts,
    output_keys=("phases", "phase_names", "total_rounds"),
    references=("analysis-bases.md §4",),
    description="Round-by-round assignment to anchoring phase 1..4.",
))
REGISTRY.register(Metric(
    name="per_phase_metrics_table", category="phase_decomposition", fn=m_per_phase_metrics_table,
    output_keys=("table",), references=("analysis-bases.md §4",),
    description="MAD, vol, return per detected anchoring phase.",
))

# Scenario-specific: wealth_dynamics (1)
REGISTRY.register(Metric(
    name="wealth_transfer_direction", category="wealth_dynamics",
    fn=m_wealth_transfer_direction,
    output_keys=("biased_net_change", "corrective_net_change", "transfer_to_corrective"),
    references=("Shleifer & Vishny (1997)",),
    description="Net wealth flow from biased to corrective agents.",
))


__all__ = ["REGISTRY", "Metric", "MetricsRegistry", "MetricUnavailable"]
