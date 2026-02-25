"""HerdEffectLLM - LLM-based Investors for Emergent Herding Simulation

This module implements LLM-powered investors that simulate different trading
personalities through prompts. Unlike the rule-based HerdEffect, each investor
here uses an LLM to make decisions based on their defined financial characteristics.

Architecture:
    - Market: Rule-based (same as HerdEffect) - collects orders, clears market
    - LLMInvestor: Base class handling LLM interaction via lmbase
    - 5 Investor Types: Momentum, Contrarian, RiskAverse, Aggressive, Noise

LLM Provider:
    Uses lmbase.inference.api_call.LangChainAPIInference for ByteDance Doubao API.
    Set environment variable ARK_API_KEY for authentication.

LLM Output Format:
    {
        "action": "buy" | "sell" | "hold",
        "bid_price": float,
        "quantity": float,
        "reasoning": string
    }

Flow per Round:
    Market broadcasts (price, volume) → LLM Investors generate orders → Market clears
"""

import os
import json
import random
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

# lmbase for LLM inference
from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput


# =============================================================================
# Market Player - Rule-Based Order Clearing (Same as HerdEffect)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with order-based clearing mechanism.

    This is a rule-based player (NOT LLM) that:
    1. Collects all buy/sell orders from investors
    2. Calculates clearing price based on supply-demand dynamics
    3. Broadcasts market data to all investors

    Price dynamics: P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε
    """

    INITIAL_PRICE = 100.0
    FUNDAMENTAL_VALUE = 100.0
    SUPPLY_ELASTICITY = 0.1
    MEAN_REVERSION = 0.02
    NOISE_STD = 0.5
    HISTORY_LIMIT = 200

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        # Initialize on first round
        if "price" not in self.state.custom_state:
            self.state.custom_state["price"] = self.INITIAL_PRICE
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/HerdEffectLLM/history"
            )
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
                initial_values=[self.INITIAL_PRICE],
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=self.HISTORY_LIMIT,
                initial_values=[0],
            )

        # Collect orders from LLM investors
        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order.get(
                            "bid_price", self.state.custom_state["price"]
                        ),
                        "quantity": order.get("quantity", 0),
                        "strategy": order.get("strategy", "unknown"),
                        "reasoning": order.get("reasoning", ""),
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Order-based clearing
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty

        # Price dynamics
        price_impact = self.SUPPLY_ELASTICITY * net_demand
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price
        total_volume = total_buy_qty + total_sell_qty

        # Update state
        prev_price = self.state.custom_state["price"]
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)

        # Log
        print(f"\n{'='*60}")
        print(f"[Market] Round {round_num}")
        print(f"  Price: {prev_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)")
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  LLM Orders ({len(orders)}):")
            for o in orders:
                print(
                    f"    {o['investor']:20s} [{o['strategy']:12s}]: "
                    f"P={o['price']:7.2f}, Q={o['quantity']:+7.2f}"
                )
                if o.get("reasoning"):
                    print(f"      → {o['reasoning'][:80]}...")

        market_data = {
            "price": new_price,
            "prev_price": prev_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
            "fundamental": self.FUNDAMENTAL_VALUE,
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
# LLM Investor Base Class
# =============================================================================


class LLMInvestor(GeneralPlayer):
    """
    Base class for LLM-powered investors using lmbase.

    Handles:
    - LLM client initialization via lmbase.LangChainAPIInference
    - JSON response parsing
    - Cash/position constraints
    - Ray serialization (__getstate__/__setstate__)

    LLM Configuration:
        Uses lm_name format: "ark/ep-xxxx" for ByteDance Doubao
        Requires ARK_API_KEY environment variable

    Subclasses define STRATEGY_NAME and SYSTEM_PROMPT.
    """

    STRATEGY_NAME = "llm_base"
    SYSTEM_PROMPT = "You are an investor making trading decisions."

    # Default LLM model (ByteDance Doubao)
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

        # Initialize
        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION

            # Initialize LLM client via lmbase
            load_dotenv()
            llm_config = self.config.extras.get("llm_api", {})
            lm_name = llm_config.get("lm_name", self.DEFAULT_LM_NAME)
            generation_config = llm_config.get(
                "generation_config",
                {
                    "temperature": 0.3,
                    "max_new_tokens": 500,
                },
            )

            self.state.custom_state["lm_name"] = lm_name
            self.state.custom_state["generation_config"] = generation_config

            # Create LangChainAPIInference instance
            try:
                llm_client = LangChainAPIInference(
                    lm_name=lm_name,
                    generation_config=generation_config,
                )
                self.state.custom_state["llm_client"] = llm_client
            except Exception as e:
                print(f"[{self.identity}] Failed to init LLM: {e}")
                self.state.custom_state["llm_client"] = None

            # History buffer
            record_path = self.config.extras.get(
                "record_path", "EXPERIMENT/HerdEffectLLM/history"
            )
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=self.HISTORY_LIMIT,
            )

        # Get market data
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    def __getstate__(self):
        """Prepare for Ray serialization - remove non-serializable LLM client."""
        state = self.__dict__.copy()
        # Remove LLM client from custom_state if it exists
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = state["state"].custom_state
            if "llm_client" in custom:
                custom = dict(custom)
                del custom["llm_client"]
                state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
        """Restore from Ray serialization - reinitialize LLM client."""
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom = self.state.custom_state
            if "lm_name" in custom and "llm_client" not in custom:
                try:
                    llm_client = LangChainAPIInference(
                        lm_name=custom["lm_name"],
                        generation_config=custom.get("generation_config", {}),
                    )
                    custom["llm_client"] = llm_client
                except Exception as e:
                    print(f"Failed to reinit LLM: {e}")
                    custom["llm_client"] = None

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build the user prompt with market data. Override in subclass."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]

        # Recent prices
        recent_prices = (
            list(price_history)[-5:] if len(price_history) >= 5 else list(price_history)
        )

        return f"""
