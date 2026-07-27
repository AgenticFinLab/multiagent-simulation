"""Abstract base class for canonical market coordinators (broadcasters).

Market coordinators differ from investor agents (CanonicalRulePlayer /
CanonicalLLMPlayer) in their lifecycle:

* **Investors** *consume* a market broadcast and *emit* an order.
* **Coordinators** *consume* investor orders and *emit* a market broadcast.

Coordinators are ALWAYS rule-executed — there is no LLM variant even when
investor agents use LLMs.  The pricing mechanism is deterministic-given-seed.

Lifecycle (maps to GeneralPlayer perceive → decide → act):

1. ``perceive``: collect inbound investor orders; on first call, run
   :meth:`init_market_state` to read extras and initialize all state.
2. ``decide``: call :meth:`advance_market` which computes the new market
   state and returns the broadcast dict.  The broadcast is validated through
   :func:`~masim.format.broadcast.validate_broadcast` before emission —
   any schema violation raises ``ValueError`` and aborts the round.
3. ``act``: wrap the broadcast dict as ``Action(action_type="market_broadcast")``
   and emit to every participant.

Subclasses MUST implement:
* :meth:`init_market_state(extras)` — read parameters from extras, write
  initial state to ``self.state.custom_state``.
* :meth:`advance_market(orders, round_num)` — compute new market state,
  write updated state to ``self.state.custom_state``, and return the
  broadcast dict.

Format contract:
  Every broadcast dict is validated against the archetype's registered
  :class:`~masim.format.broadcast.BroadcastSchema` (see
  :data:`~masim.format.broadcast.BROADCAST_SCHEMAS`).  The schema is
  mechanically derived from the coordinator profile in
  ``examples/AGENT_POOL/market/<stem>.md`` and enforces required fields,
  types, ranges, and enum constraints.  Emission via ``outbound_messages``
  with ``content_type="market_price"`` carries the validated payload.
"""

from __future__ import annotations

import logging
import math
import os
import random
from typing import Any, Dict, List, Optional

from masim.format.broadcast import validate_broadcast, MarketBroadcast
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("masim.agents.coordinator")


