"""stop-loss-trader — Trailing stop-loss liquidator.

Canonical implementation of the ``stop-loss-trader`` archetype documented
in ``examples/AGENT_POOL/finance/stop-loss-trader.md``. Tracks a rolling
recent high and dumps the entire position once price drops by more than
the stop-loss fraction below that high.

Theoretical basis:
    Odean (1998) — pre-commitment stop-loss as a disposition-effect
    remedy.
    Shefrin & Statman (1985) — sell-discipline heuristics.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    recent_high = max of the last ``window`` observed prices
    if position > 0  and  price < recent_high * (1 - stop_loss):
        sell full position
    else:
        hold  (does not buy)

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``window``    : int   — recent-high lookback (default 10).
    * ``stop_loss`` : float — fractional drop from high to trigger
                      (default 0.05).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleStopLossTrader(CanonicalRulePlayer):
    STRATEGY = "stop-loss-trader"
    DISPLAY_NAME = "Trailing Stop-Loss Trader"
    SUMMARY = (
        "Liquidates the whole position when price falls a fixed fraction "
        "below a rolling recent high (Odean 1998; Shefrin-Statman 1985)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["window"] = int(extras.get("window", 10))
        self.state.custom_state["stop_loss"] = float(extras.get("stop_loss", 0.05))
        self.state.custom_state["price_history_stop"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        try:
            price = float(market_data["price"])
        except (KeyError, TypeError, ValueError):
            return
        window = self.state.custom_state["window"]
        buf: List[float] = self.state.custom_state.setdefault(
            "price_history_stop", []
        )
        buf.append(price)
        if len(buf) > window:
            del buf[: len(buf) - window]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        buf: List[float] = self.state.custom_state.get("price_history_stop") or []
        if not buf or state.position <= 0:
            return hold

        recent_high = max(buf)
        if recent_high <= 0:
            return hold
        stop_loss = self.state.custom_state["stop_loss"]

        if state.price < recent_high * (1.0 - stop_loss):
            return InvestorOrder.sell(
                quantity=float(state.position),
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )
        return hold


class LLMStopLossTrader(CanonicalLLMPlayer):
    STRATEGY = "stop-loss-trader"
    DEFAULT_SYS_PROMPT = """\
You are a disciplined stop-loss trader. You track the recent high of the
market and dump your entire position the moment price drops more than
your stop-loss percentage below that high. You do not re-buy — your job
is protection, not entry timing.

Output format:
<analysis>state the recent high, current price, and stop-loss trigger.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Liquidate fully when price is more than your stop-loss below the recent
high; otherwise hold.
"""


__all__ = ["RuleStopLossTrader", "LLMStopLossTrader"]
