"""AnchoringEffect — Metric Catalogue.

This module owns *every* metric used by the AnchoringEffect analysis. Each
metric is a small function ``fn(data, config) -> dict`` registered into the
shared ``REGISTRY``. Adding a new metric requires only:

    1. Define the function (raising :class:`MetricUnavailable` if its inputs
       are not present).
    2. Append a ``REGISTRY.register(Metric(...))`` line at the bottom.

No driver edits, no signature changes — see the ``analysis.py`` files in the
four variant subpackages.

Data contract (built by ``examples.AnchoringEffect.Rule.analysis._load_data``)::

    data = {
        "market_prices":       {round: float},
        "fundamentals":        {round: float},
        "investor_quantities": {player_id: {round: float}},
        "investor_bids":       {player_id: {round: float}},
        "investor_payloads":   {player_id: {round: dict}},
    }

Each per-round payload dict contains at least ``action`` (``"buy"`` |
``"sell"`` | ``"hold"``), ``quantity`` (non-negative float), ``bid_price``
(float, may be 0 for ``hold``), ``investor`` (player id), and ``strategy``
(class name such as ``"AnchoredTrader"``).

Categories (per analysis-bases.md):

    price_dynamics, anchoring_specific, agent_behaviour, microstructure,
    statistical_inference, phase_decomposition.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np

from examples.AnchoringEffect.standard_rule_analysis import (
    Metric,
    MetricsRegistry,
    MetricUnavailable,
)


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------


def _series(values: Dict[int, float]) -> Tuple[List[int], np.ndarray]:
    """Return aligned (rounds, values) arrays sorted by round."""
    if not values:
        raise MetricUnavailable("series is empty")
    rounds = sorted(values)
    return rounds, np.asarray([float(values[r]) for r in rounds], dtype=float)


def _aligned_prices_and_fundamentals(data: Dict[str, Any]) -> Tuple[
    List[int], np.ndarray, np.ndarray
]:
    """Return (rounds, prices, fundamentals) aligned on the intersection."""
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    if not market_prices:
        raise MetricUnavailable("market_prices is empty")
    if not fundamentals:
        raise MetricUnavailable("fundamentals is empty")
    common = sorted(set(market_prices) & set(fundamentals))
    if not common:
        raise MetricUnavailable("market_prices and fundamentals share no rounds")
    prices = np.asarray([float(market_prices[r]) for r in common], dtype=float)
    funds = np.asarray([float(fundamentals[r]) for r in common], dtype=float)
    if np.any(funds == 0.0):
        raise MetricUnavailable("fundamental contains zero values")
    return common, prices, funds


def _returns(prices: np.ndarray) -> np.ndarray:
    """Arithmetic per-round returns; raises if fewer than two prices."""
    if prices.size < 2:
        raise MetricUnavailable("need at least two prices to compute returns")
    return (prices[1:] - prices[:-1]) / prices[:-1]


def _log_returns(prices: np.ndarray) -> np.ndarray:
    if prices.size < 2:
        raise MetricUnavailable("need at least two prices to compute log returns")
    return np.log(prices[1:] / prices[:-1])


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


def _payload_buy_sell(
    payload: Dict[str, Any],
) -> Tuple[float, float]:
    """Return (buy_qty, sell_qty) for a single payload using `action`.

    This is the corrected accounting: branch on ``action`` rather than the sign
    of ``quantity`` (the AnchoringEffect investor classes always emit
    non-negative quantities, so the legacy sign-based branch silently
    discarded all sells).
    """
    action = payload["action"]
    quantity = float(payload["quantity"])
    if quantity < 0:
        quantity = abs(quantity)
    if action == "buy":
        return quantity, 0.0
    if action == "sell":
        return 0.0, quantity
    return 0.0, 0.0


# ---------------------------------------------------------------------------
# Category 1 — price_dynamics
# ---------------------------------------------------------------------------


def m_price_deviation_ts(data, config):
    rounds, prices, funds = _aligned_prices_and_fundamentals(data)
    deviations = (prices - funds) / funds
    return {
        "rounds": rounds,
        "deviation_pct": (deviations * 100).tolist(),
        "max_abs_deviation_pct": float(np.max(np.abs(deviations)) * 100),
        "final_deviation_pct": float(deviations[-1] * 100),
    }


def m_mad_pct(data, config):
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    deviations = (prices - funds) / funds
    return {
        "value_pct": float(np.mean(np.abs(deviations)) * 100),
        "target_low_pct": 3.0,
        "target_high_pct": 10.0,
    }


def _half_life_threshold(prices: np.ndarray, fundamental: float) -> float:
    devs = np.abs((prices - fundamental) / fundamental)
    if devs[0] == 0:
        return 0.0
    target = devs[0] / 2.0
    for idx, dev in enumerate(devs):
        if dev <= target:
            return float(idx)
    return float(prices.size)


def m_half_life_threshold(data, config):
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    return {
        "value_rounds": _half_life_threshold(prices, float(funds.mean())),
        "method": "first round at which |deviation| <= 0.5 * |deviation_0|",
    }


def m_half_life_fitted(data, config):
    """Exponential decay regression of |deviation| onto round index."""
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    if prices.size < 5:
        raise MetricUnavailable("need >=5 rounds for exponential fit")
    devs = np.abs((prices - funds) / funds)
    # Avoid log(0); replace exact zeros with a tiny floor that won't dominate.
    floor = max(1e-6, float(np.max(devs)) * 1e-4)
    log_devs = np.log(np.maximum(devs, floor))
    rounds_idx = np.arange(prices.size, dtype=float)
    # log|D(t)| = log D0 - t / tau  =>  slope = -1/tau
    slope, intercept = np.polyfit(rounds_idx, log_devs, 1)
    if slope >= 0 or not np.isfinite(slope):
        # No decay detected; return NaN to flag failure.
        return {
            "value_rounds": float("nan"),
            "tau": float("nan"),
            "intercept_log_d0": float(intercept),
            "slope_per_round": float(slope),
            "method": "OLS log|deviation| vs. round; half_life = ln(2) * tau",
        }
    tau = -1.0 / float(slope)
    return {
        "value_rounds": float(np.log(2.0) * tau),
        "tau": float(tau),
        "intercept_log_d0": float(intercept),
        "slope_per_round": float(slope),
        "method": "OLS log|deviation| vs. round; half_life = ln(2) * tau",
    }


def m_rolling_volatility_ts(data, config):
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    if prices.size < 2:
        raise MetricUnavailable("need >=2 prices for volatility")
    returns_pct = (np.diff(prices) / prices[:-1]) * 100
    window = 10
    vols = []
    for i in range(returns_pct.size):
        start = max(0, i - window + 1)
        vols.append(float(np.std(returns_pct[start : i + 1])))
    return {"window": window, "rolling_vol_pct": vols}


def m_mean_volatility_pct(data, config):
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    return {
        "value_pct": float(np.std(returns) * 100),
        "target_low_pct": 0.5,
        "target_high_pct": 2.0,
    }


def m_max_drawdown_pct(data, config):
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    if prices.size < 2:
        raise MetricUnavailable("need >=2 prices for drawdown")
    peak = prices[0]
    worst = 0.0
    for price in prices:
        peak = max(peak, price)
        if peak > 0:
            dd = (peak - price) / peak
            if dd > worst:
                worst = dd
    return {
        "value_pct": float(-worst * 100),
        "target_low_pct": -20.0,
        "target_high_pct": -5.0,
    }


def m_return_skewness(data, config):
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    if returns.size < 3:
        raise MetricUnavailable("need >=3 returns for skewness")
    mean = float(np.mean(returns))
    std = float(np.std(returns))
    if std < 1e-12:
        raise MetricUnavailable("zero return variance")
    skew = float(np.mean(((returns - mean) / std) ** 3))
    return {"value": skew}


def m_return_kurtosis(data, config):
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    if returns.size < 4:
        raise MetricUnavailable("need >=4 returns for kurtosis")
    mean = float(np.mean(returns))
    std = float(np.std(returns))
    if std < 1e-12:
        raise MetricUnavailable("zero return variance")
    excess = float(np.mean(((returns - mean) / std) ** 4) - 3.0)
    return {"value_excess": excess}


def m_return_autocorr_lag1(data, config):
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    if returns.size < 3:
        raise MetricUnavailable("need >=3 returns for autocorrelation")
    centered = returns - float(np.mean(returns))
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero return variance")
    autocov = float(np.mean(centered[:-1] * centered[1:]))
    return {
        "value": autocov / var,
        "target_low": 0.0,
        "target_high": 0.30,
    }


def m_return_autocorr_profile(data, config):
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    max_lag = min(10, returns.size - 1)
    if max_lag < 1:
        raise MetricUnavailable("need >1 returns for autocorr profile")
    centered = returns - float(np.mean(returns))
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero return variance")
    profile = []
    for lag in range(1, max_lag + 1):
        autocov = float(np.mean(centered[:-lag] * centered[lag:]))
        profile.append(autocov / var)
    return {
        "lags": list(range(1, max_lag + 1)),
        "ac_values": profile,
    }


def m_variance_ratio_lo_mackinlay(data, config):
    """Lo & MacKinlay (1988) variance ratio test at periods 2, 4, 8."""
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    log_returns = _log_returns(prices)
    n = log_returns.size
    if n < 16:
        raise MetricUnavailable("need >=16 returns for variance-ratio test")
    var_1 = float(np.var(log_returns, ddof=0))
    if var_1 < 1e-18:
        raise MetricUnavailable("zero return variance")
    ratios = {}
    for q in (2, 4, 8):
        if n < q * 2:
            continue
        # Aggregate q-period log returns
        trimmed = log_returns[: (n // q) * q]
        agg = trimmed.reshape(-1, q).sum(axis=1)
        var_q = float(np.var(agg, ddof=0)) / q
        ratios[f"vr_q{q}"] = var_q / var_1
    if not ratios:
        raise MetricUnavailable("not enough rounds for any q")
    return {"interpretation": "1.0 = random walk; >1 momentum; <1 mean-reversion", **ratios}


# ---------------------------------------------------------------------------
# Category 2 — anchoring_specific
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
        "target_low_pct": 2.0,
        "target_high_pct": 5.0,
    }


def m_anchor_dispersion(data, config):
    """Standard deviation of perceived_target across AnchoredTrader instances.

    Requires `perceived_target` in each AT payload — currently not emitted by
    the Rule variant. Self-skips when missing so the registry keeps working.
    """
    payloads = data["investor_payloads"]
    targets_per_round: Dict[int, List[float]] = {}
    for pid, round_payloads in payloads.items():
        for round_num, payload in round_payloads.items():
            if payload.get("strategy") != "AnchoredTrader":
                continue
            if "perceived_target" not in payload:
                continue
            targets_per_round.setdefault(round_num, []).append(
                float(payload["perceived_target"])
            )
    if not targets_per_round:
        raise MetricUnavailable(
            "no AnchoredTrader payload contained `perceived_target`"
        )
    rounds_sorted = sorted(targets_per_round)
    dispersions = [float(np.std(targets_per_round[r])) for r in rounds_sorted]
    return {
        "rounds": rounds_sorted,
        "dispersion_per_round": dispersions,
        "mean_dispersion": float(np.mean(dispersions)),
        "max_dispersion": float(np.max(dispersions)),
    }


def m_under_revision_ratio(data, config):
    """Fraction of rounds in which sign(P - F) is the same as round 1."""
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    deviations = prices - funds
    initial_sign = np.sign(deviations[0])
    if initial_sign == 0:
        raise MetricUnavailable("initial deviation has zero sign")
    same_sign = float(np.mean(np.sign(deviations) == initial_sign))
    return {
        "value": same_sign,
        "interpretation": (
            "1.0 = price never crosses fundamental, indicating strong "
            "anchoring; <0.7 means corrective force is meaningful"
        ),
    }


def m_regime_transition_lag(data, config):
    """Round at which |deviation| first falls below 1%."""
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    deviations_pct = np.abs((prices - funds) / funds) * 100
    for idx, dev in enumerate(deviations_pct):
        if dev < 1.0:
            return {
                "value_rounds": idx,
                "threshold_pct": 1.0,
                "reached": True,
            }
    return {
        "value_rounds": int(prices.size),
        "threshold_pct": 1.0,
        "reached": False,
    }


def m_price_to_anchor_distance_ts(data, config):
    """Distance of market price from the canonical anchor (initial price)."""
    rounds, prices, _ = _aligned_prices_and_fundamentals(data)
    anchor = _initial_anchor(config)
    distance_pct = ((prices - anchor) / anchor * 100).tolist()
    return {
        "rounds": rounds,
        "anchor_price": anchor,
        "distance_pct": distance_pct,
        "mean_abs_distance_pct": float(np.mean(np.abs(distance_pct))),
    }


# ---------------------------------------------------------------------------
# Category 3 — agent_behaviour
# ---------------------------------------------------------------------------


def m_agent_volume_buy_sell(data, config):
    """Per-agent buy/sell volumes. Branches on payload['action'] (corrected)."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    per_agent: Dict[str, Dict[str, float]] = {}
    for pid, round_payloads in payloads.items():
        total_buy = 0.0
        total_sell = 0.0
        for payload in round_payloads.values():
            buy, sell = _payload_buy_sell(payload)
            total_buy += buy
            total_sell += sell
        per_agent[pid] = {
            "total_buy": total_buy,
            "total_sell": total_sell,
            "total_volume": total_buy + total_sell,
        }
    return {"per_agent": per_agent}


