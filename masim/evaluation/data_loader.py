"""Evaluation Data Loader — Standard data extraction from MASim simulation results.

Provides domain-agnostic utilities for loading simulation data from the MASim
record store into analysis-friendly Python dicts. These functions understand
MASim's internal storage layout (batch stores, turn payloads, player roles)
and normalize them into clean {round_num: value} mappings.

Usage:
    from masim.evaluation.data_loader import (
        load_data,
        batch_to_rounds,
        market_players,
        market_data_from_payload,
        series,
    )
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def batch_to_rounds(values: list) -> Dict[int, float]:
    """Convert a batch store list to {round_num: value} dict (1-based rounds).

    Parameters
    ----------
    values : list
        Raw list from player.batch(store_name).all() — indexed 0..N-1.

    Returns
    -------
    dict mapping round numbers (1-based) to float values.
    """
    return {i + 1: v for i, v in enumerate(values)}


def market_players(results) -> Dict[str, Any]:
    """Find coordinator/environment players that carry market batch stores.

    Searches for players by role in priority order:
    1. 'coordinator' role
    2. 'environment' role
    3. Players with 'market' or 'environment' in their ID

    Parameters
    ----------
    results : MASim Results object
        The loaded simulation results.

    Returns
    -------
    dict of {player_id: player} that may carry price/fundamental stores.
    """
    candidates = results.players_by_role("coordinator")
    if candidates:
        return candidates
    candidates = results.players_by_role("environment")
    if candidates:
        return candidates
    return {
        pid: player
        for pid, player in results.players.items()
        if "market" in pid.lower() or "environment" in pid.lower()
    }


def market_data_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract market-state dict from known MASim turn payload shapes.

    MASim stores market state in different payload structures depending on
    the coordinator implementation. This function normalizes across known shapes:
    - payload["market_data"]
    - payload["environment_data"]
    - payload["state"]
    - payload["observation"]
    - payload itself (if it directly contains "price"/"fundamental")
    - payload["decision_payload"] (recursive)

    Parameters
    ----------
    payload : dict
        A single turn's payload from a coordinator player.

    Returns
    -------
    dict with market state fields (e.g., "price", "fundamental").
    Empty dict if no market data is found.
    """
    if not isinstance(payload, dict):
        return {}
    for key in ("market_data", "environment_data", "state", "observation"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    if {"price", "fundamental"}.intersection(payload):
        return payload
    decision_payload = payload.get("decision_payload")
    if isinstance(decision_payload, dict):
        return market_data_from_payload(decision_payload)
    return {}


def load_data(results) -> Dict[str, Any]:
    """Load price/fundamental batch stores and investor turn payloads.

    This is the standard data extraction function used by all finance scenario
    analysis scripts. It produces the canonical data dict that metrics and
    visualization functions consume.

    Parameters
    ----------
    results : MASim Results object
        The loaded simulation results (from masim.utils.load_results).

    Returns
    -------
    dict with keys:
        market_prices       : {round_num: float}
        fundamentals        : {round_num: float}
        investor_quantities : {player_id: {round_num: float}}
        investor_bids       : {player_id: {round_num: float}}
        investor_payloads   : {player_id: {round_num: dict}}
    """
    market_prices: Dict[int, float] = {}
    fundamentals: Dict[int, float] = {}

    for player in market_players(results).values():
        if "price" in player.batch_store_names:
            market_prices.update(batch_to_rounds(player.batch("price").all()))
        if "fundamental" in player.batch_store_names:
            fundamentals.update(batch_to_rounds(player.batch("fundamental").all()))
        for round_num, payload in player.turns.payloads().items():
            mdata = market_data_from_payload(payload)
            if round_num not in market_prices and "price" in mdata:
                market_prices[round_num] = float(mdata["price"])
            if round_num not in fundamentals:
                if "fundamental" in mdata:
                    fundamentals[round_num] = float(mdata["fundamental"])
                elif "fundamental_value" in mdata:
                    fundamentals[round_num] = float(mdata["fundamental_value"])

    investor_quantities: Dict[str, Dict[int, float]] = {}
    investor_bids: Dict[str, Dict[int, float]] = {}
    investor_payloads: Dict[str, Dict[int, dict]] = {}
    for pid, player in results.players_by_role("player").items():
        qty = player.turns.field("quantity")
        if qty:
            investor_quantities[pid] = qty
        bid = player.turns.field("bid_price")
        if bid:
            investor_bids[pid] = bid
        payloads = player.turns.payloads()
        if payloads:
            investor_payloads[pid] = payloads

    return {
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "investor_quantities": investor_quantities,
        "investor_bids": investor_bids,
        "investor_payloads": investor_payloads,
    }


def series(values: Dict[int, float]) -> Tuple[List[int], np.ndarray]:
    """Convert a {round: float} mapping to aligned (rounds, values) arrays.

    Parameters
    ----------
    values : dict
        Mapping from round numbers to float values.

    Returns
    -------
    tuple of (sorted_rounds_list, numpy_array_of_values)

    Raises
    ------
    ValueError
        If the input dict is empty.
    """
    if not values:
        raise ValueError("series is empty — cannot convert to arrays")
    rounds = sorted(values)
    return rounds, np.asarray([float(values[r]) for r in rounds], dtype=float)


# ---------------------------------------------------------------------------
# Standard data-contract helpers for metric functions
# ---------------------------------------------------------------------------


def aligned_prices_and_fundamentals(data: Dict[str, Any]) -> Tuple[
    List[int], np.ndarray, np.ndarray
]:
    """Return (rounds, prices, fundamentals) aligned on the round intersection.

    This is the standard way to obtain aligned price/fundamental arrays from
    the canonical data dict. Used by metric functions across all method-category
    files (timeseries, microstructure, etc.).

    Parameters
    ----------
    data : dict
        The standard MASim data dict with keys "market_prices" and "fundamentals".

    Returns
    -------
    tuple of (sorted_rounds_list, prices_array, fundamentals_array)

    Raises
    ------
    MetricUnavailable
        If market_prices or fundamentals is empty, or they share no rounds,
        or fundamentals contain zero values.
    """
    from masim.evaluation.registry import MetricUnavailable

    market_prices = data.get("market_prices")
    fundamentals = data.get("fundamentals")
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


def payload_buy_sell(payload: Dict[str, Any]) -> Tuple[float, float]:
    """Return (buy_qty, sell_qty) for a single investor payload.

    This is the standard accounting for the MASim data contract where payloads
    contain ``action`` (buy/sell/hold) and ``quantity`` (non-negative float).

    Parameters
    ----------
    payload : dict
        A single turn payload dict with "action" and "quantity" fields.

    Returns
    -------
    tuple of (buy_quantity, sell_quantity)
    """
    action = payload.get("action", "hold")
    quantity = abs(float(payload.get("quantity", 0.0)))
    if action == "buy":
        return quantity, 0.0
    if action == "sell":
        return 0.0, quantity
    return 0.0, 0.0


def per_agent_initial_position(config: Dict[str, Any]) -> Dict[str, float]:
    """Extract per-agent initial position from MASim config.

    MASim configs define players with an ``extras.initial_position`` field.
    When ``num_instances > 1``, the template is inflated into ``{identity}_1``,
    ``{identity}_2``, etc.

    Parameters
    ----------
    config : dict
        The MASim scenario config dict (with "players" key).

    Returns
    -------
    dict mapping agent identity string to initial position float.
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


def per_agent_initial_cash(config: Dict[str, Any]) -> Dict[str, float]:
    """Extract per-agent initial cash from MASim config.

    MASim configs define players with an ``extras.initial_cash`` field.
    When ``num_instances > 1``, the template is inflated into ``{identity}_1``,
    ``{identity}_2``, etc.

    Parameters
    ----------
    config : dict
        The MASim scenario config dict (with "players" key).

    Returns
    -------
    dict mapping agent identity string to initial cash float.
    """
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


# ---------------------------------------------------------------------------
# Legacy-compatible aliases (underscore-prefixed names that existing code uses)
# ---------------------------------------------------------------------------

_batch_to_rounds = batch_to_rounds
_load_data = load_data
_market_players = market_players
_market_data_from_payload = market_data_from_payload
_series = series
_aligned_prices_and_fundamentals = aligned_prices_and_fundamentals
_payload_buy_sell = payload_buy_sell
_per_agent_initial_position = per_agent_initial_position
_per_agent_initial_cash = per_agent_initial_cash
