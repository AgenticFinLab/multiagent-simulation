"""HerdEffectLLM - LLM-based Investors for Emergent Herding Simulation

This module implements LLM-powered investors that simulate different trading
personalities through prompts. Unlike the rule-based HerdEffect, each investor
here uses an LLM to make decisions based on their defined financial characteristics.

Architecture:
    - Market: Rule-based (same as HerdEffect) - collects orders, clears market
    - LLMInvestor: Base class handling LLM interaction via lmbase
    - 5 Investor Types: Momentum, Contrarian, RiskAverse, Aggressive, Noise

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "HerdEffectLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/HerdEffect/LLM/run_herd_llm.py \
       -c configs/HerdEffect/LLM/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import logging
import os
import json
import random
import re
import importlib
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

# Shared utility for parsing LLM responses with analysis/decision format
from masim.utils.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("HerdEffectLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """
    Central market with order-based clearing mechanism.

    Parameters from config extras:
        - initial_price, fundamental_value, supply_elasticity
        - mean_reversion, noise_std, custom_state_hot_limit, record_path
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
            initial_price = extras["initial_price"]

            self.state.custom_state["price"] = initial_price
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
                initial_values=[initial_price],
            )
            self.state.custom_state["volume_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "volume"),
                entry_limit=custom_state_hot_limit,
                initial_values=[0],
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
        orders = self.state.custom_state["orders"]

        fundamental_value = extras["fundamental_value"]
        supply_elasticity = extras["supply_elasticity"]
        mean_reversion_rate = extras["mean_reversion"]
        noise_std = extras["noise_std"]

        # Order-based clearing
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty

        # Price dynamics
        price_impact = supply_elasticity * net_demand
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price
        total_volume = total_buy_qty + total_sell_qty

        # Update state
        prev_price = self.state.custom_state["price"]
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)

        # Log
        logger.debug(f"\n{'='*60}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"[Market] Round {round_num}"
        )  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"  Price: {prev_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        logger.debug(
            f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}"
        )  # pylint: disable=logging-fstring-interpolation
        if orders:
            logger.debug(
                f"  LLM Orders ({len(orders)}):"
            )  # pylint: disable=logging-fstring-interpolation
            for o in orders:
                logger.debug(
                    f"    {o['investor']:20s} [{o['strategy']:12s}]: "
                    f"P={o['price']:7.2f}, Q={o['quantity']:+7.2f}"
                )
                if o["reasoning"]:
                    logger.debug(
                        f"      → {o['reasoning'][:80]}..."
                    )  # pylint: disable=logging-fstring-interpolation

        market_data = {
            "price": new_price,
            "prev_price": prev_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
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


class LLMInvestor(GeneralPlayer):
    """
    Base class for LLM-powered investors using lmbase.

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
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
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
                volume=market_data["volume"],
                net_demand=market_data["net_demand"],
                fundamental=market_data["fundamental"],
                recent_prices=recent_prices,
                cash=cash,
                position=position,
                portfolio_value=cash + position * market_data["price"],
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

Respond with ONLY valid JSON:
{{"action": "buy" | "sell" | "hold", "bid_price": <your price>, "quantity": <shares>, "reasoning": "<brief>"}}
"""

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with thinking and decision sections.

        Delegates to shared utility in masim.utils.llm_utils.py
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
            infer_output = llm_client.run([infer_input]).outputs[0]
            try:
                decision = self._parse_llm_response(infer_output.response)
                break
            except Exception as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug(
                        f"[{self.identity}] LLM parse failed, retrying..."
                    )  # pylint: disable=logging-fstring-interpolation

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after {max_retries} retries: {last_error}"
            )

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        # Guard: LLMs sometimes output bid_price=0 for hold actions.
        # Use the current market price so recorded bids stay meaningful.
        if bid_price <= 0:
            bid_price = market_data["price"]
        quantity = self._apply_constraints(bid_price, quantity, market_data["price"])

        if quantity > 0:
            cost = quantity * bid_price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            proceeds = abs(quantity) * bid_price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] += quantity

        logger.debug(
            f"[{self.identity:20s}] R{round_num} ({strategy_name:12s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
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


class LLMMomentumInvestor(LLMInvestor):
    """LLM-powered MomentumInvestor: trend following strategy. Theory: simulation-bases.md §4.1."""

    pass


class LLMContrarianInvestor(LLMInvestor):
    """LLM-powered ContrarianInvestor: value investing against the crowd. Theory: simulation-bases.md §4.2."""

    pass


class LLMRiskAverseInvestor(LLMInvestor):
    """LLM-powered RiskAverseInvestor: volatility-sensitive mean-variance strategy. Theory: simulation-bases.md §4.3."""

    pass


class LLMAggressiveInvestor(LLMInvestor):
    """LLM-powered AggressiveInvestor: leveraged momentum with acceleration bonus. Theory: simulation-bases.md §4.5."""

    pass


class LLMNoiseTrader(LLMInvestor):
    """LLM-powered NoiseTrader: random uninformed trading. Theory: simulation-bases.md §4.4."""

    pass
