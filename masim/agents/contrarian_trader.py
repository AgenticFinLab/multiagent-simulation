"""contrarian-trader — Mean-reversion contrarian trader.

Canonical implementation of the ``contrarian-trader`` archetype documented
in ``masim/agents/defines/finance/contrarian-trader.md``. Fades extreme
cumulative moves and trades against the prevailing trend on a lookback
horizon — converges on fundamental after overshoots.

Theoretical basis:
    De Bondt & Thaler (1985) — long-horizon reversal.
    Jegadeesh (1990) — one-month reversal in individual stocks.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    cum_return = (price - price_{t - lookback}) / price_{t - lookback}

    If ``cum_return > +threshold``: sell — expect reversal after up-move.
    If ``cum_return < -threshold``: buy  — expect bounce after down-move.
    Otherwise: hold.

    Quantity = ``min(base_position_size, |cum_return| * sizing_scale)``.
    Requires a full ``lookback+1``-tick history before it can act.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback``            : int > 0 — window over which cumulative
                                 return is measured (default 10).
    * ``threshold``            : float in [0, 1] — cumulative-return trigger
                                 (default 0.05).
    * ``base_position_size``  : float > 0 — order-size cap (default 20.0).
    * ``sizing_scale``        : float > 0 — cum-return→quantity factor
                                 (default 400.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleContrarianTrader(CanonicalRulePlayer):
    STRATEGY = "contrarian-trader"
    DISPLAY_NAME = "Mean-Reversion Contrarian Trader"
    SUMMARY = (
        "Fades extreme deviations; trades against the prevailing trend "
        "(De Bondt & Thaler 1985; Jegadeesh 1990)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback"] = int(extras.get("lookback", 10))
        self.state.custom_state["threshold"] = float(extras.get("threshold", 0.05))
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 20.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 400.0)
        )
        self.state.custom_state["recent_prices"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        recent = self.state.custom_state["recent_prices"]
        recent.append(float(market_data["price"]))
        lookback = self.state.custom_state["lookback"]
        # keep lookback + 1 so we have both endpoints of the cum-return window
        if len(recent) > lookback + 1:
            self.state.custom_state["recent_prices"] = recent[-(lookback + 1):]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        recent = self.state.custom_state["recent_prices"]
        lookback = self.state.custom_state["lookback"]
        threshold = self.state.custom_state["threshold"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if len(recent) <= lookback:
            # Not yet enough history to compute cumulative return.
            return hold

        ref_price = recent[-(lookback + 1)]
        if ref_price <= 0:
            return hold
        cum_return = (state.price - ref_price) / ref_price

        if abs(cum_return) <= threshold:
            return hold

        quantity = min(base, abs(cum_return) * sizing)
        # Contrarian: sell the up-move, buy the down-move.
        factory = InvestorOrder.sell if cum_return > 0 else InvestorOrder.buy
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMContrarianTrader(CanonicalLLMPlayer):
    STRATEGY = "contrarian-trader"
    DEFAULT_SYS_PROMPT = """\
You are a mean-reversion contrarian trader. When the market has been
rallying you expect a reversal and lean short; when it has been selling
off you expect a bounce and lean long. You care about the size of the
cumulative move, not one-tick noise.

Output format:
<analysis>describe the cumulative move over the recent window
           and why you fade or hold.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Trade contrarian: fade extended rallies, buy sharp sell-offs, hold
otherwise.
"""


__all__ = ["RuleContrarianTrader", "LLMContrarianTrader"]
