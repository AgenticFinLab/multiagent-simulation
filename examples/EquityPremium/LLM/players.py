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

Usage
-----
1. **Via Streamlit Web UI (Recommended):**

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```
   Then select "EquityPremiumLLM" from the scenario dropdown.

2. **Command Line:**

   ```bash
   python examples/EquityPremium/LLM/run_equity_premium_llm.py \
       -c configs/EquityPremium/LLM/simulation.yml
   ```

Environment Variables:
    ARK_API_KEY: ByteDance Doubao API key (required for LLM calls)
"""

import logging
import os
import json
import random
import re
import sys
import importlib
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
                folder=os.path.join(base_path, "stock"),
                entry_limit=custom_state_hot_limit,
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

        logger.debug("\n%s", "=" * 60)
        logger.debug(
            "[Market] Round %s: Stock $%.2f → $%.2f (%+.2f%%)",
            round_num,
            current_price,
            new_price,
            stock_return * 100,
        )
        logger.debug("  Bond Return: %.2f%% annual", bond_return * 100 * 252)

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
        analysis = ""
        analysis_match = re.search(r"<analysis>(.*?)</analysis>", text, re.DOTALL)
        if not analysis_match:
            analysis_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
        if analysis_match:
            analysis = analysis_match.group(1).strip()

        decision_text = text
        decision_match = re.search(r"<decision>(.*?)</decision>", text, re.DOTALL)
        if decision_match:
            decision_text = decision_match.group(1).strip()

        parsed = None
        try:
            parsed = json.loads(decision_text)
        except Exception:
            match = re.search(r"\{.*\}", decision_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
        if parsed is None:
            raise ValueError(f"Parse failed: {text[:100]}")

        # Validate required fields with fallback to trigger retry
        required_fields = ["stock_qty", "reasoning"]
        missing_or_null = []
        for field in required_fields:
            if field not in parsed or parsed[field] is None:
                missing_or_null.append(field)
        if missing_or_null:
            raise ValueError(f"Fields missing or null: {missing_or_null}")

        parsed["analysis"] = analysis
        return parsed

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        llm_config = self.config.extras["llm"]
        system_prompt = load_prompt(llm_config["sys_message"])

        decision = None
        last_error = None
        for attempt in range(3):
            try:
                output = llm_client.run(
                    [
                        InferInput(
                            system_msg=system_prompt,
                            user_msg=self._build_prompt(market_data),
                        )
                    ]
                )
                decision = self._parse_response(output.outputs[0].response)
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


class LLMMyopicLossAverse(LLMInvestor):
    """LLM-driven myopic loss averse — frequent evaluation with high loss sensitivity via LLM. Theory: simulation-bases.md §4.1."""

    pass


class LLMLongTermInvestor(LLMInvestor):
    """LLM-driven long-horizon investor — accepts more equity risk via extended evaluation window. Theory: simulation-bases.md §4.2."""

    pass


class LLMInstitutionalInvestor(LLMInvestor):
    """LLM-driven institutional investor — balanced allocation using risk-neutral framework. Theory: simulation-bases.md §4.3."""

    pass


class LLMRiskAverseSaver(LLMInvestor):
    """LLM-driven risk-averse saver — strong bond preference with prospect theory reasoning. Theory: simulation-bases.md §4.4."""

    pass


class LLMRationalOptimizer(LLMInvestor):
    """LLM-driven rational optimizer — expected utility maximizer modeling benchmark behavior. Theory: simulation-bases.md §4.5."""

    pass


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMMyopicLossAverse",
    "LLMLongTermInvestor",
    "LLMInstitutionalInvestor",
    "LLMRiskAverseSaver",
    "LLMRationalOptimizer",
]
