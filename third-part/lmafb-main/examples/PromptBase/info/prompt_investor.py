"""
LLMMetaCognitiveInvestor: Meta-Cognitive Investment Agent with LLM Decision Engine

An investor that combines rational finance, behavioral awareness, and meta-cognitive
reflection by using an LLM to learn from past decisions and adapt strategy dynamically.

This implementation extends LearningInvestor by delegating the meta-cognitive reasoning
and belief updates to a Large Language Model.

Academic Foundation:
- Inherits learning framework from LearningInvestor
- Uses LLM as a meta-cognitive reflection engine
- Maintains Bayesian learning with LLM-guided belief updates
- Incorporates self-awareness of biases and performance patterns

Key Features:
1. Meta-cognitive reflection on past decisions
2. Adaptive learning from prediction errors
3. Bias recognition and correction
4. Confidence calibration based on accuracy
5. Strategic adjustment of exploration vs exploitation
"""

import os
import json
import asyncio
import numpy as np
from typing import List
from datetime import datetime
from dotenv import load_dotenv

from llmgt.utils.llm_init import init_llm_client
from llmgt.communication.base import M2IMessage
from llmgt.investor import base
from algorithmic_investor import LearningInvestor


class LLMMetaCognitiveInvestor(LearningInvestor):
    """
    Meta-Cognitive Investor with LLM-powered decision-making.

    Extends LearningInvestor by using LLM to:
    1. Reflect on past decision quality and prediction accuracy
    2. Recognize and correct cognitive biases
    3. Adaptively update beliefs about market parameters
    4. Generate meta-cognitively informed allocation decisions

    The LLM acts as a meta-cognitive layer, evaluating its own
    performance and learning patterns to improve future decisions.
    """

    def __init__(self, config, market_ids):
        """
        Initialize LLMMetaCognitiveInvestor with learning parameters and LLM interface.
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
        Core decision routine using LLM for meta-cognitive learning and allocation.

        Process Flow:
        1. Record timing information
        2. Extract current market prices
        3. Compute realized returns
        4. Compute recent performance metrics
        5. Calculate current portfolio allocation
        6. Format state into prompt for LLM
        7. Call LLM API to generate meta-cognitive decision
        8. Parse LLM response
        9. Generate trading actions
        10. Update wealth
        11. Return decision with meta-cognitive reasoning
        """
        # 1. Record timing
        message_received_time = datetime.now().isoformat()
        await asyncio.sleep(self.computation_delay)
        decision_start_time = datetime.now().isoformat()

        # 2. Extract current market prices
        current_market_prices = {}
        for msg in messages:
            market_id = msg.market_id
            decision_content = msg.decision_content
            if "current_price" in decision_content:
                price = float(decision_content["current_price"])
            else:
                price = float(decision_content["clearing"]["price"])
            current_market_prices[market_id] = price
            self.price_history.append(price)

        # 3. Compute realized return
        realized_return = None
        if len(self.price_history) >= 2:
            previous_price = self.price_history[-2]
            current_price = self.price_history[-1]
            realized_return = (current_price - previous_price) / previous_price
            self.return_history.append(realized_return)

        # 4. Compute recent performance metrics (inline)
        if len(self.return_history) < 2:
            avg_return = 0.0
            prediction_accuracy = 0.5
            confidence_trend = "stable"
            num_observations = 0
        else:
            recent_returns = list(self.return_history)[-10:]
            avg_return = float(np.mean(recent_returns))

            # Calculate prediction accuracy
            correct_predictions = sum(
                1 for r in recent_returns
                if (r > 0 and self.expected_return > self.risk_free_rate) or
                (r < 0 and self.expected_return < self.risk_free_rate)
            )
            prediction_accuracy = correct_predictions / len(recent_returns)

            # Confidence trend
            if self.confidence > 0.7:
                confidence_trend = "high and stable"
            elif self.confidence < 0.3:
                confidence_trend = "low and declining"
            else:
                confidence_trend = "moderate"

            num_observations = len(recent_returns)

        # 5. Calculate current portfolio allocation (inline)
        portfolio_value = self.wealth
        total_holdings_value = 0.0
        for market_id, position in self.current_positions.items():
            if market_id in current_market_prices:
                total_holdings_value += position["shares"] * current_market_prices[market_id]
        current_allocation = total_holdings_value / portfolio_value if portfolio_value > 0 else 0.0

        # 6. Format meta-cognitive parameters into prompt
        meta_cognitive_param_block = f"""
        CURRENT BELIEFS & LEARNING STATE:
        - Expected Return (E[R]): {self.expected_return:.3f}
        - Volatility (σ): {self.volatility:.3f}
        - Confidence (ψ): {self.confidence:.3f}
        - Learning Rate (α_μ): {self.learning_rate_mean}
        - Learning Rate (α_σ): {self.learning_rate_vol}
        - Memory Decay (β): {self.memory_decay}

        RECENT PERFORMANCE (META-COGNITIVE FEEDBACK):
        - Last Realized Return: {f"{realized_return:.3%}" if realized_return is not None else "N/A"}
        - Average Return (last 10): {avg_return:.3%}
        - Prediction Accuracy: {prediction_accuracy:.1%}
        - Confidence Trend: {confidence_trend}
        - Observations: {num_observations}

        RATIONAL PARAMETERS:
        - Risk Aversion (A): {self.risk_aversion}
        - Risk-Free Rate (r_f): {self.risk_free_rate:.2%}

        CURRENT PORTFOLIO:
        - Wealth: ${self.wealth:.2f}
        - Current Allocation: {current_allocation:.2%}
        - Portfolio Value: ${portfolio_value:.2f}

        CONSTRAINTS:
        - Min Cash Reserve: {self.min_cash_reserve:.2%}
        - Max Position: {self.max_position_size:.2%}
        - Transaction Cost: {self.transaction_cost_rate:.2%}
        - Balancing Threshold: {self.balancing_threshold:.2%}
        """

        # 7. Format market information
        market_info = "\n".join(
            [f"- {mid}: current price ${p:.2f}" for mid, p in current_market_prices.items()]
        )

        # 8. Construct complete LLM prompt
        llm_input = (
                self.decision_prompt
                + "\n---\nCurrent market data:\n"
                + market_info
                + "\n---\n"
                + meta_cognitive_param_block
                + "\nPlease reflect on your past performance, recognize any biases, "
                  "and decide your next action (buy/sell/hold) and target allocation."
        )

        # 9. Call the LLM
        llm_messages = [
            {
                "role": "system",
                "content": (
                    "You are a meta-cognitive investment agent. "
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

        # 10. Parse LLM response
        parsed_response = json.loads(response_content)
        decision_summary = parsed_response["decision_summary"]
        target_allocation = decision_summary["target_allocation"]
        trading_action_type = decision_summary["action"]
        llm_decision_reasoning = parsed_response["reasoning"]

        # 11. Generate trading actions
        trading_actions = {}
        total_transaction_cost = 0.0

        for market_id, current_price in current_market_prices.items():
            # Get current position value
            current_stock_value = sum(
                pos["shares"] * current_price
                for mid, pos in self.current_positions.items()
                if mid == market_id
            )
            portfolio_value = self.wealth

            # Current allocation ratio
            current_allocation = current_stock_value / portfolio_value if portfolio_value > 0 else 0.0

            # Determine if balancing needed
            should_balance = self._should_balance(current_allocation, target_allocation)

            # Calculate shares to trade based on action type
            if should_balance or self._round_index == 0:
                # Target position value in dollars
                if trading_action_type.lower() == "buy":
                    shares_to_trade = (target_allocation - current_allocation) * portfolio_value / current_price
                elif trading_action_type.lower() == "sell":
                    shares_to_trade = (target_allocation - current_allocation) * portfolio_value / current_price
                else:
                    shares_to_trade = 0.0

                # Calculate transaction cost
                trade_value = abs(shares_to_trade * current_price)
                transaction_cost = trade_value * self.transaction_cost_rate
                total_transaction_cost += transaction_cost

                # Update positions
                if market_id not in self.current_positions:
                    self.current_positions[market_id] = {"shares": 0.0, "avg_price": current_price}

                current_shares = self.current_positions[market_id]["shares"]
                new_shares = current_shares + shares_to_trade
                self.current_positions[market_id]["shares"] = new_shares

                # Update average cost basis (only on purchases)
                if shares_to_trade > 0:
                    old_value = current_shares * self.current_positions[market_id]["avg_price"]
                    new_value = shares_to_trade * current_price
                    if new_shares > 0:
                        self.current_positions[market_id]["avg_price"] = (old_value + new_value) / new_shares
            else:
                shares_to_trade = 0.0

            # Note: "buy" and "sell" use same calculation
            # The sign of shares_to_trade determines direction
            trading_actions[market_id] = {
                "order_type": "market",
                "shares": float(shares_to_trade),
                "price": float(current_price),
                "target_allocation": float(target_allocation),
            }

        # 12. Update wealth
        self.wealth -= total_transaction_cost
        self.total_transaction_costs += total_transaction_cost

        # 13. Build reasoning
        complete_reasoning = (
            f"🧠 LLM-Driven Meta-Cognitive Investment Decision\n"
            f"LLM Model: {self.model_name}\n"
            f"Expected Return: {self.expected_return:.3f}, Volatility: {self.volatility:.3f}\n"
            f"Confidence: {self.confidence:.3f} ({confidence_trend})\n"
            f"Prediction Accuracy: {prediction_accuracy:.1%}\n"
            f"Target Allocation: {target_allocation:.2%}\n"
            f"Current Allocation: {current_allocation:.2%}\n"
            f"Action: {trading_action_type.upper()}\n"
            f"\n--- LLM Meta-Cognitive Reasoning ---\n"
            f"{llm_decision_reasoning}"
        )

        # 14. Calculate confidence score
        confidence_score = float(self.confidence)

        # 15. Check violations
        violations = {}
        if target_allocation > self.max_position_size:
            violations["max_position"] = f"Target {target_allocation:.2%} > max {self.max_position_size:.2%}"
        if (1 - target_allocation) < self.min_cash_reserve:
            violations["min_cash"] = f"Cash {(1 - target_allocation):.2%} < min {self.min_cash_reserve:.2%}"

        self._round_index += 1

        # 16. Package decision
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
                "expected_return": float(self.expected_return),
                "volatility": float(self.volatility),
                "confidence": float(self.confidence),
                "prediction_accuracy": float(prediction_accuracy),
                "avg_recent_return": float(avg_return),
                "llm_model_used": str(self.model_name),
                "trading_action": str(trading_action_type),
                "transaction_costs_total": float(self.total_transaction_costs),
            }
        )

        investment_decision.ensure_valid()
        return investment_decision
