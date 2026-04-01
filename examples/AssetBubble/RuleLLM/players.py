"""AssetBubbleRuleLLM - Hybrid Rule+LLM Asset Bubble Simulation

Design:
    - Market coordinator: identical rule-based price dynamics as AssetBubble
    - Investors: LLM-powered, but each agent's system prompt embeds the explicit
      quantitative rules (formulas, thresholds) from the rule-based counterpart,
      alongside a rich persona/profile description.

This hybrid lets LLM agents exercise natural language reasoning while remaining
grounded in the same financial principles as the rule-based simulation, enabling
meaningful comparison across three variants:
    AssetBubble       - pure rule-based
    AssetBubbleLLM    - pure LLM (persona only)
    AssetBubbleRuleLLM - hybrid (persona + explicit rules in prompt)

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "AssetBubbleRuleLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/AssetBubble/RuleLLM/run_bubble_rulellm.py \
       -c configs/AssetBubble/RuleLLM/simulation.yml
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

logger = logging.getLogger("AssetBubbleRuleLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# =============================================================================
# Market - Rule-Based Coordinator (identical to AssetBubble.Market)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with bubble-prone price dynamics.

    Price model (rule-based, unchanged from AssetBubble):
        P(t+1) = P(t) + lambda x NetDemand + gamma x [F - P(t)] + epsilon
    where:
        lambda = price_impact  (high -> amplifies demand)
        gamma  = mean_reversion (low -> slow correction)
        F      = fundamental value (grows at fundamental_growth rate)

    Parameters from config extras:
        - fundamental_value, initial_price, price_impact, mean_reversion
        - fundamental_growth, noise_std, short_cost_rate, custom_state_hot_limit
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
            self.state.custom_state["fundamental"] = extras["fundamental_value"]

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["fundamental_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "fundamental"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=custom_state_hot_limit,
            )
            self.state.custom_state["bubble_metric_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "bubble_metric"),
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
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        current_fundamental = self.state.custom_state["fundamental"]
        orders = self.state.custom_state["orders"]

        # Update fundamental value (slow growth)
        fundamental_growth = extras["fundamental_growth"]
        new_fundamental = current_fundamental * (1 + fundamental_growth)

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics: bubble-prone model
        price_impact = extras["price_impact"] * net_demand
        mean_reversion = extras["mean_reversion"] * (new_fundamental - current_price)
        noise = random.gauss(0, extras["noise_std"])

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price
        return_pct = price_return * 100

        # Bubble metric: Price / Fundamental
        bubble_ratio = new_price / new_fundamental

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["fundamental_history"].append(new_fundamental)
        self.state.custom_state["volume_history"].append(total_volume)
        self.state.custom_state["bubble_metric_history"].append(bubble_ratio)

        # Log
        logger.debug(f"\n{'='*70}")
        logger.debug(f"[Market] Round {round_num}")
        logger.debug(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({return_pct:+.2f}%)"
        )
        logger.debug(
            f"  Fundamental: {new_fundamental:.2f}, Bubble Ratio: {bubble_ratio:.2f}x"
        )
        logger.debug(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            logger.debug(f"  RuleLLM Orders ({len(orders)}):")
            for o in orders:
                logger.debug(
                    f"    {o['investor']:25s} [{o['strategy']:20s}]: Q={o['quantity']:+8.2f}"
                )
                if o["reasoning"]:
                    logger.debug(f"      → {o['reasoning'][:80]}...")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": return_pct,
            "fundamental": new_fundamental,
            "bubble_ratio": bubble_ratio,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
            "short_cost_rate": extras["short_cost_rate"],
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
    Base class for hybrid Rule+LLM investors.

    Each subclass uses a system prompt that encodes BOTH:
    - Persona description (who the agent is, behavioral traits)
    - Quantitative decision rules in text form (the exact formula from rule-based)

    The agent uses LLM reasoning to interpret market data and apply those rules,
    potentially deviating slightly when qualitative context warrants.

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
            self.state.custom_state["short_position"] = 0.0

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
        """Build user prompt with current market state, including round number."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        short_pos = self.state.custom_state["short_position"]
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

        # Fallback inline template (round included)
        return f"""
Round: {round_num}
Current Price: ${market_data['price']:.2f} | Prev: ${market_data['prev_price']:.2f} | Return: {market_data['return_pct']:+.2f}%
Fundamental: ${market_data['fundamental']:.2f} | P/F Ratio: {market_data['bubble_ratio']:.2f}x
Volume: {market_data['volume']:.2f} | Net Demand: {market_data['net_demand']:+.2f}
Short Cost: {market_data['short_cost_rate']:.1%} | Recent Prices: {recent_prices}
Portfolio → Cash: ${cash:.2f} | Long: {position:.2f} | Short: {short_pos:.2f} | Value: ${cash + position * market_data['price']:.2f}

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
            # Allow limited short selling
            max_sellable = position + 50
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
                "cash": self.state.custom_state["cash"],
                "position": self.state.custom_state["position"],
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
            if abs(quantity) <= self.state.custom_state["position"]:
                self.state.custom_state["position"] += quantity
            else:
                sold_long = self.state.custom_state["position"]
                short_qty = abs(quantity) - sold_long
                self.state.custom_state["position"] = 0
                self.state.custom_state["short_position"] += short_qty

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
# Concrete Hybrid Investor Types
# =============================================================================


class RuleLLMMomentumSpeculator(RuleLLMInvestor):
    """Hybrid: Greater Fool Theory momentum rules + LLM narrative reasoning."""

    pass


class RuleLLMRationalArbitrageur(RuleLLMInvestor):
    """Hybrid: Limits to Arbitrage deviation formula + LLM analytical reasoning."""

    pass


class RuleLLMNoiseTrader(RuleLLMInvestor):
    """Hybrid: Noise Trader Risk sentiment formula + LLM crowd-following reasoning."""

    pass


class RuleLLMValueInvestor(RuleLLMInvestor):
    """Hybrid: Value investing frequency + deviation rules + LLM patient reasoning."""

    pass


class RuleLLMLeveragedBuyer(RuleLLMInvestor):
    """Hybrid: Leverage amplification + margin call rules + LLM risk-aware reasoning."""

    pass