def m_agent_action_frequency(data, config):
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    per_agent: Dict[str, Dict[str, int]] = {}
    for pid, round_payloads in payloads.items():
        counts = {"buy": 0, "sell": 0, "hold": 0}
        for payload in round_payloads.values():
            action = payload["action"]
            counts[action] = counts.get(action, 0) + 1
        per_agent[pid] = counts
    return {"per_agent": per_agent}


def m_agent_net_position_ts(data, config):
    """Cumulative position evolution per agent (initial_position + Δ)."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    initial_positions = _per_agent_initial_position(config)
    per_agent: Dict[str, Dict[str, Any]] = {}
    for pid, round_payloads in payloads.items():
        rounds_sorted = sorted(round_payloads)
        position = float(initial_positions.get(pid, 0.0))
        positions = []
        for round_num in rounds_sorted:
            payload = round_payloads[round_num]
            buy, sell = _payload_buy_sell(payload)
            position = position + buy - sell
            positions.append(position)
        per_agent[pid] = {
            "rounds": rounds_sorted,
            "positions": positions,
            "final_position": position,
        }
    return {"per_agent": per_agent}


def _per_agent_initial_position(config: Dict[str, Any]) -> Dict[str, float]:
    """Inflate per-template initial_position into per-instance ids.

    Player names like ``anchored_trader`` with ``num_instances=2`` are expanded
    to ``anchored_trader_1`` and ``anchored_trader_2``.
    """
    initial: Dict[str, float] = {}
    for entry in config["players"].values():
        player_config = entry["config"]
        extras = player_config["extras"]
        if "initial_position" not in extras:
            continue
        identity = player_config["identity"]
        initial_position = float(extras["initial_position"])
        num_instances = int(entry.get("num_instances", 1))
        if num_instances <= 1:
            initial[identity] = initial_position
        else:
            for i in range(1, num_instances + 1):
                initial[f"{identity}_{i}"] = initial_position
    return initial


def _per_agent_initial_cash(config: Dict[str, Any]) -> Dict[str, float]:
    cash: Dict[str, float] = {}
    for entry in config["players"].values():
        player_config = entry["config"]
        extras = player_config["extras"]
        if "initial_cash" not in extras:
            continue
        identity = player_config["identity"]
        initial_cash = float(extras["initial_cash"])
        num_instances = int(entry.get("num_instances", 1))
        if num_instances <= 1:
            cash[identity] = initial_cash
        else:
            for i in range(1, num_instances + 1):
                cash[f"{identity}_{i}"] = initial_cash
    return cash


def m_agent_pnl_terminal(data, config):
    """Terminal mark-to-market PnL per agent.

    PnL = (final_cash - initial_cash) + final_position * final_price
          - initial_position * initial_price
    where ``final_cash`` is reconstructed from the trade tape using each
    payload's ``bid_price`` (or, if unavailable, the prevailing market price).
    """
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    market_prices = data["market_prices"]
    if not market_prices:
        raise MetricUnavailable("market_prices is empty")
    initial_cash = _per_agent_initial_cash(config)
    initial_position = _per_agent_initial_position(config)
    initial_price = _initial_anchor(config)
    final_round = max(market_prices)
    final_price = float(market_prices[final_round])
    per_agent: Dict[str, Dict[str, float]] = {}
    for pid, round_payloads in payloads.items():
        cash = float(initial_cash.get(pid, 0.0))
        position = float(initial_position.get(pid, 0.0))
        for round_num in sorted(round_payloads):
            payload = round_payloads[round_num]
            bid_price = float(payload.get("bid_price", 0.0)) or float(
                market_prices.get(round_num, 0.0)
            )
            buy, sell = _payload_buy_sell(payload)
            cash -= buy * bid_price
            cash += sell * bid_price
            position += buy - sell
        terminal_value = cash + position * final_price
        initial_value = float(initial_cash.get(pid, 0.0)) + float(
            initial_position.get(pid, 0.0)
        ) * initial_price
        per_agent[pid] = {
            "terminal_cash": cash,
            "terminal_position": position,
            "terminal_value": terminal_value,
            "initial_value": initial_value,
            "pnl": terminal_value - initial_value,
            "pnl_pct": (
                (terminal_value - initial_value) / initial_value * 100
                if initial_value > 0
                else 0.0
            ),
        }
    return {"per_agent": per_agent, "final_price": final_price}


def m_agent_sharpe_terminal(data, config):
    """Per-agent Sharpe = mean(round PnL) / std(round PnL) using bid_price tape."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    market_prices = data["market_prices"]
    if not market_prices:
        raise MetricUnavailable("market_prices is empty")
    initial_position = _per_agent_initial_position(config)
    per_agent: Dict[str, Dict[str, float]] = {}
    for pid, round_payloads in payloads.items():
        position = float(initial_position.get(pid, 0.0))
        prev_price = float(market_prices[min(market_prices)])
        round_pnl: List[float] = []
        for round_num in sorted(round_payloads):
            payload = round_payloads[round_num]
            price = float(market_prices.get(round_num, prev_price))
            mtm = position * (price - prev_price)
            buy, sell = _payload_buy_sell(payload)
            bid = float(payload.get("bid_price", 0.0)) or price
            trade_pnl = sell * (bid - price) - buy * (bid - price)
            round_pnl.append(mtm + trade_pnl)
            position = position + buy - sell
            prev_price = price
        if not round_pnl:
            continue
        mean_pnl = float(np.mean(round_pnl))
        std_pnl = float(np.std(round_pnl))
        sharpe = mean_pnl / std_pnl if std_pnl > 1e-12 else float("nan")
        per_agent[pid] = {
            "mean_round_pnl": mean_pnl,
            "std_round_pnl": std_pnl,
            "sharpe": sharpe,
        }
    return {"per_agent": per_agent}


