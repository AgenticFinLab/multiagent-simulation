"""short-seller — Individual short seller with staged forced covering.

Canonical implementation of the ``short-seller`` archetype documented in
``examples/AGENT_POOL/finance/short-seller.md``. Holds an initial negative
position and covers half of the remaining short whenever price runs
sufficiently far above the entry price.

Theoretical basis:
    Asquith, Pathak & Ritter (2005) — Short interest, institutional
        ownership, and stock returns.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    IF position >= 0: hold. (deactivated once fully covered)
    loss_pct = (price - short_entry_price) / short_entry_price
    IF loss_pct > cover_threshold:
        qty    = max(1, int(|position| * 0.5))
        qty    = min(qty, |position|)
        action = "buy"
    ELSE: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``short_entry_price`` : float > 0 — reference short entry price
                              (default 30.0).
    * ``cover_threshold``   : float in (0, 1) — loss trigger
                              (default 0.20, Asquith et al. 2005).
    * ``initial_position``  : int < 0 — starting short position
                              (default -50; also read via base ``initial_position``).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleShortSeller(CanonicalRulePlayer):
    STRATEGY = "short-seller"
    DISPLAY_NAME = "Individual Short Seller"
    SUMMARY = (
        "Individual short — covers half of the remaining short position when "
        "losses exceed a loss threshold (Asquith et al. 2005)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["short_entry_price"] = float(
            extras.get("short_entry_price", 30.0)
        )
        self.state.custom_state["cover_threshold"] = float(
            extras.get("cover_threshold", 0.20)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hold = replace(
            InvestorOrder.hold(
                price=state.price, investor=self.identity, strategy=self.STRATEGY
            ),
            extras={"is_short_cover": False},
        )
        # Already flat / long — permanently deactivated (never sells).
        if state.position >= 0:
            return hold
        entry = cs["short_entry_price"]
        if entry <= 0 or state.price <= 0:
            return hold

        loss_pct = (state.price - entry) / entry
        if loss_pct <= cs["cover_threshold"]:
            return hold

        abs_pos = abs(state.position)
        qty = max(1, int(abs_pos * 0.5))
        qty = min(qty, int(abs_pos))
        if qty <= 0:
            return hold
        return replace(
            InvestorOrder.buy(
                quantity=float(qty),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            ),
            extras={"is_short_cover": True},
        )


class LLMShortSeller(CanonicalLLMPlayer):
    STRATEGY = "short-seller"
    DEFAULT_SYS_PROMPT = """\
You are an individual short seller. You entered the trade at a known
entry price and hold a fixed short position. Whenever the market runs
against you far enough — losses exceeding your tolerance — you cover
half of the remaining short by buying. You never add to the short and
never sell.

Output format:
<analysis>state your loss vs entry and whether the cover threshold is breached.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Cover half of your remaining short only when the loss against your entry
exceeds tolerance. Never add to the short.
"""


__all__ = ["RuleShortSeller", "LLMShortSeller"]
