"""long-term-investor — Dollar-cost-averaging long-term investor.

Canonical implementation of the ``long-term-investor`` archetype documented
in ``examples/AGENT_POOL/finance/long-term-investor.md``. Dollar-cost-
averages a fixed cash amount at a fixed cadence, tracks a running
average entry price, and trims only when the position has multiplied by
a "sell ceiling" multiple.

Theoretical basis:
    Statman (1995) — behavioural foundations of dollar-cost averaging.
    Constantinides (1979) — optimal periodic investment under transaction
    costs.
    Shiller (2000) — long-horizon mean reversion and the case for
    patient buying.

Decision rule (verbatim from AGENT_POOL profile §Behavioral Framework):

    Maintain an internal ``tick_count`` (incremented every round) and an
    ``avg_entry_price`` VWAP over accumulated buys.

    If ``tick_count % investment_interval == 0`` (an investment tick):
        If ``cash >= periodic_investment``:
            buy ``quantity = periodic_investment / price``.

    Else if ``position > 0`` and ``avg_entry_price > 0`` and
    ``price / avg_entry_price > sell_ceiling``:
        sell ``quantity = position * sell_fraction``.

    Else: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``periodic_investment``  : float > 0 — cash allocated per DCA tick
                                  (default 5000.0).
    * ``investment_interval``  : int > 0 — rounds between DCA buys
                                  (default 20).
    * ``sell_ceiling``         : float > 1 — multiple of the average entry
                                  price above which trimming activates
                                  (default 5.0).
    * ``sell_fraction``        : float in (0, 1] — fraction of the current
                                  position trimmed when the ceiling is hit
                                  (default 0.10).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLongTermInvestor(CanonicalRulePlayer):
    STRATEGY = "long-term-investor"
    DISPLAY_NAME = "Dollar-Cost-Averaging Long-Term Investor"
    SUMMARY = (
        "Dollar-cost-averages fixed cash at a fixed cadence and trims only "
        "when price has multiplied over average entry (Statman 1995)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["periodic_investment"] = float(
            extras.get("periodic_investment", 5000.0)
        )
        self.state.custom_state["investment_interval"] = int(
            extras.get("investment_interval", 20)
        )
        self.state.custom_state["sell_ceiling"] = float(
            extras.get("sell_ceiling", 5.0)
        )
        self.state.custom_state["sell_fraction"] = float(
            extras.get("sell_fraction", 0.10)
        )
        self.state.custom_state["tick_count"] = 0
        self.state.custom_state["avg_entry_price"] = 0.0
        self.state.custom_state["acquired_units"] = 0.0

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        periodic = self.state.custom_state["periodic_investment"]
        interval = self.state.custom_state["investment_interval"]
        ceiling = self.state.custom_state["sell_ceiling"]
        fraction = self.state.custom_state["sell_fraction"]

        tick = self.state.custom_state["tick_count"] + 1
        self.state.custom_state["tick_count"] = tick

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )

        if state.price <= 0:
            return hold

        # DCA buy tick.
        if interval > 0 and tick % interval == 0:
            if state.cash >= periodic:
                qty = periodic / state.price
                if qty > 0:
                    return InvestorOrder.buy(
                        quantity=qty,
                        price=state.price,
                        investor=self.identity,
                        strategy=self.STRATEGY,
                    )
            return hold

        # Trim on sell ceiling.
        avg_entry = self.state.custom_state["avg_entry_price"]
        if (
            state.position > 0
            and avg_entry > 0
            and math.isfinite(avg_entry)
            and (state.price / avg_entry) > ceiling
        ):
            qty = state.position * fraction
            if qty > 0:
                return InvestorOrder.sell(
                    quantity=qty,
                    price=state.price,
                    investor=self.identity,
                    strategy=self.STRATEGY,
                )
        return hold

    async def act(self, decision_payload):  # type: ignore[override]
        """Update running VWAP entry price on finalised buys."""
        action = decision_payload.get("action", "hold")
        quantity = float(decision_payload.get("quantity", 0.0) or 0.0)
        bid_price = float(decision_payload.get("bid_price") or 0.0)
        market_data = self.state.custom_state.get("market_data") or {}
        fill_price = (
            bid_price if bid_price > 0 else float(market_data.get("price", 0.0))
        )
        if action == "buy" and quantity > 0 and fill_price > 0:
            acquired = float(self.state.custom_state.get("acquired_units", 0.0))
            avg_entry = float(self.state.custom_state.get("avg_entry_price", 0.0))
            new_total = acquired + quantity
            if new_total > 0:
                self.state.custom_state["avg_entry_price"] = (
                    avg_entry * acquired + fill_price * quantity
                ) / new_total
                self.state.custom_state["acquired_units"] = new_total
        return await super().act(decision_payload)


class LLMLongTermInvestor(CanonicalLLMPlayer):
    STRATEGY = "long-term-investor"
    DEFAULT_SYS_PROMPT = """\
You are a long-term investor who dollar-cost-averages a fixed cash amount
at a fixed cadence. You do not react to short-term price moves. You only
trim your position when price has multiplied several times over your
average entry price.

Output format:
<analysis>state whether this round is an investment tick and whether the
           sell ceiling has been breached.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Follow your DCA schedule: buy a fixed cash amount when it is an
investment tick; trim only if price has multiplied above your ceiling
over average entry. Otherwise hold.
"""


__all__ = ["RuleLongTermInvestor", "LLMLongTermInvestor"]