def m_silent_agent_count(data, config):
    """Count agents whose total non-hold action count is zero."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    silent: List[str] = []
    for pid, round_payloads in payloads.items():
        traded = any(
            payload["action"] in ("buy", "sell")
            for payload in round_payloads.values()
        )
        if not traded:
            silent.append(pid)
    return {
        "silent_agents": silent,
        "silent_count": len(silent),
        "total_agents": len(payloads),
        "silent_ratio": len(silent) / len(payloads) if payloads else 0.0,
    }


# ---------------------------------------------------------------------------
# Category 4 — microstructure
# ---------------------------------------------------------------------------


def _per_round_signed_demand(payloads: Dict[str, Dict[int, dict]]) -> Dict[int, float]:
    """Net demand (buy - sell) per round, summed across all agents."""
    demand: Dict[int, float] = {}
    for round_payloads in payloads.values():
        for round_num, payload in round_payloads.items():
            buy, sell = _payload_buy_sell(payload)
            demand[round_num] = demand.get(round_num, 0.0) + (buy - sell)
    return demand


def _per_round_total_volume(payloads: Dict[str, Dict[int, dict]]) -> Dict[int, float]:
    volume: Dict[int, float] = {}
    for round_payloads in payloads.values():
        for round_num, payload in round_payloads.items():
            buy, sell = _payload_buy_sell(payload)
            volume[round_num] = volume.get(round_num, 0.0) + (buy + sell)
    return volume


def m_order_imbalance_ts(data, config):
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    demand = _per_round_signed_demand(payloads)
    volume = _per_round_total_volume(payloads)
    rounds = sorted(demand)
    imbalance = []
    for round_num in rounds:
        denom = volume[round_num]
        imbalance.append(demand[round_num] / denom if denom > 0 else 0.0)
    return {
        "rounds": rounds,
        "imbalance": imbalance,
        "mean_imbalance": float(np.mean(imbalance)) if imbalance else 0.0,
    }


def m_signed_volume_autocorr(data, config):
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    demand = _per_round_signed_demand(payloads)
    rounds = sorted(demand)
    if len(rounds) < 3:
        raise MetricUnavailable("need >=3 rounds for autocorrelation")
    series = np.asarray([demand[r] for r in rounds], dtype=float)
    centered = series - float(np.mean(series))
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero signed-volume variance")
    autocov = float(np.mean(centered[:-1] * centered[1:]))
    return {"value": autocov / var}


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


def m_corrective_to_biased_volume_ratio(data, config):
    """RationalUpdater absolute volume / (AnchoredTrader + HistoricalAnchor) absolute volume."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    biased_total = 0.0
    corrective_total = 0.0
    for round_payloads in payloads.values():
        for payload in round_payloads.values():
            strategy = payload.get("strategy")
            buy, sell = _payload_buy_sell(payload)
            volume = buy + sell
            if strategy in ("AnchoredTrader", "HistoricalAnchor"):
                biased_total += volume
            elif strategy == "RationalUpdater":
                corrective_total += volume
    if biased_total <= 0:
        raise MetricUnavailable("no biased agent volume recorded")
    ratio = corrective_total / biased_total
    return {
        "value": ratio,
        "biased_volume": biased_total,
        "corrective_volume": corrective_total,
        "interpretation": (
            "ratio > 1.0 means rational arbitrage outweighs anchoring "
            "demand; the AnchoringEffect calibration expects ratio < 1.0"
        ),
    }


