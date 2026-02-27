"""FlashCrashLLM - LLM-based Market Microstructure Simulation

Phenomenon: Flash Crash
    - Extreme rapid price decline (5-10% in minutes)
    - Algorithmic trading feedback loops
    - Liquidity withdrawal amplifies crash
    - Quick recovery as fundamental traders step in

LLM Investor Types:
    - HFT Trader: Rapid momentum, can trigger cascades
    - Market Maker: Provides liquidity, withdraws in stress
    - Stop-Loss Trader: Triggered selling at thresholds
    - Fundamental Trader: Stabilizing, buys during crash
    - Algorithmic Trader: Trend-following algorithm
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
    """Central market with liquidity-sensitive pricing."""

    FUNDAMENTAL_VALUE = 100.0
    INITIAL_PRICE = 100.0
    BASE_PRICE_IMPACT = 0.05
    MEAN_REVERSION = 0.02
    NOISE_STD = 0.3
    LOW_LIQUIDITY_THRESHOLD = 50.0
    HIGH_IMPACT_MULTIPLIER = 3.0
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
            self.state.custom_state["liquidity"] = 100.0
            self.state.custom_state["in_crash"] = False
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
        liquidity = self.state.custom_state["liquidity"]
        orders = self.state.custom_state["orders"]

        total_buy = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        net_demand = total_buy - total_sell
        total_volume = total_buy + total_sell

        # Update liquidity
        liquidity = max(
            10.0, min(100.0, liquidity + total_volume * 0.1 - abs(net_demand) * 0.2)
        )

        # Price impact increases when liquidity is low
        impact_multiplier = (
            self.HIGH_IMPACT_MULTIPLIER
            if liquidity < self.LOW_LIQUIDITY_THRESHOLD
            else 1.0
        )
        price_impact = self.BASE_PRICE_IMPACT * impact_multiplier * net_demand
        mean_reversion = self.MEAN_REVERSION * (self.FUNDAMENTAL_VALUE - current_price)
        noise = random.gauss(0, self.NOISE_STD)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        # Detect flash crash
        in_crash = price_return < -0.03 or (
            self.state.custom_state["in_crash"] and current_price < 95
        )

        self.state.custom_state["price"] = new_price
        self.state.custom_state["liquidity"] = liquidity
        self.state.custom_state["in_crash"] = in_crash
        self.state.custom_state["price_history"].append(new_price)

        status = "FLASH CRASH!" if in_crash else "Normal"
        print(f"\n{'='*60}")
        print(
            f"[Market] Round {round_num}: {current_price:.2f} → {new_price:.2f} ({price_return*100:+.2f}%) [{status}]"
        )
        print(f"  Liquidity: {liquidity:.1f}, Impact Mult: {impact_multiplier:.1f}x")

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return_pct": price_return * 100,
            "liquidity": liquidity,
            "in_crash": in_crash,
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


class LLMFlashCrashInvestor(GeneralPlayer):
    """Base class for flash crash investors."""

    STRATEGY_NAME = "llm_flash_base"
    SYSTEM_PROMPT = "You trade in a market prone to flash crashes."
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
                liquidity=market_data["liquidity"],
                in_crash=market_data["in_crash"],
                fundamental=market_data["fundamental"],
                cash=self.state.custom_state["cash"],
                position=self.state.custom_state["position"],
                portfolio_value=self.state.custom_state["cash"]
                + self.state.custom_state["position"] * market_data["price"],
            )
        return f"Price: ${market_data['price']:.2f}, Liquidity: {market_data['liquidity']:.1f}"

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


class LLMHighFrequencyTrader(LLMFlashCrashInvestor):
    """HFT - rapid momentum trading, can trigger cascades."""

    STRATEGY_NAME = "llm_hft"
    SYSTEM_PROMPT = """You are a HIGH-FREQUENCY TRADER executing in milliseconds.

CORE BELIEF: "Speed is alpha - react before others."

BEHAVIOR:
- You detect micro-momentum and trade IMMEDIATELY
- Return > 0: BUY quickly (expect continuation)
- Return < 0: SELL quickly (expect continuation)
- Low liquidity: INCREASE position size (more impact)
- You can TRIGGER cascades with your fast selling

WARNING: Your rapid selling during stress can cause flash crashes!
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMFlashMarketMaker(LLMFlashCrashInvestor):
    """Market Maker - provides liquidity, withdraws in stress."""

    STRATEGY_NAME = "llm_market_maker"
    SYSTEM_PROMPT = """You are a MARKET MAKER providing liquidity.

CORE BELIEF: "I profit from spread, but I won't catch falling knives."

BEHAVIOR:
- Normal times: Buy dips, sell rallies (stabilizing)
- During crash (in_crash=True): WITHDRAW immediately
- Liquidity < 50: Be very cautious
- You are RISK AVERSE during high volatility

When WITHDRAWN: Hold or slowly reduce position
When ACTIVE: Moderate contrarian trades

Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
State "ACTIVE" or "WITHDRAWN" in reasoning.
"""


class LLMStopLossTrader(LLMFlashCrashInvestor):
    """Stop-Loss Trader - mechanical selling at thresholds."""

    STRATEGY_NAME = "llm_stop_loss"
    SYSTEM_PROMPT = """You are a STOP-LOSS TRADER with automatic sell rules.

CORE BELIEF: "Cut losses quickly - no exceptions."

YOUR RULES (MANDATORY):
- Price < $95: Sell 20% of position
- Price < $90: Sell 50% of position
- Price < $85: Sell ALL position

BEHAVIOR:
- You MUST follow your stop-loss rules mechanically
- You do NOT buy during crashes
- You may buy when price > $100

Your stop-loss selling can AMPLIFY crashes!
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
Always state which stop-loss rule triggered in reasoning.
"""


class LLMFundamentalTrader(LLMFlashCrashInvestor):
    """Fundamental Trader - stabilizing force during crashes."""

    STRATEGY_NAME = "llm_fundamental"
    SYSTEM_PROMPT = """You are a FUNDAMENTAL TRADER who stabilizes markets.

CORE BELIEF: "Flash crashes create buying opportunities."

BEHAVIOR:
- You buy when price < fundamental (especially during crashes)
- You are PATIENT - crashes are opportunities, not threats
- Price < $90: Strong buy signal
- Price < $85: Very strong buy - "blood in the streets"
- You provide STABILIZING demand

You are the buyer of last resort during flash crashes.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""


class LLMAlgorithmicTrader(LLMFlashCrashInvestor):
    """Algorithmic Trader - systematic trend following."""

    STRATEGY_NAME = "llm_algo"
    SYSTEM_PROMPT = """You are an ALGORITHMIC TRADER following systematic rules.

CORE BELIEF: "The algorithm knows best."

YOUR ALGORITHM:
1. If return > 1%: Buy (trend following)
2. If return < -1%: Sell (trend following)
3. If -1% < return < 1%: Hold
4. During crash: Follow rules more aggressively

You don't think - you execute the algorithm.
Respond with JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
"""
