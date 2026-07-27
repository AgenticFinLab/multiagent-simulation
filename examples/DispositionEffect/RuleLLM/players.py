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
import math
import os
import random
import importlib
import copy
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

logger = logging.getLogger("DispositionEffectRuleLLM")
_DECISION_PARAM_SKIP_KEYS = {
    "record_path",
    "initial_cash",
    "initial_position",
    "initial_purchase_price",
    "custom_state_hot_limit",
    "llm",
}

from masim.utils.llm_utils import (
    is_retryable_llm_error,
    parse_llm_response_with_thinking,
)


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


def format_decision_params(extras: Dict[str, Any]) -> str:
    """Format configured rule parameters for prompt injection."""
    params = {
        key: value
        for key, value in extras.items()
        if key not in _DECISION_PARAM_SKIP_KEYS
    }
    if not params:
        return "None."
    return "\n".join(f"- {key}: {value}" for key, value in sorted(params.items()))


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
        """Initialize market state and collect investor orders."""
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
        """Advance the market price and prepare the broadcast payload."""
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
            extras["minimum_price"],
            current_price + price_impact + mean_reversion + noise + news_shock,
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
        """Broadcast the market decision to connected investors."""
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
        return self.config.extras["llm"]

    def __getstate__(self) -> Dict[str, Any]:
        """Return picklable state for Ray serialization."""
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            player_state = copy.copy(state["state"])
            custom_state = dict(player_state.custom_state)
            custom_state.pop("llm_client", None)
            player_state.custom_state = custom_state
            state["state"] = player_state
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """Restore state after Ray deserialization."""
        self.__dict__.update(state)
        if hasattr(self, "state") and hasattr(self.state, "custom_state"):
            custom_state = self.state.custom_state
            if "lm_name" in custom_state and "llm_client" not in custom_state:
                custom_state["llm_client"] = LangChainAPIInference(
                    lm_name=custom_state["lm_name"],
                    generation_config=custom_state["generation_config"],
                )

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        """Initialize portfolio state, LLM client, and current market data."""
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

            load_dotenv()
            llm_config = extras["llm"]
            self.state.custom_state["lm_name"] = llm_config["lm_name"]
            self.state.custom_state["generation_config"] = llm_config[
                "generation_config"
            ]
            self.state.custom_state["llm_client"] = LangChainAPIInference(
                lm_name=llm_config["lm_name"],
                generation_config=llm_config["generation_config"],
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
        """Request an explanation, enforce the rule, and execute the order."""
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
        news_shock = market_data["news_shock"]

        if purchase_price <= 0:
            raise ValueError("purchase_price must be positive")
        gain_loss = (price - purchase_price) / purchase_price

        # Build prompt - resolve module paths to actual prompt content
        sys_msg_path = llm_config["sys_message"]
        user_msg_path = llm_config["user_message"]

        sys_msg = load_prompt(sys_msg_path)
        user_template = load_prompt(user_msg_path)

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
            decision_params=format_decision_params(extras),
        )

        # Call LLM
        max_retries = llm_config["max_retries"]
        llm_client = self.state.custom_state["llm_client"]
        decision = None
        last_error = None
        for attempt in range(max_retries):
            try:
                infer_output = llm_client.run(
                    [InferInput(system_msg=sys_msg, user_msg=user_msg)]
                )
                decision = parse_llm_response_with_thinking(
                    infer_output.response
                )
                if decision["action"] not in ("buy", "sell", "hold"):
                    raise ValueError(f"invalid action: {decision['action']}")
                proposed_price = float(decision["bid_price"])
                if not math.isfinite(proposed_price) or proposed_price <= 0:
                    raise ValueError(f"invalid bid_price: {decision['bid_price']}")
                if not str(decision["reasoning"]).strip():
                    raise ValueError("missing reasoning")
                if not str(decision["analysis"]).strip():
                    raise ValueError("missing analysis")
                break
            except Exception as e:
                decision = None
                parse_error = isinstance(
                    e, (json.JSONDecodeError, ValueError, KeyError, TypeError)
                )
                if not parse_error and not is_retryable_llm_error(e):
                    raise
                last_error = e
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM parse failed, retrying...", self.config.identity
                    )

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}"
            )

        # Extract decision
        action = decision["action"]
        # Execute at the broadcast market price; the model-proposed bid is only
        # validated for schema compliance and cannot create off-market cash flows.
        bid_price = float(price)
        if not math.isfinite(bid_price) or bid_price <= 0:
            raise ValueError(f"invalid market price: {bid_price}")
        quantity = float(decision["quantity"])
        reasoning = decision["reasoning"]
        analysis = decision["analysis"]

        if action == "sell":
            quantity = -abs(quantity)
        elif action == "buy":
            quantity = abs(quantity)
        else:
            quantity = 0.0

        if not math.isfinite(quantity):
            raise ValueError("quantity must be finite")

        # Preserve the rule-selected direction as a hard constraint while
        # allowing the documented +/-20% LLM sizing adjustment.
        rule_quantity = self._rule_quantity(price)
        if rule_quantity == 0:
            quantity = 0.0
        else:
            # The LLM may vary magnitude, never the rule-selected direction.
            magnitude = min(
                max(abs(quantity), abs(rule_quantity) * 0.8),
                abs(rule_quantity) * 1.2,
            )
            quantity = math.copysign(magnitude, rule_quantity)

        quantity = self._apply_constraints(bid_price, quantity)
        if quantity > 0:
            action = "buy"
        elif quantity < 0:
            action = "sell"
        else:
            action = "hold"

        move_reference = not isinstance(self, RuleLLMDispositionBiased)

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
            "action": action,
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
                        "action": action,
                        "strategy": strategy_name,
                        "reasoning": reasoning[:100],
                        "analysis": analysis,
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    def _rule_quantity(self, price: float) -> float:
        """Return the deterministic counterpart quantity for the current state."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        purchase_price = self.state.custom_state["purchase_price"]
        if price <= 0 or purchase_price <= 0:
            raise ValueError("price and purchase_price must be positive")

        if isinstance(self, RuleLLMDispositionBiased):
            gain_loss = (price - purchase_price) / purchase_price
            if extras["loss_aversion"] <= 1.0:
                raise ValueError("loss_aversion must be greater than 1")
            if extras["sell_fraction_gain"] <= (
                extras["loss_aversion"] * extras["sell_fraction_loss"]
            ):
                raise ValueError(
                    "sell fractions must preserve the configured loss-aversion asymmetry"
                )
            if gain_loss >= extras["gain_threshold"] and position > 0:
                return -position * extras["sell_fraction_gain"]
            if gain_loss <= extras["loss_threshold"] and position > 0:
                return -position * extras["sell_fraction_loss"]
            if (
                abs(gain_loss) < extras["reference_buy_band"]
                and position < extras["max_position"]
            ):
                target = (extras["max_position"] - position) * extras["buy_fraction"]
                affordable = cash * extras["cash_deployment_fraction"] / price
                quantity = min(target, affordable)
                if quantity >= extras["minimum_trade_quantity"]:
                    return quantity
            return 0.0

        if isinstance(self, RuleLLMRationalInvestor):
            total_value = cash + position * price
            if total_value <= 0:
                raise ValueError("total portfolio value must be positive")
            current_allocation = position * price / total_value
            if abs(current_allocation - extras["target_allocation"]) <= extras[
                "rebalance_threshold"
            ]:
                return 0.0
            target_position = total_value * extras["target_allocation"] / price
            return (target_position - position) * extras["rebalance_speed"]

        if isinstance(self, RuleLLMTaxAwareInvestor):
            gain_loss = (price - purchase_price) / purchase_price
            if gain_loss <= extras["tax_loss_threshold"] and position > 0:
                return -position * extras["tax_harvest_fraction"]
            return 0.0

        if isinstance(self, RuleLLMInstitutionalInvestor):
            gain_loss = (price - purchase_price) / purchase_price
            if (
                gain_loss >= extras["gain_threshold"]
                or gain_loss <= extras["loss_threshold"]
            ) and position > 0:
                return -position * extras["sell_fraction"]
            return 0.0

        if isinstance(self, RuleLLMIndexHolder):
            return 0.0

        raise TypeError(f"unsupported RuleLLM investor type: {type(self).__name__}")

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        """Apply cash, inventory, and configured position constraints."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if quantity > 0:
            max_affordable = cash / bid_price
            if isinstance(self, RuleLLMDispositionBiased):
                remaining_capacity = max(
                    0.0, self.config.extras["max_position"] - position
                )
                quantity = min(quantity, max_affordable, remaining_capacity)
            else:
                quantity = min(quantity, max_affordable)
        elif quantity < 0:
            quantity = max(quantity, -position)
        return quantity

    def _hold_order(
        self, round_num: int, strategy_name: str, reason: str = ""
    ) -> Dict[str, Any]:
        """Return a schema-complete hold order when market data is unavailable."""
        bid_price = self.state.custom_state["purchase_price"]
        return {
            "bid_price": bid_price,
            "quantity": 0,
            "action": "hold",
            "strategy": strategy_name,
            "reasoning": reason[:120] if reason else "hold",
            "analysis": "",
            "outbound_messages": [
                {
                    "payload": {
                        "bid_price": bid_price,
                        "quantity": 0,
                        "action": "hold",
                        "strategy": strategy_name,
                        "reasoning": reason[:100] if reason else "hold",
                        "analysis": "",
                    },
                    "content_type": "investor_bid",
                }
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        """Submit the investor order to the market."""
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


# =============================================================================
# Concrete LLM Investor Classes
# =============================================================================


class RuleLLMDispositionBiased(BaseLLMInvestor):
    """Hybrid rule+LLM disposition-biased investor — Prospect Theory rules embedded. Theory: simulation-bases.md §4.1."""

    pass


class RuleLLMRationalInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM rational investor — rebalancing rules embedded, no reference point. Theory: simulation-bases.md §4.2."""

    pass


class RuleLLMTaxAwareInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM tax-aware investor — tax-loss harvesting rules embedded. Theory: simulation-bases.md §4.3."""

    pass


class RuleLLMInstitutionalInvestor(BaseLLMInvestor):
    """Hybrid rule+LLM institutional investor — symmetric gain/loss rules embedded. Theory: simulation-bases.md §4.5."""

    pass


class RuleLLMIndexHolder(BaseLLMInvestor):
    """Hybrid passive benchmark that always holds. Theory: simulation-bases.md §4.4."""

    pass


__all__ = [
    "Market",
    "BaseLLMInvestor",
    "RuleLLMDispositionBiased",
    "RuleLLMRationalInvestor",
    "RuleLLMTaxAwareInvestor",
    "RuleLLMInstitutionalInvestor",
    "RuleLLMIndexHolder",
]
