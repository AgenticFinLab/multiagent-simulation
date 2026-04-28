"""HerdEffectRuleLLM Players - Hybrid Rule + LLM Investors

Hybrid design:
    - Market: Rule-based coordinator (same as HerdEffect)
    - Investors: LLM-driven with embedded quantitative rules in system prompts
    - Each investor receives market data, reasons via LLM, outputs trade decision

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "HerdEffectRuleLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/HerdEffect/RuleLLM/run_herd_rulellm.py \
       -c configs/HerdEffect/RuleLLM/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import json
import logging
import os
import random
import importlib
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

logger = logging.getLogger("HerdEffectRuleLLM")

from examples.llm_utils import (
    parse_llm_response_with_thinking,
    build_messages,
    call_llm,
)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


# =============================================================================
# Market - Coordinator (Rule-based, same as HerdEffect)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with order-based clearing mechanism.

    All parameters configured via extras in players.yml:
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
            self.state.custom_state["price"] = extras["initial_price"]

            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
                initial_values=[extras["initial_price"]],
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
                        "cash": order.get("cash", 0),
                        "position": order.get("position", 0),
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Order-Based Clearing
        buy_orders = [o for o in orders if o["quantity"] > 0]
        sell_orders = [o for o in orders if o["quantity"] < 0]

        total_buy_qty = sum(o["quantity"] for o in buy_orders)
        total_sell_qty = abs(sum(o["quantity"] for o in sell_orders))
        net_demand = total_buy_qty - total_sell_qty

        # Price dynamics
        supply_elasticity = extras["supply_elasticity"]
        price_impact = supply_elasticity * net_demand

        fundamental_value = extras["fundamental_value"]
        mean_reversion_rate = extras["mean_reversion"]
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)

        noise_std = extras["noise_std"]
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price
        total_volume = total_buy_qty + total_sell_qty

        # Update state
        prev_price = self.state.custom_state["price"]
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["volume_history"].append(total_volume)

        logger.debug(f"\n{'='*60}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"[Market] Round {round_num}"
        )  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"  Price: {prev_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        logger.debug(
            f"  Net Demand: {net_demand:+.2f}"
        )  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"  Total Volume: {total_volume:.2f}"
        )  # pylint: disable=logging-fstring-interpolation
        if orders:
            logger.debug(
                f"  Orders ({len(orders)}):"
            )  # pylint: disable=logging-fstring-interpolation
            for o in orders:
                logger.debug(
                    f"    {o['investor']:20s} [{o['strategy']:12s}]: "
                    f"P={o['price']:7.2f}, Q={o['quantity']:+7.2f}"
                )

        market_data = {
            "price": new_price,
            "prev_price": prev_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "round": round_num,
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
# Base LLM Investor
# =============================================================================


class BaseLLMInvestor(GeneralPlayer):
    """
    Base class for LLM investors with cash/position tracking.

    Parameters from config extras:
        - initial_cash, initial_position
        - llm config (sys_message, user_message, lm_type, lm_name, generation_config)
    """

    def _get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration from extras."""
        return self.config.extras.get("llm", {})

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]

            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
            )

        # Get market data
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["market_data"] = market_data
                self.state.custom_state["price_history"].append(market_data["price"])

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        llm_config = self._get_llm_config()
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        market_data = self.state.custom_state.get("market_data")

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        prev_price = market_data["prev_price"]
        price_return = market_data["return"]
        volume = market_data["volume"]
        net_demand = market_data["net_demand"]

        # Get recent prices for calculations
        price_history = list(self.state.custom_state["price_history"].recent)
        recent_prices_str = (
            ", ".join(f"{p:.2f}" for p in price_history[-5:])
            if price_history
            else "N/A"
        )

        # Build prompt - resolve module paths to actual prompt content
        sys_msg_path = llm_config.get("sys_message", "")
        user_msg_path = llm_config.get("user_message", "")

        sys_msg = load_prompt(sys_msg_path) if sys_msg_path else ""
        user_template = load_prompt(user_msg_path) if user_msg_path else ""

        # Format user message
        user_msg = user_template.format(
            round=round_num,
            price=price,
            prev_price=prev_price,
            return_pct=price_return * 100,
            volume=volume,
            net_demand=net_demand,
            fundamental=extras.get("fundamental", 100.0),
            recent_prices=recent_prices_str,
            cash=cash,
            position=position,
            portfolio_value=cash + position * price,
        )

        messages = build_messages(sys_msg, user_msg)

        # Call LLM
        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            try:
                infer_output = await call_llm(
                    messages=messages,
                    lm_type=llm_config.get("lm_type", "api"),
                    lm_name=llm_config.get("lm_name", ""),
                    generation_config=llm_config.get("generation_config", {}),
                )
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        f"[{self.identity}] LLM parse failed, retrying..."
                    )  # pylint: disable=logging-fstring-interpolation

        # If LLM failed after all retries, skip trading this round (hold)
        if decision is None:
            logger.warning(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}. "
                f"Skipping trade this round."
            )
            return self._hold_order(
                round_num, strategy_name, reason=f"LLM failed: {last_error}"
            )

        # Extract decision
        action = decision.get("action", "hold")
        bid_price = float(decision.get("bid_price", price))
        quantity = float(decision.get("quantity", 0))
        reasoning = decision.get("reasoning", "")
        analysis = decision.get("analysis", "")

        # Execute trade
        if quantity > 0:
            cost = quantity * bid_price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.state.custom_state["position"] += quantity
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= self.state.custom_state["position"]:
                proceeds = abs(quantity) * bid_price
                self.state.custom_state["cash"] += proceeds
                self.state.custom_state["position"] += quantity
            else:
                quantity = 0

        logger.debug(
            f"[{self.identity:20s}] R{round_num} ({strategy_name:20s}): "
            f"P={bid_price:7.2f}, Q={quantity:+7.2f} | "
            f"Cash={self.state.custom_state['cash']:8.2f}, "
            f"Pos={self.state.custom_state['position']:+7.2f}"
        )

        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": reasoning[:120],
            "analysis": analysis,
            "cash": self.state.custom_state["cash"],
            "position": self.state.custom_state["position"],
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "investor": self.identity,
                        "reasoning": reasoning[:100],
                        "analysis": analysis,
                        "cash": self.state.custom_state["cash"],
                        "position": self.state.custom_state["position"],
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    def _hold_order(self, round_num, strategy_name, reason=""):
        return {
            "bid_price": 0,
            "quantity": 0,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": reason[:120] if reason else "hold",
            "analysis": "",
            "cash": self.state.custom_state.get("cash", 0),
            "position": self.state.custom_state.get("position", 0),
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": strategy_name,
                        "investor": self.identity,
                        "reasoning": reason[:100] if reason else "hold",
                        "analysis": "",
                        "cash": self.state.custom_state.get("cash", 0),
                        "position": self.state.custom_state.get("position", 0),
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Concrete LLM Investor Classes
# =============================================================================


class RuleLLMMomentumInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM MomentumInvestor: following trend signals. Theory: simulation-bases.md §4.1."""

    pass


class RuleLLMContrarianInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM ContrarianInvestor: betting against the crowd. Theory: simulation-bases.md §4.2."""

    pass


class RuleLLMRiskAverseInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM RiskAverseInvestor: managing volatility. Theory: simulation-bases.md §4.3."""

    pass


class RuleLLMAggressiveInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM AggressiveInvestor: acceleration bonus momentum. Theory: simulation-bases.md §4.5."""

    pass


class RuleLLMNoiseTrader(BaseLLMInvestor):
    """Hybrid rule+LLM NoiseTrader: random uninformed decisions. Theory: simulation-bases.md §4.4."""

    pass
