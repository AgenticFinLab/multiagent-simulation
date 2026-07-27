"""hedged-carry-trader — Volatility-gated hedged carry trader.

Canonical implementation of the ``hedged-carry-trader`` archetype documented
in ``examples/AGENT_POOL/finance/hedged-carry-trader.md``. Enters partially
hedged carry positions during low-volatility regimes and unwinds when
volatility rises.

Theoretical basis:
    Menkhoff, Sarno, Schmeling & Schrimpf (2012) — Carry trades and
    global foreign exchange volatility.
    Brunnermeier, Nagel & Pedersen (2008) — Carry trades and currency
    crashes.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    adj_qty = base_size * (1 - hedge_ratio)
    If volatility is available and below ``vol_threshold`` and carry is
        favorable (``deviation >= 0`` — funding currency at fair or
        above): buy ``adj_qty`` capped by cash / price.
    If volatility is available and at/above ``vol_threshold`` and
        ``position > 0``: sell ``min(adj_qty, position)`` to unwind.
    Otherwise: hold.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``hedge_ratio``    : float — hedged fraction (default 0.30).
    * ``vol_threshold``  : float — exit trigger (default 0.05).
    * ``base_size``      : float — base order size (default 500.0).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHedgedCarryTrader(CanonicalRulePlayer):
    STRATEGY = "hedged-carry-trader"
    DISPLAY_NAME = "Hedged Carry Trader"
    SUMMARY = (
        "Enters partially hedged carry when volatility is low and unwinds "
        "when it spikes (Menkhoff et al. 2012; Brunnermeier et al. 2008)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["hedge_ratio"] = float(extras.get("hedge_ratio", 0.30))
        cs["vol_threshold"] = float(extras.get("vol_threshold", 0.05))
        cs["base_size"] = float(extras.get("base_size", 500.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        hedge_ratio = cs["hedge_ratio"]
        vol_threshold = cs["vol_threshold"]
        base_size = cs["base_size"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        # `volatility` is a canonical StandardMarketState field (see
        # masim/format/state.py) but is Optional there because not every
        # scenario models a rolling-volatility signal. When the direct
        # attribute is None we fall through to the raw payload as a
        # documented backup (some coordinators broadcast a scalar
        # ``volatility`` field alongside the price series); if it is not
        # present, the strategy holds instead of trading blind. This is
        # an *explicit* optional lookup — routed through raw_optional so
        # a code reader (or lint sweep) can see that a bare .get is not
        # a silent-default bug.
        volatility = state.volatility
        if volatility is None:
            volatility = state.raw_optional(
                "volatility", default=math.nan, cast=float
            )
        if math.isnan(volatility) or state.price <= 0:
            return hold

        adj_qty = base_size * (1.0 - hedge_ratio)
        if adj_qty <= 0:
            return hold

        # Carry favorable = deviation >= 0 (funding currency at fair or above).
        deviation_ok = (
            not math.isnan(state.deviation) and state.deviation >= 0.0
        )

        if volatility < vol_threshold and deviation_ok:
            quantity = min(adj_qty, state.cash / state.price)
            if quantity <= 0:
                return hold
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if volatility >= vol_threshold and state.position > 0:
            quantity = min(adj_qty, state.position)
            if quantity <= 0:
                return hold
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMHedgedCarryTrader(CanonicalLLMPlayer):
    STRATEGY = "hedged-carry-trader"
    DEFAULT_SYS_PROMPT = """\
You are a hedged carry trader. In calm markets with favorable carry
conditions you accumulate a partially hedged long position. When
volatility rises above your threshold you unwind that position to
avoid crash risk. You size all trades net of your hedge ratio.

Output format:
<analysis>state the volatility regime and your carry stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (change {price_change:+.2%}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Enter carry when volatility is low; unwind when volatility rises.
"""


__all__ = ["RuleHedgedCarryTrader", "LLMHedgedCarryTrader"]
