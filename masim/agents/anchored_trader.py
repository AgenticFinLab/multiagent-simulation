"""anchored-trader — Anchoring-bias retail trader.

Canonical implementation of the ``anchored-trader`` archetype documented in
``examples/AGENT_POOL/finance/anchored-trader.md``. The archetype identifier
(``STRATEGY = "anchored-trader"``) matches the AGENT_POOL profile filename
stem verbatim and is the single source of truth used by
:mod:`masim.interface.customized.agent_catalog`, generated ``players.yml``
files, and the marketplace UI. Rule and LLM siblings share the same STRATEGY
so they are paired into one ``AgentEntry``.

Theoretical basis:
    Tversky & Kahneman (1974) — anchoring and adjustment heuristic.
    Northcraft & Neale (1987) — anchoring in expert judgement.
    Campbell & Sharpe (2009) — anchoring in forecast revisions.

Decision rule (verbatim from AGENT_POOL profile §Behavioral Framework):

    On the first market broadcast, fix ``anchor <- price``. On every
    subsequent round compute::

        target        = anchor + alpha * (fundamental - anchor)
        perceived_dev = (price - target) / target

    If ``perceived_dev < -threshold``: emit ``buy`` with
    ``quantity = min(base_position_size, |perceived_dev| * sizing_scale)``.
    If ``perceived_dev > threshold``: emit ``sell`` with the same sizing.
    Otherwise: ``hold``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``alpha``               : float in [0, 1] — fraction of the anchor→
                                 fundamental gap incorporated into the target
                                 (default 0.30, Tversky & Kahneman 1974).
    * ``threshold``           : float in [0, 1] — no-trade band around the
                                 anchor-pulled target (default 0.03,
                                 Campbell & Sharpe 2009).
    * ``base_position_size``  : float > 0 — maximum order size (default 20.0).
    * ``sizing_scale``        : float > 0 — deviation→quantity conversion
                                 factor (default 1000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleAnchoredTrader(CanonicalRulePlayer):
    STRATEGY = "anchored-trader"
    DISPLAY_NAME = "Anchoring-Bias Retail Trader"
    SUMMARY = (
        "Anchors to the first observed price; adjusts only partially toward "
        "the published fundamental (Tversky & Kahneman 1974)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["alpha"] = float(extras.get("alpha", 0.30))
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.03))
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 20.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 1000.0)
        )
        self.state.custom_state["anchor_price"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        if self.state.custom_state.get("anchor_price") is None:
            self.state.custom_state["anchor_price"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        anchor = self.state.custom_state.get("anchor_price")
        if anchor is None:
            # Should not happen (on_market_data set it), but stay defensive.
            anchor = state.price
        alpha = self.state.custom_state["alpha"]
        threshold = self.state.custom_state["threshold"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]

        target = anchor + alpha * (state.fundamental - anchor)
        if target <= 0:
            return InvestorOrder.hold(
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        perceived_dev = (state.price - target) / target

        if abs(perceived_dev) <= threshold:
            return InvestorOrder.hold(
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        quantity = min(base, abs(perceived_dev) * sizing)
        factory = InvestorOrder.buy if perceived_dev < 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMAnchoredTrader(CanonicalLLMPlayer):
    STRATEGY = "anchored-trader"
    DEFAULT_SYS_PROMPT = """\
You are an anchoring-bias retail trader. The first price you ever observed
feels like the "right" price; you only partially adjust toward the published
fundamental, never fully. When current price seems far from your anchor-
pulled target, you trade in the corrective direction; otherwise you hold.

Output format:
<analysis>state your current anchor, your partial-adjustment target,
           and how price compares.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Decide using your anchor-adjusted expectation: buy if price is well below
your anchor-pulled target, sell if well above, otherwise hold.
"""


__all__ = ["RuleAnchoredTrader", "LLMAnchoredTrader"]
