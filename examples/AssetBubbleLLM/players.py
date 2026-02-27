"""AssetBubbleLLM - LLM-based Asset Bubble Simulation

Phenomenon: Asset Bubbles with LLM Decision-Making
    LLM investors simulate different bubble-related trading personalities:
    - Greater Fool speculator (extremely destabilizing)
    - Rational arbitrageur (weakly stabilizing due to limits)
    - Noise trader (destabilizing through herding)
    - Fundamental investor (weakly stabilizing)
    - Leveraged buyer (amplifies both bubbles and crashes)

Theoretical Foundation:
    - Greater Fool Theory: Buy expensive expecting to sell higher
    - Limits to Arbitrage (Shleifer & Vishny, 1997)
    - Noise Trader Risk (De Long et al., 1990)
    - Synchronization Risk (Abreu & Brunnermeier, 2003)

All parameters are configured via players.yml config file.
"""

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


def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """
    Central market with bubble-prone price dynamics.

    Parameters from config extras:
        - fundamental_value, initial_price, price_impact, mean_reversion
        - fundamental_growth, noise_std, short_cost_rate, history_limit, record_path
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
            history_limit = extras["history_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]

            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=history_limit,
            )
            self.state.custom_state["bubble_metric_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "bubble_metric"),
                entry_limit=history_limit,
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

        # Bubble metric
        bubble_ratio = new_price / new_fundamental

        # Update state
        self.state.custom_state["price"] = new_price
        self.state.custom_state["fundamental"] = new_fundamental
        self.state.custom_state["price_history"].append(new_price)
        self.state.custom_state["bubble_metric_history"].append(bubble_ratio)

        # Log
        print(f"\n{'='*70}")
        print(f"[Market] Round {round_num}")
        print(
            f"  Price: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(
            f"  Fundamental: {new_fundamental:.2f}, Bubble Ratio: {bubble_ratio:.2f}x"
        )
        print(f"  Net Demand: {net_demand:+.2f}, Volume: {total_volume:.2f}")
        if orders:
            print(f"  LLM Orders ({len(orders)}):")
            for o in orders:
                print(
                    f"    {o['investor']:20s} [{o['strategy']:15s}]: Q={o['quantity']:+8.2f}"
                )
                if o["reasoning"]:
                    print(f"      → {o['reasoning'][:80]}...")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return": price_return,
            "return_pct": price_return * 100,
            "fundamental": new_fundamental,
            "bubble_ratio": bubble_ratio,
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


class LLMBubbleInvestor(GeneralPlayer):
    """
    Base class for LLM-powered bubble investors.

    Parameters from config extras:
        - initial_cash, initial_position, history_limit, record_path, llm config
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
            history_limit = extras["history_limit"]

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
                entry_limit=history_limit,
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
        """Build user prompt with bubble-specific market data."""
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
- Bubble Ratio (Price/Fundamental): {market_data['bubble_ratio']:.2f}x
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
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))

        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))

        raise ValueError(f"Failed to parse LLM response: {response_text[:100]}")

    def _apply_constraints(
        self, bid_price: float, quantity: float, current_price: float
    ) -> float:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]

        if quantity > 0:
            max_affordable = cash / bid_price if bid_price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif quantity < 0:
            max_sellable = position + 50  # Allow some short selling
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
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_llm_response(infer_output.response)
                break
            except ValueError as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"LLM failed after {max_retries} attempts: {e}")
                print(f"[{self.identity}] LLM parse failed, retrying...")

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        quantity = self._apply_constraints(bid_price, quantity, market_data["price"])

        # Execute trade
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

        print(
            f"[{self.identity:20s}] R{round_num} ({strategy_name:15s}): "
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


class LLMGreaterFoolSpeculator(LLMBubbleInvestor):
    """LLM Greater Fool Speculator - Primary bubble driver."""

    pass


class LLMRationalArbitrageur(LLMBubbleInvestor):
    """LLM Rational Arbitrageur - Limited corrective force."""

    pass


class LLMSentimentTrader(LLMBubbleInvestor):
    """LLM Sentiment Trader - Herding noise trader."""

    pass


class LLMValueInvestor(LLMBubbleInvestor):
    """LLM Value Investor - Weak stabilizing force."""

    pass


class LLMLeveragedSpeculator(LLMBubbleInvestor):
    """LLM Leveraged Speculator - Amplifies both directions."""

    pass
