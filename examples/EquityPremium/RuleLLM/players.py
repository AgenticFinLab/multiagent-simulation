"""EquityPremium RuleLLM stock/bond allocation simulation."""

from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, Optional

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

from examples.EquityPremium.LLM.players import Market
from examples.EquityPremium.decision import parse_equity_premium_decision

logger = logging.getLogger("EquityPremium.RuleLLM")


def load_prompt(prompt_path: str) -> str:
    """Load a prompt constant from a module path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class RuleLLMInvestor(GeneralPlayer):
    """Base RuleLLM investor for stock/bond allocation decisions."""

    _llm: Optional[LangChainAPIInference] = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize the API client."""
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
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            initial_cash = extras["initial_cash"]
            self.state.custom_state["cash"] = initial_cash * extras["initial_cash_ratio"]
            self.state.custom_state["stocks"] = extras["initial_stock_shares"]
            self.state.custom_state["bonds"] = initial_cash * extras["initial_bond_ratio"]

        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        """Build user prompt from stock/bond market state."""
        stock_value = self.state.custom_state["stocks"] * market_data["stock_price"]
        total_value = (
            self.state.custom_state["cash"]
            + stock_value
            + self.state.custom_state["bonds"]
        )
        stock_pct = (stock_value / total_value) * 100 if total_value > 0 else 0.0
        llm_cfg = self.config.extras["llm"]
        template = load_prompt(llm_cfg["user_message"])
        return template.format(
            round=market_data["round"],
            stock_price=market_data["stock_price"],
            prev_stock_price=market_data["prev_stock_price"],
            stock_return_pct=market_data["stock_return_pct"],
            bond_return_pct=market_data["bond_return_pct"] * 252,
            cash=self.state.custom_state["cash"],
            stocks=self.state.custom_state["stocks"],
            bonds=self.state.custom_state["bonds"],
            stock_pct=stock_pct,
            total_value=total_value,
        )

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_cfg = self.config.extras["llm"]
        system_prompt = load_prompt(llm_cfg["sys_message"])
        user_prompt = self._build_prompt(market_data)
        llm_client = self._get_llm()

        decision: Optional[Dict[str, Any]] = None
        last_error = ""
        for attempt in range(3):
            infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
            infer_output = llm_client.run([infer_input])
            try:
                decision = parse_equity_premium_decision(
                    infer_output.outputs[0].response
                )
                break
            except ValueError as exc:
                last_error = str(exc)

        if decision is None:
            # Strict fail-fast: do NOT fabricate a hold decision. Raise so
            # the simulator surfaces the failure to the runner which halts
            # the whole round loudly.
            raise RuntimeError(
                f"[{self.identity}] LLM decision unavailable after 3 retries. "
                f"Last error: {last_error}"
            )

        stock_qty = float(decision["stock_qty"])
        price = market_data["stock_price"]
        cash = self.state.custom_state["cash"]
        stocks = self.state.custom_state["stocks"]

        if stock_qty > 0:
            stock_qty = min(stock_qty, cash / price if price > 0 else 0.0)
        else:
            stock_qty = max(stock_qty, -stocks)

        if stock_qty > 0:
            self.state.custom_state["cash"] -= stock_qty * price
            self.state.custom_state["stocks"] += stock_qty
        elif stock_qty < 0:
            self.state.custom_state["cash"] += abs(stock_qty) * price
            self.state.custom_state["stocks"] += stock_qty

        strategy_name = self.__class__.__name__
        order = {
            "stock_qty": stock_qty,
            "strategy": strategy_name,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:120],
            "analysis": decision["analysis"],
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


class RuleLLMMyopicLossAverse(RuleLLMInvestor):
    """RuleLLM myopic loss-averse allocator. Theory: simulation-bases.md §4.1."""


class RuleLLMLongTermInvestor(RuleLLMInvestor):
    """RuleLLM long-horizon allocator. Theory: simulation-bases.md §4.2."""


class RuleLLMInstitutionalInvestor(RuleLLMInvestor):
    """RuleLLM risk-neutral institutional allocator. Theory: simulation-bases.md §4.3."""


class RuleLLMRiskAverseSaver(RuleLLMInvestor):
    """RuleLLM conservative saver allocator. Theory: simulation-bases.md §4.4."""


class RuleLLMRationalOptimizer(RuleLLMInvestor):
    """RuleLLM noise-trader/rational benchmark allocator. Theory: simulation-bases.md §4.5."""


__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMMyopicLossAverse",
    "RuleLLMLongTermInvestor",
    "RuleLLMInstitutionalInvestor",
    "RuleLLMRiskAverseSaver",
    "RuleLLMRationalOptimizer",
]
