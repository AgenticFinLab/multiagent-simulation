"""Load completed simulation data from EXPERIMENT/ for replay in the Web UI.

The read-model dataclasses defined here (:class:`ReplayAgentAction`,
:class:`ReplayMarketBroadcast`, :class:`RoundData`) are *log-replay
view-models* — they parse persisted simulation logs for post-hoc
inspection. They are NOT part of the runtime format contract, which lives
in :mod:`masim.format`. The classes were renamed with ``Replay`` prefixes
on 2026-07-24 to eliminate a name collision with
:class:`masim.format.MarketBroadcast` and to make it clear that the
runtime broadcast contract is the source of truth. Action strings are
normalised to the canonical lowercase enum
(:data:`masim.format.INVESTOR_ORDER_ACTION_VALUES`).

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
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import streamlit as st

# Import path helper for nested scenario support
from masim.interface.config_loader import _experiment_path

# Canonical action enum — used to normalise log-derived action_str
from masim.format import BUY, SELL, HOLD

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures — LOG-REPLAY VIEW MODELS
# (Runtime contracts live in masim.format; do NOT use these at runtime.)
# ---------------------------------------------------------------------------


@dataclass
class ReplayAgentAction:
    """Decoded action sent from an investor to the market (log-replay view).

    This is a lossy view of a persisted log entry, not the canonical
    :class:`masim.format.InvestorOrder`. The ``action_str`` property returns
    the canonical lowercase enum from :data:`masim.format.INVESTOR_ORDER_ACTION_VALUES`.
    """

    round_num: int
    agent_id: str
    content: Dict[str, Any]

    @property
    def action_str(self) -> str:
        """Human-readable action label derived from content.

        Returns one of the canonical enum values ``buy``, ``sell``, ``hold``.
        We accept both the current ``stock_qty`` field name and the legacy
        ``quantity`` field name for backward-compatibility with older logs;
        the log-source is a historical artefact, not a runtime contract,
        so a missing quantity is interpreted as ``hold`` — this is the
        one place where a defensive fallback is legitimate because we are
        parsing a fixed on-disk file, not making a runtime decision.
        """
        qty = self.content.get("stock_qty", self.content.get("quantity", None))
        if qty is None:
            return HOLD
        if qty > 0:
            return BUY
        elif qty < 0:
            return SELL
        return HOLD

    @property
    def quantity(self) -> float:
        return float(self.content.get("stock_qty", self.content.get("quantity", 0)))

    @property
    def price(self) -> Optional[float]:
        return self.content.get("bid_price", self.content.get("price", None))

    @property
    def strategy(self) -> str:
        return self.content.get("strategy", "")

    @property
    def reasoning(self) -> str:
        return self.content.get("reasoning", "")

    @property
    def analysis(self) -> str:
        """LLM's analysis/reasoning before the decision."""
        return self.content.get("analysis", "")


@dataclass
class ReplayMarketBroadcast:
    """Price broadcast from the market to investors (log-replay view).

    This is a lossy view of a persisted broadcast, NOT the canonical
    :class:`masim.format.MarketBroadcast`. It carries only the fields the
    UI needs for a stock-scenario replay; for the full authoritative
    broadcast, load the raw payload via the format layer instead.
    """

    round_num: int
    stock_price: Optional[float] = None
    prev_stock_price: Optional[float] = None
    stock_return: Optional[float] = None
    fundamental: Optional[float] = None

    @classmethod
    def from_content(
        cls, round_num: int, content: Dict[str, Any]
    ) -> "ReplayMarketBroadcast":
        return cls(
            round_num=round_num,
            stock_price=content.get("stock_price", content.get("price")),
            prev_stock_price=content.get("prev_stock_price"),
            stock_return=content.get("stock_return"),
            fundamental=content.get("fundamental"),
        )


@dataclass
class RoundData:
    """All observable events for a single simulation round."""

    round_num: int
    execution_levels: List[List[str]] = field(default_factory=list)
    market_broadcast: Optional[ReplayMarketBroadcast] = None
    agent_actions: List[ReplayAgentAction] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@st.cache_data(ttl=10)