def m_momentum_anchoring_coupling(data, config):
    """Pearson correlation between AT and MT net demand series."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    at_demand = _strategy_demand(payloads, {"AnchoredTrader"})
    mt_demand = _strategy_demand(payloads, {"MomentumTrader"})
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
    return {
        "value": corr,
        "interpretation": (
            "positive correlation = MT amplifies AT-induced drift; "
            "AnchoringEffect calibration expects mild positive coupling"
        ),
    }


# ---------------------------------------------------------------------------
# Category 5 — statistical_inference
# ---------------------------------------------------------------------------


def _block_bootstrap_indices(n: int, block: int, num: int) -> np.ndarray:
    """Generate (num, n) array of moving-block-bootstrap indices."""
    rng = np.random.default_rng(42)
    indices = np.empty((num, n), dtype=int)
    for sim in range(num):
        out = []
        while len(out) < n:
            start = rng.integers(0, n - block + 1)
            out.extend(range(start, start + block))
        indices[sim] = out[:n]
    return indices


def m_mad_block_bootstrap_ci_95(data, config):
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    if prices.size < 30:
        raise MetricUnavailable("need >=30 rounds for bootstrap")
    devs = np.abs((prices - funds) / funds)
    block = max(5, int(round(prices.size ** (1 / 3))))
    indices = _block_bootstrap_indices(prices.size, block, num=500)
    mad_samples = np.mean(devs[indices], axis=1) * 100
    return {
        "mean_pct": float(np.mean(mad_samples)),
        "ci95_low_pct": float(np.percentile(mad_samples, 2.5)),
        "ci95_high_pct": float(np.percentile(mad_samples, 97.5)),
        "block_length": block,
        "num_replicates": 500,
    }


def m_half_life_block_bootstrap_ci_95(data, config):
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    if prices.size < 30:
        raise MetricUnavailable("need >=30 rounds for bootstrap")
    devs = np.abs((prices - funds) / funds)
    floor = max(1e-6, float(np.max(devs)) * 1e-4)
    log_devs = np.log(np.maximum(devs, floor))
    rounds_idx = np.arange(prices.size, dtype=float)
    block = max(5, int(round(prices.size ** (1 / 3))))
    indices = _block_bootstrap_indices(prices.size, block, num=500)
    halves = []
    for sample_idx in indices:
        slope, _ = np.polyfit(rounds_idx, log_devs[sample_idx], 1)
        if slope >= 0 or not np.isfinite(slope):
            continue
        halves.append(float(np.log(2.0) / -slope))
    if len(halves) < 50:
        raise MetricUnavailable(
            "insufficient bootstrap samples produced finite half-life"
        )
    halves_arr = np.asarray(halves)
    return {
        "mean_rounds": float(np.mean(halves_arr)),
        "ci95_low_rounds": float(np.percentile(halves_arr, 2.5)),
        "ci95_high_rounds": float(np.percentile(halves_arr, 97.5)),
        "valid_replicates": len(halves),
        "block_length": block,
    }


def m_ljung_box_returns_pvalue(data, config):
    """Ljung-Box Q-statistic at lag 10; null = no autocorrelation."""
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    n = returns.size
    if n < 20:
        raise MetricUnavailable("need >=20 returns for Ljung-Box")
    mean = float(np.mean(returns))
    centered = returns - mean
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero return variance")
    max_lag = 10
    q_stat = 0.0
    for lag in range(1, max_lag + 1):
        autocov = float(np.mean(centered[:-lag] * centered[lag:]))
        rho = autocov / var
        q_stat += rho * rho / (n - lag)
    q_stat *= n * (n + 2)
    # Asymptotic chi-square(max_lag) survival function via series approximation.
    p_value = _chi2_sf(q_stat, df=max_lag)
    return {
        "q_statistic": q_stat,
        "max_lag": max_lag,
        "p_value": float(p_value),
        "interpretation": (
            "p < 0.05 rejects the null of no autocorrelation in returns; "
            "anchoring scenarios typically show p < 0.10"
        ),
    }


def _chi2_sf(x: float, df: int) -> float:
    """Survival function of chi-square via the regularized upper gamma series.

    Avoids a SciPy dependency. Uses the relation ``sf = Q(df/2, x/2)``.
    """
    if x <= 0:
        return 1.0
    a = df / 2.0
    return float(_gammaincc(a, x / 2.0))


def _gammaincc(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x).

    Computed via the lower-series for x < a + 1, otherwise the
    Lentz continued-fraction expansion. Sufficient accuracy for tail tests.
    """
    import math

    if x < 0 or a <= 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1.0:
        # Lower series
        ap = a
        summand = 1.0 / a
        delta = summand
        for _ in range(200):
            ap += 1.0
            delta *= x / ap
            summand += delta
            if abs(delta) < abs(summand) * 1e-12:
                break
        gamser = summand * math.exp(-x + a * math.log(x) - gln)
        return 1.0 - gamser
    # Continued fraction
    b = x + 1.0 - a
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 201):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-300:
            d = 1e-300
        c = b + an / c
        if abs(c) < 1e-300:
            c = 1e-300
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def m_adf_unit_root_pvalue(data, config):
    """OLS-based augmented Dickey-Fuller t-statistic on price series.

    The exact MacKinnon p-values are not reproduced (no SciPy / statsmodels);
    we report the t-statistic and a coarse approximate p-value derived from
    the standard normal tail (conservative). A negative t below approx -2.86
    rejects the unit-root null at 5%.
    """
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    if prices.size < 30:
        raise MetricUnavailable("need >=30 rounds for ADF")
    delta_p = np.diff(prices)
    p_lag = prices[:-1]
    # Simple ADF(0): Δp_t = α + β p_{t-1} + ε_t
    x = np.column_stack([np.ones_like(p_lag), p_lag])
    beta, _residuals, _rank, _sv = np.linalg.lstsq(x, delta_p, rcond=None)
    fitted = x @ beta
    resid = delta_p - fitted
    n = delta_p.size
    sigma2 = float(np.sum(resid * resid)) / max(n - 2, 1)
    xtx_inv = np.linalg.inv(x.T @ x)
    se_beta1 = float(np.sqrt(sigma2 * xtx_inv[1, 1]))
    if se_beta1 < 1e-12:
        raise MetricUnavailable("ADF standard error degenerate")
    t_stat = float(beta[1] / se_beta1)
    # Conservative normal-tail p-value (one-sided lower):
    # p = Phi(t_stat) where Phi is the standard normal CDF.
    p_value = 0.5 * (1.0 + _erf(t_stat / np.sqrt(2.0)))
    return {
        "t_statistic": t_stat,
        "approx_p_value": float(p_value),
        "interpretation": (
            "Approximate one-sided p (normal tail; not MacKinnon). "
            "t_stat below -2.86 generally rejects the unit-root null."
        ),
    }


