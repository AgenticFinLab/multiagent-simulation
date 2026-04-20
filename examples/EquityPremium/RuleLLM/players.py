"""EquityPremiumRuleLLM - Hybrid Rule+LLM EquityPremium Simulation

Design:
    - Market coordinator: identical rule-based price dynamics as EquityPremium
    - Investors: LLM-powered, but each agent's system prompt embeds the explicit
      quantitative rules (formulas, thresholds) from the rule-based counterpart,
      alongside a rich persona/profile description.

This hybrid lets LLM agents exercise natural language reasoning while remaining
grounded in the same financial principles as the rule-based simulation, enabling
meaningful comparison across three variants:
    EquityPremium        - pure rule-based
    EquityPremiumLLM     - pure LLM (persona only)
    EquityPremiumRuleLLM - hybrid (persona + explicit rules in prompt)

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "EquityPremiumRuleLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/EquityPremium/RuleLLM/run_equity_premium_rulellm.py \
       -c configs/EquityPremium/RuleLLM/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import logging
import os
import json
import random
import re
import sys
import importlib
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

# Add examples directory to path for shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("EquityPremiumRuleLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# =============================================================================
# Market - Rule-Based Coordinator (identical to EquityPremium.Market)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with liquidity-sensitive pricing.

    Price model (rule-based, unchanged from EquityPremium):
        Price impact increases when liquidity is low (equity premium mechanism).
        P(t+1) = P(t) + price_impact * liquidity_factor * NetDemand
                 + mean_reversion * (F - P(t)) + epsilon

    Parameters from config extras:
        - fundamental_value, initial_price
        - base_price_impact, mean_reversion, noise_std
        - low_liquidity_threshold, high_impact_multiplier, base_liquidity
        - custom_state_hot_limit, record_path
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["liquidity"] = 100.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["liquidity_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "liquidity"),
                entry_limit=custom_state_hot_limit,
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
                        "provides_liquidity": order.get("provides_liquidity", False),
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        base_liquidity = extras["base_liquidity"]
        low_liquidity_threshold = extras["low_liquidity_threshold"]
        high_impact_multiplier = extras["high_impact_multiplier"]
        base_price_impact = extras["base_price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        liquidity_provision = sum(
            abs(o["quantity"]) for o in orders if o["provides_liquidity"]
        )
        total_liquidity = base_liquidity + liquidity_provision

        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        if total_liquidity < low_liquidity_threshold:
            liquidity_factor = high_impact_multiplier
        else:
            liquidity_factor = (
                1.0 + (low_liquidity_threshold / total_liquidity - 1.0) * 0.5
            )

        price_impact = base_price_impact * net_demand * liquidity_factor
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = total_liquidity
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["liquidity_history"].append(total_liquidity)

        logger.debug(f"\n{'='*70}")
        logger.debug(f"[Market] Round {round_num}")
        logger.debug(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        logger.debug(
            f"  Liquidity: {total_liquidity:.1f}, Impact Factor: {liquidity_factor:.2f}"
        )
        logger.debug(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "liquidity": total_liquidity,
            "round": round_num,
            "fundamental": fundamental_value,
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
# Base RuleLLM Investor
# =============================================================================


class RuleLLMInvestor(GeneralPlayer):
    """
    Base class for hybrid Rule+LLM equity premium investors.

    Each subclass uses a system prompt that encodes BOTH:
    - Persona description (who the agent is, behavioral traits)
    - Quantitative decision rules in text form (the exact formula from rule-based)

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path
        - llm: sys_message, user_message, lm_name, generation_config
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

            load_dotenv()
            llm_config = extras["llm"]
            lm_name = llm_config["lm_name"]
            generation_config = llm_config["generation_config"]

            self.state.custom_state["lm_name"] = lm_name
            self.state.custom_state["generation_config"] = generation_config

            llm_client = LangChainAPIInference(
                lm_name=lm_name,
                generation_config=generation_config,
            )
            self.state.custom_state["llm_client"] = llm_client

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
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
        """Build user prompt with current market state."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        price_history = self.state.custom_state["price_history"]
        round_num = self.state.custom_state["round"]

        recent_prices = (
            list(price_history)[-5:] if len(price_history) >= 5 else list(price_history)
        )

        llm_config = self.config.extras["llm"]
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
                round=round_num,
                price=market_data["price"],
                prev_price=market_data["prev_price"],
                return_pct=market_data["return_pct"],
                liquidity=market_data["liquidity"],
                fundamental=market_data["fundamental"],
                volume=market_data["volume"],
                net_demand=market_data["net_demand"],
                recent_prices=recent_prices,
                cash=cash,
                position=position,
                portfolio_value=cash + position * market_data["price"],
            )

        # Fallback inline template
        return f"""
