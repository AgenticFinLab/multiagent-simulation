"""vol-arbitrageur — Model-based volatility mean-reversion arbitrageur.

Canonical implementation of the ``vol-arbitrageur`` archetype documented
in ``masim/agents/defines/finance/vol-arbitrageur.md``. Trades large
dislocations back toward fundamental under a per-round capital cap that
encodes the limits-to-arbitrage discipline.

Theoretical basis:
    Shleifer & Vishny (1997) — Limits of arbitrage / capital constraints.
    Mixon (2007) — Volatility term-structure practice; linear size in
    deviation magnitude.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    deviation = state.deviation = (price - fundamental) / fundamental

    If ``|deviation| <= entry_threshold``: hold.
    Else:
        q_raw = min(cap, int(|deviation| * sizing_coefficient))
        If ``deviation > 0`` and ``position > 0``:
            sell q = min(q_raw, position).      (fade the expensive)
        Elif ``deviation < 0``:
            sell not applicable; buy q = min(q_raw, int(cash / price)).
        Else: hold (no inventory to sell into the up-side).

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``entry_threshold``     : float — activation gate (default 0.05).
    * ``sizing_coefficient``  : float — linear-size coefficient K_arb
                                 (default 20000.0).
    * ``per_round_cap``       : float — hard per-round unit cap
                                 (default 5000.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleVolArbitrageur(CanonicalRulePlayer):
    STRATEGY = "vol-arbitrageur"
    DISPLAY_NAME = "Volatility Mean-Reversion Arbitrageur"
    SUMMARY = (
        "Capital-constrained mean-reversion arb; fades large deviations "
        "under a per-round cap (Shleifer & Vishny 1997; Mixon 2007)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["entry_threshold"] = float(
            extras.get("entry_threshold", 0.05)
        )
        self.state.custom_state["sizing_coefficient"] = float(
            extras.get("sizing_coefficient", 20000.0)
        )
        self.state.custom_state["per_round_cap"] = float(
            extras.get("per_round_cap", 5000.0)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if math.isnan(state.fundamental) or math.isnan(state.deviation):
            return hold
        if state.price <= 0:
            return hold

        deviation = state.deviation
        theta = self.state.custom_state["entry_threshold"]
        if abs(deviation) <= theta:
            return hold

        cap = self.state.custom_state["per_round_cap"]
        k_arb = self.state.custom_state["sizing_coefficient"]
        q_raw = min(cap, float(int(abs(deviation) * k_arb)))

        if deviation > 0:
            # Fade the expensive side by selling long inventory.
            if state.position <= 0:
                return hold
            quantity = min(q_raw, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        # deviation < 0 → fade the cheap side by buying.
        max_affordable = float(int(state.cash / state.price)) if state.cash > 0 else 0.0
        quantity = min(q_raw, max_affordable)
        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMVolArbitrageur(CanonicalLLMPlayer):
    STRATEGY = "vol-arbitrageur"
    DEFAULT_SYS_PROMPT = """\
You are a model-based volatility-arbitrage desk. You trade against
large dislocations of price from your fundamental estimate — selling
when the proxy is expensive, buying when it is cheap — but you honour
a per-round capital cap that limits your convergence sizing. Small
deviations below your activation gate leave you flat.

Output format:
<analysis>brief reasoning (1-2 sentences) on deviation vs. entry gate.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Fade large deviations: sell rich, buy cheap, size linearly in |deviation|
subject to your per-round cap. Hold inside the activation band.
"""


__all__ = ["RuleVolArbitrageur", "LLMVolArbitrageur"]