def _erf(x: float) -> float:
    """Abramowitz-Stegun 7.1.26 approximation; |error| < 1.5e-7."""
    import math

    sign = 1.0 if x >= 0 else -1.0
    x_abs = abs(x)
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    t = 1.0 / (1.0 + p * x_abs)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(
        -x_abs * x_abs
    )
    return sign * y


# ---------------------------------------------------------------------------
# Category 6 — phase_decomposition (analysis-bases.md §4)
# ---------------------------------------------------------------------------


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
        # Phase 1 -> 2 transition: stable above threshold for 5 rounds OR i >= 10
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


def m_phase_assignment_ts(data, config):
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
        # Returns are aligned with diff so its index range is start ... end-1
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


# ---------------------------------------------------------------------------
# Category 7 — wealth_dynamics
# ---------------------------------------------------------------------------


def m_agent_wealth_terminal(data, config):
    """Final portfolio value = cash + position * final_price per agent."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    final_price = float(prices[-1])
    initial_cash = _per_agent_initial_cash(config)
    initial_positions = _per_agent_initial_position(config)
    per_agent: Dict[str, Dict[str, Any]] = {}
    for pid, round_payloads in payloads.items():
        cash = initial_cash.get(pid, 0.0)
        position = initial_positions.get(pid, 0.0)
        rounds_sorted = sorted(round_payloads)
        for round_num in rounds_sorted:
            payload = round_payloads[round_num]
            buy, sell = _payload_buy_sell(payload)
            bid = float(payload.get("bid_price", final_price))
            cash -= buy * bid
            cash += sell * bid
            position = position + buy - sell
        wealth = cash + position * final_price
        per_agent[pid] = {
            "cash": cash,
            "position": position,
            "wealth": wealth,
            "final_price": final_price,
        }
    return {"per_agent": per_agent, "final_price": final_price}


def m_gini_coefficient(data, config):
    """Gini index of terminal wealth across agents (0=equal, 1=concentrated)."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    final_price = float(prices[-1])
    initial_cash = _per_agent_initial_cash(config)
    initial_positions = _per_agent_initial_position(config)
    wealths = []
    for pid, round_payloads in payloads.items():
        cash = initial_cash.get(pid, 0.0)
        position = initial_positions.get(pid, 0.0)
        for payload in round_payloads.values():
            buy, sell = _payload_buy_sell(payload)
            bid = float(payload.get("bid_price", final_price))
            cash -= buy * bid
            cash += sell * bid
            position = position + buy - sell
        wealths.append(cash + position * final_price)
    wealths_arr = np.sort(np.asarray(wealths, dtype=float))
    n = wealths_arr.size
    if n < 2 or np.sum(wealths_arr) <= 0:
        raise MetricUnavailable("insufficient wealth data for Gini")
    index = np.arange(1, n + 1)
    gini = float((2.0 * np.sum(index * wealths_arr) / (n * np.sum(wealths_arr))) - (n + 1) / n)
    return {"value": max(0.0, gini), "n_agents": n}


def m_wealth_transfer_direction(data, config):
    """Net wealth change from biased agents to rational/corrective agents."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    final_price = float(prices[-1])
    initial_cash = _per_agent_initial_cash(config)
    initial_positions = _per_agent_initial_position(config)
    biased_strategies = {"AnchoredTrader", "HistoricalAnchor", "DispositionTrader"}
    corrective_strategies = {"RationalUpdater", "FundamentalAnalyst", "ContrarianTrader"}
    biased_wealth_change = 0.0
    corrective_wealth_change = 0.0
    for pid, round_payloads in payloads.items():
        cash = initial_cash.get(pid, 0.0)
        position = initial_positions.get(pid, 0.0)
        initial_wealth = cash + position * final_price
        strategy = None
        for payload in round_payloads.values():
            buy, sell = _payload_buy_sell(payload)
            bid = float(payload.get("bid_price", final_price))
            cash -= buy * bid
            cash += sell * bid
            position = position + buy - sell
            if strategy is None:
                strategy = payload.get("strategy")
        terminal_wealth = cash + position * final_price
        change = terminal_wealth - initial_wealth
        if strategy in biased_strategies:
            biased_wealth_change += change
        elif strategy in corrective_strategies:
            corrective_wealth_change += change
    return {
        "biased_net_change": biased_wealth_change,
        "corrective_net_change": corrective_wealth_change,
        "transfer_to_corrective": corrective_wealth_change - biased_wealth_change,
        "interpretation": (
            "positive transfer_to_corrective means rational agents captured "
            "wealth from biased agents — expected in anchoring scenarios"
        ),
    }


# ---------------------------------------------------------------------------
# Category 8 — information_efficiency
# ---------------------------------------------------------------------------


def m_price_efficiency_ratio(data, config):
    """Var(price_change) / Var(F - P_prev); closer to 1.0 = more efficient."""
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    if prices.size < 10:
        raise MetricUnavailable("need >=10 rounds for efficiency ratio")
    price_changes = np.diff(prices)
    mispricing = funds[:-1] - prices[:-1]
    var_change = float(np.var(price_changes))
    var_misprice = float(np.var(mispricing))
    if var_misprice < 1e-12:
        raise MetricUnavailable("zero mispricing variance")
    ratio = var_change / var_misprice
    return {
        "value": ratio,
        "interpretation": (
            "ratio = 1.0: price changes fully reflect mispricing (efficient); "
            "ratio << 1: sluggish correction (anchoring-dominated); "
            "ratio >> 1: over-correction"
        ),
    }


def m_forecast_error_persistence(data, config):
    """Lag-1 autocorrelation of the deviation series (not returns)."""
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    deviations = (prices - funds) / funds
    if deviations.size < 10:
        raise MetricUnavailable("need >=10 rounds for deviation persistence")
    centered = deviations - float(np.mean(deviations))
    var = float(np.var(centered))
    if var < 1e-12:
        raise MetricUnavailable("zero deviation variance")
    autocov = float(np.mean(centered[:-1] * centered[1:]))
    return {
        "value": autocov / var,
        "interpretation": (
            "high persistence (>0.8) = market not learning; "
            "declining toward 0 over time = information incorporation"
        ),
    }


def m_deviation_decay_slope(data, config):
    """OLS slope of |deviation| on round number (negative = converging)."""
    rounds, prices, funds = _aligned_prices_and_fundamentals(data)
    if prices.size < 10:
        raise MetricUnavailable("need >=10 rounds for decay slope")
    abs_dev = np.abs((prices - funds) / funds)
    x = np.arange(abs_dev.size, dtype=float)
    slope, intercept = np.polyfit(x, abs_dev, 1)
    return {
        "slope_per_round": float(slope),
        "intercept": float(intercept),
        "interpretation": (
            "negative slope = mispricing shrinking over time; "
            "slope ~0 = no correction"
        ),
    }


def m_information_share_by_strategy(data, config):
    """Fraction of total corrective volume by each stabilizing strategy."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    _, prices, funds = _aligned_prices_and_fundamentals(data)
    # Corrective = selling when P > F or buying when P < F
    strategy_corrective: Dict[str, float] = {}
    total_corrective = 0.0
    for round_payloads in payloads.values():
        for round_num, payload in round_payloads.items():
            if round_num not in data["market_prices"] or round_num not in data["fundamentals"]:
                continue
            price = float(data["market_prices"][round_num])
            fundamental = float(data["fundamentals"][round_num])
            buy, sell = _payload_buy_sell(payload)
            strategy = payload.get("strategy", "unknown")
            corrective_vol = 0.0
            if price > fundamental:
                corrective_vol = sell
            elif price < fundamental:
                corrective_vol = buy
            if corrective_vol > 0:
                strategy_corrective[strategy] = strategy_corrective.get(strategy, 0.0) + corrective_vol
                total_corrective += corrective_vol
    if total_corrective <= 0:
        raise MetricUnavailable("no corrective volume detected")
    shares = {k: v / total_corrective for k, v in strategy_corrective.items()}
    return {
        "shares": shares,
        "total_corrective_volume": total_corrective,
    }


