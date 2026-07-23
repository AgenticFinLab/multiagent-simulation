"""noise-trader — Random uninformed retail trader.

Canonical implementation of the ``noise-trader`` archetype documented in
``examples/AGENT_POOL/finance/noise-trader.md``. Supplies zero-mean random
order flow; neither converges nor diverges from fundamental on average.

The archetype identifier (``STRATEGY = "noise-trader"``) matches the
AGENT_POOL profile filename stem verbatim and is the single source of truth
used by :mod:`masim.interface.customized.agent_catalog`, generated
``players.yml`` files, and the marketplace UI. Rule and LLM siblings MUST
share the same STRATEGY so ``load_agent_catalog`` pairs them into one
``AgentEntry``.

Theoretical basis: Black (1986) — Noise Trader Risk.

Decision rule:
    With probability ``trade_probability`` (default 0.05) per round, place a
    random buy or sell of size ``random.uniform(min_order, max_order)``.

Parameters (read from ``extras``):
    * ``trade_probability``: float, [0, 1] — chance of trading per round.
    * ``min_order``: float — lower bound of order size.
    * ``max_order``: float — upper bound of order size.
"""

from __future__ import annotations

import random
from typing import Any, Dict

from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleNoiseTrader(CanonicalRulePlayer):
    STRATEGY = "noise-trader"
    DISPLAY_NAME = "Noise Trader"
    SUMMARY = "Random uninformed retail trader supplying microstructure noise (Black 1986)."
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["trade_probability"] = float(
            extras.get("trade_probability", 0.05)
        )
        self.state.custom_state["min_order"] = float(extras.get("min_order", 100.0))
        self.state.custom_state["max_order"] = float(extras.get("max_order", 500.0))

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        if random.random() >= self.state.custom_state["trade_probability"]:
            return InvestorOrder.hold(
                price=state.price,
                investor=self.identity,
                strategy=self.STRATEGY,
            )

        quantity = random.uniform(
            self.state.custom_state["min_order"],
            self.state.custom_state["max_order"],
        )
        factory = InvestorOrder.buy if random.random() > 0.5 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMNoiseTrader(CanonicalLLMPlayer):
    STRATEGY = "noise-trader"
    DEFAULT_SYS_PROMPT = (
        "You are a noise trader: an uninformed retail participant who trades\n"
        "small, mostly random orders for liquidity reasons. You do not study\n"
        "fundamentals or trends carefully; you just take small positions when\n"
        "the mood strikes. Hold most rounds.\n\n"
        "Output format:\n"
        "<analysis>brief reasoning (1-2 sentences)</analysis>\n"
        "<decision>{\"action\": \"buy\"|\"sell\"|\"hold\", \"quantity\": float,\n"
        "           \"bid_price\": float, \"reasoning\": \"...\"}</decision>\n"
    )
    DEFAULT_USER_PROMPT = (
        "Round {round}: price={price:.2f} (prev {prev_price:.2f},\n"
        "change {price_change:+.2%}), fundamental={fundamental:.2f}\n"
        "(deviation {deviation:+.2%}). Your portfolio: cash={cash:.2f},\n"
        "position={position:.2f}, portfolio_value={portfolio_value:.2f}.\n"
        "Decide: hold (most likely), or place a small noise trade.\n"
    )


__all__ = ["RuleNoiseTrader", "LLMNoiseTrader"]
