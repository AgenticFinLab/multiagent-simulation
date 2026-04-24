"""Volmageddon LLM Simulation

February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours trading

Design:
    - Market: Rule-based coordinator (identical to Volmageddon.Rule.Market).
    - Investors: LLM-powered with system prompts that encode persona + strategy.

All parameters configured via players.yml.
"""

import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.llm_utils import parse_llm_response_with_thinking
from .prompts import (
    LLM_SHORT_VOL_TRADER_SYS,
    LLM_VOL_ETN_MANAGER_SYS,
    LLM_LONG_VOL_HEDGER_SYS,
    LLM_VOL_ARBITRAGEUR_SYS,
    LLM_EQUITY_TRADER_SYS,
)
from ..Rule.players import Market  # noqa: F401 — re-exported

logger = logging.getLogger("Volmageddon.LLM")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven Volmageddon investors."""

    _system_prompt: str = ""
    _llm: Optional[LangChainAPIInference] = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
        if self._llm is None:
            llm_cfg = self.config.extras["llm"]
            self._llm = LangChainAPIInference(
                lm_name=llm_cfg["model"],
                generation_config={"temperature": llm_cfg.get("temperature", 0.3)},
            )
        return self._llm

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
            self.state.custom_state["price"] = extras.get("initial_price", 100.0)
            self.state.custom_state["fundamental"] = extras.get(
                "fundamental_value", 100.0
            )
            self.state.custom_state["deviation"] = 0.0

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["price"] = market_data.get("price", 100.0)
                self.state.custom_state["fundamental"] = market_data.get(
                    "fundamental", 100.0
                )
                self.state.custom_state["deviation"] = market_data.get("deviation", 0.0)

    def _build_prompt(self) -> str:
        price = self.state.custom_state.get("price", 100.0)
        fundamental = self.state.custom_state.get("fundamental", 100.0)
        deviation = self.state.custom_state.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]
        portfolio_value = cash + position * price

        return (
            f"Round {round_num} — Market Update\n"
            f"Current Price: ${price:.2f}  Fundamental: ${fundamental:.2f}  "
            f"Deviation: {deviation * 100:+.2f}%\n"
            f"Portfolio — Cash: ${cash:.2f}  Position: {position} shares  "
            f"Value: ${portfolio_value:.2f}\n\n"
            "Based on your strategy and the current market conditions, decide your action.\n"
            "Respond with <analysis>...</analysis> then <decision>...</decision> containing "
            'JSON: {"action": "buy" or "sell" or "hold", "quantity": integer}'
        )

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state.get("price", 100.0)
        strategy_name = self.__class__.__name__
        round_num = self.state.custom_state["round"]
        llm_client = self._get_llm()

        user_prompt = self._build_prompt()
        system_prompt = self._system_prompt

        decision: Dict[str, Any] = {"action": "hold", "quantity": 0}
        max_retries = 3
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
                break
            except (ValueError, KeyError):
                if attempt == max_retries - 1:
                    logger.warning(
                        "[%s] LLM parse failed after %d attempts; holding.",
                        self.identity,
                        max_retries,
                    )
                    decision = {"action": "hold", "quantity": 0}

        action = decision.get("action", "hold")
        quantity = int(decision.get("quantity", 0))

        valid_actions = ["buy", "sell", "hold"]
        if action not in valid_actions:
            action = "hold"
            quantity = 0
        quantity = max(0, min(quantity, 5000))

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "buy":
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif action == "sell":
            quantity = min(quantity, int(position))

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        logger.debug(
            "[%-25s] R%d (%s): action=%s qty=%d | Cash=%.2f Pos=%d",
            self.identity,
            round_num,
            strategy_name,
            action,
            quantity,
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )

        order = {
            "action": action,
            "quantity": quantity,
            "agent_type": strategy_name,
            "reasoning": decision.get("reasoning", "")[:120],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_order",
            payload=decision_payload,
            source_id=self.identity,
        )


class LLMShortVolTrader(LLMInvestor):
    """LLM-driven short volatility trader selling VIX futures/ETNs for carry."""

    _system_prompt = LLM_SHORT_VOL_TRADER_SYS


class LLMVolETNManager(LLMInvestor):
    """LLM-driven inverse VIX ETN manager with procyclical rebalancing mechanics."""

    _system_prompt = LLM_VOL_ETN_MANAGER_SYS


class LLMLongVolHedger(LLMInvestor):
    """LLM-driven long volatility hedger holding VIX as portfolio insurance."""

    _system_prompt = LLM_LONG_VOL_HEDGER_SYS


class LLMVolArbitrageur(LLMInvestor):
    """LLM-driven volatility arbitrageur trading VIX term structure dislocations."""

    _system_prompt = LLM_VOL_ARBITRAGEUR_SYS


class LLMEquityTrader(LLMInvestor):
    """LLM-driven equity trader navigating volatility spikes and fundamental dislocations."""

    _system_prompt = LLM_EQUITY_TRADER_SYS


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMShortVolTrader",
    "LLMVolETNManager",
    "LLMLongVolHedger",
    "LLMVolArbitrageur",
    "LLMEquityTrader",
]