Round: {round_num}
Current Price: ${market_data['price']:.2f} | Prev: ${market_data['prev_price']:.2f} | Return: {market_data['return_pct']:+.2f}%
Liquidity: {market_data['liquidity']:.1f} | Fundamental: ${market_data['fundamental']:.2f}
Volume: {market_data['volume']:.2f} | Net Demand: {market_data['net_demand']:+.2f}
Recent Prices: {recent_prices}
Portfolio → Cash: ${cash:.2f} | Position: {position:.2f} | Value: ${cash + position * market_data['price']:.2f}

Respond with ONLY valid JSON:
{{"action": "buy"|"sell"|"hold", "bid_price": <float>, "quantity": <float, +buy/-sell>, "reasoning": "<brief>"}}
"""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with analysis and decision sections.

        Delegates to shared utility in examples/llm_utils.py
        """
        return parse_llm_response_with_thinking(response_text)

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        """Enforce cash/position limits."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position
            quantity = max(-max_sellable, quantity)

        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        strategy_name = self.__class__.__name__

        user_prompt = self._build_prompt(market_data)

        llm_config = self.config.extras["llm"]
        system_prompt = load_prompt(llm_config["sys_message"])

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.outputs[0].response)
                break
            except ValueError as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        f"[{self.identity}] LLM parse failed (attempt {attempt+1}), retrying..."
                    )

        # If LLM failed after all retries, skip trading this round (hold)
        if decision is None:
            logger.warning(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}. "
                f"Skipping trade this round."
            )
            order = {
                "bid_price": market_data["price"],
                "quantity": 0.0,
                "strategy": strategy_name,
                "investor": self.identity,
                "reasoning": f"LLM parse failed: held position",
                "analysis": "",
                "provides_liquidity": False,
            }
            return {
                **order,
                "outbound_messages": [
                    {"payload": order, "content_type": "investor_bid"}
                ],
            }

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        quantity = self._apply_constraints(bid_price, quantity, market_data["price"])

        # Execute trade and update portfolio
        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        logger.debug(
            f"[{self.identity:25s}] R{round_num} ({strategy_name:25s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:120],
            "analysis": decision["analysis"],
            "provides_liquidity": decision.get("provides_liquidity", False),
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
# Concrete Hybrid Investor Types
# =============================================================================


class RuleLLMMyopicLossAverse(RuleLLMInvestor):
    """Hybrid: MyopicLossAverseInvestor rules + LLM reasoning."""

    pass


class RuleLLMLongTermInvestor(RuleLLMInvestor):
    """Hybrid: LongHorizonInvestor rules + LLM reasoning."""

    pass


class RuleLLMInstitutionalInvestor(RuleLLMInvestor):
    """Hybrid: RiskNeutralInvestor rules + LLM reasoning."""

    pass


class RuleLLMRiskAverseSaver(RuleLLMInvestor):
    """Hybrid: ConservativeInvestor rules + LLM reasoning."""

    pass


class RuleLLMRationalOptimizer(RuleLLMInvestor):
    """Hybrid: NoiseTrader rules + LLM reasoning."""

    pass
