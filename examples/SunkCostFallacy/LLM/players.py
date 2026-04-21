import asyncio
import json
import logging
import random
import re

from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.llm_client import LLMClient

from examples.SunkCostFallacy.LLM.prompts import format_user_prompt, get_prompt
from examples.SunkCostFallacy.Rule.players import Market

logger = logging.getLogger("SunkCostFallacy.LLM")


class SunkCostHolder(GeneralPlayer):
    """LLM-driven SunkCostHolder. Holds losing positions because of prior investment, refuses to cut losses"""
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(model=llm_config["model"], api_key=llm_config["api_key"], base_url=llm_config["base_url"])
        self.agent_type = extras["agent_type"]

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        return {}

    async def act(self, decision_payload: dict) -> Action:
        if not self.llm_client or not self.agent_type:
            return Action(action_type="hold", payload={}, source_id=self.identity)
        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(price=self.state.custom_state["price"], fundamental=self.state.custom_state["fundamental"], deviation=self.state.custom_state["deviation"], cash=self.state.custom_state["cash"], position=self.state.custom_state["position"], round_num=self.state.custom_state["round"])
        try:
            response = await self.llm_client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
            decision = self._parse_decision(response)
        except Exception:
            decision = {"action": "hold", "quantity": 0}
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        if action == "buy":
            price = self.state.custom_state["price"]
            cash = self.state.custom_state["cash"]
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            position = self.state.custom_state["position"]
            quantity = min(quantity, max(position, 0))
        quantity = max(0, quantity)
        # Max order size
        quantity = min(quantity, 1000)
        if action == "buy" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "from": self.identity, "action": action, "quantity": quantity, "agent_type": self.agent_type}
        return Action(action_type="order", payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]}, source_id=self.identity)

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


class CommitmentEscalator(GeneralPlayer):
    """LLM-driven CommitmentEscalator. Doubles down on losing positions, increasing exposure to justify prior commitment"""
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(model=llm_config["model"], api_key=llm_config["api_key"], base_url=llm_config["base_url"])
        self.agent_type = extras["agent_type"]

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        return {}

    async def act(self, decision_payload: dict) -> Action:
        if not self.llm_client or not self.agent_type:
            return Action(action_type="hold", payload={}, source_id=self.identity)
        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(price=self.state.custom_state["price"], fundamental=self.state.custom_state["fundamental"], deviation=self.state.custom_state["deviation"], cash=self.state.custom_state["cash"], position=self.state.custom_state["position"], round_num=self.state.custom_state["round"])
        try:
            response = await self.llm_client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
            decision = self._parse_decision(response)
        except Exception:
            decision = {"action": "hold", "quantity": 0}
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        if action == "buy":
            price = self.state.custom_state["price"]
            cash = self.state.custom_state["cash"]
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            position = self.state.custom_state["position"]
            quantity = min(quantity, max(position, 0))
        quantity = max(0, quantity)
        # Max order size
        quantity = min(quantity, 1000)
        if action == "buy" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "from": self.identity, "action": action, "quantity": quantity, "agent_type": self.agent_type}
        return Action(action_type="order", payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]}, source_id=self.identity)

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


class RationalCutter(GeneralPlayer):
    """LLM-driven RationalCutter. Cuts losses ruthlessly based on forward-looking assessment, ignores past investment"""
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(model=llm_config["model"], api_key=llm_config["api_key"], base_url=llm_config["base_url"])
        self.agent_type = extras["agent_type"]

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        return {}

    async def act(self, decision_payload: dict) -> Action:
        if not self.llm_client or not self.agent_type:
            return Action(action_type="hold", payload={}, source_id=self.identity)
        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(price=self.state.custom_state["price"], fundamental=self.state.custom_state["fundamental"], deviation=self.state.custom_state["deviation"], cash=self.state.custom_state["cash"], position=self.state.custom_state["position"], round_num=self.state.custom_state["round"])
        try:
            response = await self.llm_client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
            decision = self._parse_decision(response)
        except Exception:
            decision = {"action": "hold", "quantity": 0}
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        if action == "buy":
            price = self.state.custom_state["price"]
            cash = self.state.custom_state["cash"]
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            position = self.state.custom_state["position"]
            quantity = min(quantity, max(position, 0))
        quantity = max(0, quantity)
        # Max order size
        quantity = min(quantity, 1000)
        if action == "buy" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "from": self.identity, "action": action, "quantity": quantity, "agent_type": self.agent_type}
        return Action(action_type="order", payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]}, source_id=self.identity)

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


class OpportunityCostTrader(GeneralPlayer):
    """LLM-driven OpportunityCostTrader. Evaluates positions by opportunity cost, reallocates capital from underperformers"""
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(model=llm_config["model"], api_key=llm_config["api_key"], base_url=llm_config["base_url"])
        self.agent_type = extras["agent_type"]

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        return {}

    async def act(self, decision_payload: dict) -> Action:
        if not self.llm_client or not self.agent_type:
            return Action(action_type="hold", payload={}, source_id=self.identity)
        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(price=self.state.custom_state["price"], fundamental=self.state.custom_state["fundamental"], deviation=self.state.custom_state["deviation"], cash=self.state.custom_state["cash"], position=self.state.custom_state["position"], round_num=self.state.custom_state["round"])
        try:
            response = await self.llm_client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
            decision = self._parse_decision(response)
        except Exception:
            decision = {"action": "hold", "quantity": 0}
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        if action == "buy":
            price = self.state.custom_state["price"]
            cash = self.state.custom_state["cash"]
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            position = self.state.custom_state["position"]
            quantity = min(quantity, max(position, 0))
        quantity = max(0, quantity)
        # Max order size
        quantity = min(quantity, 1000)
        if action == "buy" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "from": self.identity, "action": action, "quantity": quantity, "agent_type": self.agent_type}
        return Action(action_type="order", payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]}, source_id=self.identity)

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


class NoiseTrader(GeneralPlayer):
    """LLM-driven NoiseTrader. Random uninformed trader providing baseline liquidity"""
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(model=llm_config["model"], api_key=llm_config["api_key"], base_url=llm_config["base_url"])
        self.agent_type = extras["agent_type"]

    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")

    async def decide(self) -> dict:
        return {}

    async def act(self, decision_payload: dict) -> Action:
        if not self.llm_client or not self.agent_type:
            return Action(action_type="hold", payload={}, source_id=self.identity)
        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(price=self.state.custom_state["price"], fundamental=self.state.custom_state["fundamental"], deviation=self.state.custom_state["deviation"], cash=self.state.custom_state["cash"], position=self.state.custom_state["position"], round_num=self.state.custom_state["round"])
        try:
            response = await self.llm_client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
            decision = self._parse_decision(response)
        except Exception:
            decision = {"action": "hold", "quantity": 0}
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        if action == "buy":
            price = self.state.custom_state["price"]
            cash = self.state.custom_state["cash"]
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
        elif action == "sell":
            position = self.state.custom_state["position"]
            quantity = min(quantity, max(position, 0))
        quantity = max(0, quantity)
        # Max order size
        quantity = min(quantity, 1000)
        if action == "buy" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            price = self.state.custom_state["price"]
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        order = {"type": "order", "from": self.identity, "action": action, "quantity": quantity, "agent_type": self.agent_type}
        return Action(action_type="order", payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]}, source_id=self.identity)

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "SunkCostHolder, CommitmentEscalator, RationalCutter, OpportunityCostTrader, NoiseTrader"]
