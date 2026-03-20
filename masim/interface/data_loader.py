"""Load completed simulation data from EXPERIMENT/ for replay in the Web UI.

Data layout (produced by the simulator):
  EXPERIMENT/{scenario}/
    communication/
      msg-store-information.json        # index of block files
      msg_block_{n}.json                # {msg_id: {timestamp, size_bytes, encoded}}
    records/history/
      batch-store-information.json      # index of batch files
      batch_block_{n}.json              # {batch_id: [{round, execution_levels, ...}]}
    monitoring/metrics/
      batch_block_{n}.json              # metrics (not used for replay)
    analysis/
      summary.json
      *.png

This module exposes:
  - has_experiment_data(scenario_name)  → bool
  - load_rounds(scenario_name)          → list[RoundData]  (sorted by round number)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

EXPERIMENT_DIR = Path("EXPERIMENT")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class AgentAction:
    """Decoded action sent from an investor to the market."""

    round_num: int
    agent_id: str
    content: Dict[str, Any]

    @property
    def action_str(self) -> str:
        """Human-readable action label derived from content."""
        qty = self.content.get("stock_qty", self.content.get("quantity", None))
        if qty is None:
            return "HOLD"
        if qty > 0:
            return "BUY"
        elif qty < 0:
            return "SELL"
        return "HOLD"

    @property
    def quantity(self) -> float:
        return float(self.content.get("stock_qty", self.content.get("quantity", 0)))

    @property
    def price(self) -> Optional[float]:
        return self.content.get("bid_price", self.content.get("price", None))

    @property
    def strategy(self) -> str:
        return self.content.get("strategy", "")


@dataclass
class MarketBroadcast:
    """Price broadcast from the market to investors."""

    round_num: int
    stock_price: Optional[float] = None
    prev_stock_price: Optional[float] = None
    stock_return: Optional[float] = None

    @classmethod
    def from_content(cls, round_num: int, content: Dict[str, Any]) -> "MarketBroadcast":
        return cls(
            round_num=round_num,
            stock_price=content.get("stock_price", content.get("price")),
            prev_stock_price=content.get("prev_stock_price"),
            stock_return=content.get("stock_return"),
        )


@dataclass
class RoundData:
    """All observable events for a single simulation round."""

    round_num: int
    execution_levels: List[List[str]] = field(default_factory=list)
    market_broadcast: Optional[MarketBroadcast] = None
    agent_actions: List[AgentAction] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def has_experiment_data(scenario_name: str) -> bool:
    """Return True if communication or history data exists for the scenario.

    Args:
        scenario_name: Scenario directory name (e.g. 'EquityPremium').

    Returns:
        True when at least one msg_block_*.json or batch_block_*.json exists.
    """
    base = EXPERIMENT_DIR / scenario_name
    comm_dir = base / "communication"
    hist_dir = base / "records" / "history"

    has_comm = comm_dir.is_dir() and bool(list(comm_dir.glob("msg_block_*.json")))
    has_hist = hist_dir.is_dir() and bool(list(hist_dir.glob("batch_block_*.json")))
    return has_comm or has_hist


def load_rounds(scenario_name: str) -> List[RoundData]:
    """Load and reconstruct per-round data from saved EXPERIMENT files.

    Reads all msg_block_*.json and batch_block_*.json files, then
    assembles them into a sorted list of RoundData objects.

    Args:
        scenario_name: Scenario directory name.

    Returns:
        List of RoundData sorted by round_num (1-indexed).
    """
    base = EXPERIMENT_DIR / scenario_name

    # ── 1. Load execution_levels from history blocks ──────────────────────
    exec_levels: Dict[int, List[List[str]]] = {}
    hist_dir = base / "records" / "history"
    if hist_dir.is_dir():
        for block_file in sorted(hist_dir.glob("batch_block_*.json")):
            try:
                raw = json.loads(block_file.read_text(encoding="utf-8"))
                for _batch_id, records in raw.items():
                    if not isinstance(records, list):
                        continue
                    for rec in records:
                        rnd = rec.get("round")
                        lvls = rec.get("execution_levels", [])
                        if rnd is not None:
                            exec_levels[int(rnd)] = lvls
            except Exception:
                pass

    # ── 2. Load messages from communication blocks ────────────────────────
    #    Key message types:
    #      market → investor  : market_price broadcast
    #      investor → market  : action/order
    market_broadcasts: Dict[int, MarketBroadcast] = {}
    agent_actions: Dict[int, List[AgentAction]] = {}

    comm_dir = base / "communication"
    if comm_dir.is_dir():
        for block_file in sorted(comm_dir.glob("msg_block_*.json")):
            try:
                raw = json.loads(block_file.read_text(encoding="utf-8"))
                for _msg_id, msg_wrapper in raw.items():
                    encoded = msg_wrapper.get("encoded", "")
                    if not encoded:
                        continue
                    try:
                        msg = json.loads(encoded)
                    except Exception:
                        continue

                    sender = msg.get("sender_id", "")
                    recipient = msg.get("recipient_id", "")
                    round_num = int(msg.get("extras", {}).get("round_num", 0))
                    if round_num <= 0:
                        continue

                    payload = msg.get("payload", {})
                    content = payload.get("content", {})
                    content_type = payload.get("content_type", "")

                    if sender == "market" and content_type == "market_price":
                        # Only store the first broadcast per round (all are identical)
                        if round_num not in market_broadcasts:
                            market_broadcasts[round_num] = MarketBroadcast.from_content(
                                round_num, content
                            )

                    elif recipient == "market" and sender != "market":
                        # Investor → market action
                        action = AgentAction(
                            round_num=round_num,
                            agent_id=sender,
                            content=content,
                        )
                        agent_actions.setdefault(round_num, []).append(action)

            except Exception:
                pass

    # ── 3. Assemble RoundData objects ─────────────────────────────────────
    all_rounds: set = (
        set(exec_levels.keys())
        | set(market_broadcasts.keys())
        | set(agent_actions.keys())
    )
    if not all_rounds:
        return []

    result: List[RoundData] = []
    for rnd in sorted(all_rounds):
        rd = RoundData(
            round_num=rnd,
            execution_levels=exec_levels.get(rnd, []),
            market_broadcast=market_broadcasts.get(rnd),
            agent_actions=sorted(agent_actions.get(rnd, []), key=lambda a: a.agent_id),
        )
        result.append(rd)

    return result
