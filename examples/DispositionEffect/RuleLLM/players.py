"""DispositionEffectRuleLLM Players - Hybrid Rule + LLM Investors

Hybrid design:
    - Market: Rule-based coordinator (same as DispositionEffect)
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
   Then select "DispositionEffectRuleLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/DispositionEffect/RuleLLM/run_disposition_rulellm.py \
       -c configs/DispositionEffect/RuleLLM/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)

Requirements:
    pip install lmbase python-dotenv
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

logger = logging.getLogger("DispositionEffectRuleLLM")

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
# Market - Coordinator (Rule-based, same as DispositionEffect)
# =============================================================================


class Market(GeneralPlayer):
    """
    Central market with standard price dynamics.

    Parameters from config extras:
        - initial_price, fundamental_value
        - price_impact, mean_reversion, noise_std
        - news_probability, news_impact_range
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

            self.state.custom_state["price"] = extras["initial_price"]
            custom_state_hot_limit = extras["custom_state_hot_limit"]
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
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
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]

        # Random news shock
        news_probability = extras["news_probability"]
        news_impact_range = extras["news_impact_range"]
        news_shock = 0.0
        if random.random() < news_probability:
            news_shock = random.uniform(-news_impact_range, news_impact_range)

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty
        total_volume = total_buy_qty + total_sell_qty

        # Price dynamics
        price_impact_rate = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        fundamental_value = extras["fundamental_value"]
        noise_std = extras["noise_std"]

        price_impact = price_impact_rate * net_demand
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(
            1.0, current_price + price_impact + mean_reversion + noise + news_shock
        )
        price_return = (new_price - current_price) / current_price

        # Update
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        logger.debug(
            "\n%s\n[Market] Round %d\n  Price: %.2f → %.2f (%+.2f%%)%s\n  Net Demand: %+.2f, Volume: %.2f%s",
            "=" * 70,
            round_num,
            current_price,
            new_price,
            price_return * 100,
            f"\n  NEWS SHOCK: {news_shock:+.2f}" if news_shock != 0 else "",
            net_demand,
            total_volume,
            (
                ("\n  Orders (%d):\n" % len(orders))
                + "\n".join(
                    f"    {o['investor']:24s} [{o['strategy']:20s}]: Q={o['quantity']:+8.2f}"
                    for o in orders
                )
                if orders
                else ""
            ),
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "volume": total_volume,
            "net_demand": net_demand,
            "news_shock": news_shock,
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
# Base LLM Investor with Reference Point Tracking
# =============================================================================


class BaseLLMInvestor(GeneralPlayer):
    """
    Base class for LLM investors with reference point tracking.

    Parameters from config extras:
        - initial_cash, initial_position, initial_purchase_price
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
            initial_cash = extras["initial_cash"]
            initial_position = extras["initial_position"]
            initial_purchase_price = extras["initial_purchase_price"]

            self.state.custom_state["cash"] = initial_cash
            self.state.custom_state["position"] = initial_position
            self.state.custom_state["purchase_price"] = initial_purchase_price
            self.state.custom_state["total_cost"] = (
                initial_position * initial_purchase_price
            )

        market_data = None
        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                break
        self.state.custom_state["market_data"] = market_data

    def update_reference_point(
        self, quantity: float, price: float, move_reference: bool = True
    ):
        """Update position and cost basis after trade."""
        position = self.state.custom_state["position"]
        total_cost = self.state.custom_state["total_cost"]

        if quantity > 0:
            new_cost = quantity * price
            total_cost += new_cost
            position += quantity
            if move_reference and position > 0:
                self.state.custom_state["purchase_price"] = total_cost / position
        elif quantity < 0:
            if position > 0:
                cost_per_share = total_cost / position
                total_cost -= abs(quantity) * cost_per_share
            position += quantity

        self.state.custom_state["position"] = position
        self.state.custom_state["total_cost"] = max(0, total_cost)

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        llm_config = self._get_llm_config()
        round_num = self.state.custom_state["round"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        market_data = self.state.custom_state["market_data"]

        strategy_name = self.__class__.__name__

        if market_data is None:
            return self._hold_order(round_num, strategy_name)

        price = market_data["price"]
        prev_price = market_data["prev_price"]
        price_return = market_data["return"]
        volume = market_data["volume"]
        net_demand = market_data["net_demand"]
        news_shock = market_data.get("news_shock", 0)

        # Compute gain/loss
        if purchase_price > 0:
            gain_loss = (price - purchase_price) / purchase_price
        else:
            gain_loss = 0

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
            news_event=f"Shock: {news_shock:+.2f}" if news_shock != 0 else "None",
            cash=cash,
            position=position,
            purchase_price=purchase_price,
            gain_loss_pct=gain_loss * 100,
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
                    logger.debug(f"[{self.identity}] LLM parse failed, retrying...")  # pylint: disable=logging-fstring-interpolation

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

        # Determine move_reference based on agent type
        move_reference = "DispositionBiased" not in strategy_name

        # Execute trade
        if quantity > 0:
            cost = quantity * bid_price
            if cost <= cash:
                self.state.custom_state["cash"] -= cost
                self.update_reference_point(quantity, bid_price, move_reference)
            else:
                quantity = 0
        elif quantity < 0:
            if abs(quantity) <= position:
                proceeds = abs(quantity) * bid_price
                self.state.custom_state["cash"] += proceeds
                self.update_reference_point(quantity, bid_price)
            else:
                quantity = 0

        logger.debug(
            "[%s] R%d (%s): Q=%+8.2f [%s] g/l=%+.1f%% | Cash=%10.2f, Pos=%+8.2f",
            self.config.identity,
            round_num,
            strategy_name,
            quantity,
            action,
            gain_loss * 100,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        return {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "reasoning": reasoning[:120],
            "analysis": analysis,
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": quantity,
                        "strategy": strategy_name,
                        "reasoning": reasoning[:100],
                        "analysis": analysis,
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
            "reasoning": reason[:120] if reason else "hold",
            "analysis": "",
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": 0,
                        "quantity": 0,
                        "strategy": strategy_name,
                        "reasoning": reason[:100] if reason else "hold",
                        "analysis": "",
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Concrete LLM Investor Classes
# =============================================================================


class RuleLLMDispositionBiased(BaseLLMInvestor):
    """Hybrid rule+LLM investor with disposition effect rules."""

    pass


class RuleLLMRationalInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM rational investor with rebalancing rules."""

    pass


class RuleLLMTaxAwareInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM tax-aware investor with tax-loss harvesting rules."""

    pass


class RuleLLMInstitutionalInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM institutional investor with symmetric rules."""

    pass


class RuleLLMLossAverse(BaseLLMInvestor):
    """Hybrid rule+LLM investor with extreme loss aversion rules."""

    pass


__all__ = [
    "Market",
    "BaseLLMInvestor",
    "RuleLLMDispositionBiased",
    "RuleLLMRationalInvestor",
    "RuleLLMTaxAwareInvestor",
    "RuleLLMInstitutionalInvestor",
    "RuleLLMLossAverse",
]
