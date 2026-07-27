"""LossAversion RuleLLM Simulation

Loss aversion from prospect theory causes investors to hold losers too long
and sell winners too early.

Design:
- Market: Rule-based (same as Rule variant)
- Investors: Hybrid Rule+LLM with explicit quantitative rules in system prompts

All parameters are configured via players.yml config file.
"""

import logging
from typing import Any, Dict, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.utils.llm_utils import parse_llm_response_with_thinking
from examples.LossAversion.RuleLLM.prompts import (
    RULELLM_LOSS_AVERSE_PROMPT,
    RULELLM_BREAK_EVEN_PROMPT,
    RULELLM_RATIONAL_PROMPT,
    RULELLM_MOMENTUM_PROMPT,
    RULELLM_MARKET_MAKER_PROMPT,
    RULELLM_USER_TEMPLATE,
)
from examples.LossAversion.Rule.players import Market  # noqa: F401

logger = logging.getLogger("LossAversion.RuleLLM")


def _decision_parameters_text(extras: Dict[str, Any], agent_class: str) -> str:
    """Format required Rule-variant parameters for prompt grounding."""
    parameter_keys = {
        "RuleLLMLossAverseInvestor": (
            "loss_aversion_lambda",
            "sell_gain_threshold",
            "gain_sell_fraction",
            "loss_sell_fraction",
            "base_size",
        ),
        "RuleLLMBreakEvenTrader": (
            "risk_increase_factor", "loss_trigger", "sizing_scale", "base_size",
        ),
        "RuleLLMRationalTrader": (
            "risk_aversion", "deviation_threshold", "sizing_scale", "base_size",
        ),
        "RuleLLMMomentumTrader": ("entry_threshold", "sizing_scale", "base_size"),
        "RuleLLMMarketMaker": ("inventory_limit", "base_size"),
    }
    keys = parameter_keys[agent_class] + ("quantity_tolerance",)
    return "\n".join(f"- {key}: {extras[key]}" for key in keys)


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


def _rule_decision(
    agent_class: str,
    extras: Dict[str, Any],
    price: float,
    fundamental: float,
    cash: float,
    position: int,
    entry_price: float,
) -> tuple[str, int]:
    """Return the authoritative Rule sign and quantity for hybrid bounds."""
    deviation = (price - fundamental) / fundamental
    pnl = (price - entry_price) / entry_price
    if agent_class == "RuleLLMLossAverseInvestor":
        if pnl > extras["sell_gain_threshold"]:
            return "sell", min(position, int(position * extras["gain_sell_fraction"]), extras["base_size"])
        if pnl < -extras["sell_gain_threshold"] * extras["loss_aversion_lambda"]:
            return "sell", min(position, int(position * extras["loss_sell_fraction"]), extras["base_size"])
    elif agent_class == "RuleLLMBreakEvenTrader" and pnl < extras["loss_trigger"]:
        return "buy", min(
            int(abs(pnl) * extras["risk_increase_factor"] * extras["sizing_scale"]),
            int(cash / price), extras["base_size"],
        )
    elif agent_class == "RuleLLMRationalTrader" and abs(deviation) > extras["deviation_threshold"]:
        quantity = min(
            int(abs(deviation) * extras["risk_aversion"] * extras["sizing_scale"]),
            extras["base_size"],
        )
        return ("buy", min(quantity, int(cash / price))) if deviation < 0 else ("sell", min(quantity, position))
    elif agent_class == "RuleLLMMomentumTrader" and abs(deviation) > extras["entry_threshold"]:
        quantity = min(int(abs(deviation) * extras["sizing_scale"]), extras["base_size"])
        return ("buy", min(quantity, int(cash / price))) if deviation > 0 else ("sell", min(quantity, position))
    elif agent_class == "RuleLLMMarketMaker" and abs(position) < extras["inventory_limit"]:
        if deviation > 0:
            return "sell", min(extras["base_size"], position)
        if deviation < 0:
            return "buy", min(
                extras["base_size"], int(cash / price),
                max(extras["inventory_limit"] - position, 0),
            )
    return "hold", 0


