import asyncio
import json
import logging
import random
import re

from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.llm_client import LLMClient

from examples.ConfirmationBias.LLM.prompts import format_user_prompt, get_prompt

logger = logging.getLogger("ConfirmationBias.LLM")

from examples.ConfirmationBias.Rule.players import Market



class BeliefAnchor(GeneralPlayer):
    """
    LLM-driven BeliefAnchor.

    Forms strong prior beliefs and selectively filters confirming evidence

    Theoretical Basis: Confirmatory evidence filtering (Nickerson, 1998)
    Market Role: destabilizing
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(
            model=llm_config["model"],
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
        )
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
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(
            price=self.state.custom_state["price"],
            fundamental=self.state.custom_state["fundamental"],
            deviation=self.state.custom_state["deviation"],
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
            round_num=self.state.custom_state["round"],
        )

        try:
            response = await self.llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
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

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.agent_type,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


class SelectiveScanner(GeneralPlayer):
    """
    LLM-driven SelectiveScanner.

    Actively seeks information supporting current position while ignoring contradictions

    Theoretical Basis: Selective information search (Lord et al., 1979)
    Market Role: destabilizing
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(
            model=llm_config["model"],
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
        )
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
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(
            price=self.state.custom_state["price"],
            fundamental=self.state.custom_state["fundamental"],
            deviation=self.state.custom_state["deviation"],
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
            round_num=self.state.custom_state["round"],
        )

        try:
            response = await self.llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
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

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.agent_type,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


class BalancedAnalyst(GeneralPlayer):
    """
    LLM-driven BalancedAnalyst.

    Evaluates all evidence equally regardless of prior beliefs

    Theoretical Basis: Bayesian rationality (Rabin & Schrag, 1999 baseline)
    Market Role: stabilizing
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(
            model=llm_config["model"],
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
        )
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
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(
            price=self.state.custom_state["price"],
            fundamental=self.state.custom_state["fundamental"],
            deviation=self.state.custom_state["deviation"],
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
            round_num=self.state.custom_state["round"],
        )

        try:
            response = await self.llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
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

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.agent_type,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


class ContrarianTrader(GeneralPlayer):
    """
    LLM-driven ContrarianTrader.

    Specifically looks for disconfirming evidence to trade against biased consensus

    Theoretical Basis: Contrarian strategy against biased markets
    Market Role: stabilizing
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(
            model=llm_config["model"],
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
        )
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
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(
            price=self.state.custom_state["price"],
            fundamental=self.state.custom_state["fundamental"],
            deviation=self.state.custom_state["deviation"],
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
            round_num=self.state.custom_state["round"],
        )

        try:
            response = await self.llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
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

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.agent_type,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )

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
    """
    LLM-driven NoiseTrader.

    Random uninformed trader providing baseline liquidity

    Theoretical Basis: Noise trader model (Black, 1986)
    Market Role: neutral
    """
    def __init__(self, config=None):
        super().__init__(config)
        self.llm_client = None
        self.agent_type = ""

    async def initialize(self) -> None:
        await super().initialize()
        extras = self.config.extras
        llm_config = extras["llm"]
        self.llm_client = LLMClient(
            model=llm_config["model"],
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
        )
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
            return Action(
                action_type="hold",
                payload={},
                source_id=self.identity,
            )

        system_prompt = get_prompt(self.agent_type)
        user_prompt = format_user_prompt(
            price=self.state.custom_state["price"],
            fundamental=self.state.custom_state["fundamental"],
            deviation=self.state.custom_state["deviation"],
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
            round_num=self.state.custom_state["round"],
        )

        try:
            response = await self.llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
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

        order = {
            "type": "order",
            "from": self.identity,
            "action": action,
            "quantity": quantity,
            "agent_type": self.agent_type,
        }

        return Action(
            action_type="order",
            payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
            source_id=self.identity,
        )

    def _parse_decision(self, response: str) -> dict:
        """Parse LLM response into trading decision."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "BeliefAnchor, SelectiveScanner, BalancedAnalyst, ContrarianTrader, NoiseTrader"]
