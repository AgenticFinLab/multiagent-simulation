"""LossAversion LLM Simulation

Loss aversion from prospect theory causes investors to hold losers too long
and sell winners too early.

Design:
- Market: Rule-based (same as Rule variant)
- Investors: LLM-driven with individual system prompts

All parameters are configured via players.yml config file.
"""

import logging
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.utils.llm_utils import parse_llm_response_with_thinking
from examples.LossAversion.LLM.prompts import (
    LLM_LOSS_AVERSE_PROMPT,
    LLM_BREAK_EVEN_PROMPT,
    LLM_RATIONAL_PROMPT,
    LLM_MOMENTUM_PROMPT,
    LLM_MARKET_MAKER_PROMPT,
    LLM_USER_TEMPLATE,
)
from examples.LossAversion.Rule.players import Market  # noqa: F401

logger = logging.getLogger("LossAversion.LLM")


def _decision_parameters_text(extras: Dict[str, Any], agent_class: str) -> str:
    """Expose each archetype's configured behavioral parameters to the model."""
    parameter_keys = {
        "LLMLossAverseInvestor": (
            "loss_aversion_lambda", "sell_gain_threshold",
            "gain_sell_fraction", "loss_sell_fraction", "base_size",
        ),
        "LLMBreakEvenTrader": (
            "risk_increase_factor", "loss_trigger", "sizing_scale", "base_size",
        ),
        "LLMRationalTrader": (
            "risk_aversion", "deviation_threshold", "sizing_scale", "base_size",
        ),
        "LLMMomentumTrader": ("entry_threshold", "sizing_scale", "base_size"),
        "LLMMarketMaker": ("inventory_limit", "base_size"),
    }
    return "\n".join(
        f"- {key}: {extras[key]}" for key in parameter_keys[agent_class]
    )


def _validate_decision(decision: Dict[str, Any]) -> None:
    """Validate the canonical trading decision contract."""
    if decision["action"] not in ("buy", "sell", "hold"):
        raise ValueError(f"Invalid action: {decision['action']}")
    if float(decision["bid_price"]) <= 0:
        raise ValueError(f"Invalid bid_price: {decision['bid_price']}")
    if int(decision["quantity"]) < 0:
        raise ValueError(f"Invalid quantity: {decision['quantity']}")
    if not str(decision["reasoning"]).strip():
        raise ValueError("Missing reasoning")


class LLMInvestor(GeneralPlayer):
    """Base class for LLM-driven investors in LossAversion simulation.

    Subclasses set _system_prompt to their agent-specific persona.
    """

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        self.state.custom_state["round"] = observation.round

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["entry_price"] = extras["initial_price"]

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload if hasattr(inb, "payload") else inb
                if isinstance(payload, dict) and payload.get("type") == "market_update":
                    self.state.custom_state["price"] = payload["price"]
                    self.state.custom_state["fundamental"] = payload["fundamental"]
                    self.state.custom_state["deviation"] = payload["deviation"]

    async def decide(self) -> Dict[str, Any]:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        round_num = self.state.custom_state["round"]

        llm_cfg = self.config.extras["llm"]
        llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )

        user_msg = LLM_USER_TEMPLATE.format(
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            entry_price=self.state.custom_state["entry_price"],
            portfolio_value=cash + position * price,
            decision_parameters=_decision_parameters_text(
                self.config.extras, self.__class__.__name__
            ),
        )

        decision = None
        last_error = None
        for attempt in range(3):
            try:
                output = llm.run(
                    [InferInput(system_msg=self._system_prompt, user_msg=user_msg)]
                )
                decision = parse_llm_response_with_thinking(output.outputs[0].response)
                _validate_decision(decision)
                break
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    logger.debug(
                        "[%s] LLM parse failed (attempt %d), retrying...",
                        self.identity,
                        attempt + 1,
                    )

        if decision is None:
            raise RuntimeError(
                f"[{self.identity}] LLM parse failed after 3 retries: {last_error}"
            )

        action = decision["action"]
        quantity = int(decision["quantity"])
        quantity = min(quantity, int(self.config.extras["base_size"]))

        # Enforce constraints
        if action == "buy":
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
            if self.__class__.__name__ == "LLMMarketMaker":
                quantity = min(
                    quantity,
                    max(int(self.config.extras["inventory_limit"]) - position, 0),
                )
        elif action == "sell":
            quantity = min(quantity, max(position, 0))
        else:
            quantity = 0

        if action == "buy" and quantity > 0:
            old_position = self.state.custom_state["position"]
            old_entry = self.state.custom_state["entry_price"]
            new_position = old_position + quantity
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] = new_position
            self.state.custom_state["entry_price"] = (
                old_entry * old_position + price * quantity
            ) / new_position
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity

        order = {
            "type": "order",
            "action": action,
            "bid_price": price,
            "quantity": quantity,
            "agent_type": self.__class__.__name__,
            "reasoning": decision["reasoning"][:120],
            "cash": self.state.custom_state["cash"],
            "position": self.state.custom_state["position"],
            "entry_price": self.state.custom_state["entry_price"],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "order"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="order",
            payload=decision_payload,
            source_id=self.identity,
        )


class LLMLossAverseInvestor(LLMInvestor):
    """LLM-driven LossAverseInvestor. Theory: simulation-bases.md §4.1"""

    _system_prompt = LLM_LOSS_AVERSE_PROMPT


class LLMBreakEvenTrader(LLMInvestor):
    """LLM-driven BreakEvenTrader. Theory: simulation-bases.md §4.2"""

    _system_prompt = LLM_BREAK_EVEN_PROMPT


class LLMRationalTrader(LLMInvestor):
    """LLM-driven RationalTrader. Theory: simulation-bases.md §4.3"""

    _system_prompt = LLM_RATIONAL_PROMPT


class LLMMomentumTrader(LLMInvestor):
    """LLM-driven MomentumTrader. Theory: simulation-bases.md §4.4"""

    _system_prompt = LLM_MOMENTUM_PROMPT


class LLMMarketMaker(LLMInvestor):
    """LLM-driven MarketMaker. Theory: simulation-bases.md §4.5"""

    _system_prompt = LLM_MARKET_MAKER_PROMPT


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMLossAverseInvestor",
    "LLMBreakEvenTrader",
    "LLMRationalTrader",
    "LLMMomentumTrader",
    "LLMMarketMaker",
]