Current Market Data:
- Price: ${market_data['price']:.2f}
- Previous Price: ${market_data['prev_price']:.2f}
- Return: {market_data['return_pct']:+.2f}%
- Volume: {market_data['volume']:.2f}
- Net Demand: {market_data['net_demand']:+.2f}
- Fundamental Value: ${market_data['fundamental']:.2f}
- Recent Prices: {recent_prices}

Your Portfolio:
- Cash: ${cash:.2f}
- Position: {position:.2f} shares
- Portfolio Value: ${cash + position * market_data['price']:.2f}

Make your trading decision. Respond with ONLY valid JSON:
{{
    "action": "buy" | "sell" | "hold",
    "bid_price": <your limit price>,
    "quantity": <number of shares, positive for buy, negative for sell>,
    "reasoning": "<brief explanation>"
}}
"""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response to extract JSON."""
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            # Try to find JSON object
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            # Return default
            return {
                "action": "hold",
                "bid_price": 100.0,
                "quantity": 0,
                "reasoning": "Failed to parse LLM response",
            }

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        """Apply cash/position constraints to quantity."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:  # Buying
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:  # Selling
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state.get("llm_client")

        # Build prompt
        user_prompt = self._build_prompt(market_data)
        system_prompt = self.config.extras.get("system_prompt", self.SYSTEM_PROMPT)

        # Default decision
        decision = {
            "action": "hold",
            "bid_price": market_data["price"],
            "quantity": 0,
            "reasoning": "No LLM response",
        }

        # Call LLM via lmbase
        if llm_client:
            try:
                # Create InferInput for lmbase
                infer_input = InferInput(
                    system_msg=system_prompt,
                    user_msg=user_prompt,
                )
                # Run inference
                infer_output = llm_client.run(infer_input)
                # Parse response
                decision = self._parse_llm_response(infer_output.response)
            except Exception as e:
                decision["reasoning"] = f"LLM error: {str(e)[:80]}"

        # Extract and constrain values
        bid_price = float(decision.get("bid_price", market_data["price"]))
        quantity = float(decision.get("quantity", 0))
        quantity = self._apply_constraints(bid_price, quantity, market_data["price"])

        # Update position and cash
        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        print(
            f"[{self.identity:20s}] R{round_num} ({self.STRATEGY_NAME:12s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "reasoning": decision.get("reasoning", "")[:100],
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
# LLM Investor Types - Differentiated by System Prompts
# =============================================================================


class LLMMomentumInvestor(LLMInvestor):
    """
    LLM-powered Momentum Investor - Trend Following

    Personality: Follows price trends, buys when price rises, sells when falls.
    Effect: DESTABILIZING - amplifies trends
    """

    STRATEGY_NAME = "llm_momentum"
    SYSTEM_PROMPT = """You are a MOMENTUM INVESTOR following trend-following strategy.

CORE BELIEF: "The trend is your friend" - prices that rise will continue to rise.

