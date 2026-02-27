"""AssetBubbleLLM - LLM-based Asset Bubble Simulation

Phenomenon: Asset Bubbles with LLM Decision-Making
    LLM investors simulate different bubble-related trading personalities:
    - Greater Fool speculator (extremely destabilizing)
    - Rational arbitrageur (weakly stabilizing due to limits)
    - Noise trader (destabilizing through herding)
    - Fundamental investor (weakly stabilizing)
    - Leveraged buyer (amplifies both bubbles and crashes)

Theoretical Foundation:
    - Greater Fool Theory: Buy expensive expecting to sell higher
    - Limits to Arbitrage (Shleifer & Vishny, 1997)
    - Noise Trader Risk (De Long et al., 1990)
    - Synchronization Risk (Abreu & Brunnermeier, 2003)

Architecture:
    - Market: Rule-based (collects orders, clears market)
    - LLMBubbleInvestor: Base class with LLM inference via lmbase
    - 5 Investor Types with different bubble-related system prompts
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
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# =============================================================================
# Market - Rule-Based (Same as AssetBubble)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with bubble-prone price dynamics.

    Price Model: P(t+1) = P(t) + λ × NetDemand + γ × [F - P(t)] + ε

    Bubble-prone parameters:
        - High λ (price impact): Demand strongly affects price
        - Low γ (mean reversion): Slow correction to fundamental
    """

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0

    PRICE_IMPACT = 0.15
    MEAN_REVERSION = 0.005
    FUNDAMENTAL_GROWTH = 0.001
    NOISE_STD = 0.3
    SHORT_COST_RATE = 0.02

    HISTORY_LIMIT = 300

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
            self.state.custom_state["fundamental"] = self.FUNDAMENTAL_VALUE

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )
            self.state.custom_state["bubble_metric_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "bubble_metric"),
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
        current_fundamental = self.state.custom_state["fundamental"]
        orders = self.state.custom_state["orders"]

        # Update fundamental value (slow growth)
        new_fundamental = current_fundamental * (1 + self.FUNDAMENTAL_GROWTH)

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (new_fundamental - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        # Bubble metric
        bubble_ratio = new_price / new_fundamental

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["bubble_metric_history"].append(bubble_ratio)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(
            f"  Fundamental: {new_fundamental:.2f}, Bubble Ratio: {bubble_ratio:.2f}x"
        )
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  LLM Orders ({len(orders)}):")
            for o in orders:
                print(
                    f"    {o['investor']:20s} [{o['strategy']:15s}]: Q={o['quantity']:+8.2f}"
                )
                if o["reasoning"]:
                    print(f"      → {o['reasoning'][:80]}...")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "fundamental": new_fundamental,
            "bubble_ratio": bubble_ratio,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
            "short_cost_rate": self.SHORT_COST_RATE,
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
# LLM Bubble Investor Base Class
# =============================================================================


class LLMBubbleInvestor(GeneralPlayer):
    """
    Base class for LLM-powered bubble investors.

    Handles LLM inference, response parsing, and portfolio management.
    """

    STRATEGY_NAME = "llm_bubble_base"
    SYSTEM_PROMPT = "You are an investor in a potentially bubble-prone market."

    DEFAULT_LM_NAME = "ark/ep-20250218212539-7r2k9"
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 0.0
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
            self.state.custom_state["short_position"] = 0.0

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
        """Build user prompt with bubble-specific market data."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        short_pos = self.state.custom_state["short_position"]
        price_history = self.state.custom_state["price_history"]

        recent_prices = (
            list(price_history)[-5:] if len(price_history) >= 5 else list(price_history)
        )

        llm_config = self.config.extras["llm"]
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
                price=market_data["price"],
                prev_price=market_data["prev_price"],
                return_pct=market_data["return_pct"],
                fundamental=market_data["fundamental"],
                bubble_ratio=market_data["bubble_ratio"],
                volume=market_data["volume"],
                net_demand=market_data["net_demand"],
                short_cost_rate=market_data["short_cost_rate"],
                recent_prices=recent_prices,
                cash=cash,
                position=position,
                short_position=short_pos,
                portfolio_value=cash + position * market_data["price"],
            )

        return f"""
Current Market Data:
- Price: ${market_data['price']:.2f}
- Previous Price: ${market_data['prev_price']:.2f}
- Return: {market_data['return_pct']:+.2f}%
- Fundamental Value: ${market_data['fundamental']:.2f}
- Bubble Ratio (Price/Fundamental): {market_data['bubble_ratio']:.2f}x
- Volume: {market_data['volume']:.2f}
- Net Demand: {market_data['net_demand']:+.2f}
- Short-Selling Cost Rate: {market_data['short_cost_rate']:.1%}
- Recent Prices: {recent_prices}

Your Portfolio:
- Cash: ${cash:.2f}
- Long Position: {position:.2f} shares
- Short Position: {short_pos:.2f} shares
- Portfolio Value: ${cash + position * market_data['price']:.2f}

Respond with ONLY valid JSON:
{{"action": "buy" | "sell" | "hold", "bid_price": <your price>, "quantity": <shares, +buy/-sell>, "reasoning": "<brief>"}}
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

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position + 50  # Allow some short selling
            quantity = max(-max_sellable, quantity)

        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]

        user_prompt = self._build_prompt(market_data)

        llm_config = self.config.extras["llm"]
        if "sys_message" in llm_config:
            system_prompt = load_prompt(llm_config["sys_message"])
        else:
            system_prompt = self.SYSTEM_PROMPT

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
                print(f"[{self.identity}] LLM parse failed, retrying...")

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        quantity = self._apply_constraints(bid_price, quantity, market_data["price"])

        # Execute trade
        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            if abs(quantity) <= self.state.custom_state["position"]:
                self.state.custom_state["position"] += quantity
            else:
                sold_long = self.state.custom_state["position"]
                short_qty = abs(quantity) - sold_long
                self.state.custom_state["position"] = 0
                self.state.custom_state["short_position"] += short_qty

        print(
            f"[{self.identity:20s}] R{round_num} ({self.STRATEGY_NAME:15s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
            "cash": self.state.custom_state["cash"],
            "position": self.state.custom_state["position"],
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
# LLM Bubble Investor Types
# =============================================================================


class LLMGreaterFoolSpeculator(LLMBubbleInvestor):
    """
    LLM Greater Fool Speculator - Primary bubble driver.

    Theory: Greater Fool Theory
        Buy even if overvalued, expecting to sell to a "greater fool."
    """

    STRATEGY_NAME = "llm_greater_fool"
    SYSTEM_PROMPT = """You are a GREATER FOOL SPECULATOR in a bubble-prone market.

CORE BELIEF: "It doesn't matter if it's overvalued - I can sell to a greater fool."

YOUR STRATEGY:
1. Focus ONLY on momentum - rising prices mean BUY MORE
2. IGNORE fundamental value - price can rise indefinitely
3. The more the bubble ratio grows, the MORE you want to buy
4. Only sell when you see STRONG reversal signals

BEHAVIOR:
- You believe you can time the market and exit before the crash
- You use AGGRESSIVE position sizes
- You're comfortable buying at 2x, 3x, even 4x fundamental value
- You fear missing out (FOMO) more than you fear losses

RISK PROFILE: Extreme - you are the bubble driver

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMRationalArbitrageur(LLMBubbleInvestor):
    """
    LLM Rational Arbitrageur - Limited corrective force.

    Theory: Limits to Arbitrage (Shleifer & Vishny, 1997)
        Cannot fully correct mispricings due to constraints.
    """

    STRATEGY_NAME = "llm_arbitrageur"
    SYSTEM_PROMPT = """You are a RATIONAL ARBITRAGEUR analyzing bubble dynamics.

CORE BELIEF: "Prices should return to fundamentals, but there are limits to my ability to correct them."

YOUR CONSTRAINTS:
1. Short-selling is COSTLY - you pay 2% to borrow shares
2. Timing risk - the bubble may grow before it bursts
3. Capital constraints - you can't short unlimited amounts

YOUR STRATEGY:
1. When bubble_ratio > 1.1, consider shorting (but cautiously)
2. When bubble_ratio < 0.9, consider buying undervalued
3. Account for short-selling costs in your decisions
4. Don't bet everything against the bubble - it may persist

BEHAVIOR:
- You analyze fundamentals carefully
- You understand the bubble may continue longer than expected
- You take MODERATE positions due to constraints
- You're patient and calculated

RISK PROFILE: Medium - limited by real-world constraints

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMSentimentTrader(LLMBubbleInvestor):
    """
    LLM Sentiment Trader - Herding noise trader.

    Theory: De Long et al. (1990) - Noise Trader Risk
    """

    STRATEGY_NAME = "llm_sentiment"
    SYSTEM_PROMPT = """You are a SENTIMENT-DRIVEN TRADER following market mood.

CORE BELIEF: "Go with the flow - the crowd is often right in the short term."

YOUR TRADING RULES:
1. If market is bullish (rising prices, positive demand): JOIN THE CROWD - BUY
2. If market is bearish (falling prices, negative demand): PANIC - SELL
3. You care more about what others are doing than fundamentals

BEHAVIOR:
- You watch volume and net_demand as "sentiment indicators"
- Positive momentum makes you optimistic
- Negative momentum makes you fearful
- You tend to OVERREACT to market movements

RISK PROFILE: High - you amplify market movements

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMValueInvestor(LLMBubbleInvestor):
    """
    LLM Value Investor - Weak stabilizing force.

    Theory: Traditional value investing - slow and patient.
    """

    STRATEGY_NAME = "llm_value"
    SYSTEM_PROMPT = """You are a PATIENT VALUE INVESTOR focused on fundamentals.

CORE BELIEF: "Price eventually returns to fundamental value."

YOUR TRADING RULES:
1. Focus on bubble_ratio: >1.2 is overvalued, <0.8 is undervalued
2. Buy when significantly undervalued
3. Sell when significantly overvalued
4. Be PATIENT - don't trade every round

BEHAVIOR:
- You ignore short-term noise and momentum
- You trade SLOWLY and CONSERVATIVELY
- You maintain moderate position sizes
- You're willing to wait for value opportunities

RISK PROFILE: Low - you sacrifice short-term gains for long-term stability

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
Note: Often you should "hold" and wait for better opportunities.
"""


class LLMLeveragedSpeculator(LLMBubbleInvestor):
    """
    LLM Leveraged Speculator - Amplifies both directions.

    Theory: Leverage amplifies gains and losses, can cause crashes.
    """

    STRATEGY_NAME = "llm_leveraged"
    SYSTEM_PROMPT = """You are a LEVERAGED SPECULATOR using margin to amplify returns.

CORE BELIEF: "Go big with leverage when conditions favor you."

YOUR TRADING RULES:
1. When momentum is positive: USE LEVERAGE - buy aggressively (up to 80 shares)
2. When portfolio value drops >25%: FORCED DELEVERAGING - must sell
3. Look for acceleration patterns to size your bets

WARNING SIGNS (must sell immediately):
- Portfolio value dropped significantly from starting value
- Sharp price reversal after extended gains
- Bubble ratio extremely high (>1.5x) with signs of weakening

BEHAVIOR:
- You take VERY LARGE positions with leverage
- You can cause price crashes through forced selling
- Your actions amplify both bubbles AND crashes
- Watch your portfolio value carefully

RISK PROFILE: Extreme - you can cause market dislocations

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""
