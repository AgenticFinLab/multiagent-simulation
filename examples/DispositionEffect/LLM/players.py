"""DispositionEffectLLM - LLM-based Multi-Agent Market Simulation

LLM investors with different loss aversion and trading personalities.

All parameters are configured via players.yml config file.

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "DispositionEffectLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/DispositionEffect/LLM/run_disposition_llm.py \
       -c configs/DispositionEffect/LLM/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import os
import random
import sys
import importlib
import logging
import math
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import torch  # Load native DLLs before MASim/NumPy on Windows.

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

# Add examples directory to path for shared utilities
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from masim.utils.llm_utils import parse_llm_response_with_thinking

logger = logging.getLogger("DispositionEffectLLM")


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """
    Central market with news shocks.

    Parameters from config extras:
        - initial_price, fundamental_value, price_impact, mean_reversion
        - noise_std, news_probability, news_impact_range, custom_state_hot_limit, record_path
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
        price_impact = extras["price_impact"]
        mean_reversion_rate = extras["mean_reversion"]
        noise_std = extras["noise_std"]
        news_probability = extras["news_probability"]
        news_impact_range = extras["news_impact_range"]

        # Random news shock
        news_shock = 0.0
        news_event = None
        if random.random() < news_probability:
            news_shock = random.uniform(-news_impact_range, news_impact_range)
            news_event = "positive" if news_shock > 0 else "negative"

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty

        # Price update
        price_impact_effect = price_impact * net_demand
        mean_reversion = mean_reversion_rate * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(
            1.0,
            current_price + price_impact_effect + mean_reversion + noise + news_shock,
        )
        price_return = (new_price - current_price) / current_price

        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        if news_event:
            print(f"  NEWS: {news_event} shock ({news_shock:+.2f})")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "fundamental": fundamental_value,
            "news_event": news_event,
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
            self.state.custom_state["purchase_price"] = extras["initial_purchase_price"]

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
        purchase_price = self.state.custom_state["purchase_price"]
        current_price = market_data["price"]
        if purchase_price <= 0:
            raise ValueError("purchase_price must be positive")

        gain_loss = (current_price - purchase_price) / purchase_price * 100
        gain_loss_status = (
            "GAIN" if gain_loss > 0 else "LOSS" if gain_loss < 0 else "EVEN"
        )

        llm_config = self.config.extras["llm"]
        template = load_prompt(llm_config["user_message"])
        return template.format(
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            return_pct=market_data["return_pct"],
            fundamental=market_data["fundamental"],
            purchase_price=purchase_price,
            gain_loss=gain_loss,
            gain_loss_status=gain_loss_status,
            news_event=market_data["news_event"],
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
            max_position=self.config.extras["max_position"],
            max_order_quantity=self.config.extras["max_order_quantity"],
        )

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response with thinking and decision sections.

        Delegates to shared utility in masim.utils.llm_utils.py
        """
        return parse_llm_response_with_thinking(response_text)

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        """Apply solvency, inventory, and per-order safety constraints."""
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        max_position = self.config.extras["max_position"]
        max_order_quantity = self.config.extras["max_order_quantity"]
        if not math.isfinite(quantity):
            raise ValueError("quantity must be finite")
        quantity = max(-max_order_quantity, min(max_order_quantity, quantity))
        if quantity > 0:
            if bid_price <= 0:
                raise ValueError("bid_price must be positive")
            max_affordable = cash / bid_price
            remaining_capacity = max(0.0, max_position - position)
            quantity = min(quantity, max_affordable, remaining_capacity)
        elif quantity < 0:
            quantity = max(-position, quantity)
        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        strategy_name = self.__class__.__name__

        user_prompt = self._build_prompt(market_data)
        llm_config = self.config.extras["llm"]
        system_prompt = load_prompt(llm_config["sys_message"])

        max_retries = llm_config["max_retries"]
        decision = None
        last_error = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.response)
                if decision["action"] not in ("buy", "sell", "hold"):
                    raise ValueError(f"invalid action: {decision['action']}")
                if float(decision["bid_price"]) <= 0:
                    raise ValueError(f"invalid bid_price: {decision['bid_price']}")
                if not str(decision["reasoning"]).strip():
                    raise ValueError("missing reasoning")
                break
            except Exception as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug("[%s] LLM parse failed, retrying...", self.identity)

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM failed after {max_retries} attempts: {last_error}"
            )

        # The market broadcast is the execution price.  The LLM-proposed price
        # is validated above for schema compliance but cannot mint cash through
        # off-market trades.
        bid_price = float(market_data["price"])
        if not math.isfinite(bid_price) or bid_price <= 0:
            raise ValueError(f"invalid market price: {bid_price}")
        quantity = float(decision["quantity"])
        if decision["action"] == "sell":
            quantity = -abs(quantity)
        elif decision["action"] == "buy":
            quantity = abs(quantity)
        else:
            quantity = 0.0

        quantity = self._apply_constraints(bid_price, quantity)
        action = decision["action"]
        if quantity > 0:
            action = "buy"
        elif quantity < 0:
            action = "sell"
        else:
            action = "hold"

        # Update purchase price if buying
        if quantity > 0:
            old_position = self.state.custom_state["position"]
            old_cost = old_position * self.state.custom_state["purchase_price"]
            new_cost = quantity * bid_price
            total_position = old_position + quantity
            if total_position > 0:
                self.state.custom_state["purchase_price"] = (
                    old_cost + new_cost
                ) / total_position
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        print(
            f"[{self.identity:20s}] R{round_num} ({strategy_name:15s}): Q={quantity:+7.2f}"
        )

        order = {
            "action": action,
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision["analysis"],
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


class LLMDispositionBiased(LLMInvestor):
    """LLM-driven disposition-biased investor — sells winners early, holds losers. Theory: simulation-bases.md §4.1."""

    pass


class LLMRationalInvestor(LLMInvestor):
    """LLM-driven rational investor — trades on fundamentals, ignores reference point. Theory: simulation-bases.md §4.2."""

    pass


class LLMTaxAwareInvestor(LLMInvestor):
    """LLM-driven tax-aware investor — harvests losses, defers gains for tax optimization. Theory: simulation-bases.md §4.3."""

    pass


class LLMInstitutionalInvestor(LLMInvestor):
    """LLM-driven institutional investor — professional symmetric thresholds, weak disposition. Theory: simulation-bases.md §4.5."""

    pass


class LLMLossAverse(LLMInvestor):
    """LLM-driven extreme loss-averse investor — very reluctant to realize losses. Theory: simulation-bases.md §4.1."""

    pass


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMDispositionBiased",
    "LLMRationalInvestor",
    "LLMTaxAwareInvestor",
    "LLMInstitutionalInvestor",
    "LLMLossAverse",
]
