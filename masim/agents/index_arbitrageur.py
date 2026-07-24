"""index-arbitrageur — Futures/cash program-trading desk.

Canonical implementation of the ``index-arbitrageur`` archetype documented
in ``examples/AGENT_POOL/finance/index-arbitrageur.md``. When the observed
spot/fair-value deviation exceeds the no-arbitrage band, submits a fixed-
size cash-side order that closes the mispricing.

Theoretical basis:
    Stoll & Whaley (1990) — index arbitrage program trading between
    futures and the cash index.

Decision rule (from AGENT_POOL profile §Mathematical Model):

    If deviation >  arb_threshold: sell base_size (clamped by position).
    If deviation < -arb_threshold: buy  base_size (clamped by cash).
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``arb_threshold`` : float — no-arbitrage band (default 0.01,
                           Stoll & Whaley 1990).
    * ``base_size``     : float — fixed arbitrage lot size (default 80.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleIndexArbitrageur(CanonicalRulePlayer):
    STRATEGY = "index-arbitrageur"
    DISPLAY_NAME = "Index Arbitrage Desk"
    SUMMARY = (
        "Program-trading desk that arbitrages spot/fair-value deviations "
        "with a fixed lot size (Stoll & Whaley 1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["arb_threshold"] = float(
            extras.get("arb_threshold", 0.01)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 80.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        theta = self.state.custom_state["arb_threshold"]
        base = self.state.custom_state["base_size"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if math.isnan(deviation) or math.isnan(state.fundamental):
            return hold

        if deviation > theta:
            return InvestorOrder.sell(
                quantity=float(base),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if deviation < -theta:
            return InvestorOrder.buy(
                quantity=float(base),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMIndexArbitrageur(CanonicalLLMPlayer):
    STRATEGY = "index-arbitrageur"
    DEFAULT_SYS_PROMPT = """\
You run an index arbitrage desk. You do not form directional views and
you do not quote two-sided liquidity; you only act when the spot/fair-
value deviation exceeds a small no-arbitrage band. When it does, you
transmit the futures pressure into the cash basket with a fixed program
trade — selling the basket when spot is rich, buying it when cheap.

Output format:
<analysis>state the deviation vs your no-arbitrage band and the resulting
program trade.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Program-trade the basket: sell when spot is above the band, buy when
below, hold inside.
"""


__all__ = ["RuleIndexArbitrageur", "LLMIndexArbitrageur"]
