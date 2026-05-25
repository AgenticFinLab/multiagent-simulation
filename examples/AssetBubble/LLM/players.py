"""AssetBubbleLLM - LLM-based Multi-Agent Market Simulation

LLM investors with different trading personalities:
    - Aggressive Momentum Trader
    - Fundamental Analyst
    - Sentiment Trader
    - Value Investor
    - Leveraged Trader

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "AssetBubbleLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/AssetBubble/LLM/run_bubble_llm.py \
       -c configs/AssetBubble/LLM/simulation.yml
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
from masim.format.order import validate_order

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

# Add examples directory to path for shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("AssetBubbleLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """
    Central market coordinating price discovery.

    Parameters from config extras:
        - fundamental_value, initial_price, price_impact, mean_reversion
        - fundamental_growth, noise_std, short_cost_rate, custom_state_hot_limit, record_path
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
            self.state.custom_state["valuation_ratio_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "valuation_ratio"),
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

        price_impact = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_growth = extras["fundamental_growth"]
        noise_std = extras["noise_std"]
        short_cost_rate = extras["short_cost_rate"]

        # Update fundamental value (slow growth)
        new_fundamental = current_fundamental * (1 + fundamental_growth)

        # Aggregate orders
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact_effect = price_impact * net_demand
        mean_reversion = mean_reversion_rate * (new_fundamental - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(
            1.0, current_price + price_impact_effect + mean_reversion + noise
        )
        price_return = (new_price - current_price) / current_price

        # Price/Fundamental ratio
        valuation_ratio = new_price / new_fundamental

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["valuation_ratio_history"].append(valuation_ratio)

        # Log
        logger.debug(f"\n{'='*70}")
        logger.debug(f"[Market] Round {round_num}")
        logger.debug(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        logger.debug(
            f"  Fundamental: {new_fundamental:.2f}, P/F Ratio: {valuation_ratio:.2f}x"
        )
        logger.debug(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            logger.debug(f"  LLM Orders ({len(orders)}):")
            for o in orders:
                logger.debug(
                    f"    {o['investor']:20s} [{o['strategy']:15s}]: Q={o['quantity']:+8.2f}"
                )
                if o["reasoning"]:
                    logger.debug(f"      → {o['reasoning'][:80]}...")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "fundamental": new_fundamental,
            # Price-to-fundamental ratio
            "bubble_ratio": valuation_ratio,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
            "short_cost_rate": short_cost_rate,
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


class LLMInvestor(GeneralPlayer):
    """
    Base class for LLM-powered investors.

    Parameters from config extras:
        - initial_cash, initial_position, custom_state_hot_limit, record_path, llm config
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
        """Build user prompt with current market data."""
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
- Price/Fundamental Ratio: {market_data['bubble_ratio']:.2f}x
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
        """Parse LLM response with thinking and decision sections.

        Delegates to shared utility in examples/llm_utils.py
        """
        return parse_llm_response_with_thinking(response_text)

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            # Allow some short selling
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
            except Exception as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug(f"[{self.identity}] LLM parse failed, retrying...")

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after {max_retries} retries: {last_error}"
            )

        action = decision["action"]
        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        # Guard: LLMs sometimes output bid_price=0 for hold actions.
        # Use the current market price so recorded bids stay meaningful.
        if bid_price <= 0:
            bid_price = market_data["price"]
        quantity = self._apply_constraints(bid_price, quantity, market_data["price"])

        # Execute trade
        if action == "buy" and quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            proceeds = quantity * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] -= quantity

        logger.debug(
            f"[{self.identity:20s}] R{round_num} ({strategy_name:15s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision["analysis"],
            "cash": self.state.custom_state["cash"],
            "position": self.state.custom_state["position"],
        }


        validate_order(order)

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


class LLMGreaterFoolSpeculator(LLMInvestor):
    """LLM aggressive momentum trader. Theory: simulation-bases.md §4.1 — MomentumSpeculator."""

    pass


class LLMRationalArbitrageur(LLMInvestor):
    """LLM fundamental analyst. Theory: simulation-bases.md §4.2 — RationalArbitrageur."""

    pass


class LLMSentimentTrader(LLMInvestor):
    """LLM sentiment trader. Theory: simulation-bases.md §4.3 — NoiseTrader."""

    pass


class LLMValueInvestor(LLMInvestor):
    """LLM value investor. Theory: simulation-bases.md §4.4 — FundamentalInvestor."""

    pass


class LLMLeveragedSpeculator(LLMInvestor):
    """LLM leveraged speculator. Theory: simulation-bases.md §4.5 — LeveragedBuyer."""

    pass


class LLMConservativeHolder(LLMInvestor):
    """LLM conservative holder. Theory: simulation-bases.md §4.6 — ConservativeHolder."""

    pass