class RuleLLMInvestor(GeneralPlayer):
    """Base class for hybrid Rule+LLM investors in LossAversion simulation.

    Each subclass sets _system_prompt to embed both persona and quantitative rules.
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

        user_msg = RULELLM_USER_TEMPLATE.format(
            round_num=round_num,
            price=price,
            fundamental=fundamental,
            deviation=deviation * 100,
            cash=cash,
            position=position,
            entry_price=self.state.custom_state["entry_price"],
            portfolio_value=cash + position * price,
            decision_parameters=_decision_parameters_text(
                self.config.extras,
                self.__class__.__name__,
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

        rule_action, rule_quantity = _rule_decision(
            self.__class__.__name__, self.config.extras, price, fundamental,
            cash, position, self.state.custom_state["entry_price"],
        )
        if self.__class__.__name__ == "RuleLLMLossAverseInvestor":
            if "last_realization_domain" not in self.state.custom_state:
                self.state.custom_state["last_realization_domain"] = None
            pnl = (price - self.state.custom_state["entry_price"]) / self.state.custom_state["entry_price"]
            active_domain = None
            if pnl > self.config.extras["sell_gain_threshold"]:
                active_domain = "gain"
            elif pnl < -self.config.extras["sell_gain_threshold"] * self.config.extras["loss_aversion_lambda"]:
                active_domain = "loss"
            if active_domain is None:
                self.state.custom_state["last_realization_domain"] = None
            elif self.state.custom_state["last_realization_domain"] == active_domain:
                rule_action, rule_quantity = "hold", 0
            elif rule_action == "sell":
                self.state.custom_state["last_realization_domain"] = active_domain
        action = rule_action
        if rule_action == "hold" or rule_quantity <= 0:
            quantity = 0
        else:
            tolerance = float(self.config.extras["quantity_tolerance"])
            lower = max(1, int(rule_quantity * (1 - tolerance)))
            upper = max(lower, int(rule_quantity * (1 + tolerance)))
            quantity = min(max(quantity, lower), upper, int(self.config.extras["base_size"]))

        if action == "buy":
            max_qty = int(cash / price) if price > 0 else 0
            quantity = min(quantity, max_qty)
            if self.__class__.__name__ == "RuleLLMMarketMaker":
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


class RuleLLMLossAverseInvestor(RuleLLMInvestor):
    """Hybrid: LossAverseInvestor rules + LLM reasoning. Theory: simulation-bases.md §4.1"""

    _system_prompt = RULELLM_LOSS_AVERSE_PROMPT


class RuleLLMBreakEvenTrader(RuleLLMInvestor):
    """Hybrid: BreakEvenTrader rules + LLM reasoning. Theory: simulation-bases.md §4.2"""

    _system_prompt = RULELLM_BREAK_EVEN_PROMPT


class RuleLLMRationalTrader(RuleLLMInvestor):
    """Hybrid: RationalTrader rules + LLM reasoning. Theory: simulation-bases.md §4.3"""

    _system_prompt = RULELLM_RATIONAL_PROMPT


class RuleLLMMomentumTrader(RuleLLMInvestor):
    """Hybrid: MomentumTrader rules + LLM reasoning. Theory: simulation-bases.md §4.4"""

    _system_prompt = RULELLM_MOMENTUM_PROMPT


class RuleLLMMarketMaker(RuleLLMInvestor):
    """Hybrid: MarketMaker rules + LLM reasoning. Theory: simulation-bases.md §4.5"""

    _system_prompt = RULELLM_MARKET_MAKER_PROMPT


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMLossAverseInvestor",
    "RuleLLMBreakEvenTrader",
    "RuleLLMRationalTrader",
    "RuleLLMMomentumTrader",
    "RuleLLMMarketMaker",
]
