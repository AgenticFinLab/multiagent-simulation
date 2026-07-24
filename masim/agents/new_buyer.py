"""new-buyer — Late-cycle retail entrant.

Canonical implementation of the ``new-buyer`` archetype documented in
``examples/AGENT_POOL/finance/new-buyer.md``. A late-cycle retail entrant
who never sells: enters with a fixed fraction of cash whenever the trailing
return exceeds an entry threshold, then intends to hold indefinitely.

Theoretical basis:
    Guiso, Sapienza & Zingales (2008) — trust and stock-market participation.
    Benartzi & Thaler (2001) — naive diversification / retail allocation.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    recent_return = (price - price[-lookback]) / price[-lookback]

    If ``recent_return > entry_threshold`` AND ``cash > 0``:
        buy — quantity = ``budget_fraction * cash / price``,
        multiplied by ``(1 + eps)`` with ``eps ~ N(0, noise_sigma)`` and
        floored to zero.
    Otherwise: hold. (Never sells.)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``entry_threshold`` : float — trailing return trigger (default 0.05).
    * ``budget_fraction`` : float in [0,1] — cash fraction per entry
                             (default 0.10).
    * ``noise_sigma``     : float — sizing noise stddev (default 0.05).
    * ``lookback``        : int > 0 — lookback for the return signal
                             (default 20).
    * ``seed``            : optional int — RNG seed for reproducibility.
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleNewBuyer(CanonicalRulePlayer):
    STRATEGY = "new-buyer"
    DISPLAY_NAME = "Late-Cycle Retail Entrant"
    SUMMARY = (
        "Enters after a trailing rally exceeds the threshold and never sells "
        "(Guiso et al. 2008; Benartzi & Thaler 2001)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["entry_threshold"] = float(
            extras.get("entry_threshold", 0.05)
        )
        self.state.custom_state["budget_fraction"] = float(
            extras.get("budget_fraction", 0.10)
        )
        self.state.custom_state["noise_sigma"] = float(
            extras.get("noise_sigma", 0.05)
        )
        self.state.custom_state["lookback"] = int(extras.get("lookback", 20))
        self.state.custom_state["prices"] = []
        seed = extras.get("seed")
        self.state.custom_state["rng"] = random.Random(seed)

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        prices = self.state.custom_state["prices"]
        prices.append(float(market_data["price"]))
        lookback = self.state.custom_state["lookback"]
        # Keep only what we need for the lookback window.
        if len(prices) > lookback + 2:
            del prices[: len(prices) - (lookback + 2)]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        threshold = self.state.custom_state["entry_threshold"]
        budget = self.state.custom_state["budget_fraction"]
        sigma = self.state.custom_state["noise_sigma"]
        lookback = self.state.custom_state["lookback"]
        prices = self.state.custom_state["prices"]
        rng: random.Random = self.state.custom_state["rng"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        # Need enough history to define the trailing return.
        if len(prices) <= lookback:
            return hold
        base_price = prices[-(lookback + 1)]
        if base_price <= 0 or state.price <= 0:
            return hold
        recent_return = (state.price - base_price) / base_price

        if recent_return <= threshold or state.cash <= 0:
            return hold

        base_qty = budget * state.cash / state.price
        noise = rng.gauss(0.0, sigma) if sigma > 0 else 0.0
        quantity = max(0.0, base_qty * (1.0 + noise))
        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMNewBuyer(CanonicalLLMPlayer):
    STRATEGY = "new-buyer"
    DEFAULT_SYS_PROMPT = """\
You are a late-cycle retail entrant. You have been watching the market
from the sidelines. When the trailing return over your lookback window
crosses your entry threshold, you finally step in and deploy a fixed
fraction of your cash. Once in, you intend to hold — you never sell.
Between entries you hold.

Output format:
<analysis>describe the trailing rally you see and whether it justifies entering.</analysis>
<decision>{"action": "buy"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide as a late-cycle entrant: buy a fixed fraction of cash if the
trailing rally is strong enough; otherwise hold. Never sell.
"""


__all__ = ["RuleNewBuyer", "LLMNewBuyer"]
