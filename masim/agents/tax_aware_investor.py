"""tax-aware-investor — Tax-loss harvester / gain deferrer.

Canonical implementation of the ``tax-aware-investor`` archetype documented
in ``examples/AGENT_POOL/finance/tax-aware-investor.md``. Anchors to a
running cost basis: harvests losses aggressively (opposite of the
disposition effect) and defers gains until they become very large.

Theoretical basis:
    Constantinides (1983) — optimal tax-loss harvesting.
    Dammon, Spatt & Zhang (2004) — optimal asset location and gain
    deferral.
    Arnott, Berkin & Ye (2001) — empirical harvesting alpha.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    gain_pct = (price - cost_basis) / cost_basis

    if gain_pct < tax_loss_threshold:
        sell tax_harvest_fraction * position          # harvest
    elif gain_pct > capital_gains_hold:
        sell gain_sell_fraction   * position          # realise big gain
    else:
        hold                                          # defer

    ``cost_basis`` is seeded from the first observed price (or from
    ``initial_cost_basis`` if provided) and is left unchanged for the
    remaining lot after a partial sell.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``tax_loss_threshold``   : float — negative pnl trigger for harvest
                                 (default -0.05).
    * ``capital_gains_hold``   : float — positive pnl trigger for gain
                                 realisation (default 0.20).
    * ``tax_harvest_fraction`` : float — fraction sold on harvest
                                 (default 0.50).
    * ``gain_sell_fraction``   : float — fraction sold on gain
                                 (default 0.30).
    * ``initial_cost_basis``   : float — optional seed for cost basis;
                                 if unset, seeded from first observed
                                 price.
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleTaxAwareInvestor(CanonicalRulePlayer):
    STRATEGY = "tax-aware-investor"
    DISPLAY_NAME = "Tax-Aware Investor"
    SUMMARY = (
        "Harvests losses fast and defers gains — the mirror-image of the "
        "disposition effect (Constantinides 1983; Dammon-Spatt-Zhang 2004; "
        "Arnott-Berkin-Ye 2001)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["tax_loss_threshold"] = float(
            extras.get("tax_loss_threshold", -0.05)
        )
        self.state.custom_state["capital_gains_hold"] = float(
            extras.get("capital_gains_hold", 0.20)
        )
        self.state.custom_state["tax_harvest_fraction"] = float(
            extras.get("tax_harvest_fraction", 0.50)
        )
        self.state.custom_state["gain_sell_fraction"] = float(
            extras.get("gain_sell_fraction", 0.30)
        )
        seed = extras.get("initial_cost_basis")
        self.state.custom_state["cost_basis"] = (
            float(seed) if seed is not None else None
        )

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("cost_basis") is None:
            try:
                self.state.custom_state["cost_basis"] = float(
                    market_data["price"]
                )
            except (KeyError, TypeError, ValueError):
                return

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        cost_basis = self.state.custom_state.get("cost_basis")
        if cost_basis is None or cost_basis <= 0:
            return hold
        if state.position <= 0:
            return hold

        gain_pct = (state.price - cost_basis) / cost_basis

        loss_thr = self.state.custom_state["tax_loss_threshold"]
        gain_thr = self.state.custom_state["capital_gains_hold"]
        harvest_frac = self.state.custom_state["tax_harvest_fraction"]
        gain_frac = self.state.custom_state["gain_sell_fraction"]

        if gain_pct < loss_thr:
            quantity = min(harvest_frac * state.position, state.position)
        elif gain_pct > gain_thr:
            quantity = min(gain_frac * state.position, state.position)
        else:
            return hold

        if quantity <= 0:
            return hold
        return InvestorOrder.sell(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMTaxAwareInvestor(CanonicalLLMPlayer):
    STRATEGY = "tax-aware-investor"
    DEFAULT_SYS_PROMPT = """\
You are a tax-aware investor who optimises after-tax wealth. You harvest
losses fast (selling losers to bank the tax deduction) and defer gains
as long as possible (only trimming very large gains). You never trade on
momentum, fundamentals, or technicals — only unrealised gain vs your
cost basis.

Output format:
<analysis>state gain vs cost basis and which branch fires.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Harvest a fraction of position when loss exceeds your loss threshold;
realise a fraction on very large gains; otherwise hold.
"""


__all__ = ["RuleTaxAwareInvestor", "LLMTaxAwareInvestor"]
