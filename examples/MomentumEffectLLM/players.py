"""MomentumEffectLLM - LLM-based Momentum Trading Simulation

Phenomenon: Momentum Effect with LLM Decision-Making
    - Past winners continue to outperform (positive momentum)
    - Past losers continue to underperform (negative momentum)
    - LLM investors interpret price trends through their strategies

Theoretical Foundation:
    - Jegadeesh & Titman (1993): Original momentum documentation
    - Conservatism Bias: Underreaction to new information
    - Information Diffusion: Gradual incorporation of information

LLM Investor Types:
    - Momentum Trader: Buys past winners, sells past losers
    - Contrarian Trader: Mean reversion strategy
    - Technical Trader: Moving average crossovers
    - Trend Follower: Strong directional bets
    - Fundamental Anchor: Value-based reversion
"""

import os
import json
import random
import re
import importlib
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# =============================================================================
# Market - Coordinator
# =============================================================================


class Market(GeneralPlayer):
    """Central market with momentum-aware dynamics."""

    INITIAL_PRICE = 100.0
    INITIAL_FUNDAMENTAL = 100.0
    PRICE_IMPACT = 0.08
    MEAN_REVERSION = 0.01
    NOISE_STD = 0.3
    DRIFT_PERSISTENCE = 0.95
    DRIFT_VOLATILITY = 0.5
    HISTORY_LIMIT = 200

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)

            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["fundamental"] = self.INITIAL_FUNDAMENTAL
            self.state.custom_state["drift"] = 0.0
            self.state.custom_state["returns"] = []

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order["bid_price"],
                        "quantity": order["quantity"],
                        "strategy": order["strategy"],
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        drift = self.state.custom_state["drift"]
        orders = self.state.custom_state["orders"]
        returns = self.state.custom_state["returns"]

        # Update fundamental with drift (creates momentum opportunities)
        new_drift = self.DRIFT_PERSISTENCE * drift + random.gauss(
            0, self.DRIFT_VOLATILITY
        )
        new_fundamental = fundamental + new_drift
        new_fundamental = max(50, min(150, new_fundamental))

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty

        # Price update
        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (new_fundamental - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        returns.append(price_return)
        if len(returns) > 20:
            returns.pop(0)

        # Calculate momentum indicators
        momentum_5 = sum(returns[-5:]) if len(returns) >= 5 else 0
        momentum_10 = sum(returns[-10:]) if len(returns) >= 10 else 0

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental
        self.state.custom_state["drift"] = new_drift
        self.state.custom_state["price_history"].append(new_price)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(
            f"  Momentum5: {momentum_5*100:+.2f}%, Momentum10: {momentum_10*100:+.2f}%"
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "momentum_5": momentum_5,
            "momentum_10": momentum_10,
            "fundamental": new_fundamental,
            "round": round_num,
            "recent_returns": returns[-10:],
        }

        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_price"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# LLM Momentum Investor Base Class
# =============================================================================


class LLMMomentumInvestor(GeneralPlayer):
    """Base class for LLM-powered momentum investors."""

    STRATEGY_NAME = "llm_momentum_base"
    SYSTEM_PROMPT = "You are an investor analyzing momentum patterns."
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 50.0
    HISTORY_LIMIT = 100

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION

            load_dotenv()
            llm_config = self.config.extras["llm"]
            lm_name = llm_config["lm_name"]
            generation_config = llm_config["generation_config"]

            self.state.custom_state["lm_name"] = lm_name
            self.state.custom_state["generation_config"] = generation_config

            llm_client = LangChainAPIInference(
                lm_name=lm_name,
                generation_config=generation_config,
            )
            self.state.custom_state["llm_client"] = llm_client

            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = state["state"].custom_state
            if "llm_client" in custom:
                custom = dict(custom)
                del custom["llm_client"]
                state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "lm_name" in custom and "llm_client" not in custom:
                llm_client = LangChainAPIInference(
                    lm_name=custom["lm_name"],
                    generation_config=custom["generation_config"],
                )
                custom["llm_client"] = llm_client

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]

        recent_prices = (
            list(price_history)[-10:]
            if len(price_history) >= 10
            else list(price_history)
        )

        llm_config = self.config.extras["llm"]
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
                price=market_data["price"],
                prev_price=market_data["prev_price"],
                return_pct=market_data["return_pct"],
                momentum_5=market_data["momentum_5"] * 100,
                momentum_10=market_data["momentum_10"] * 100,
                fundamental=market_data["fundamental"],
                recent_returns=[f"{r*100:.2f}%" for r in market_data["recent_returns"]],
                recent_prices=recent_prices,
                cash=cash,
                position=position,
                portfolio_value=cash + position * market_data["price"],
            )

        return f"""
Market Data:
- Price: ${market_data['price']:.2f}, Return: {market_data['return_pct']:+.2f}%
- Momentum (5-period): {market_data['momentum_5']*100:+.2f}%
- Momentum (10-period): {market_data['momentum_10']*100:+.2f}%
- Fundamental: ${market_data['fundamental']:.2f}
- Recent Prices: {recent_prices}

Your Portfolio:
- Cash: ${cash:.2f}, Position: {position:.2f} shares
- Portfolio Value: ${cash + position * market_data['price']:.2f}

Respond with JSON: {{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}}
"""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Failed to parse LLM response: {response_text[:100]}")

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            quantity = max(-position, quantity)
        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]

        user_prompt = self._build_prompt(market_data)
        llm_config = self.config.extras["llm"]
        system_prompt = (
            load_prompt(llm_config["sys_message"])
            if "sys_message" in llm_config
            else self.SYSTEM_PROMPT
        )

        max_retries = 3
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.response)
                break
            except ValueError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM failed after {max_retries} attempts: {e}")

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        quantity = self._apply_constraints(bid_price, quantity)

        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        print(
            f"[{self.identity:20s}] R{round_num} ({self.STRATEGY_NAME:15s}): Q={quantity:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
        }

        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# LLM Momentum Investor Types
