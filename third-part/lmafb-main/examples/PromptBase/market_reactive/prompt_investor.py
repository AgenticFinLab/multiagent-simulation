"""
LLMMarketReactiveInvestor: LLM-Driven Technical Signal Investment Strategy

Extends MarketReactiveInvestor by delegating signal interpretation and allocation
decisions to a Large Language Model.

This implementation:
1. Inherits all signal extraction logic from MarketReactiveInvestor
2. Extracts market microstructure signals (momentum, volume, volatility, spread, demand)
3. Sends signals to LLM for interpretation and decision-making
4. LLM applies market microstructure theory and technical analysis
5. Returns allocation based on LLM's signal interpretation

Academic Foundation:
- Inherits theoretical framework from MarketReactiveInvestor
- Uses LLM as a flexible signal interpreter
- Maintains market microstructure principles (order flow, liquidity, momentum)
"""

import os
import json
import asyncio
from typing import List
from datetime import datetime
from dotenv import load_dotenv

from llmgt.utils.llm_init import init_llm_client
from llmgt.communication.base import M2IMessage
from llmgt.investor import base
from algorithmic_investor import MarketReactiveInvestor


class LLMMarketReactiveInvestor(MarketReactiveInvestor):
    """
    Market-Reactive Investor with LLM-powered signal interpretation.

    Extends MarketReactiveInvestor by using LLM to:
    1. Interpret market microstructure signals
    2. Apply technical analysis principles
    3. Combine multiple signals intelligently
    4. Generate allocation decisions based on signal patterns

    The LLM acts as a technical analyst, evaluating market signals
    and determining optimal allocation based on order flow dynamics.
    """

    def __init__(self, config, market_ids):
        """
        Initialize LLMMarketReactiveInvestor with signal extraction and LLM interface.
        """
        super().__init__(config, market_ids)

        # Initialize LLM Client
        self.llm_api_config = config.extras["llm_api"]

        # Load API key from environment variables
        load_dotenv()
        self.llm_api_config["api_key"] = os.getenv("API_KEY")
        
        self.client, self.model_name = init_llm_client(
            self.llm_api_config
        )
        self.decision_prompt = config.extras["decision_prompt"]

    def __getstate__(self):
        """Prepare for serialization (Ray compatibility)."""
        state = self.__dict__.copy()
        del state['client']
        return state

    def __setstate__(self, state):
        """Restore from serialization (Ray compatibility)."""
        self.__dict__.update(state)
        self.client, self.model_name = init_llm_client(
            self.llm_api_config
        )

    async def decide(self, messages: List[M2IMessage]) -> base.InvestorDecision:
        """
        Core decision routine using LLM for signal interpretation and allocation.

        Process Flow:
        1. Record timing information
        2. Extract market microstructure signals
        3. Format signals into prompt for LLM
        4. Call LLM API to interpret signals
        5. Parse LLM response
        6. Generate trading actions
        7. Update wealth
        8. Return decision with LLM reasoning
        """
        # 1. Record timing
        message_received_time = datetime.now().isoformat()
        await asyncio.sleep(self.computation_delay)
        decision_start_time = datetime.now().isoformat()

        # 2. Extract market signals (using parent class method)
        msg = messages[-1]
        market_id = msg.market_id
        decision_content = msg.decision_content
        signals = self._extract_signals(decision_content)
        price = (decision_content.get("clearing", {}).get("price")
                 or decision_content.get("price")
                 or ((decision_content.get("ask") + decision_content.get("bid")) / 2
                     if decision_content.get("ask") is not None and decision_content.get("bid") is not None else 0.0))

        # 3. Calculate current portfolio state
        portfolio_value = self.wealth
        current_shares = self.current_positions.get(market_id, {}).get("shares", 0.0)
        current_value = current_shares * price
        current_allocation = current_value / portfolio_value if portfolio_value > 0 else 0.0

        # 4. Format market signals into prompt
        market_signals_block = f"""
        CURRENT MARKET SIGNALS:
        1. Momentum (Price Trend): {signals['momentum']:+.4f} ({signals['momentum'] * 100:+.2f}%)
        2. Volume Change: {signals['volume_change']:+.4f} ({signals['volume_change'] * 100:+.2f}%)
        3. Volatility (Risk): {signals['volatility']:.4f} ({signals['volatility'] * 100:.2f}%)
        4. Bid-Ask Spread (Liquidity): {signals['spread']:.4f}
        5. Excess Demand (Order Flow): {(signals.get('excess_demand') or 0.0):+.2f}

        SIGNAL INTERPRETATION GUIDE:
        - Momentum: {'Strong uptrend' if signals['momentum'] > 0.02 else 'Strong downtrend' if signals['momentum'] < -0.02 else 'Weak/neutral trend'}
        - Volume: {'Increasing conviction' if signals['volume_change'] > 0.3 else 'Decreasing conviction' if signals['volume_change'] < -0.3 else 'Stable activity'}
        - Volatility: {'High risk environment' if signals['volatility'] > 0.2 else 'Low risk environment' if signals['volatility'] < 0.1 else 'Moderate risk'}
        - Spread: {'Wide (poor liquidity)' if signals['spread'] > 0.05 else 'Narrow (good liquidity)' if signals['spread'] < 0.01 else 'Moderate liquidity'}
        - Demand: {'Strong buy pressure' if signals['excess_demand'] > 1000 else 'Strong sell pressure' if signals['excess_demand'] < -1000 else 'Balanced'}

        CURRENT PORTFOLIO:
        - Wealth: ${self.wealth:.2f}
        - Current Allocation: {current_allocation:.2%}
        - Current Price: ${price:.2f}
        - Current Shares: {current_shares:.2f}

        CONSTRAINTS:
        - Min Allocation: {self.min_allocation:.2%}
        - Max Allocation: {self.max_allocation:.2%}
        - Transaction Cost Rate: {self.transaction_cost_rate:.2%}
        """

        # 5. Format market information
        market_info = f"- {market_id}: current price ${price:.2f}"

        # 6. Construct complete LLM prompt
        llm_input = (
                self.decision_prompt
                + "\n---\nCurrent market data:\n"
                + market_info
                + "\n---\n"
                + market_signals_block
                + "\nPlease analyze these market signals and determine your optimal allocation."
        )

        # 7. Call the LLM
        llm_messages = [
            {
                "role": "system",
                "content": (
                    "You are a market microstructure expert and technical analyst. "
                    "You MUST respond with ONLY a valid JSON object. "
                    "No markdown, no code fences, no explanatory text."
                )
            },
            {"role": "user", "content": llm_input}
        ]

        llm_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=llm_messages,
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=800
        )

        response_content = llm_response.choices[0].message.content.strip()

        # 8. Parse LLM response
        parsed_response = json.loads(response_content)
        decision_summary = parsed_response["decision_summary"]
        target_allocation = decision_summary["target_allocation"]
        trading_action_type = decision_summary["action"]
        llm_decision_reasoning = parsed_response["reasoning"]

        # 9. Generate trading actions
        trading_actions = {}

        # Calculate target position
        target_value = portfolio_value * target_allocation
        target_shares = target_value / (price if price else 1e-8)
        shares_to_trade = target_shares - current_shares

        # Calculate transaction cost
        trade_value = abs(shares_to_trade * price)
        transaction_cost = trade_value * self.transaction_cost_rate

        # Update position
        self.current_positions[market_id] = {"shares": target_shares, "avg_price": price}

        # Create trading action
        trading_actions[market_id] = {
            "order_type": "market",
            "shares": float(shares_to_trade),
            "price": float(price),
            "target_allocation": float(target_allocation),
        }

        # 10. Update wealth
        self.wealth -= transaction_cost

        # 11. Build reasoning
        complete_reasoning = (
            f"📈 LLM-Driven Market-Reactive Decision\n"
            f"LLM Model: {self.model_name}\n"
            f"Market Signals:\n"
            f"  - Momentum: {signals['momentum']:+.2%}\n"
            f"  - Volume Change: {signals['volume_change']:+.2%}\n"
            f"  - Volatility: {signals['volatility']:.2%}\n"
            f"  - Spread: {signals['spread']:.4f}\n"
            f"  - Excess Demand: {signals['excess_demand']:+.2f}\n"
            f"Target Allocation: {target_allocation:.2%}\n"
            f"Current Allocation: {current_allocation:.2%}\n"
            f"Action: {trading_action_type.upper()}\n"
            f"\n--- LLM Signal Analysis ---\n"
            f"{llm_decision_reasoning}"
        )

        # 12. Calculate confidence
        confidence_score = 1.0

        # 13. Check violations
        violations = {}
        if target_allocation > self.max_allocation:
            violations["max_allocation"] = f"Target {target_allocation:.2%} > max {self.max_allocation:.2%}"
        if target_allocation < self.min_allocation:
            violations["min_allocation"] = f"Target {target_allocation:.2%} < min {self.min_allocation:.2%}"

        self._round_index += 1

        # 14. Package decision
        investment_decision = base.InvestorDecision(
            action=trading_actions,
            reason=complete_reasoning,
            confidence=confidence_score,
            violations=violations,
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=decision_start_time,
            additions={
                "target_allocation": float(target_allocation),
                "current_allocation": float(current_allocation),
                "momentum": float(signals['momentum']),
                "volume_change": float(signals['volume_change']),
                "volatility": float(signals['volatility']),
                "spread": float(signals['spread']),
                "excess_demand": float(signals['excess_demand']),
                "llm_model_used": str(self.model_name),
                "trading_action": str(trading_action_type),
                "transaction_cost": float(transaction_cost),
            }
        )

        investment_decision.ensure_valid()
        return investment_decision
