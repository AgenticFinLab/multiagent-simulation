"""EquityPremiumLLM - LLM-based Equity Premium Puzzle Simulation

Phenomenon: Equity Premium Puzzle (Mehra & Prescott, 1985)
    - Stocks historically return ~6% more than bonds
    - Standard theory cannot explain this with reasonable risk aversion
    - Myopic Loss Aversion (Benartzi & Thaler, 1995) provides explanation:
      * Investors evaluate portfolios frequently
      * Losses hurt more than gains (λ ≈ 2.25)
      * Short evaluation → stocks look risky → high premium demanded

LLM Investor Types:
    - Myopic Loss Averse: Evaluates frequently, demands high premium
    - Long-Term Investor: Evaluates infrequently, more stocks
    - Institutional Investor: Balanced allocation
    - Risk-Averse Saver: Prefers bonds
    - Rational Optimizer: Expected utility maximizer
"""

import os
import json
import random
import re
import math
import importlib
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """Market with two assets: stock and bond."""

    STOCK_EXPECTED_RETURN = 0.06 / 252  # ~6% annual / 252 days
    BOND_RETURN = 0.01 / 252  # ~1% annual risk-free
    STOCK_VOLATILITY = 0.15 / math.sqrt(252)  # ~15% annual vol
    INITIAL_STOCK_PRICE = 100.0
    HISTORY_LIMIT = 200

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "stock_price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["stock_price"] = self.INITIAL_STOCK_PRICE
            self.state.custom_state["stock_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "stock"), entry_limit=self.HISTORY_LIMIT
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
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["stock_price"]
        orders = self.state.custom_state["orders"]

        net_stock_demand = sum(o["stock_qty"] for o in orders)
        demand_impact = 0.001 * net_stock_demand

        base_return = self.STOCK_EXPECTED_RETURN + random.gauss(
            0, self.STOCK_VOLATILITY
        )
        stock_return = base_return + demand_impact

        new_price = max(1.0, current_price * (1 + stock_return))
        total_volume = sum(abs(o["stock_qty"]) for o in orders)

        self.state.custom_state["stock_price"] = new_price
        self.state.custom_state["stock_history"].append(new_price)

        print(f"\n{'='*60}")
        print(
            f"[Market] Round {round_num}: Stock ${current_price:.2f} → ${new_price:.2f} ({stock_return*100:+.2f}%)"
        )
        print(f"  Bond Return: {self.BOND_RETURN*100*252:.2f}% annual")

        market_data = {
            "stock_price": new_price,
            "prev_stock_price": current_price,
            "stock_return": stock_return,
            "stock_return_pct": stock_return * 100,
            "bond_return": self.BOND_RETURN,
            "bond_return_pct": self.BOND_RETURN * 100,
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


class LLMEquityInvestor(GeneralPlayer):
    """Base class for equity premium investors."""

    STRATEGY_NAME = "llm_equity_base"
    SYSTEM_PROMPT = "You allocate between stocks and bonds."
    INITIAL_CASH = 10000.0

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        self.state.custom_state["round"] = observation.round
        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH * 0.5  # 50% cash
            self.state.custom_state["stocks"] = 50.0  # 50 shares
            self.state.custom_state["bonds"] = self.INITIAL_CASH * 0.25  # 25% bonds

            load_dotenv()
            llm_config = self.config.extras["llm"]
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
        if "user_message" in llm_config:
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
        return f"Stock: ${market_data['stock_price']:.2f}, Return: {market_data['stock_return_pct']:.2f}%"

    def _parse_response(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Parse failed: {text[:100]}")

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        llm_client = self.state.custom_state["llm_client"]
        llm_config = self.config.extras["llm"]
        system_prompt = (
            load_prompt(llm_config["sys_message"])
            if "sys_message" in llm_config
            else self.SYSTEM_PROMPT
        )

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

        order = {
            "stock_qty": stock_qty,
            "strategy": self.STRATEGY_NAME,
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


class LLMMyopicLossAverse(LLMEquityInvestor):
    """Myopic loss averse - evaluates frequently, demands high premium."""

    STRATEGY_NAME = "llm_myopic_loss_averse"
    SYSTEM_PROMPT = """You are a MYOPIC LOSS-AVERSE INVESTOR (Benartzi & Thaler, 1995).

YOUR PSYCHOLOGY:
1. You evaluate your portfolio EVERY round (myopic)
2. Losses hurt 2.25x more than gains feel good (loss aversion λ=2.25)
3. Stocks look VERY risky to you because of daily volatility
4. You demand HIGH premium (require stocks to have much higher expected return)

BEHAVIOR:
- After ANY negative return: Consider reducing stocks
- After positive return: May increase slightly
- You PREFER bonds because they feel safer
- Target allocation: 30-50% stocks (low due to risk perception)

Your frequent evaluation makes stocks seem riskier than they are!
Respond with JSON: {"stock_qty": float, "reasoning": string}
Positive = buy stocks, Negative = sell stocks
"""


class LLMLongTermInvestor(LLMEquityInvestor):
    """Long-term investor - evaluates infrequently, more stocks."""

    STRATEGY_NAME = "llm_long_term"
    SYSTEM_PROMPT = """You are a LONG-TERM INVESTOR with annual evaluation horizon.

YOUR PSYCHOLOGY:
1. You evaluate performance over LONG periods (annual, not daily)
2. Daily volatility doesn't bother you
3. You focus on long-term expected returns
4. You understand stocks outperform over time

BEHAVIOR:
- Daily returns are NOISE - you ignore them
- You maintain HIGH stock allocation (60-80%)
- You only rebalance when allocation drifts significantly
- You BUY stocks when others panic (contrarian in short-term)

Your long horizon makes stocks look less risky!
Respond with JSON: {"stock_qty": float, "reasoning": string}
"""


class LLMInstitutionalInvestor(LLMEquityInvestor):
    """Institutional investor - balanced allocation."""

    STRATEGY_NAME = "llm_institutional"
    SYSTEM_PROMPT = """You are an INSTITUTIONAL INVESTOR with balanced mandate.

YOUR APPROACH:
1. Target allocation: 60% stocks, 40% bonds
2. Rebalance when allocation drifts > 5%
3. Process-driven, unemotional
4. You represent pension funds, endowments

BEHAVIOR:
- Calculate current stock allocation
- If > 65%: Sell stocks
- If < 55%: Buy stocks
- Otherwise: Hold

Respond with JSON: {"stock_qty": float, "reasoning": string}
"""


class LLMRiskAverseSaver(LLMEquityInvestor):
    """Risk-averse saver - prefers bonds."""

    STRATEGY_NAME = "llm_risk_averse"
    SYSTEM_PROMPT = """You are a RISK-AVERSE SAVER who prefers safety.

YOUR PSYCHOLOGY:
1. You HATE volatility
2. You prefer guaranteed returns (bonds)
3. Target: 20-30% stocks maximum
4. Sleep-at-night portfolio

BEHAVIOR:
- Any significant drop → reduce stocks
- High stock allocation → sell to reduce
- You demand VERY high premium for stock risk

Respond with JSON: {"stock_qty": float, "reasoning": string}
"""


class LLMRationalOptimizer(LLMEquityInvestor):
    """Rational optimizer - expected utility maximizer."""

    STRATEGY_NAME = "llm_rational"
    SYSTEM_PROMPT = """You are a RATIONAL EXPECTED UTILITY MAXIMIZER.

YOUR APPROACH:
1. Stocks: ~6% expected return, 15% volatility
2. Bonds: ~1% return, near-zero volatility
3. You calculate optimal allocation based on risk-return tradeoff
4. With reasonable risk aversion, optimal is 50-70% stocks

DECISION:
- Expected returns favor stocks significantly
- Daily volatility is irrelevant for long-term
- You maintain high stock allocation

Respond with JSON: {"stock_qty": float, "reasoning": string}
"""