# =============================================================================


class LLMMomentumTrader(LLMMomentumInvestor):
    """Buys past winners, sells past losers."""

    STRATEGY_NAME = "llm_momentum_trader"
    SYSTEM_PROMPT = """You are a MOMENTUM TRADER following Jegadeesh & Titman's strategy.

CORE BELIEF: "Winners keep winning, losers keep losing."

YOUR STRATEGY:
1. BUY when momentum is positive (price trending up)
2. SELL when momentum is negative (price trending down)
3. Stronger momentum = larger position

SIGNALS:
- Momentum_5 > 3%: Strong buy signal
- Momentum_5 > 1%: Moderate buy
- Momentum_5 < -3%: Strong sell signal
- Momentum_5 < -1%: Moderate sell

You believe in trend persistence. Don't fight the trend.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMContrarianTrader(LLMMomentumInvestor):
    """Mean reversion strategy - opposing momentum."""

    STRATEGY_NAME = "llm_contrarian"
    SYSTEM_PROMPT = """You are a CONTRARIAN TRADER betting on mean reversion.

CORE BELIEF: "What goes up must come down."

YOUR STRATEGY:
1. SELL when prices have risen too much (momentum too positive)
2. BUY when prices have fallen too much (momentum too negative)
3. You fade the trend

SIGNALS:
- Price > 110% of fundamental: Sell (overvalued)
- Price < 90% of fundamental: Buy (undervalued)
- Momentum_5 > 5%: Overbought - prepare to sell
- Momentum_5 < -5%: Oversold - prepare to buy

You provide stability by going against the crowd.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMTechnicalTrader(LLMMomentumInvestor):
    """Moving average crossover strategy."""

    STRATEGY_NAME = "llm_technical"
    SYSTEM_PROMPT = """You are a TECHNICAL TRADER using price patterns.

CORE BELIEF: "Price patterns predict future movements."

YOUR STRATEGY:
1. Track short-term vs long-term price averages
2. BUY when short-term crosses above long-term (golden cross)
3. SELL when short-term crosses below long-term (death cross)

ANALYSIS:
- Compare recent prices to earlier prices
- Look for breakouts above recent highs
- Look for breakdowns below recent lows
- Momentum reversal = potential trend change

You follow technical signals mechanically.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMTrendFollower(LLMMomentumInvestor):
    """Aggressive trend following."""

    STRATEGY_NAME = "llm_trend_follower"
    SYSTEM_PROMPT = """You are an AGGRESSIVE TREND FOLLOWER.

CORE BELIEF: "The trend is your friend until the end."

YOUR STRATEGY:
1. Identify the dominant trend
2. Take LARGE positions in trend direction
3. Cut losses quickly if trend reverses
4. Let winners run

RULES:
- If momentum_10 > 0: You are BULLISH - buy aggressively
- If momentum_10 < 0: You are BEARISH - sell aggressively
- Trend reversal (momentum sign change) = reverse position immediately

You are not afraid to take big positions.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMFundamentalAnchor(LLMMomentumInvestor):
    """Value-based anchor providing fundamental gravity."""

    STRATEGY_NAME = "llm_fundamental"
    SYSTEM_PROMPT = """You are a FUNDAMENTAL VALUE INVESTOR.

CORE BELIEF: "Price should reflect fundamental value."

YOUR STRATEGY:
1. Compare price to fundamental value
2. BUY when price < fundamental (undervalued)
3. SELL when price > fundamental (overvalued)
4. You don't care about momentum - only value

VALUE ZONES:
- Price/Fundamental < 0.90: Strong buy
- Price/Fundamental < 0.95: Moderate buy
- Price/Fundamental > 1.10: Strong sell
- Price/Fundamental > 1.05: Moderate sell

You provide an anchor that eventually pulls prices back.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""