def has_experiment_data(scenario_name: str) -> bool:
    """Return True if communication or history data exists for the scenario.

    Args:
        scenario_name: Scenario directory name (e.g. 'EquityPremium').

    Returns:
        True when at least one msg_block_*.json or batch_block_*.json exists.
    """
    base = _experiment_path(scenario_name)
    comm_dir = base / "communication"
    hist_dir = base / "records" / "history"

    has_comm = comm_dir.is_dir() and bool(list(comm_dir.glob("msg_block_*.json")))
    has_hist = hist_dir.is_dir() and bool(list(hist_dir.glob("batch_block_*.json")))
    return has_comm or has_hist


@st.cache_data(ttl=10)
def count_experiment_rounds(scenario_name: str) -> int:
    """Count the number of recorded rounds in saved experiment data.

    Lightweight alternative to load_rounds() — scans batch_block JSON files
    in records/history/ for unique round numbers without fully parsing
    agent actions.

    Args:
        scenario_name: Scenario directory name.

    Returns:
        Number of unique rounds found, or 0 if no data.
    """
    base = _experiment_path(scenario_name)
    hist_dir = base / "records" / "history"
    if not hist_dir.is_dir():
        return 0

    round_nums: set = set()
    for block_file in hist_dir.glob("batch_block_*.json"):
        try:
            raw = json.loads(block_file.read_text(encoding="utf-8"))
            for _batch_id, records in raw.items():
                if not isinstance(records, list):
                    continue
                for rec in records:
                    rnd = rec.get("round")
                    if rnd is not None:
                        round_nums.add(int(rnd))
        except Exception:
            continue
    return len(round_nums)


def load_rounds(scenario_name: str) -> List[RoundData]:
    """Load and reconstruct per-round data from saved EXPERIMENT files.

    Reads all msg_block_*.json and batch_block_*.json files, then
    assembles them into a sorted list of RoundData objects.

    Args:
        scenario_name: Scenario directory name.

    Returns:
        List of RoundData sorted by round_num (1-indexed).
    """
    base = _experiment_path(scenario_name)

    # ── 1. Load execution_levels from history blocks ──────────────────────
    exec_levels: Dict[int, List[List[str]]] = {}
    _skipped_blocks = 0
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
            except Exception as exc:
                _skipped_blocks += 1
                logger.warning(
                    "Skipped corrupt history block %s: %s", block_file.name, exc
                )

    # ── 2. Load messages from communication blocks ────────────────────────
    #    Key message types:
    #      market → investor  : market_price broadcast
    #      investor → market  : action/order
    market_broadcasts: Dict[int, ReplayMarketBroadcast] = {}
    agent_actions: Dict[int, List[ReplayAgentAction]] = {}

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
                            market_broadcasts[round_num] = ReplayMarketBroadcast.from_content(
                                round_num, content
                            )

                    elif recipient == "market" and sender != "market":
                        # Investor → market action
                        action = ReplayAgentAction(
                            round_num=round_num,
                            agent_id=sender,
                            content=content,
                        )
                        agent_actions.setdefault(round_num, []).append(action)

            except Exception as exc:
                _skipped_blocks += 1
                logger.warning(
                    "Skipped corrupt message block %s: %s", block_file.name, exc
                )

    # ── 3. Assemble RoundData objects ─────────────────────────────────────
    if _skipped_blocks:
        logger.warning(
            "Data loading for '%s': %d block file(s) skipped due to parse errors.",
            scenario_name,
            _skipped_blocks,
        )

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

    # Backfill prev_stock_price / stock_return for replay. Saved experiment
    # data often omits these, which left the "Price Change" metric blank and
    # unchanging on Load Results. Walk rounds in order and derive the return
    # from the previous round's cleared price (mirrors the live-run path).
    prev_price: Optional[float] = None
    for rd in result:
        mb = rd.market_broadcast
        if mb is None or mb.stock_price is None:
            continue
        if mb.prev_stock_price is None:
            mb.prev_stock_price = prev_price
        if mb.stock_return is None and prev_price not in (None, 0):
            mb.stock_return = (mb.stock_price - prev_price) / prev_price
        prev_price = mb.stock_price

    return result
