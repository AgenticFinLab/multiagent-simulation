"""market-maker-gamma — Short-gamma dealer forced-buying.

Canonical implementation of the ``market-maker-gamma`` archetype
documented in ``examples/AGENT_POOL/finance/market-maker-gamma.md``.
Models a dealer who is short gamma (short calls hedged with delta) and
must mechanically buy the underlying as it rises above the option's
reference strike, amplifying the up-move — the "gamma squeeze" mechanism.

Theoretical basis:
    Jarrow & Li (working paper) — option-hedging feedback on the
    underlying.
    Hu, Pan, Wang & Zhu (2022) — gamma exposure and price impact.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = (price - fundamental) / fundamental

    If ``deviation <= 0``: hold (no upside gap to hedge).
    Else:
        hedge_qty = int(|deviation| * gamma_intensity * notional_scale)
        qty       = min(hedge_qty, int(cash / price))
    Emit buy (never sells; the delta hedge only tops up as price rises).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``gamma_intensity`` : float — hedge intensity per unit deviation
                             (default 0.30).
    * ``notional_scale``  : float — notional of underlying per unit
                             hedge signal (default 5000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleMarketMakerGamma(CanonicalRulePlayer):
    STRATEGY = "market-maker-gamma"
    DISPLAY_NAME = "Short-Gamma Dealer Hedger"
    SUMMARY = (
        "Delta-hedges a short-gamma book by mechanically buying as price "
        "rises above the reference (Jarrow-Li; Hu et al. 2022)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["gamma_intensity"] = float(
            extras.get("gamma_intensity", 0.30)
        )
        self.state.custom_state["notional_scale"] = float(
            extras.get("notional_scale", 5000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        gamma = self.state.custom_state["gamma_intensity"]
        notional = self.state.custom_state["notional_scale"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        deviation = state.deviation
        if deviation != deviation or math.isnan(deviation):
            return hold
        if deviation <= 0 or state.price <= 0:
            return hold

        hedge_qty = int(abs(deviation) * gamma * notional)
        affordable = int(state.cash / state.price) if state.price > 0 else 0
        qty = float(min(hedge_qty, max(affordable, 0)))
        if qty <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=qty,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMMarketMakerGamma(CanonicalLLMPlayer):
    STRATEGY = "market-maker-gamma"
    DEFAULT_SYS_PROMPT = """\
You are a dealer who is short gamma on this name (short call options
hedged with the underlying). As the price rises above your reference
you must mechanically buy more of the underlying to stay delta-neutral.
You never sell to hedge — a rising price always forces more buying —
and when the price is at or below reference the hedge is inactive.

Output format:
<analysis>state your upside gap and the resulting delta-hedge buy.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Decide as a short-gamma dealer: buy to hedge when price is above
reference, hold otherwise (never sell).
"""


__all__ = ["RuleMarketMakerGamma", "LLMMarketMakerGamma"]