YOUR TRADING RULES:
1. If price is RISING (positive return): BUY aggressively
2. If price is FALLING (negative return): SELL to cut losses
3. The stronger the trend, the larger your position

BEHAVIOR:
- You believe in price momentum and market trends
- You react QUICKLY to price movements
- You are NOT concerned with fundamental value
- You follow the crowd when trends are strong

RISK PROFILE: High - you buy high and sell low if trend reverses

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMContrarianInvestor(LLMInvestor):
    """
    LLM-powered Contrarian Investor - Value Investing

    Personality: Buys when others sell, sells when others buy.
    Effect: STABILIZING - dampens price swings
    """

    STRATEGY_NAME = "llm_contrarian"
    SYSTEM_PROMPT = """You are a CONTRARIAN/VALUE INVESTOR.

CORE BELIEF: "Be fearful when others are greedy, greedy when others are fearful."

YOUR TRADING RULES:
1. If price > fundamental value (100): SELL - market is overvalued
2. If price < fundamental value (100): BUY - market is undervalued
3. The larger the deviation from fundamental, the larger your position

BEHAVIOR:
- You believe prices always return to fundamental value
- You buy when everyone else is selling (market panic)
- You sell when everyone else is buying (market euphoria)
- You are PATIENT and wait for value opportunities

RISK PROFILE: Medium - may buy into falling markets too early

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMRiskAverseInvestor(LLMInvestor):
    """
    LLM-powered Risk-Averse Investor - Volatility Sensitive

    Personality: Reduces exposure when volatility is high.
    Effect: Can trigger early exits from bubbles
    """

    STRATEGY_NAME = "llm_risk_averse"
    SYSTEM_PROMPT = """You are a RISK-AVERSE INVESTOR focused on capital preservation.

CORE BELIEF: "Protect your capital - high volatility means high risk."

YOUR TRADING RULES:
1. If recent prices are VOLATILE (large swings): REDUCE position
2. If market is CALM (small price changes): May increase position
3. Always maintain a large cash buffer for safety

BEHAVIOR:
- You HATE losing money more than you like making money
- You watch price swings closely - erratic markets scare you
- You prefer small, steady gains over risky big wins
- You EXIT early when you sense trouble brewing

RISK PROFILE: Low - you sacrifice returns for safety

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMAggressiveInvestor(LLMInvestor):
    """
    LLM-powered Aggressive Investor - Leveraged Momentum

    Personality: Amplified momentum with acceleration trading.
    Effect: EXTREMELY DESTABILIZING - creates rapid bubbles
    """

    STRATEGY_NAME = "llm_aggressive"
    SYSTEM_PROMPT = """You are an AGGRESSIVE/LEVERAGED MOMENTUM INVESTOR.

CORE BELIEF: "Go big or go home - maximize gains in strong trends."

YOUR TRADING RULES:
1. If price is rising AND accelerating: BUY HEAVILY (large position)
2. If price is falling AND accelerating down: SELL EVERYTHING
3. Look for "price acceleration" - when the rate of change is increasing

BEHAVIOR:
- You use LEVERAGE mentally - take larger positions than others
- You look for ACCELERATION signals (price rising faster and faster)
- You are EXTREMELY reactive to market movements
- You aim for maximum profit, accepting maximum risk

RISK PROFILE: Very High - can cause flash crashes

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
Note: quantity can be up to 80 shares (larger than other investors)
"""


class LLMNoiseTrader(LLMInvestor):
    """
    LLM-powered Noise Trader - Random/Uninformed

    Personality: Makes somewhat random decisions, provides liquidity.
    Effect: Can accidentally trigger herd behavior
    """

    STRATEGY_NAME = "llm_noise"
    SYSTEM_PROMPT = """You are a NOISE TRADER - an uninformed retail investor.

CORE BELIEF: You trade based on gut feelings, rumors, and random impulses.

YOUR TRADING RULES:
1. You don't follow any strict strategy
2. You make decisions based on "feelings" about the market
3. Sometimes you buy randomly, sometimes you sell randomly
4. You tend to gradually reduce extreme positions (mean revert)

BEHAVIOR:
- You are NOT sophisticated - you don't analyze deeply
- You react to news and rumors (even if they're noise)
- You provide LIQUIDITY to the market
- Your trades are somewhat RANDOM but not completely

RISK PROFILE: Random - you're the "average retail investor"

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
Be somewhat random in your decisions - you're not a professional.
"""
