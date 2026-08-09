"""trend-follower — CTA/managed-futures time-series-momentum trader.

Canonical implementation of the ``trend-follower`` archetype documented
in ``masim/agents/defines/finance/trend-follower.md``. Detects a trend
signal from the deviation of price relative to a short moving average
and trades in the direction of that deviation, with position size scaled
by signal strength and a procyclical volatility multiplier.

Theoretical basis:
    Moskowitz, Ooi & Pedersen (2012) — Time-Series Momentum.

Decision rule (from AGENT_POOL profile §Behavioral Framework):

    MA        = mean(price_history[-lookback_window:])
    trend     = (price - MA) / MA
    strength  = min(|trend| / 0.05, 1.0)
    vol_ratio = volatility / baseline_volatility
    vol_multiplier = clamp(1.0 + volatility_sensitivity * (vol_ratio - 1),
                           0.5, 2.0)

    If ``|trend| <= trend_threshold``: hold.
    Else: direction = sign(trend); quantity =
          |direction| * base_position_size * strength * vol_multiplier,
          clamped to [0, 60].

Parameters (read from ``extras``; defaults from AGENT_POOL §Parameters):
    * ``lookback_window``         : int   — MA window (default 3).
    * ``trend_threshold``         : float — minimum |trend| (default 0.005).
    * ``base_position_size``      : float — base order size (default 30.0).
    * ``volatility_sensitivity``  : float — vol-scaling coefficient
                                     (default 0.8).
    * ``baseline_volatility``     : float — reference vol level
                                     (default 1.0).
    * ``max_quantity``            : float — |quantity| clamp (default 60.0).
"""

from __future__ import annotations

from typing import Any, Dict

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.format.state import StandardMarketState
from masim.format.order import InvestorOrder


class RuleTrendFollower(CanonicalRulePlayer):
    STRATEGY = "trend-follower"
    DISPLAY_NAME = "CTA Time-Series Momentum Trend Follower"
    SUMMARY = (
        "Trend-following CTA style: rides MA deviation with "
        "volatility-proportional sizing (Moskowitz, Ooi & Pedersen 2012)."
    )
    REQUIRES_FEATURES: tuple = ()

    def init_extras(self, extras: Dict[str, Any]) -> None:
        self.state.custom_state["lookback_window"] = int(
            extras.get("lookback_window", 3)
        )
        self.state.custom_state["trend_threshold"] = float(
            extras.get("trend_threshold", 0.005)
        )
        self.state.custom_state["base_position_size"] = float(
            extras.get("base_position_size", 30.0)
        )
        self.state.custom_state["volatility_sensitivity"] = float(
            extras.get("volatility_sensitivity", 0.8)
        )
        self.state.custom_state["baseline_volatility"] = float(
            extras.get("baseline_volatility", 1.0)
        )
        self.state.custom_state["max_quantity"] = float(
            extras.get("max_quantity", 60.0)
        )
        self.state.custom_state["price_series"] = []

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        # Maintain a rolling price buffer sized to lookback_window; the last
        # element is the current tick's price, used with the MA of the
        # window (which now includes the current price) — matches the
        # profile's Case 1 worked example where MA = mean of the window
        # ending at t and trend is computed against price(t+1). We store
        # lookback_window + 1 to allow computing trend against a prior MA.
        window = self.state.custom_state["lookback_window"]
        series = self.state.custom_state["price_series"]
        series.append(float(market_data["price"]))
        if len(series) > window + 1:
            self.state.custom_state["price_series"] = series[-(window + 1):]

    def decide_order(self, state: StandardMarketState) -> InvestorOrder:
        hold = InvestorOrder.hold(
            price=state.price, investor=self.identity, strategy=self.STRATEGY
        )
        window = self.state.custom_state["lookback_window"]
        series = self.state.custom_state["price_series"]

        # Need at least lookback_window prior prices to form the MA against
        # which the current price is compared.
        if len(series) < window + 1:
            return hold

        prior = series[-(window + 1):-1]  # exactly lookback_window entries
        ma = sum(prior) / len(prior)
        if ma <= 0:
            return hold
        trend = (state.price - ma) / ma

        threshold = self.state.custom_state["trend_threshold"]
        if abs(trend) <= threshold:
            return hold

        base = self.state.custom_state["base_position_size"]
        vol_sens = self.state.custom_state["volatility_sensitivity"]
        baseline_vol = self.state.custom_state["baseline_volatility"]
        cap = self.state.custom_state["max_quantity"]

        strength = min(abs(trend) / 0.05, 1.0)

        # Volatility multiplier — fall back to 1.0 when the scenario does
        # not broadcast volatility (per profile Missing-Signal Policy).
        if state.volatility is None or baseline_vol <= 0:
            vol_multiplier = 1.0
        else:
            vol_ratio = state.volatility / baseline_vol
            vol_multiplier = 1.0 + vol_sens * (vol_ratio - 1.0)
            if vol_multiplier < 0.5:
                vol_multiplier = 0.5
            elif vol_multiplier > 2.0:
                vol_multiplier = 2.0

        raw_quantity = base * strength * vol_multiplier
        quantity = min(cap, raw_quantity)
        if quantity <= 0:
            return hold

        factory = InvestorOrder.buy if trend > 0 else InvestorOrder.sell
        return factory(
            quantity=quantity,
            price=state.price,
            investor=self.identity,
            strategy=self.STRATEGY,
        )


class LLMTrendFollower(CanonicalLLMPlayer):
    STRATEGY = "trend-follower"
    DEFAULT_SYS_PROMPT = """\
You are a systematic trend-follower running a CTA-style time-series
momentum strategy. You compute the deviation of the current price from
a short moving average of recent prices; when that deviation exceeds
your threshold you trade in the direction of the trend. You scale up
in high-volatility regimes and down in calm regimes.

Output format:
<analysis>brief reasoning (1-2 sentences) on the MA deviation and trend.</analysis>
<decision>{"action": "buy"|"sell"|"hold", "quantity": <float>,
           "bid_price": <float>, "reasoning": "<audit trail>"}</decision>
"""
    DEFAULT_USER_PROMPT = """\
Round {round}: price={price:.2f} (prev {prev_price:.2f},
change {price_change:+.2%}), fundamental={fundamental:.2f}.
Portfolio: cash={cash:.2f}, position={position:.2f},
portfolio_value={portfolio_value:.2f}.
Follow the trend: buy if price is meaningfully above its recent moving
average, sell if it is meaningfully below, hold otherwise.
"""


__all__ = ["RuleTrendFollower", "LLMTrendFollower"]
