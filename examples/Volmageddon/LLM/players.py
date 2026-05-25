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

from examples.llm_utils import parse_llm_quantity_response_with_thinking

from .prompts import (
    LLM_EQUITY_TRADER_SYS,
    LLM_LONG_VOL_HEDGER_SYS,
    LLM_SHORT_VOL_TRADER_SYS,
    LLM_VOL_ETN_MANAGER_SYS,
    LLM_VOL_ARBITRAGEUR_SYS,
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
                lm_name=llm_cfg["lm_name"],
                generation_config=llm_cfg["generation_config"],
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
            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["fundamental"] = extras["fundamental_value"]
            self.state.custom_state["deviation"] = 0.0

        if observation.inbounds:
            for inb in observation.inbounds:
                market_data = inb.payload
                self.state.custom_state["price"] = market_data["price"]
                self.state.custom_state["fundamental"] = market_data["fundamental"]
                self.state.custom_state["deviation"] = market_data["deviation"]

    def _build_prompt(self) -> str:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
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
            'JSON: {"action": "buy" or "sell" or "hold", "quantity": integer, '
            '"reasoning": "brief rationale"}. Do not include any price field.'
        )

    def _parse_decision(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate the Volmageddon quantity-order contract."""
        decision = parse_llm_quantity_response_with_thinking(response_text)
        missing = [
            field
            for field in ("action", "quantity", "reasoning")
            if field not in decision or decision[field] is None
        ]
        if missing:
            raise ValueError(f"missing decision fields: {', '.join(missing)}")

        action = str(decision["action"]).lower()
        if action not in {"buy", "sell", "hold"}:
            raise ValueError(f"invalid action: {decision['action']!r}")

        try:
            quantity = int(float(decision["quantity"]))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid quantity: {decision['quantity']!r}") from exc
        if quantity < 0:
            raise ValueError(f"negative quantity: {quantity}")

        reasoning = str(decision["reasoning"]).strip()
        if not reasoning:
            raise ValueError("empty reasoning")

        return {
            "action": action,
            "quantity": quantity,
            "reasoning": reasoning,
            "analysis": str(decision["analysis"]) if "analysis" in decision else "",
        }

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        strategy_name = self.__class__.__name__
        round_num = self.state.custom_state["round"]
        llm_client = self._get_llm()

        user_prompt = self._build_prompt()
        system_prompt = self._system_prompt

        max_retries = 3
        decision: Optional[Dict[str, Any]] = None
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = self._parse_decision(infer_output.outputs[0].response)
                break
            except (ValueError, KeyError) as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d/%d): %s",
                        self.identity,
                        attempt + 1,
                        max_retries,
                        exc,
                    )

        if decision is None:
            logger.warning(
                "[%s] LLM parse contract failed after %d attempts: %s. Holding.",
                self.identity,
                max_retries,
                last_error,
            )
            decision = {
                "action": "hold",
                "quantity": 0,
                "reasoning": f"fallback hold after LLM parse failure: {last_error}",
                "analysis": "",
            }
            parser_fallback = True
        else:
            parser_fallback = False

        action = decision["action"]
        quantity = int(decision["quantity"])
        reasoning = decision["reasoning"][:120]
        analysis = decision["analysis"]
        quantity = max(0, min(quantity, 5000))

        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        if action == "hold":
            quantity = 0
        elif action == "buy":
            max_affordable = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_affordable)
        elif action == "sell":
            quantity = min(quantity, int(position))
        if quantity <= 0:
            action = "hold"
            quantity = 0

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
            "type": "order",
            "action": action,
            "quantity": quantity,
            "agent_type": strategy_name,
            "reasoning": reasoning,
            "analysis": analysis,
            "parser_fallback": parser_fallback,
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
    """LLM-driven short volatility trader.

    Theory: simulation-bases.md §4.1
    """

    _system_prompt = LLM_SHORT_VOL_TRADER_SYS


class LLMVolETNManager(LLMInvestor):
    """LLM-driven inverse VIX ETN manager.

    Theory: simulation-bases.md §4.2
    """

    _system_prompt = LLM_VOL_ETN_MANAGER_SYS


class LLMLongVolHedger(LLMInvestor):
    """LLM-driven long volatility hedger.

    Theory: simulation-bases.md §4.3
    """

    _system_prompt = LLM_LONG_VOL_HEDGER_SYS


class LLMVolArbitrageur(LLMInvestor):
    """LLM-driven volatility arbitrageur.

    Theory: simulation-bases.md §4.4
    """

    _system_prompt = LLM_VOL_ARBITRAGEUR_SYS


class LLMEquityTrader(LLMInvestor):
    """LLM-driven equity trader.

    Theory: simulation-bases.md §4.5
    """

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
