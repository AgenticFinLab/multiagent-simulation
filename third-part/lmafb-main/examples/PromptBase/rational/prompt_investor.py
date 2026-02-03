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
from datetime import datetime
from dotenv import load_dotenv

from llmgt.utils.llm_init import init_llm_client
from llmgt.communication.base import M2IMessage
from llmgt.investor import base
from algorithmic_investor import RationalInvestor


class LLMRationalInvestor(RationalInvestor):
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

    async def decide(self, messages: list[M2IMessage]) -> base.InvestorDecision:
        """
        Core decision routine using LLM for allocation determination.

        Process Flow:
        1. Record timing information
        2. Extract current market prices from messages
        3. Format market data into text representation
        4. Format investor parameters into text representation
        5. Construct complete prompt for LLM
        6. Call LLM API to generate decision
        7. Parse JSON response into structured decision
        8. Generate trading actions
        9. Return decision with LLM reasoning
        """
        message_received_time = datetime.now().isoformat()
        await asyncio.sleep(self.computation_delay)
        decision_start_time = datetime.now().isoformat()

        # 1.Extract current market info
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

        # 2.Format injected parameters into prompt
        param_block = f"""
        Parameters:
        - Risk aversion coefficient (A): {self.risk_aversion}
        - Risk-free rate (r): {self.risk_free_rate}
        - Expected return estimate (μ̂): {self.expected_return}
        - Volatility estimate (σ̂): {self.volatility}
        - Min cash reserve: {self.min_cash_reserve}
        - Max position size: {self.max_position_size}
        - Transaction cost rate: {self.transaction_cost_rate}
        - Decision method: {self.decision_method}
        """

        # 3.Format Market Information for Prompt
        market_info = "\n".join(
            [f"- {mid}: current price ${p:.2f}" for mid, p in current_market_prices.items()]
        )

        # 4.Construct Complete LLM Prompt
        llm_input = (
            self.decision_prompt
            + "\n---\nCurrent market data:\n"
            + market_info
            + "\n---\n"
            + param_block
            + "\nPlease decide your next action (buy/sell/hold) and target allocation."
        )

        # 5.Call the LLM
        messages = [
            {
                "role": "system",
                "content": "You are a quantitative trading assistant. You MUST respond with valid JSON only. No "
                           "markdown, no explanations outside JSON, no code fences."
            },
            {"role": "user", "content": llm_input}
        ]

        resp = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=500
        )

        content = resp.choices[0].message.content.strip()

        # 6.Parse LLM Response
        parsed = json.loads(content)
        # Extract structured decision from JSON
        decision_summary = parsed.get("decision_summary", {})
        target_risky_allocation = decision_summary.get("target_allocation", 0.5)
        trading_action_type = decision_summary.get("action", "hold")
        decision_reasoning = parsed.get("reasoning", "")

        # 7.Generate Trading Actions
        market_trading_actions = {}
        for market_id, price in current_market_prices.items():
            # Get current position value
            current_stock_value = sum(
                pos["shares"] * price for mid, pos in self.current_positions.items() if mid == market_id
            )
            portfolio_value = self.wealth
            # Current allocation ratio
            current_allocation = current_stock_value / portfolio_value if portfolio_value > 0 else 0.0

            # Target position value in dollars
            if trading_action_type.lower() == "buy":
                shares_to_trade = (target_risky_allocation - current_allocation) * portfolio_value / price
            elif trading_action_type.lower() == "sell":
                shares_to_trade = (target_risky_allocation - current_allocation) * portfolio_value / price
            else:
                shares_to_trade = 0.0

            # Note: "buy" and "sell" use same calculation
            # The sign of shares_to_trade determines direction
            market_trading_actions[market_id] = {
                "order_type": "market",
                "shares": float(shares_to_trade),
                "price": float(price),
                "target_allocation": float(target_risky_allocation),
            }

        # 8.Build Complete Reasoning Narrative
        # Combine market data and LLM reasoning for decision explanation
        complete_reasoning = (
            f"🤖 LLM-Driven Investment Decision (Type I Enhanced)\n"
            f"LLM Model: {self.model_name}\n"
            f"Target Allocation: {target_risky_allocation:.2%}\n"
            f"Action: {trading_action_type.upper()}\n"
            f"\n--- LLM Reasoning ---\n"
            f"{decision_reasoning}"
        )

        self._round_index += 1

        # 9.Package decision
        # Create decision object with all information
        investment_decision = base.InvestorDecision(
            action=market_trading_actions,
            reason=complete_reasoning,
            confidence=1.0,
            violations={},
            round_index=self._round_index,
            message_received_time=message_received_time,
            decision_start_time=decision_start_time,
            additions={
                "target_allocation": float(target_risky_allocation),
                "llm_model_used": str(self.model_name),
                "trading_action": str(trading_action_type),
            }
        )

        # Validate decision object
        investment_decision.ensure_valid()

        return investment_decision
