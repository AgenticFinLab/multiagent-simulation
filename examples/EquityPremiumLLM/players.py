"""EquityPremiumLLM - LLM-based Multi-Agent Asset Allocation Simulation

LLM Investor Types:
    - Loss-Averse Investor: Evaluates frequently, sensitive to losses
    - Long-Term Investor: Evaluates infrequently, more risk-tolerant
    - Institutional Investor: Balanced allocation
    - Risk-Averse Saver: Prefers low-risk assets
    - Rational Optimizer: Expected utility maximizer

Market Parameters (from config.extras):
    - record_path: Path for output records
    - stock_expected_return: Daily expected stock return
    - bond_return: Daily risk-free bond return
    - stock_volatility: Daily stock volatility
    - initial_stock_price: Starting stock price
    - custom_state_hot_limit: Maximum history buffer size

Investor Parameters (from config.extras):
    - record_path: Path for output records
    - initial_cash: Starting cash (used with ratios)
    - initial_cash_ratio: Fraction of cash to hold
    - initial_stock_shares: Starting stock shares
    - initial_bond_ratio: Fraction in bonds
    - custom_state_hot_limit: Maximum history buffer size
    - llm: LLM configuration (sys_message, user_message, lm_name, generation_config)
"""

import logging
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

logger = logging.getLogger("EquityPremiumLLM")


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """Market with two assets: stock and bond.

    All parameters read from config.extras (no class constants).
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "stock_price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["stock_price"] = extras["initial_stock_price"]
            self.state.custom_state["stock_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "stock"), entry_limit=custom_state_hot_limit
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "stock_qty": order["stock_qty"],
                        "strategy": order["strategy"],
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["stock_price"]
        orders = self.state.custom_state["orders"]

        # Get parameters from config
        stock_expected_return = extras["stock_expected_return"]
        bond_return = extras["bond_return"]
        stock_volatility = extras["stock_volatility"]

        net_stock_demand = sum(o["stock_qty"] for o in orders)
        demand_impact = 0.001 * net_stock_demand

        base_return = stock_expected_return + random.gauss(0, stock_volatility)
        stock_return = base_return + demand_impact

        new_price = max(1.0, current_price * (1 + stock_return))

        self.state.custom_state["stock_price"] = new_price
        self.state.custom_state["stock_history"].append(new_price)

        logger.debug(f"\n{'='*60}")
        logger.debug(
            f"[Market] Round {round_num}: Stock ${current_price:.2f} → ${new_price:.2f} ({stock_return*100:+.2f}%)"
        )
        logger.debug(f"  Bond Return: {bond_return*100*252:.2f}% annual")

        market_data = {
            "stock_price": new_price,
            "prev_stock_price": current_price,
            "stock_return": stock_return,
            "stock_return_pct": stock_return * 100,
            "bond_return": bond_return,
            "bond_return_pct": bond_return * 100,
            "round": round_num,
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


class LLMInvestor(GeneralPlayer):
    """Base class for equity premium investors.

    All parameters read from config.extras (no class constants).
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            initial_cash = extras["initial_cash"]
            self.state.custom_state["cash"] = (
                initial_cash * extras["initial_cash_ratio"]
            )
            self.state.custom_state["stocks"] = extras["initial_stock_shares"]
            self.state.custom_state["bonds"] = (
                initial_cash * extras["initial_bond_ratio"]
            )

            load_dotenv()
            llm_config = extras["llm"]
            self.state.custom_state["lm_name"] = llm_config["lm_name"]
            self.state.custom_state["generation_config"] = llm_config[
                "generation_config"
            ]
            self.state.custom_state["llm_client"] = LangChainAPIInference(
                lm_name=llm_config["lm_name"],
                generation_config=llm_config["generation_config"],
            )

        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload

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
                custom["llm_client"] = LangChainAPIInference(
                    lm_name=custom["lm_name"],
                    generation_config=custom["generation_config"],
                )

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        stock_value = self.state.custom_state["stocks"] * market_data["stock_price"]
        total_value = (
            self.state.custom_state["cash"]
            + stock_value
            + self.state.custom_state["bonds"]
        )
        stock_pct = (stock_value / total_value) * 100 if total_value > 0 else 0

        llm_config = self.config.extras["llm"]
        template = load_prompt(llm_config["user_message"])
        return template.format(
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

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse LLM response and validate required fields are present and non-null."""
        parsed = None
        try:
            parsed = json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
        if parsed is None:
            raise ValueError(f"Parse failed: {text[:100]}")

        # Validate required fields are present and non-null (fail-fast)
        required_fields = ["stock_qty", "reasoning"]
        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"Missing required field '{field}' in LLM response")
            if parsed[field] is None:
                raise ValueError(f"Field '{field}' is null in LLM response")

        return parsed

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        llm_config = self.config.extras["llm"]
        system_prompt = load_prompt(llm_config["sys_message"])

        for _ in range(3):
            try:
                output = llm_client.run(
                    [
                        InferInput(
                            system_msg=system_prompt,
                            user_msg=self._build_prompt(market_data),
                        )
                    ]
                )
                decision = self._parse_response(output.response)
                break
            except:
                decision = {"stock_qty": 0, "reasoning": "error"}

        stock_qty = float(decision["stock_qty"])
        cash, stocks = (
            self.state.custom_state["cash"],
            self.state.custom_state["stocks"],
        )
        price = market_data["stock_price"]

        if stock_qty > 0:
            stock_qty = min(stock_qty, cash / price if price > 0 else 0)
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
            "reasoning": decision["reasoning"][:100],
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


class LLMMyopicLossAverse(LLMInvestor):
    """Myopic loss averse - evaluates frequently, demands high premium."""

    pass


class LLMLongTermInvestor(LLMInvestor):
    """Long-term investor - evaluates infrequently, more stocks."""

    pass


class LLMInstitutionalInvestor(LLMInvestor):
    """Institutional investor - balanced allocation."""

    pass


class LLMRiskAverseSaver(LLMInvestor):
    """Risk-averse saver - prefers bonds."""

    pass


class LLMRationalOptimizer(LLMInvestor):
    """Rational optimizer - expected utility maximizer."""

    pass
