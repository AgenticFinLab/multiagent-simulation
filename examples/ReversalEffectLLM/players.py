"""ReversalEffectLLM - LLM-based Long-term Mean Reversion Simulation

Phenomenon: Reversal Effect (De Bondt & Thaler, 1985)
    - Past losers outperform past winners over 3-5 year periods
    - Market overreacts to information, then corrects

LLM Investor Types:
    - Contrarian Investor: Buys losers, sells winners (KEY driver)
    - Overconfident Trader: Overreacts to news
    - Momentum Investor: Short-term trend following
    - Value Investor: Slow fundamental approach
    - Noise Trader: Random liquidity
"""

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


def load_prompt(prompt_path: str) -> str:
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


class Market(GeneralPlayer):
    """Central market with mean reversion dynamics."""

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0
    PRICE_IMPACT = 0.08
    MEAN_REVERSION = 0.01
    NOISE_STD = 0.5
    HISTORY_LIMIT = 200

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            record_path = self.config.extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            self.state.custom_state["price"] = self.INITIAL_PRICE
            self.state.custom_state["cumulative_return"] = 0.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"), entry_limit=self.HISTORY_LIMIT
            )

        orders = []
        if observation.inbounds:
            for inb in observation.inbounds:
                order = inb.payload
                orders.append(
                    {
                        "investor": inb.sender_id,
                        "price": order["bid_price"],
                        "quantity": order["quantity"],
                        "strategy": order["strategy"],
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        orders = self.state.custom_state["orders"]
        cumulative_return = self.state.custom_state["cumulative_return"]

        total_buy = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy - total_sell

        price_impact = self.PRICE_IMPACT * net_demand
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price
        cumulative_return += price_return

        self.state.custom_state["price"] = new_price
        self.state.custom_state["cumulative_return"] = cumulative_return
        self.state.custom_state["price_history"].append(new_price)

        # Classify as "winner" or "loser" based on cumulative return
        performance = (
            "winner"
            if cumulative_return > 0.1
            else "loser" if cumulative_return < -0.1 else "neutral"
        )

        print(f"\n{'='*60}")
        print(
            f"[Market] Round {round_num}: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%)"
        )
        print(f"  Cumulative: {cumulative_return*100:+.2f}% ({performance})")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return_pct": price_return * 100,
            "cumulative_return": cumulative_return * 100,
            "performance": performance,
            "fundamental": self.FUNDAMENTAL_VALUE,
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


class LLMReversalInvestor(GeneralPlayer):
    """Base class for LLM reversal investors."""

    STRATEGY_NAME = "llm_reversal_base"
    SYSTEM_PROMPT = "You analyze long-term mean reversion patterns."
    INITIAL_CASH = 10000.0
    INITIAL_POSITION = 50.0

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self.state.custom_state["cash"] = self.INITIAL_CASH
            self.state.custom_state["position"] = self.INITIAL_POSITION

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
        llm_config = self.config.extras["llm"]
        if "user_message" in llm_config:
            template = load_prompt(llm_config["user_message"])
            return template.format(
                price=market_data["price"],
                prev_price=market_data["prev_price"],
                return_pct=market_data["return_pct"],
                cumulative_return=market_data["cumulative_return"],
                performance=market_data["performance"],
                fundamental=market_data["fundamental"],
                cash=self.state.custom_state["cash"],
                position=self.state.custom_state["position"],
                portfolio_value=self.state.custom_state["cash"]
                + self.state.custom_state["position"] * market_data["price"],
            )
        return f"Price: ${market_data['price']:.2f}, Cumulative: {market_data['cumulative_return']:.2f}%"

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
                decision = {
                    "action": "hold",
                    "bid_price": market_data["price"],
                    "quantity": 0,
                    "reasoning": "error",
                }

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])
        cash, position = (
            self.state.custom_state["cash"],
            self.state.custom_state["position"],
        )
        if quantity > 0:
            quantity = min(quantity, cash / bid_price if bid_price > 0 else 0)
        else:
            quantity = max(quantity, -position)

        if quantity > 0:
            self.state.custom_state["cash"] -= quantity * bid_price
            self.state.custom_state["position"] += quantity
        elif quantity < 0:
            self.state.custom_state["cash"] += abs(quantity) * bid_price
            self.state.custom_state["position"] += quantity

        order = {
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": self.STRATEGY_NAME,
            "investor": self.identity,
            "reasoning": decision["reasoning"][:100],
        }
        return {
            **order,
            "outbound_messages": [{"payload": order, "content_type": "investor_bid"}],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )


class LLMContrarianInvestor(LLMReversalInvestor):
    """Contrarian - buys losers, sells winners."""

    STRATEGY_NAME = "llm_contrarian"
    SYSTEM_PROMPT = """You are a CONTRARIAN INVESTOR following De Bondt & Thaler's reversal strategy.

CORE BELIEF: "Markets overreact - past losers will become future winners."

STRATEGY:
- If stock is a "loser" (cumulative return < -10%): BUY aggressively
- If stock is a "winner" (cumulative return > +10%): SELL aggressively
- The more extreme the past performance, the stronger your opposite bet

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMOverconfidentTrader(LLMReversalInvestor):
    """Overconfident - overreacts to recent news/returns."""

    STRATEGY_NAME = "llm_overconfident"
    SYSTEM_PROMPT = """You are an OVERCONFIDENT TRADER who overreacts to news.

CORE BELIEF: "I know where this is going - the trend will continue!"

BEHAVIOR:
- You believe recent returns predict future returns (WRONG but you believe it)
- Positive return → You extrapolate → BUY MORE
- Negative return → You panic → SELL MORE
- You overweight recent information

You CREATE the overreaction that contrarians profit from.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMValueInvestor(LLMReversalInvestor):
    """Value investor - focuses on fundamental value."""

    STRATEGY_NAME = "llm_value"
    SYSTEM_PROMPT = """You are a VALUE INVESTOR focused on fundamentals.

CORE BELIEF: "Price should equal fundamental value."

STRATEGY:
- Price < 0.95 × Fundamental: Buy
- Price > 1.05 × Fundamental: Sell
- You are patient - you don't chase momentum

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMMomentumChaser(LLMReversalInvestor):
    """Short-term momentum chaser."""

    STRATEGY_NAME = "llm_momentum_chaser"
    SYSTEM_PROMPT = """You are a SHORT-TERM MOMENTUM CHASER.

CORE BELIEF: "Winners keep winning in the short run."

STRATEGY:
- Recent return > 0: Buy (expect continuation)
- Recent return < 0: Sell (expect continuation)
- You focus on SHORT-TERM trends only

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMNoiseTrader(LLMReversalInvestor):
    """Noise trader - provides liquidity with random behavior."""

    STRATEGY_NAME = "llm_noise"
    SYSTEM_PROMPT = """You are a NOISE TRADER with no clear strategy.

BEHAVIOR:
- Your decisions are somewhat random
- You may buy or sell based on "gut feeling"
- You provide liquidity to the market
- Small positions, no strong conviction

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""
