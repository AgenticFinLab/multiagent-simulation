import logging

"""LTCMCollapse RuleLLM Simulation

August-September 1998 LTCM crisis - Russian default triggered liquidity crisis

Design:
- Market: Rule-based (same as Rule variant)
- Investors: Hybrid rule+LLM with personas from prompts.py
"""

import json
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.llm_client import LLMClient

from examples.LTCMCollapse.RuleLLM.prompts import format_user_prompt, get_prompt
from examples.LTCMCollapse.Rule.players import Market

logger = logging.getLogger("LTCMCollapse.RuleLLM")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven investors."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_client = None
        self.agent_type = ""
    
    async def perceive(self, observation, prev_result=None) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        
        if "cash" not in self.state.custom_state:
            self._initialize_investor_state()
        
        for msg in observation.messages:
            if msg.get("type") == "market_update":
                self.state.custom_state["price"] = msg.get("price")
                self.state.custom_state["fundamental"] = msg.get("fundamental")
                self.state.custom_state["deviation"] = msg.get("deviation")
    
    def _initialize_investor_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["cash"] = extras["initial_cash"]
        self.state.custom_state["position"] = extras["initial_position"]
        
        llm_config = extras["llm"]
        self.llm_client = LLMClient(
            model=llm_config["model"],
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url"),
        )
        self.agent_type = extras["agent_type"]
    
    async def step(self):
        if not self.llm_client or not self.agent_type:
            return Action(
                    action_type="hold",
                    payload={},
                    source_id=self.identity,
                )
        
        system_prompt = get_prompt(self.agent_type)
        if not system_prompt:
            return Action(
                    action_type="hold",
                    payload={},
                    source_id=self.identity,
                )
        
        user_prompt = self._format_user_prompt()
        
        try:
            response = await self.llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=500,
            )
            
            raw_decision = self._parse_decision(response)
            decision = self._validate_decision(raw_decision)
            self._update_portfolio(decision)
            
            order = {
                "type": "order",
                "action": decision["action"],
                "quantity": decision["quantity"],
                "agent_type": self.agent_type,
            }
            return Action(
                    action_type="order",
                    payload={"order": order, "outbound_messages": [{"payload": order, "content_type": "order"}]},
                    source_id=self.identity,
                )
        except Exception as e:
            logger.error("LLM call failed: %%s", e)
            return Action(
                    action_type="hold",
                    payload={},
                    source_id=self.identity,
                )
    
    def _format_user_prompt(self) -> str:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        
        return format_user_prompt(
            price=price,
            fundamental=fundamental,
            deviation=deviation,
            cash=cash,
            position=position,
            round_num=round_num,
        )
    
    def _parse_decision(self, response: str) -> dict:
        try:
            start = response.find("<decision>")
            end = response.find("</decision>")
            if start != -1 and end != -1:
                json_str = response[start + 10:end].strip()
                return json.loads(json_str)
            start = response.find("{")
            end = response.rfind("}")
            if start != -1 and end != -1:
                return json.loads(response[start:end + 1])
        except json.JSONDecodeError:
            pass
        return {"action": "hold", "quantity": 0}
    
    def _validate_decision(self, decision: dict) -> dict:
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        
        valid_actions = ["buy", "sell", "hold", "market_making"]
        if action not in valid_actions:
            action = "hold"
        
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 0
        quantity = max(0, min(quantity, 5000))
        
        if action == "buy":
            price = self.state.custom_state["price"]
            cash = self.state.custom_state["cash"]
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
        
        if action == "sell":
            position = self.state.custom_state["position"]
            quantity = min(quantity, position)
        
        return {"action": action, "quantity": quantity}
    
    def _update_portfolio(self, decision: dict) -> None:
        action = decision.get("action", "hold")
        quantity = decision.get("quantity", 0)
        price = self.state.custom_state["price"]
        
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity


class LLMConvergenceArbitrageur(LLMInvestor):
    """LLM-driven ConvergenceArbitrageur."""
    
    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "convergence_arbitrageur"

class LLMLeverageTrader(LLMInvestor):
    """LLM-driven LeverageTrader."""
    
    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "leverage_trader"

class LLMRiskManager(LLMInvestor):
    """LLM-driven RiskManager."""
    
    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "risk_manager"

class LLMLiquidityProvider(LLMInvestor):
    """LLM-driven LiquidityProvider."""
    
    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "liquidity_provider"

class LLMCentralBank(LLMInvestor):
    """LLM-driven CentralBank."""
    
    def _initialize_investor_state(self) -> None:
        super()._initialize_investor_state()
        self.agent_type = "central_bank"


__all__ = ["Market", "LLMInvestor", "LLMConvergenceArbitrageur", "LLMLeverageTrader", "LLMRiskManager", "LLMLiquidityProvider", "LLMCentralBank"]
