"""FlashCrash2010 LLM-Based Simulation

This module implements the 2010 Flash Crash simulation with LLM-driven agents.

Theoretical Foundation:
- Kirilenko et al. (2017): HFT liquidity provision and withdrawal
- Biais, Foucault & Moinas (2015): Order book dynamics
- Brunnermeier & Pedersen (2005): Predatory trading

Design:
- Market: Rule-based (same as Rule variant)
- Investors: LLM-driven with personas from prompts.py

Parameters from config (see configs/FlashCrash2010/LLM/players.yml)
"""

import asyncio
import json
import logging
import random
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.llm_client import LLMClient

from examples.FlashCrash2010.Rag.prompts import format_user_prompt, get_prompt

logger = logging.getLogger("FlashCrash2010.LLM")


class Market(GeneralPlayer):
    """
    Order book market with dynamic depth and spread.

    IDENTICAL to Rule variant - Market remains rule-based.
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            self._initialize_market_state()

        orders = self._extract_orders(observation)
        market_result = self._clear_market(orders)
        self._update_state(market_result)
        self._log_market_state()

    def _initialize_market_state(self) -> None:
        extras = self.config.extras

        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["base_depth"] = extras["base_depth"]
        self.state.custom_state["price_history"] = []
        self.state.custom_state["volume_history"] = []
        self.state.custom_state["spread_history"] = []
        self.state.custom_state["hft_participation"] = []

        self.state.custom_state["price_impact"] = extras["price_impact"]
        self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
        self.state.custom_state["noise_std"] = extras["noise_std"]
        self.state.custom_state["stress_threshold"] = extras["stress_threshold"]

        logger.info(
            "Market initialized: price=%.2f, fundamental=%.2f",
            extras["initial_price"],
            extras["fundamental_value"],
        )

    def _extract_orders(self, observation: Observation) -> list:
        orders = []
        for msg in observation.messages:
            if msg.get("type") == "order":
                orders.append(
                    {
                        "agent_id": msg.get("from"),
                        "action": msg.get("action"),
                        "quantity": msg.get("quantity"),
                        "agent_type": msg.get("agent_type"),
                    }
                )
        return orders

    def _clear_market(self, orders: list) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        base_depth = self.state.custom_state["base_depth"]

        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]

        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_flow = total_buy - total_sell

        hft_orders = [o for o in orders if o.get("agent_type") == "hft"]
        hft_participation = len(hft_orders) / len(orders) if orders else 0
        self.state.custom_state["hft_participation"].append(hft_participation)

        recent_returns = self._calculate_recent_returns()
        volatility = (
            sum(abs(r) for r in recent_returns) / len(recent_returns)
            if recent_returns
            else 0
        )

        depth = self._calculate_dynamic_depth(base_depth, volatility, hft_participation)

        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]

        price_change = (price_impact * net_flow / depth) if depth > 0 else 0
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)

        new_price = price + price_change + reversion + noise
        new_price = max(new_price, 0.01)

        spread = self._calculate_spread(volatility, hft_participation)
        bid = new_price * (1 - spread / 2)
        ask = new_price * (1 + spread / 2)

        volume = min(total_buy, total_sell) + abs(total_buy - total_sell) * 0.5

        return {
            "price": new_price,
            "bid": bid,
            "ask": ask,
            "spread": spread,
            "depth": depth,
            "volume": volume,
            "net_flow": net_flow,
            "hft_participation": hft_participation,
            "volatility": volatility,
        }

    def _calculate_recent_returns(self, window: int = 10) -> list:
        history = self.state.custom_state["price_history"]
        if len(history) < 2:
            return []

        returns = []
        for i in range(1, min(window, len(history))):
            if history[-i - 1] > 0:
                ret = (history[-i] - history[-i - 1]) / history[-i - 1]
                returns.append(ret)
        return returns

    def _calculate_dynamic_depth(
        self,
        base_depth: float,
        volatility: float,
        hft_participation: float,
    ) -> float:
        stress_factor = 1.0

        if volatility > 0.01:
            stress_factor *= 0.5
        if volatility > 0.02:
            stress_factor *= 0.3
        if hft_participation < 0.3:
            stress_factor *= 0.5

        return base_depth * max(stress_factor, 0.1)

    def _calculate_spread(self, volatility: float, hft_participation: float) -> float:
        base_spread = 0.0001
        spread = base_spread + volatility * 0.5

        if hft_participation < 0.3:
            spread *= 3.0
        if volatility > 0.02:
            spread *= 5.0

        return min(spread, 0.05)

    def _update_state(self, market_result: Dict[str, Any]) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["bid"] = market_result["bid"]
        self.state.custom_state["ask"] = market_result["ask"]
        self.state.custom_state["spread"] = market_result["spread"]
        self.state.custom_state["depth"] = market_result["depth"]

        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])
        self.state.custom_state["spread_history"].append(market_result["spread"])

    def _log_market_state(self) -> None:
        price = self.state.custom_state["price"]
        spread = self.state.custom_state["spread"]
        depth = self.state.custom_state["depth"]
        hft_part = (
            self.state.custom_state["hft_participation"][-1]
            if self.state.custom_state.get("hft_participation")
            else 0
        )

        logger.debug(
            "Round %d: price=%.2f, spread=%.4f, depth=%.0f, hft=%.1f%%",
            self.state.custom_state["round"],
            price,
            spread,
            depth,
            hft_part * 100,
        )

    async def step(self) -> Action:
        price = self.state.custom_state["price"]
        bid = self.state.custom_state["bid"]
        ask = self.state.custom_state["ask"]
        fundamental = self.state.custom_state["fundamental"]
        spread = self.state.custom_state["spread"]
        depth = self.state.custom_state["depth"]

        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0

        market_update = {
            "type": "market_update",
            "price": price,
            "bid": bid,
            "ask": ask,
            "fundamental": fundamental,
            "deviation": deviation,
            "spread": spread,
            "depth": depth,
            "round": self.state.custom_state["round"],
        }

        return Action(
            action_type="market_broadcast",
            payload={
                "market_data": market_update,
                "outbound_messages": [
                    {"payload": market_update, "content_type": "market_update"}
                ],
            },
            source_id=self.identity,
        )


class LLMInvestor(GeneralPlayer):
    """
    Base class for LLM-driven investors.

    Uses LLM to make trading decisions based on market state and persona.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_client: Optional[LLMClient] = None
        self.agent_type: str = ""

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()

        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self._update_market_info(msg)

    def _initialize_investor_state(self) -> None:
        extras = self.config.extras

        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]

        # Initialize LLM client
        llm_config = extras["llm"]
        self.llm_client = LLMClient(
            model=llm_config["model"],
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url"),
        )

        # Get agent type from config
        self.agent_type = extras["agent_type"]

        logger.info("LLM Investor initialized: type=%s", self.agent_type)

    def _update_market_info(self, msg: Dict[str, Any]) -> None:
        self.state.custom_state["price"] = msg.get("price")
        self.state.custom_state["fundamental"] = msg.get("fundamental")
        self.state.custom_state["spread"] = msg.get("spread")
        self.state.custom_state["depth"] = msg.get("depth")
        self.state.custom_state["deviation"] = msg.get("deviation")

    def _format_user_prompt(self) -> str:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        spread = self.state.custom_state["spread"]
        depth = self.state.custom_state["depth"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]

        portfolio_value = cash + position * price

        return format_user_prompt(
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            spread=spread,
            depth=depth,
            cash=cash,
            position=position,
            portfolio_value=portfolio_value,
            round_num=round_num,
        )

    def _parse_decision(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract decision."""
        try:
            # Extract JSON from response
            start_idx = response.find("<decision>")
            end_idx = response.find("</decision>")

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx + 10 : end_idx].strip()
                decision = json.loads(json_str)
                return decision

            # Fallback: try to find JSON directly
            start_idx = response.find("{")
            end_idx = response.rfind("}")
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx : end_idx + 1]
                decision = json.loads(json_str)
                return decision

        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON: %s", response)

        # Default: hold
        return {"action": "hold", "quantity": 0}

    def _validate_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and constrain LLM decision."""
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)

        # Validate action
        valid_actions = ["buy", "sell", "hold", "market_making"]
        if action not in valid_actions:
            action = "hold"

        # Validate quantity
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 0

        quantity = max(0, quantity)
        # Max order size
        quantity = min(quantity, 1000)

        # Check constraints for buy
        if action == "buy":
            price = self.state.custom_state["price"]
            cash = self.state.custom_state["cash"]
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)

        # Check constraints for sell
        if action == "sell":
            position = self.state.custom_state["position"]
            quantity = min(quantity, position)

        return {"action": action, "quantity": quantity}

    async def step(self) -> Action:
        if not self.llm_client or not self.agent_type:
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        # Get system prompt
        system_prompt = get_prompt(self.agent_type)
        if not system_prompt:
            logger.warning("No prompt found for agent type: %s", self.agent_type)
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        # Format user prompt
        user_prompt = self._format_user_prompt()

        try:
            # Call LLM
            response = await self.llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=500,
            )

            # Parse and validate decision
            raw_decision = self._parse_decision(response)
            decision = self._validate_decision(raw_decision)

            # Update state
            self._update_portfolio(decision)

            # Create order
            order = {
                "type": "order",
                "action": decision["action"],
                "quantity": decision["quantity"],
                "agent_type": self.agent_type,
            }

            return Action(
                action_type="order",
                payload={
                    "order": order,
                    "outbound_messages": [{"payload": order, "content_type": "order"}],
                },
                source_id=self.identity,
            )

        except Exception as e:
            logger.error("LLM call failed: %s", e)
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

    def _update_portfolio(self, decision: Dict[str, Any]) -> None:
        """Update portfolio state based on decision."""
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        price = self.state.custom_state["price"]

        if action == "buy" and quantity > 0:
            cost = quantity * price
            self.state.custom_state["cash"] -= cost
            self.state.custom_state["position"] += quantity

        elif action == "sell" and quantity > 0:
            proceeds = quantity * price
            self.state.custom_state["cash"] += proceeds
            self.state.custom_state["position"] -= quantity


class LLMHFTMarketMaker(LLMInvestor):
    """LLM-driven HFT Market Maker."""

    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "hft_market_maker"


class LLMMomentumChaser(LLMInvestor):
    """LLM-driven Momentum Chaser."""

    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "momentum_chaser"


class LLMFundamentalTrader(LLMInvestor):
    """LLM-driven Fundamental Trader."""

    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "fundamental_trader"


class LLMStopLossTrader(LLMInvestor):
    """LLM-driven Stop-Loss Trader."""

    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "stop_loss_trader"

        extras = self.config.extras
        self.state.custom_state["entry_price"] = extras["entry_price"]
        self.state.custom_state["stop_pct"] = extras["stop_percentage"]
        stop_level = extras["entry_price"] * (1 - extras["stop_percentage"])
        self.state.custom_state["stop_level"] = stop_level


class LLMNoiseTrader(LLMInvestor):
    """LLM-driven Noise Trader."""

    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "noise_trader"
