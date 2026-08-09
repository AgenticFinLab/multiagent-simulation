"""rational-portfolio-manager — Contrarian portfolio manager on short-term reversals.

Canonical implementation of the ``rational-portfolio-manager`` archetype
documented in ``masim/agents/defines/finance/rational-portfolio-manager.md``.
Trades contrarian to the single-tick return (not to fundamental), with
size scaled by |single-tick return| and risk aversion.

Theoretical basis:
    De Bondt & Thaler (1985) — overreaction and short-horizon reversals.
    Grossman & Miller (1988) — market making with inventory risk.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    r = (price - prev_price) / prev_price

    If ``|r| > deviation_threshold``:
        qty = min(base_size, int(|r| * risk_aversion * quantity_scale))
        direction = -sign(r)  (contrarian on short-term move)
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``risk_aversion``       : float — sizing coefficient (default 0.7).
    * ``base_size``           : float — per-tick order cap (default 500).
    * ``quantity_scale``      : float — r→qty conversion (default 3000).
    * ``deviation_threshold`` : float — activation band (default 0.02).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleRationalPortfolioManager(CanonicalRulePlayer):
    STRATEGY = "rational-portfolio-manager"
    DISPLAY_NAME = "Rational Portfolio Manager"
    SUMMARY = (
        "Contrarian on short-horizon reversals; sizes trades by risk "
        "aversion (De Bondt & Thaler 1985; Grossman & Miller 1988)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["risk_aversion"] = float(
            extras.get("risk_aversion", 0.7)
        )
        self.state.custom_state["base_size"] = float(extras.get("base_size", 500.0))
        self.state.custom_state["quantity_scale"] = float(
            extras.get("quantity_scale", 3000.0)
        )
        self.state.custom_state["deviation_threshold"] = float(
            extras.get("deviation_threshold", 0.02)
        )

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.prev_price <= 0:
            return hold

        threshold = self.state.custom_state["deviation_threshold"]
        base = self.state.custom_state["base_size"]
        scale = self.state.custom_state["quantity_scale"]
        gamma = self.state.custom_state["risk_aversion"]

        r = (state.price - state.prev_price) / state.prev_price
        if abs(r) <= threshold:
            return hold

        raw_qty = abs(r) * gamma * scale
        quantity = min(base, float(int(raw_qty)))
        if quantity <= 0:
            return hold

        # Contrarian on the short-term move.
        factory = InvestorOrder.sell if r > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMRationalPortfolioManager(CanonicalLLMPlayer):
    STRATEGY = "rational-portfolio-manager"
    DEFAULT_SYS_PROMPT = """\
You are a portfolio manager who exploits short-term overreaction. When
the market has just made a large one-tick move you fade it: sell into
sharp rallies, buy into sharp declines. Small moves you ignore. Trade
size scales with the move magnitude filtered through your risk aversion.

Output format:
<analysis>state the single-tick return and your contrarian stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}
(deviation {deviation:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Fade sharp short-term moves; hold when moves are small.
"""


__all__ = ["RuleRationalPortfolioManager", "LLMRationalPortfolioManager"]