# ---------------------------------------------------------------------------
# Category 9 — tail_risk_and_concentration
# ---------------------------------------------------------------------------


def m_value_at_risk_95(data, config):
    """5th percentile of per-round returns (left tail risk)."""
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    returns = _returns(prices)
    if returns.size < 20:
        raise MetricUnavailable("need >=20 returns for VaR")
    var_95 = float(np.percentile(returns * 100, 5.0))
    return {
        "value_pct": var_95,
        "interpretation": "5th percentile of returns; more negative = higher tail risk",
    }


def m_conditional_var_95(data, config):
    """Expected shortfall: mean of returns below VaR-95."""
    _, prices, _ = _aligned_prices_and_fundamentals(data)
    returns = _returns(prices) * 100
    if returns.size < 20:
        raise MetricUnavailable("need >=20 returns for CVaR")
    threshold = float(np.percentile(returns, 5.0))
    tail = returns[returns <= threshold]
    if tail.size == 0:
        raise MetricUnavailable("no returns below VaR threshold")
    return {
        "value_pct": float(np.mean(tail)),
        "var_95_pct": threshold,
        "n_tail_obs": int(tail.size),
    }


def m_herfindahl_volume_concentration(data, config):
    """HHI of volume across agents (0=dispersed, 1=one agent dominates)."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    agent_volumes = []
    for round_payloads in payloads.values():
        vol = 0.0
        for payload in round_payloads.values():
            buy, sell = _payload_buy_sell(payload)
            vol += buy + sell
        agent_volumes.append(vol)
    total = sum(agent_volumes)
    if total <= 0:
        raise MetricUnavailable("no trading volume")
    shares = [v / total for v in agent_volumes]
    hhi = float(sum(s * s for s in shares))
    return {
        "value": hhi,
        "n_agents": len(agent_volumes),
        "interpretation": (
            "HHI near 1/N = dispersed; HHI near 1.0 = one agent dominates"
        ),
    }


def m_strategy_correlation_matrix(data, config):
    """Pairwise Pearson correlation of net demand between strategy types."""
    payloads = data["investor_payloads"]
    if not payloads:
        raise MetricUnavailable("no investor payloads recorded")
    # Aggregate demand by strategy per round
    strategy_demand: Dict[str, Dict[int, float]] = {}
    for round_payloads in payloads.values():
        for round_num, payload in round_payloads.items():
            strategy = payload.get("strategy", "unknown")
            buy, sell = _payload_buy_sell(payload)
            net = buy - sell
            if strategy not in strategy_demand:
                strategy_demand[strategy] = {}
            strategy_demand[strategy][round_num] = (
                strategy_demand[strategy].get(round_num, 0.0) + net
            )
    strategies = sorted(strategy_demand)
    if len(strategies) < 2:
        raise MetricUnavailable("need >=2 strategies for correlation matrix")
    # Align on common rounds
    common_rounds = set.intersection(
        *(set(strategy_demand[s]) for s in strategies)
    )
    if len(common_rounds) < 10:
        raise MetricUnavailable("need >=10 common rounds for correlation")
    common_sorted = sorted(common_rounds)
    matrix: Dict[str, Dict[str, float]] = {}
    arrays = {
        s: np.asarray([strategy_demand[s][r] for r in common_sorted], dtype=float)
        for s in strategies
    }
    for s1 in strategies:
        row: Dict[str, float] = {}
        for s2 in strategies:
            if np.std(arrays[s1]) < 1e-12 or np.std(arrays[s2]) < 1e-12:
                row[s2] = 0.0
            else:
                row[s2] = float(np.corrcoef(arrays[s1], arrays[s2])[0, 1])
        matrix[s1] = row
    return {"matrix": matrix, "strategies": strategies, "n_rounds": len(common_sorted)}


# ---------------------------------------------------------------------------
# REGISTRY — order is important: it controls plot order and JSON ordering.
# ---------------------------------------------------------------------------


REGISTRY = MetricsRegistry()


# Category 1 — price_dynamics (12)
REGISTRY.register(Metric(
    name="price_deviation_ts",
    category="price_dynamics",
    fn=m_price_deviation_ts,
    output_keys=("rounds", "deviation_pct", "max_abs_deviation_pct", "final_deviation_pct"),
    references=("Campbell & Sharpe (2009)",),
    description="Signed (P-F)/F deviation per round.",
))
REGISTRY.register(Metric(
    name="mad_pct",
    category="price_dynamics",
    fn=m_mad_pct,
    output_keys=("value_pct", "target_low_pct", "target_high_pct"),
    references=("Campbell & Sharpe (2009)",),
    description="Time-averaged |deviation|; primary anchoring magnitude.",
))
REGISTRY.register(Metric(
    name="half_life_threshold",
    category="price_dynamics",
    fn=m_half_life_threshold,
    output_keys=("value_rounds", "method"),
    references=("Campbell & Sharpe (2009)",),
    description="First round at which |deviation| falls below half its initial value (advisory).",
))
REGISTRY.register(Metric(
    name="half_life_fitted",
    category="price_dynamics",
    fn=m_half_life_fitted,
    output_keys=("value_rounds", "tau", "intercept_log_d0", "slope_per_round", "method"),
    references=("Fama & French (1988)", "Campbell & Sharpe (2009)"),
    description="Half-life from OLS exponential decay fit on log|deviation|.",
))
REGISTRY.register(Metric(
    name="rolling_volatility_ts",
    category="price_dynamics",
    fn=m_rolling_volatility_ts,
    output_keys=("window", "rolling_vol_pct"),
    references=("Andersen, Bollerslev, Diebold & Labys (2003)",),
    description="10-round rolling std of percent returns.",
))
REGISTRY.register(Metric(
    name="mean_volatility_pct",
    category="price_dynamics",
    fn=m_mean_volatility_pct,
    output_keys=("value_pct", "target_low_pct", "target_high_pct"),
    references=("Black (1986)",),
    description="Std of full-sample percent returns.",
))
REGISTRY.register(Metric(
    name="max_drawdown_pct",
    category="price_dynamics",
    fn=m_max_drawdown_pct,
    output_keys=("value_pct", "target_low_pct", "target_high_pct"),
    references=("Northcraft & Neale (1987)",),
    description="Worst peak-to-trough percent decline.",
))
REGISTRY.register(Metric(
    name="return_skewness",
    category="price_dynamics",
    fn=m_return_skewness,
    output_keys=("value",),
    references=("Cont (2001) — Empirical properties of asset returns",),
    description="Sample skewness of percent returns.",
))
REGISTRY.register(Metric(
    name="return_kurtosis",
    category="price_dynamics",
    fn=m_return_kurtosis,
    output_keys=("value_excess",),
    references=("Cont (2001)",),
    description="Excess kurtosis of percent returns (0 = Gaussian).",
))
REGISTRY.register(Metric(
    name="return_autocorr_lag1",
    category="price_dynamics",
    fn=m_return_autocorr_lag1,
    output_keys=("value", "target_low", "target_high"),
    references=("Lo & MacKinlay (1988)",),
    description="Lag-1 autocorrelation of percent returns.",
))
REGISTRY.register(Metric(
    name="return_autocorr_profile",
    category="price_dynamics",
    fn=m_return_autocorr_profile,
    output_keys=("lags", "ac_values"),
    references=("Lo & MacKinlay (1988)",),
    description="Autocorrelation at lags 1..10.",
))
REGISTRY.register(Metric(
    name="variance_ratio_lo_mackinlay",
    category="price_dynamics",
    fn=m_variance_ratio_lo_mackinlay,
    output_keys=("interpretation",),
    references=("Lo & MacKinlay (1988)",),
    description="Variance ratios at periods 2/4/8 — random walk test.",
))


# Category 2 — anchoring_specific (5)
REGISTRY.register(Metric(
    name="bias_magnitude_pct",
    category="anchoring_specific",
    fn=m_bias_magnitude_pct,
    output_keys=("value_pct", "alpha", "anchor_price", "fundamental_value",
                 "target_low_pct", "target_high_pct"),
    references=("Tversky & Kahneman (1974)",),
    description="(1-alpha) * |anchor - F|/F using config initial_price.",
))
REGISTRY.register(Metric(
    name="anchor_dispersion",
    category="anchoring_specific",
    fn=m_anchor_dispersion,
    output_keys=("rounds", "dispersion_per_round", "mean_dispersion", "max_dispersion"),
    references=("Tversky & Kahneman (1974)",),
    description="Std of perceived_target across AnchoredTrader instances (requires payload field).",
))
REGISTRY.register(Metric(
    name="under_revision_ratio",
    category="anchoring_specific",
    fn=m_under_revision_ratio,
    output_keys=("value", "interpretation"),
    references=("Campbell & Sharpe (2009)",),
    description="Fraction of rounds where sign(P-F) matches initial sign.",
))
REGISTRY.register(Metric(
    name="regime_transition_lag",
    category="anchoring_specific",
    fn=m_regime_transition_lag,
    output_keys=("value_rounds", "threshold_pct", "reached"),
    references=("Campbell & Sharpe (2009)",),
    description="First round where |deviation| < 1%.",
))
REGISTRY.register(Metric(
    name="price_to_anchor_distance_ts",
    category="anchoring_specific",
    fn=m_price_to_anchor_distance_ts,
    output_keys=("rounds", "anchor_price", "distance_pct", "mean_abs_distance_pct"),
    references=("Tversky & Kahneman (1974)",),
    description="Percent distance of price from canonical anchor.",
))


# Category 3 — agent_behaviour (6)
REGISTRY.register(Metric(
    name="agent_volume_buy_sell",
    category="agent_behaviour",
    fn=m_agent_volume_buy_sell,
    output_keys=("per_agent",),
    references=("Black (1986)", "Grossman & Stiglitz (1980)"),
    description="Per-agent buy/sell/total volume from corrected action accounting.",
))
REGISTRY.register(Metric(
    name="agent_action_frequency",
    category="agent_behaviour",
    fn=m_agent_action_frequency,
    output_keys=("per_agent",),
    references=("Glosten & Milgrom (1985)",),
    description="Per-agent {buy, sell, hold} action counts.",
))
REGISTRY.register(Metric(
    name="agent_net_position_ts",
    category="agent_behaviour",
    fn=m_agent_net_position_ts,
    output_keys=("per_agent",),
    references=("Glosten & Milgrom (1985)",),
    description="Cumulative position over time per agent.",
))
REGISTRY.register(Metric(
    name="agent_pnl_terminal",
    category="agent_behaviour",
    fn=m_agent_pnl_terminal,
    output_keys=("per_agent", "final_price"),
    references=("De Bondt & Thaler (1985)",),
    description="Per-agent terminal mark-to-market PnL.",
))
REGISTRY.register(Metric(
    name="agent_sharpe_terminal",
    category="agent_behaviour",
    fn=m_agent_sharpe_terminal,
    output_keys=("per_agent",),
    references=("Sharpe (1966) — Mutual fund performance",),
    description="Per-agent Sharpe ratio of round-PnL series.",
))
REGISTRY.register(Metric(
    name="silent_agent_count",
    category="agent_behaviour",
    fn=m_silent_agent_count,
    output_keys=("silent_agents", "silent_count", "total_agents", "silent_ratio"),
    references=("analysis-bases.md §2 red-flag rule",),
    description="Number of agents that never traded; expected 0.",
))


# Category 4 — microstructure (4)
REGISTRY.register(Metric(
    name="order_imbalance_ts",
    category="microstructure",
    fn=m_order_imbalance_ts,
    output_keys=("rounds", "imbalance", "mean_imbalance"),
    references=("Chordia, Roll & Subrahmanyam (2002)",),
    description="Net signed demand normalised by gross volume per round.",
))
REGISTRY.register(Metric(
    name="signed_volume_autocorr",
    category="microstructure",
    fn=m_signed_volume_autocorr,
    output_keys=("value",),
    references=("Hasbrouck (1991)",),
    description="Lag-1 autocorrelation of net signed demand.",
))
REGISTRY.register(Metric(
    name="corrective_to_biased_volume_ratio",
    category="microstructure",
    fn=m_corrective_to_biased_volume_ratio,
    output_keys=("value", "biased_volume", "corrective_volume", "interpretation"),
    references=("Shleifer & Vishny (1997)",),
    description="RU volume / (AT + HA) volume — limits to arbitrage proxy.",
))
REGISTRY.register(Metric(
    name="momentum_anchoring_coupling",
    category="microstructure",
    fn=m_momentum_anchoring_coupling,
    output_keys=("value", "interpretation"),
    references=("Hong & Stein (1999)",),
    description="Pearson corr between AT and MT net demand.",
))


# Category 5 — statistical_inference (4)
REGISTRY.register(Metric(
    name="mad_block_bootstrap_ci_95",
    category="statistical_inference",
    fn=m_mad_block_bootstrap_ci_95,
    output_keys=("mean_pct", "ci95_low_pct", "ci95_high_pct",
                 "block_length", "num_replicates"),
    references=("Politis & Romano (1994)",),
    description="Moving-block bootstrap 95% CI for MAD.",
))
REGISTRY.register(Metric(
    name="half_life_block_bootstrap_ci_95",
    category="statistical_inference",
    fn=m_half_life_block_bootstrap_ci_95,
    output_keys=("mean_rounds", "ci95_low_rounds", "ci95_high_rounds",
                 "valid_replicates", "block_length"),
    references=("Politis & Romano (1994)",),
    description="Moving-block bootstrap 95% CI for fitted half-life.",
))
REGISTRY.register(Metric(
    name="ljung_box_returns_pvalue",
    category="statistical_inference",
    fn=m_ljung_box_returns_pvalue,
    output_keys=("q_statistic", "max_lag", "p_value", "interpretation"),
    references=("Ljung & Box (1978)",),
    description="Q-statistic for return autocorrelation up to lag 10.",
))
REGISTRY.register(Metric(
    name="adf_unit_root_pvalue",
    category="statistical_inference",
    fn=m_adf_unit_root_pvalue,
    output_keys=("t_statistic", "approx_p_value", "interpretation"),
    references=("Dickey & Fuller (1979)", "MacKinnon (1991)"),
    description="ADF(0) unit-root statistic on price series.",
))


# Category 6 — phase_decomposition (2)
REGISTRY.register(Metric(
    name="phase_assignment_ts",
    category="phase_decomposition",
    fn=m_phase_assignment_ts,
    output_keys=("phases", "phase_names", "total_rounds"),
    references=("analysis-bases.md §4",),
    description="Round-by-round assignment to phase 1..4.",
))
REGISTRY.register(Metric(
    name="per_phase_metrics_table",
    category="phase_decomposition",
    fn=m_per_phase_metrics_table,
    output_keys=("table",),
    references=("analysis-bases.md §4",),
    description="MAD, vol, return per detected phase.",
))


# Category 7 — wealth_dynamics (3)
REGISTRY.register(Metric(
    name="agent_wealth_terminal",
    category="wealth_dynamics",
    fn=m_agent_wealth_terminal,
    output_keys=("per_agent", "final_price"),
    references=("De Bondt & Thaler (1985)",),
    description="Final portfolio value (cash + position * final_price) per agent.",
))
REGISTRY.register(Metric(
    name="gini_coefficient",
    category="wealth_dynamics",
    fn=m_gini_coefficient,
    output_keys=("value", "n_agents"),
    references=("Gini (1912)",),
    description="Wealth concentration index at terminal round.",
))
REGISTRY.register(Metric(
    name="wealth_transfer_direction",
    category="wealth_dynamics",
    fn=m_wealth_transfer_direction,
    output_keys=("biased_net_change", "corrective_net_change",
                 "transfer_to_corrective", "interpretation"),
    references=("Shleifer & Vishny (1997)",),
    description="Net wealth flow from biased (AT+HA+DT) to corrective (RU+FA+CT) agents.",
))


# Category 8 — information_efficiency (4)
REGISTRY.register(Metric(
    name="price_efficiency_ratio",
    category="information_efficiency",
    fn=m_price_efficiency_ratio,
    output_keys=("value", "interpretation"),
    references=("Fama (1970)",),
    description="Var(price_change)/Var(mispricing); 1.0 = efficient market.",
))
REGISTRY.register(Metric(
    name="forecast_error_persistence",
    category="information_efficiency",
    fn=m_forecast_error_persistence,
    output_keys=("value", "interpretation"),
    references=("Campbell & Sharpe (2009)",),
    description="Lag-1 autocorrelation of deviation series (not returns).",
))
REGISTRY.register(Metric(
    name="deviation_decay_slope",
    category="information_efficiency",
    fn=m_deviation_decay_slope,
    output_keys=("slope_per_round", "intercept", "interpretation"),
    references=("Fama & French (1988)",),
    description="OLS slope of |deviation| on round number; negative = converging.",
))
REGISTRY.register(Metric(
    name="information_share_by_strategy",
    category="information_efficiency",
    fn=m_information_share_by_strategy,
    output_keys=("shares", "total_corrective_volume"),
    references=("Grossman & Stiglitz (1980)",),
    description="Fraction of total corrective volume by each stabilizing strategy.",
))


# Category 9 — tail_risk_and_concentration (4)
REGISTRY.register(Metric(
    name="value_at_risk_95",
    category="tail_risk_and_concentration",
    fn=m_value_at_risk_95,
    output_keys=("value_pct", "interpretation"),
    references=("Jorion (2006) — Value at Risk",),
    description="5th percentile of per-round returns (left tail).",
))
REGISTRY.register(Metric(
    name="conditional_var_95",
    category="tail_risk_and_concentration",
    fn=m_conditional_var_95,
    output_keys=("value_pct", "var_95_pct", "n_tail_obs"),
    references=("Artzner et al. (1999) — Coherent measures of risk",),
    description="Mean of returns below VaR-95 (expected shortfall).",
))
REGISTRY.register(Metric(
    name="herfindahl_volume_concentration",
    category="tail_risk_and_concentration",
    fn=m_herfindahl_volume_concentration,
    output_keys=("value", "n_agents", "interpretation"),
    references=("Hirschman (1945)",),
    description="HHI of volume across agents; 1/N = dispersed.",
))
REGISTRY.register(Metric(
    name="strategy_correlation_matrix",
    category="tail_risk_and_concentration",
    fn=m_strategy_correlation_matrix,
    output_keys=("matrix", "strategies", "n_rounds"),
    references=("Hong & Stein (1999)",),
    description="Pairwise Pearson corr of net demand between strategy types.",
))


__all__ = ["REGISTRY", "Metric", "MetricsRegistry", "MetricUnavailable"]
