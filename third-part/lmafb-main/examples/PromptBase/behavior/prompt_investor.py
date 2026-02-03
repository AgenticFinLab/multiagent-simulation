"""
LLMInvestorTypeI: Large Language Model-Driven Investment Decision System

An investor that leverages large language models (LLMs) to make investment decisions.
Combines the structural foundation of classical finance (RationalInvestor) with the
flexibility and reasoning capabilities of LLMs.

This implementation uses OpenAI-compatible LLM APIs to generate allocation decisions
based on market data and investor parameters formatted into natural language prompts.


Academic References

Classical Finance Theory (from RationalInvestor):
[1] Markowitz, H. M. (1952). "Portfolio Selection." The Journal of Finance.
[2] Arrow, K. J. (1965). "Aspects of the Theory of Risk-Bearing."
[3] Kelly, J. L. (1956). "A New Interpretation of Information Rate."

Large Language Model Applications in Finance:
[4] Huang, A., Wang, H., & Yang, Y. (2023).
    "GPT goes to Wall Street: Roles, Promises, and Challenges for Generative AI
     in Financial Decision-Making."
    arXiv preprint arXiv:2307.10485.

    Evaluates LLMs' ability to process financial information and make decisions.
    Shows LLMs can understand complex market contexts but may lack risk awareness.

[5] Chan, W. H., & Yahya, M. F. (2024).
    "Large Language Models for Financial Time Series Analysis and Market Prediction."
    arXiv preprint.

    Demonstrates LLMs can identify patterns in financial text and market signals.
    Highlights importance of constraint enforcement and guardrails.

[6] Cao, S., Lin, W., & Wang, X. (2023).
    "Can ChatGPT Predict Stock Price Movements? Return Predictability and Large
     Language Models."

    Studies LLM-based prediction in finance. Shows LLMs incorporate domain knowledge
    but need structured constraints for realistic portfolio allocation.


This investor combines:

1. STRUCTURAL FOUNDATION (RationalInvestor):
   - Classical portfolio theory constraints
   - Risk management guardrails
   - Consistent state management
   - Transaction cost handling

2. DECISION-MAKING LAYER (LLM):
   - Natural language processing of market data
   - Contextual reasoning about current conditions
   - Narrative explanation of decisions
   - Flexibility to adapt to novel situations

3. INTEGRATION:
   - Prompt engineering to inject market data + parameters
   - JSON response parsing for structured output
   - State management inherited from RationalInvestor
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
from algorithmic_investor import BehavioralInvestor


class LLMBehavioralInvestor(BehavioralInvestor):
    """
    Large Language Model-Driven Rational Investor (Type I with LLM Decision Engine)

    This investor extends RationalInvestor by delegating the allocation decision
    to a Large Language Model. The LLM receives market data and investor parameters,
    then generates JSON-structured investment decisions.
    """

    def __init__(self, config, market_ids):
        """
        Initialize LLMInvestor with classical finance parameters and LLM interface.
        """
        super().__init__(config, market_ids)
        # Initialize LLM Client
        # Initialize OpenAI-compatible LLM client
        self.llm_api_config = config.extras["llm_api"]

        # Load API key from environment variables
        load_dotenv()
        self.llm_api_config["api_key"] = os.getenv("API_KEY")
        
        self.client, self.model_name = init_llm_client(
            self.llm_api_config
        )
        self.decision_prompt = config.extras["decision_prompt"]

    def __getstate__(self):
        """
        Prepare object for serialization (called by Ray before pickling).

        Called when Ray needs to serialize this object
        1. Copy all object attributes
        2. Delete llm_client (contains thread lock, cannot be serialized)
        3. Keep llm_api_config for reinitialization
        4. Return a serializable dictionary
        """
        # Get all properties of an object
        state = self.__dict__.copy()

        # Delete un-serialize LLM clients
        # Ray will reinitialize it when __setstate__() is called in the remote worker process.
        del state['client']

        return state

    def __setstate__(self, state):
        """
        Restore object from serialization (called by Ray after unpickling).

        When Ray deserializes an object in a remote worker process, the following strategies are invoked:
        1. Restore all saved attributes.
        2. Reinitialize llm_client using the saved llm_api_config.
        3. The object is fully available in the remote process.
        """
        # Restore object properties
        self.__dict__.update(state)

        # Reinitialize the LLM client
        # This is performed in the remote worker process, allowing secure use of API keys.
        self.client, self.model_name = init_llm_client(
            self.llm_api_config
        )

    async def decide(self, messages: List[M2IMessage]) -> base.InvestorDecision:
        """
        Core decision routine using LLM for behavioral allocation determination.
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

        # Track returns
        if len(self.price_history) >= 2:
            previous_price = self.price_history[-2]
            new_price = self.price_history[-1]
            realized_return = (new_price - previous_price) / previous_price
            self.return_history.append(realized_return)

        # 3. Compute behavioral factors
        self._init_reference_level()
        self._update_reference_level()

        subjective_volatility = self._subjective_volatility()
        reference_gap = self.reference_level - self.wealth
        portfolio_value = self._compute_portfolio_value()
        current_allocation = self._current_allocation(current_market_prices, portfolio_value)
        reference_status = 'BEHIND' if reference_gap > 0 else 'AHEAD'

        # 4. Format behavioral parameters into prompt
        behavioral_param_block = f"""
        BEHAVIORAL PARAMETERS:
        - Loss aversion (λ): {self.loss_aversion}
        - Reference point: ${self.reference_level:.2f} ({self.reference_point_mode})
        - Current wealth: ${self.wealth:.2f}
        - Gap from reference (Δr): ${reference_gap:.2f} ({reference_status})
        - Subjective volatility (σ_tilde): {subjective_volatility:.2%}
        - Risk perception (κ): {self.risk_perception_kappa}
        - Probability weighting (γ): {self.probability_weight_gamma}

        CURRENT PORTFOLIO:
        - Current allocation: {current_allocation:.2%}
        - Portfolio value: ${portfolio_value:.2f}
        - Alpha (gain sensitivity): {self.alpha_gain}
        - Beta (loss sensitivity): {self.beta_loss}

        CONSTRAINTS:
        - Min cash reserve: {self.min_cash_reserve:.2%}
        - Max position: {self.max_position_size:.2%}
        - Transaction cost: {self.transaction_cost_rate:.2%}
        - Rebalancing threshold: {self.balancing_threshold:.2%}

        BEHAVIORAL PRESSURES:
        - Catch-up intensity (if behind): {self.catchup_intensity}
        - Protect intensity (if ahead): {self.protect_intensity}
        """

        # 5. Format market information
        market_info = "\n".join(
            [f"- {mid}: current price ${p:.2f}" for mid, p in current_market_prices.items()]
        )

        # 6. Construct complete LLM prompt
        llm_input = (
                self.decision_prompt
                + "\n---\nCurrent market data:\n"
                + market_info
                + "\n---\n"
                + behavioral_param_block
                + "\nPlease decide your next action (buy/sell/hold) and target allocation."
        )

        # 7. Call the LLM
        llm_messages = [
            {
                "role": "system",
                "content": (
                    "You are a behavioral finance expert applying Prospect Theory. "
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
            temperature=0,
            max_tokens=500
        )

        response_content = llm_response.choices[0].message.content.strip()

        # 8. Parse LLM response
        parsed_response = json.loads(response_content)
        decision_summary = parsed_response.get("decision_summary", {})
        target_allocation = decision_summary.get("target_allocation", 0.5)
        trading_action_type = decision_summary.get("action", "hold")
        llm_decision_reasoning = parsed_response.get("reasoning", "")

        # 9. Generate trading actions
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

        print(f"\n{'=' * 60}")
        print(f"[INVESTOR DEBUG] Before creating InvestorDecision:")
        print(f"[INVESTOR DEBUG] trading_actions type: {type(trading_actions)}")
        print(f"[INVESTOR DEBUG] trading_actions: {trading_actions}")
        if isinstance(trading_actions, dict):
            print(f"[INVESTOR DEBUG] trading_actions.keys(): {list(trading_actions.keys())}")
            for k, v in trading_actions.items():
                print(f"[INVESTOR DEBUG]   '{k}': {v}")
        print(f"{'=' * 60}\n")

        # 11. Update wealth
        self.wealth -= total_transaction_cost
        self.total_transaction_costs += total_transaction_cost

        # 12. Build reasoning
        behavioral_status = 'Behind - Catch Up' if reference_gap > 0 else 'Ahead - Protect'

        complete_reasoning = (
            f"🧠 LLM-Driven Behavioral Investment Decision\n"
            f"LLM Model: {self.model_name}\n"
            f"Reference Point: ${self.reference_level:.2f} ({self.reference_point_mode})\n"
            f"Gap from Reference: ${reference_gap:.2f} ({behavioral_status})\n"
            f"Subjective Risk (σ_tilde): {subjective_volatility:.2%} (κ={self.risk_perception_kappa})\n"
            f"Loss Aversion (λ): {self.loss_aversion}\n"
            f"Target Allocation: {target_allocation:.2%}\n"
            f"Current Allocation: {current_allocation:.2%}\n"
            f"Action: {trading_action_type.upper()}\n"
            f"\n--- LLM Behavioral Reasoning ---\n"
            f"{llm_decision_reasoning}"
        )

        # 13. Calculate confidence
        relative_gap = abs(reference_gap) / self.wealth if self.wealth > 0 else 0
        confidence_score = min(max(0.7, 1.0 - 2.0 * relative_gap), 1.0)

        # 14. Check violations
        violations = {}
        if target_allocation > self.max_position_size:
            violations["max_position"] = f"Target {target_allocation:.2%} > max {self.max_position_size:.2%}"
        if (1 - target_allocation) < self.min_cash_reserve:
            violations["min_cash"] = f"Cash {(1 - target_allocation):.2%} < min {self.min_cash_reserve:.2%}"

        self._round_index += 1

        # 15. Package decision
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
                "reference_level": float(self.reference_level),
                "delta_reference": float(reference_gap),
                "subjective_volatility": float(subjective_volatility),
                "risk_perception_kappa": float(self.risk_perception_kappa),
                "loss_aversion": float(self.loss_aversion),
                "llm_model_used": str(self.model_name),
                "trading_action": str(trading_action_type),
                "transaction_costs_total": float(self.total_transaction_costs),
            }
        )

        investment_decision.ensure_valid()
        return investment_decision