class CanonicalMarketCoordinator(GeneralPlayer):
    """Base class for market coordinators (price-formation broadcasters).

    Subclasses MUST:
      * declare ``STRATEGY`` (kebab-case archetype identifier matching the
        ``examples/AGENT_POOL/market/<stem>.md`` filename).
      * implement :meth:`init_market_state`.
      * implement :meth:`advance_market`.

    Class-level metadata (mirrors investor bases for catalog discovery):
      * ``STRATEGY``           — archetype identifier (catalog key).
      * ``DISPLAY_NAME``       — UI label shown in the marketplace card.
      * ``SUMMARY``            — one-line description shown under the card.
      * ``BROADCAST_FIELDS``   — tuple of field names this coordinator emits
                                  (used for schema validation at debug level).
    """

    STRATEGY: str = "CanonicalMarketCoordinator"
    DISPLAY_NAME: str = ""
    SUMMARY: str = ""
    BROADCAST_FIELDS: tuple = ()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if not self.state.custom_state.get("_market_initialized"):
            self._run_initialization()

        # Collect inbound orders from investor agents.
        orders: List[Dict[str, Any]] = []
        if observation.inbounds:
            for inb in observation.inbounds:
                if inb.payload:
                    orders.append(inb.payload)
        self.state.custom_state["_pending_orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        orders = self.state.custom_state.pop("_pending_orders", [])
        round_num = self.state.custom_state["round"]

        broadcast = self.advance_market(orders, round_num)

        # ── Format contract enforcement ──────────────────────────────────
        # Validates against the archetype's registered BroadcastSchema.
        # Raises ValueError on missing fields, type mismatches, range
        # violations, or undeclared keys — hard-stop, not warn-only.
        validate_broadcast(self.STRATEGY, broadcast)

        return {
            "market_data": broadcast,
            "outbound_messages": [
                {"payload": broadcast, "content_type": "market_price"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )

    # ------------------------------------------------------------------
    # Hooks for subclasses (MUST override)
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Initialize market state from extras.

        Called once on the first ``perceive`` call.  Subclasses MUST read
        all required parameters from ``extras`` and write initial state to
        ``self.state.custom_state``.  Raise ``KeyError`` on missing required
        extras (never silently default).
        """
        raise NotImplementedError

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's market transition and return the broadcast dict.

        Subclasses MUST:
        1. Aggregate ``orders`` according to their mechanism.
        2. Compute new prices / state variables.
        3. Write updated state to ``self.state.custom_state``.
        4. Return the broadcast dict matching the coordinator's I/O contract.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Helpers available to subclasses
    # ------------------------------------------------------------------

    def _run_initialization(self) -> None:
        """Run the state initialization sequence once."""
        extras = self.config.extras
        self.state.custom_state["_record_path"] = extras.get("record_path", "")
        self.state.custom_state["_hot_limit"] = extras.get(
            "custom_state_hot_limit", 10000
        )
        self.init_market_state(extras)
        self.state.custom_state["_market_initialized"] = True

    def _make_history_buffer(self, name: str):
        """Create a HistoryBuffer for a named state series.

        Returns a plain :class:`collections.deque` when ``record_path`` is
        empty (e.g. in smoke tests or scenarios that don't persist history
        to disk).  The deque supports ``.append()`` so coordinators can use
        the same code path regardless of persistence mode.
        """
        from collections import deque

        record_path = self.state.custom_state.get("_record_path", "")
        hot_limit = self.state.custom_state.get("_hot_limit", 10000)
        if not record_path:
            return deque(maxlen=hot_limit)
        return HistoryBuffer(
            folder=os.path.join(record_path, "market", name),
            entry_limit=hot_limit,
        )

    @staticmethod
    def _history_append(buffer, value) -> None:
        """Append ``value`` to a HistoryBuffer if it exists (None-safe)."""
        if buffer is not None:
            buffer.append(value)

    @staticmethod
    def _aggregate_standard_orders(
        orders: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Aggregate orders using the standard buy/sell/hold action scheme.

        Returns dict with keys: buy_qty, sell_qty, net_demand, n_active.

        Contract (2026-07-24, fail-loud):
          * Every order MUST carry a validated ``action`` field (member of
            :data:`~masim.format.order.INVESTOR_ORDER_ACTION_VALUES` — the
            canonical enum). Missing / malformed / unknown actions raise
            :class:`ValueError` — silent-skip would let a bug in the
            investor emit path silently zero out demand.
          * Every order MUST carry a numeric ``quantity``; a
            non-parseable quantity raises :class:`ValueError` — the
            investor is expected to emit through
            :func:`~masim.format.order.validate_order` before dispatch,
            which already enforces this, so any malformed order that
            reaches the coordinator is a hard bug that must not be masked.
        """
        # Local import to avoid a top-level circular import against the
        # broadcast module (which itself may import from _coordinator_base
        # in the future).
        from masim.format.order import INVESTOR_ORDER_ACTION_VALUES

        buy_qty = 0.0
        sell_qty = 0.0
        n_active = 0
        for o in orders:
            if "action" not in o:
                raise ValueError(
                    "_aggregate_standard_orders: order missing required "
                    f"'action' field: {o!r}. Investor emit path must go "
                    "through masim.format.validate_order."
                )
            action = o["action"]
            if action not in INVESTOR_ORDER_ACTION_VALUES:
                raise ValueError(
                    f"_aggregate_standard_orders: order 'action'={action!r} "
                    f"not in canonical enum {sorted(INVESTOR_ORDER_ACTION_VALUES)}: "
                    f"{o!r}. Silent-skip would hide investor-side bugs."
                )
            if "quantity" not in o:
                raise ValueError(
                    "_aggregate_standard_orders: order missing required "
                    f"'quantity' field: {o!r}."
                )
            try:
                qty = float(o["quantity"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"_aggregate_standard_orders: order 'quantity'="
                    f"{o['quantity']!r} is not numeric: {o!r}. Silent-skip "
                    "would falsify aggregate demand."
                ) from exc
            if action == "buy" and qty > 0:
                buy_qty += qty
                n_active += 1
            elif action == "sell" and qty > 0:
                sell_qty += qty
                n_active += 1
            # action == "hold" or qty == 0: legitimate no-op, not skipped.
        return {
            "buy_qty": buy_qty,
            "sell_qty": sell_qty,
            "net_demand": buy_qty - sell_qty,
            "n_active": n_active,
        }

    @staticmethod
    def _safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Division guarded against zero/NaN denominator."""
        if denominator == 0 or math.isnan(denominator):
            return default
        return numerator / denominator


__all__ = ["CanonicalMarketCoordinator"]
