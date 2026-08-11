"""hft-market-maker — Binary-regime HFT market maker with velocity gate.

Canonical implementation of the ``hft-market-maker`` archetype documented
in ``masim/agents/defines/finance/hft-market-maker.md``. Provides a fixed
``quote_size`` of liquidity per round while a 5-round mean absolute
return stays below the withdrawal threshold; withdraws (hold) otherwise.

Theoretical basis:
    Kirilenko, Kyle, Samadi & Tuzun (2017) — The Flash Crash: HFT in an
    electronic market.
    Biais, Foucault & Moinas (2015) — Equilibrium fast trading.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    Append current price to internal ``price_history`` each round.
    If ``len(price_history) < 5``: default calm state (provide liquidity).
    Else compute returns_i = |P_i - P_{i-1}| / P_{i-1} for the last four
    intervals; velocity = mean(returns).
    If ``velocity > withdrawal_threshold``: hold (withdraw quotes).
    Else: emit a buy order of ``quote_size`` (provide liquidity).

Notes: The profile's calm state is symmetric two-sided quoting; because
the InvestorOrder framework carries a single directional order, the
canonical implementation uses a buy tilt sized by ``quote_size`` (the
base ``_finalize_order`` clip prevents cash busts). Scenarios wanting
alternating quotes should override in their local variant.

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``withdrawal_threshold`` : float — velocity gate (default 0.02).
    * ``normal_spread``        : float — calm-state spread (default 0.002).
    * ``stress_spread``        : float — stress spread (default 0.02).
    * ``quote_size``           : float — quote depth (default 500.0).
    * ``inventory_limit``      : int — inventory cap (default 10000).
"""

from __future__ import annotations

from typing import Any, Dict, List

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleHftMarketMaker(CanonicalRulePlayer):
    STRATEGY = "hft-market-maker"
    DISPLAY_NAME = "HFT Market Maker (Binary Regime)"
    SUMMARY = (
        "Provides fixed-size liquidity while 5-round velocity is calm; "
        "withdraws when stressed (Kirilenko et al. 2017; Biais et al. 2015)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        cs = self.state.custom_state
        cs["withdrawal_threshold"] = float(extras.get("withdrawal_threshold", 0.02))
        cs["normal_spread"] = float(extras.get("normal_spread", 0.002))
        cs["stress_spread"] = float(extras.get("stress_spread", 0.02))
        cs["quote_size"] = float(extras.get("quote_size", 500.0))
        cs["inventory_limit"] = int(extras.get("inventory_limit", 10000))
        cs["hft_price_history"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        history: List[float] = self.state.custom_state["hft_price_history"]
        try:
            history.append(float(market_data["price"]))
        except (KeyError, TypeError, ValueError):
            return

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        cs = self.state.custom_state
        threshold = cs["withdrawal_threshold"]
        quote_size = cs["quote_size"]
        inv_limit = cs["inventory_limit"]
        history: List[float] = cs["hft_price_history"]

        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        if state.price <= 0 or quote_size <= 0:
            return hold

        # Cold-start: fewer than 5 history entries → default calm state.
        stressed = False
        if len(history) >= 5:
            window = history[-5:]
            returns = []
            for i in range(1, 5):
                prev = window[i - 1]
                if prev <= 0:
                    continue
                returns.append(abs(window[i] - prev) / prev)
            if returns:
                velocity = sum(returns) / len(returns)
                stressed = velocity > threshold

        if stressed:
            return hold

        capacity = max(0.0, inv_limit - state.position)
        quantity = min(quote_size, state.cash / state.price, capacity)
        if quantity <= 0:
            return hold
        return InvestorOrder.buy(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMHftMarketMaker(CanonicalLLMPlayer):
    STRATEGY = "hft-market-maker"
    DEFAULT_SYS_PROMPT = """\
You are a high-frequency market maker with binary-regime behaviour. In
calm markets (recent absolute returns are small on average) you post
tight liquidity. As soon as recent volatility spikes above your
withdrawal threshold you pull all quotes and step aside.

Output format:
<analysis>state your calm/stressed regime and quoting stance.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}). Portfolio: cash={cash:.2f},
position={position:.2f}, portfolio_value={portfolio_value:.2f}.
Provide liquidity in calm markets, withdraw when velocity spikes.
"""


__all__ = ["RuleHftMarketMaker", "LLMHftMarketMaker"]
