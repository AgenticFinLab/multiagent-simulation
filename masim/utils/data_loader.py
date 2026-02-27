"""Simulation Data Loader

Generic utility to load simulation data from record directories.
All analysis scripts can import this to avoid duplicating data loading logic.

Usage:
    from masim.utils.data_loader import load_simulation_data

    config = load_config("configs/AssetBubble/simulation.yml")
    data = load_simulation_data(config)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_simulation_data(
    config: Dict[str, Any],
    include_messages: bool = False,
) -> Dict[str, Any]:
    """Load simulation data from record directory based on config.

    Data structure in records:
    - {record_path}/market/turns/turn_block_*.json -> market data (price, volume, etc.)
    - {record_path}/{player_id}/turns/turn_block_*.json -> investor orders

    Args:
        config: Loaded simulation configuration dict
        include_messages: Whether to also load message data (default False)

    Returns:
        Dictionary containing:
        - market_prices: {round: price}
        - fundamentals: {round: fundamental_value}
        - volumes: {round: volume}
        - investor_data: {player_id: {round: decision_payload}}
        - player_ids: List of player identities
        - market_id: Market identity (usually "market")
    """
    record_path = Path(config["setting"]["record_path"])
    players_config = config["players"]

    # Identify market and investor players from config
    market_id = None
    investor_ids: List[str] = []

    for player_key, player_cfg in players_config.items():
        identity = player_cfg["config"]["identity"]
        role = player_cfg["config"]["role"]
        if role == "coordinator":
            market_id = identity
        else:
            investor_ids.append(identity)

    # Load market data
    market_prices: Dict[int, float] = {}
    fundamentals: Dict[int, float] = {}
    volumes: Dict[int, float] = {}
    market_extras: Dict[int, Dict[str, Any]] = {}

    if market_id:
        market_data = _load_player_turns(record_path / market_id)
        for round_num, payload in market_data.items():
            if "market_data" in payload:
                md = payload["market_data"]
                market_prices[round_num] = md["price"]
                if "fundamental" in md:
                    fundamentals[round_num] = md["fundamental"]
                if "volume" in md:
                    volumes[round_num] = md["volume"]
                # Store any extra market data fields
                market_extras[round_num] = {
                    k: v
                    for k, v in md.items()
                    if k not in ("price", "fundamental", "volume")
                }

    # Load investor data
    investor_data: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for inv_id in investor_ids:
        inv_turns = _load_player_turns(record_path / inv_id)
        if inv_turns:
            investor_data[inv_id] = inv_turns

    result = {
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "volumes": volumes,
        "market_extras": market_extras,
        "investor_data": investor_data,
        "player_ids": investor_ids,
        "market_id": market_id,
    }

    if include_messages:
        result["messages"] = _load_all_messages(record_path, [market_id] + investor_ids)

    return result


def _load_player_turns(player_dir: Path) -> Dict[int, Dict[str, Any]]:
    """Load turn data for a single player.

    Args:
        player_dir: Path to player's record directory

    Returns:
        {round_num: decision_payload} mapping
    """
    turns_dir = player_dir / "turns"
    result: Dict[int, Dict[str, Any]] = {}

    if not turns_dir.exists():
        return result

    for turn_file in sorted(turns_dir.glob("turn_block_*.json")):
        with open(turn_file, "r", encoding="utf-8") as f:
            block_data = json.load(f)

        for turn_id, turn_data in block_data.items():
            # Skip metadata entries
            if turn_id.endswith("-information"):
                continue

            round_num = turn_data["round_num"]
            step_results = turn_data["turn_result"]["step_results"]

            if step_results:
                payload = step_results[0]["decision_payload"]
                result[round_num] = payload

    return result


def _load_all_messages(
    record_path: Path, player_ids: List[str]
) -> Dict[str, List[Dict[str, Any]]]:
    """Load message data for all players.

    Args:
        record_path: Root record directory
        player_ids: List of player identities

    Returns:
        {player_id: [messages]} mapping
    """
    messages: Dict[str, List[Dict[str, Any]]] = {}

    for player_id in player_ids:
        if player_id is None:
            continue
        msg_dir = record_path / player_id / "messages"
        if not msg_dir.exists():
            continue

        player_msgs: List[Dict[str, Any]] = []
        for msg_file in sorted(msg_dir.glob("msg_block_*.json")):
            with open(msg_file, "r", encoding="utf-8") as f:
                block_data = json.load(f)

            for msg_id, msg_data in block_data.items():
                if msg_id.endswith("-information"):
                    continue
                player_msgs.append(msg_data)

        messages[player_id] = player_msgs

    return messages


def get_investor_quantities(data: Dict[str, Any]) -> Dict[str, Dict[int, float]]:
    """Extract investor quantities from loaded data.

    Args:
        data: Result from load_simulation_data()

    Returns:
        {investor_id: {round: quantity}}
    """
    result: Dict[str, Dict[int, float]] = {}
    for inv_id, inv_turns in data["investor_data"].items():
        quantities: Dict[int, float] = {}
        for round_num, payload in inv_turns.items():
            if "quantity" in payload:
                quantities[round_num] = payload["quantity"]
        if quantities:
            result[inv_id] = quantities
    return result


def get_investor_orders(
    data: Dict[str, Any],
) -> Dict[str, Dict[int, Dict[str, float]]]:
    """Extract investor order details (bid_price, quantity) from loaded data.

    Args:
        data: Result from load_simulation_data()

    Returns:
        {investor_id: {round: {bid_price, quantity, ...}}}
    """
    result: Dict[str, Dict[int, Dict[str, float]]] = {}
    for inv_id, inv_turns in data["investor_data"].items():
        orders: Dict[int, Dict[str, float]] = {}
        for round_num, payload in inv_turns.items():
            order = {}
            if "bid_price" in payload:
                order["bid_price"] = payload["bid_price"]
            if "quantity" in payload:
                order["quantity"] = payload["quantity"]
            if order:
                orders[round_num] = order
        if orders:
            result[inv_id] = orders
    return result


def get_investor_bids(data: Dict[str, Any]) -> Dict[str, Dict[int, float]]:
    """Extract investor bid prices from loaded data.

    Args:
        data: Result from load_simulation_data()

    Returns:
        {investor_id: {round: bid_price}}
    """
    result: Dict[str, Dict[int, float]] = {}
    for inv_id, inv_turns in data["investor_data"].items():
        bids: Dict[int, float] = {}
        for round_num, payload in inv_turns.items():
            if "bid_price" in payload:
                bids[round_num] = payload["bid_price"]
        if bids:
            result[inv_id] = bids
    return result
