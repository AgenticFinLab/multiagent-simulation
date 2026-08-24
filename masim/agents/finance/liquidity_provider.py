"""liquidity-provider — Two-sided liquidity provider.

Canonical implementation of the ``liquidity-provider`` archetype documented
in ``masim/agents/defines/finance/liquidity-provider.md``. Quotes a two-sided
band around a short-term EMA of price; buys when price is below the bid
edge, sells when above the ask edge — earns the spread.

Theoretical basis:
    Glosten & Milgrom (1985) — bid-ask spread with informed traders.
    Hendershott, Jones & Menkveld (2011) — electronic liquidity provision.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    alpha        = 2 / (ema_window + 1)
    ema_{t}      = alpha * price + (1 - alpha) * ema_{t-1}
    fair_quote   = 0.5 * (price + ema)
    band         = half_spread * fair_quote

    If ``price < fair_quote - band``: buy (bid side hit).
    If ``price > fair_quote + band``: sell (ask side hit).
    Otherwise: hold.

    Quantity = ``min(base_position_size, dev_from_band * sizing_scale)``,
    where ``dev_from_band = |price - fair_quote| / fair_quote``.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``ema_window``          : int > 0 — EMA smoothing window (default 20).
    * ``half_spread``         : float in [0, 1] — half-width of the no-trade
                                 band as a fraction of fair quote
                                 (default 0.015).
    * ``base_position_size``  : float > 0 — order-size cap (default 30.0).
    * ``sizing_scale``        : float > 0 — dev→quantity factor
                                 (default 2000.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleLiquidityProvider(CanonicalRulePlayer):
    STRATEGY = "liquidity-provider"
    DISPLAY_NAME = "Two-Sided Liquidity Provider"
    SUMMARY = (
        "Quotes two-sided around a short-term EMA and absorbs order flow "
        "(Glosten-Milgrom 1985; Hendershott et al. 2011)."
    )
    REQUIRES_FEATURES: tuple = ()
    PARAM_SPECS: Dict[str, Any] = {
        "ema_window": {"type": "int", "range": (1, None)},
        "half_spread": {"type": "float", "range": (0.0, 1.0)},
        "base_position_size": {"type": "float", "range": (0.0, None)},
        "sizing_scale": {"type": "float", "range": (0.0, None)},
    }

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["ema_window"] = int(extras.get("ema_window", 20))
        self.state.custom_state["half_spread"] = float(
            extras.get("half_spread", 0.015)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 30.0)
        )
        self.state.custom_state["sizing_scale"] = float(
            extras.get("sizing_scale", 2000.0)
        )
        self.state.custom_state["ema"] = None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        # Seed the EMA to the first-observed price so the very first
        # decision has a well-defined smoothed reference.
        if self.state.custom_state.get("ema") is None:
            self.state.custom_state["ema"] = float(market_data["price"])

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        ema_window = self.state.custom_state["ema_window"]
        half_spread = self.state.custom_state["half_spread"]
        base = self.state.custom_state["base_position_size"]
        sizing = self.state.custom_state["sizing_scale"]
        ema = self.state.custom_state.get("ema") or state.price

        alpha = 2.0 / (ema_window + 1)
        ema = alpha * state.price + (1.0 - alpha) * ema
        self.state.custom_state["ema"] = ema

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        fair_quote = 0.5 * (state.price + ema)
        if fair_quote <= 0:
            return hold
        band = half_spread * fair_quote

        if state.price < fair_quote - band:
            dev_from_band = abs(state.price - fair_quote) / fair_quote
            quantity = min(base, dev_from_band * sizing)
            return InvestorOrder.buy(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        if state.price > fair_quote + band:
            dev_from_band = abs(state.price - fair_quote) / fair_quote
            quantity = min(base, dev_from_band * sizing)
            return InvestorOrder.sell(
                quantity=quantity,
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMLiquidityProvider(CanonicalLLMPlayer):
    STRATEGY = "liquidity-provider"
    DEFAULT_SYS_PROMPT = """\
You are a two-sided liquidity provider. You quote a bid/ask band around a
short-term smoothed reference. When price ticks below your bid you take
inventory in; when it ticks above your ask you offload. You earn the
spread and stay flat on average.

Output format:
<analysis>state your smoothed reference and where price sits vs the band.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f}),
fundamental={fundamental:.2f} (deviation {deviation:+.2%}).
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Provide liquidity: buy if price is below your bid edge, sell if above
your ask edge, hold inside the band.
"""


__all__ = ["RuleLiquidityProvider", "LLMLiquidityProvider"]
