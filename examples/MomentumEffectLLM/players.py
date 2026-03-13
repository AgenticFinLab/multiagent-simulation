"""MomentumEffectLLM - LLM-based Multi-Agent Market Simulation

LLM investors with different trading strategies:
    - Trend followers
    - Contrarian traders
    - Technical analysts
    - Value investors

Market Parameters (from config.extras):
    - record_path: Path for output records
    - initial_price: Starting price
    - initial_fundamental: Starting fundamental value
    - price_impact: Price impact coefficient
    - mean_reversion: Mean reversion strength
    - noise_std: Random noise standard deviation
    - drift_persistence: Drift autocorrelation
    - drift_volatility: Drift innovation volatility
    - custom_state_hot_limit: Maximum history buffer size

Investor Parameters (from config.extras):
    - record_path: Path for output records
    - initial_cash: Starting cash balance
    - initial_position: Starting share position
    - custom_state_hot_limit: Maximum history buffer size
    - llm: LLM configuration (sys_message, user_message, lm_name, generation_config)
"""

import os
import json
import random
import re
import importlib
from collections import deque
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """Central market with momentum-aware dynamics.

    All parameters read from config.extras (no class constants).
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
            self.state.custom_state["fundamental"] = extras["initial_fundamental"]
            self.state.custom_state["drift"] = 0.0
            self.state.custom_state["returns"] = deque(maxlen=20)  # bounded ring buffer

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
        fundamental = self.state.custom_state["fundamental"]
        drift = self.state.custom_state["drift"]
        orders = self.state.custom_state["orders"]
        returns = self.state.custom_state["returns"]

        # Get parameters from config
        price_impact_coef = extras["price_impact"]
        mean_reversion_strength = extras["mean_reversion"]
        noise_std = extras["noise_std"]
        drift_persistence = extras["drift_persistence"]
        drift_volatility = extras["drift_volatility"]

        # Update fundamental with drift (creates momentum opportunities)
        new_drift = drift_persistence * drift + random.gauss(0, drift_volatility)
        new_fundamental = fundamental + new_drift
        new_fundamental = max(50, min(150, new_fundamental))

        # Aggregate orders
        total_buy_qty = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell_qty = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy_qty - total_sell_qty

        # Price update
        price_impact = price_impact_coef * net_demand
        mean_reversion = mean_reversion_strength * (new_fundamental - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        returns.append(price_return)

        # Calculate momentum indicators
        momentum_5 = sum(returns[-5:]) if len(returns) >= 5 else 0
        momentum_10 = sum(returns[-10:]) if len(returns) >= 10 else 0

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental
        self.state.custom_state["drift"] = new_drift
        self.state.custom_state["price_history"].append(new_price)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(
            f"  Momentum5: {momentum_5*100:+.2f}%, Momentum10: {momentum_10*100:+.2f}%"
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "momentum_5": momentum_5,
            "momentum_10": momentum_10,
            "fundamental": new_fundamental,
            "round": round_num,
            "recent_returns": returns[-10:],
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
    """Base class for LLM-powered momentum investors.

    All parameters read from config.extras (no class constants).
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
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            custom_state_hot_limit = extras["custom_state_hot_limit"]

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

            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
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
            list(price_history)[-10:]
            if len(price_history) >= 10
            else list(price_history)
        )

        llm_config = self.config.extras["llm"]
        template = load_prompt(llm_config["user_message"])
        return template.format(
            price=market_data["price"],
            prev_price=market_data["prev_price"],
            return_pct=market_data["return_pct"],
            momentum_5=market_data["momentum_5"] * 100,
            momentum_10=market_data["momentum_10"] * 100,
            fundamental=market_data["fundamental"],
            recent_returns=[f"{r*100:.2f}%" for r in market_data["recent_returns"]],
            recent_prices=recent_prices,
            cash=cash,
            position=position,
            portfolio_value=cash + position * market_data["price"],
        )

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response and validate required fields are present and non-null."""
        parsed = None

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            pass
        if parsed is None:
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1))
        if parsed is None:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
        if parsed is None:
            raise ValueError(f"Failed to parse LLM response: {response_text[:100]}")

        # Validate required fields are present and non-null (fail-fast)
        required_fields = ["bid_price", "quantity", "reasoning"]
        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"Missing required field '{field}' in LLM response")
            if parsed[field] is None:
                raise ValueError(f"Field '{field}' is null in LLM response")

        return parsed

    def _apply_constraints(self, bid_price: float, quantity: float) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            quantity = max(-position, quantity)
        return quantity

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]

        user_prompt = self._build_prompt(market_data)
        llm_config = self.config.extras["llm"]
        system_prompt = load_prompt(llm_config["sys_message"])

        max_retries = 3
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.response)
                break
            except ValueError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM failed after {max_retries} attempts: {e}")

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        quantity = self._apply_constraints(bid_price, quantity)

        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        strategy_name = self.__class__.__name__
        print(
            f"[{self.identity:20s}] R{round_num} ({strategy_name:15s}): Q={quantity:+7.2f}"
        )

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
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


class LLMMomentumTrader(LLMInvestor):
    """Buys past winners, sells past losers."""

    pass


class LLMContrarianTrader(LLMInvestor):
    """Mean reversion strategy - opposing momentum."""

    pass


class LLMTechnicalTrader(LLMInvestor):
    """Moving average crossover strategy."""

    pass


class LLMTrendFollower(LLMInvestor):
    """Aggressive trend following."""

    pass


class LLMFundamentalAnchor(LLMInvestor):
    """Value-based anchor providing fundamental gravity."""

    pass
