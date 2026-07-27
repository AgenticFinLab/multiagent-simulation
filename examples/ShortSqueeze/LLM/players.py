"""ShortSqueezeLLM - LLM-based Multi-Agent Market Simulation

Market Parameters (from config.extras):
    - record_path: Path for output records
    - fundamental_value: True value
    - initial_price: Starting price
    - price_impact: Price impact coefficient
    - mean_reversion: Mean reversion strength
    - noise_std: Random noise standard deviation
    - initial_short_interest: Starting short interest percentage
    - custom_state_hot_limit: Maximum history buffer size

Investor Parameters (from config.extras):
    - record_path: Path for output records
    - initial_cash: Starting cash balance
    - initial_position: Starting share position (negative for shorts)
    - custom_state_hot_limit: Maximum history buffer size
    - llm: LLM configuration (sys_message, user_message, lm_name, generation_config)
"""

import logging
import os
import json
import random
import re
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import Action, Observation, StepResult
from masim.utils.history import HistoryBuffer
from masim.utils.llm_utils import parse_llm_response_with_thinking

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from .prompts import (
    LLM_SHORT_SELLER_SYS,
    LLM_RETAIL_COORD_SYS,
    LLM_MOMENTUM_SYS,
    LLM_VALUE_SYS,
    LLM_INSTITUTIONAL_SYS,
)

logger = logging.getLogger("ShortSqueezeLLM")


class Market(GeneralPlayer):
    """Market with short interest tracking.

    All parameters read from config.extras (no class constants).
    """

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "price" not in self.state.custom_state:
            extras = self.config.extras
            record_path = extras["record_path"]
            base_path = os.path.join(record_path, self.config.identity)
            custom_state_hot_limit = extras["custom_state_hot_limit"]

            self.state.custom_state["price"] = extras["initial_price"]
            self.state.custom_state["short_interest"] = extras["initial_short_interest"]
            self.state.custom_state["buying_pressure"] = 0.0
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(base_path, "price"),
                entry_limit=custom_state_hot_limit,
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
                        "is_short_cover": order["is_short_cover"],
                        "reasoning": order["reasoning"],
                    }
                )
        self.state.custom_state["orders"] = orders

    async def decide(self) -> Dict[str, Any]:
        extras = self.config.extras
        round_num = self.state.custom_state["round"]
        current_price = self.state.custom_state["price"]
        short_interest = self.state.custom_state["short_interest"]
        orders = self.state.custom_state["orders"]

        # Get parameters from config
        fundamental_value = extras["fundamental_value"]
        initial_price = extras["initial_price"]
        price_impact_coef = extras["price_impact"]
        mean_reversion_strength = extras["mean_reversion"]
        noise_std = extras["noise_std"]

        total_buy = sum(o["quantity"] for o in orders if o["quantity"] > 0)
        total_sell = abs(sum(o["quantity"] for o in orders if o["quantity"] < 0))
        cover_buying = sum(
            o["quantity"] for o in orders if o["is_short_cover"] and o["quantity"] > 0
        )
        net_demand = total_buy - total_sell

        # Short cover impact (forced buying creates extra impact)
        short_cover_impact = cover_buying * 0.05
        price_impact = price_impact_coef * net_demand + short_cover_impact
        mean_reversion = mean_reversion_strength * (fundamental_value - current_price)
        noise = random.gauss(0, noise_std)

        new_price = max(1.0, current_price + price_impact + mean_reversion + noise)
        price_return = (new_price - current_price) / current_price

        # Update short interest (decreases when shorts cover)
        short_interest = max(0.0, short_interest - cover_buying * 0.5)

        # Buying pressure indicator
        buying_pressure = max(0.0, (new_price / initial_price - 1) * 100)

        self.state.custom_state["price"] = new_price
        self.state.custom_state["short_interest"] = short_interest
        self.state.custom_state["buying_pressure"] = buying_pressure
        self.state.custom_state["price_history"].append(new_price)

        status = (
            "STRONG"
            if buying_pressure > 50
            else "Building" if buying_pressure > 20 else "Normal"
        )
        logger.debug(f"\n{'='*60}")  # pylint: disable=logging-fstring-interpolation
        logger.debug(
            f"[Market] Round {round_num}: ${current_price:.2f} → ${new_price:.2f} ({price_return*100:+.2f}%)"
        )
        logger.debug(
            f"  Short Interest: {short_interest:.1f}%, Buying Pressure: {buying_pressure:.1f}% [{status}]"
        )

        market_data = {
            "price": new_price,
            "prev_price": current_price,
            "return_pct": price_return * 100,
            "short_interest": short_interest,
            # Variable name kept for prompt compatibility
            "squeeze_pressure": buying_pressure,
            "fundamental": fundamental_value,
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
    """Base class for LLM-powered short-squeeze investors."""

    _system_prompt: str = ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_llm", None)
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._llm = None

    def _get_llm(self) -> LangChainAPIInference:
        """Lazy-initialize LLM client."""
        llm_cfg = self.config.extras["llm"]
        self._llm = LangChainAPIInference(
            lm_name=llm_cfg["lm_name"],
            generation_config=llm_cfg["generation_config"],
        )
        return self._llm

    async def perceive(
        self, observation: Observation, prev_result: Optional[StepResult] = None
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = extras["initial_cash"]
            self.state.custom_state["position"] = extras["initial_position"]
            self.state.custom_state["short_position"] = 0.0

        if observation.inbounds:
            for inb in observation.inbounds:
                self.state.custom_state["market_data"] = inb.payload

    def _build_prompt(self, market_data: Dict[str, Any]) -> str:
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        short_pos = self.state.custom_state["short_position"]
        return (
            f"Price: ${market_data['price']:.2f}  prev=${market_data['prev_price']:.2f}"
            f"  ret={market_data['return_pct']:.2f}%\n"
            f"Short interest: {market_data['short_interest']:.1f}%"
            f"  squeeze_pressure={market_data['squeeze_pressure']:.2f}"
            f"  fundamental=${market_data['fundamental']:.2f}\n"
            f"Portfolio: cash={cash:.2f}  position={position:.4f}"
            f"  short_pos={short_pos:.4f}"
            f"  value={cash + position * market_data['price']:.2f}\n"
            "Respond with <analysis>...</analysis> then "
            '<decision>{"action":"buy"|"sell"|"hold","bid_price":...,"quantity":...,'
            '"is_short_cover":false,"reasoning":"..."}</decision>'
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
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", decision_text, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Parse failed: {text[:100]}") from exc
        if parsed is None:
            raise ValueError(f"Parse failed: {text[:100]}")

        # Validate required fields with fallback to trigger retry.
        required_fields = ["action", "bid_price", "quantity", "reasoning"]
        missing_or_null = []
        for field in required_fields:
            if field not in parsed or parsed[field] is None:
                missing_or_null.append(field)
        if missing_or_null:
            raise ValueError(f"Fields missing or null: {missing_or_null}")

        parsed["analysis"] = analysis
        parsed.setdefault("is_short_cover", False)
        return parsed

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state["market_data"]
        system_prompt = self._system_prompt
        llm_client = self._get_llm()

        max_retries = 3
        decision = None
        last_error = None
        for attempt in range(max_retries):
            output = llm_client.run(
                [
                    InferInput(
                        system_msg=system_prompt,
                        user_msg=self._build_prompt(market_data),
                    )
                ]
            )
            try:
                decision = self._parse_response(output.outputs[0].response)
                break
            except ValueError as exc:
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
                "bid_price": market_data["price"],
                "quantity": 0,
                "is_short_cover": False,
                "reasoning": f"LLM parse failed after {max_retries} attempts: {last_error}",
                "analysis": "",
            }
            parser_fallback = True
        else:
            parser_fallback = False

        bid_price = float(decision["bid_price"])
        quantity = float(decision["quantity"])

        # Guard: LLMs sometimes output bid_price=0 for hold actions.
        # Use the current market price so recorded bids stay meaningful.
        if bid_price <= 0:
            bid_price = market_data["price"]
        is_short_cover = decision["is_short_cover"]

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

        strategy_name = self.__class__.__name__
        order = {
            "action": decision["action"],
            "bid_price": bid_price,
            "quantity": quantity,
            "strategy": strategy_name,
            "investor": self.identity,
            "is_short_cover": is_short_cover,
            "reasoning": decision["reasoning"][:100],
            "analysis": decision["analysis"],
            "parser_fallback": parser_fallback,
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


class LLMShortSeller(LLMInvestor):
    """Short seller - manages short position risk.

    Theory: simulation-bases.md §4.1
    """

    _system_prompt = LLM_SHORT_SELLER_SYS


class LLMRetailCoordinator(LLMInvestor):
    """Retail trader - aggressive bullish buyer.

    Theory: simulation-bases.md §4.3
    """

    _system_prompt = LLM_RETAIL_COORD_SYS


class LLMMomentumBuyer(LLMInvestor):
    """Momentum trader - follows price trends.

    Theory: simulation-bases.md §4.2
    """

    _system_prompt = LLM_MOMENTUM_SYS


class LLMValueInvestor(LLMInvestor):
    """Value investor - fundamentals-focused.

    Theory: simulation-bases.md §4.4
    """

    _system_prompt = LLM_VALUE_SYS


class LLMInstitutionalHolder(LLMInvestor):
    """Large institutional holder - manages large position.

    Theory: simulation-bases.md §4.5
    """

    _system_prompt = LLM_INSTITUTIONAL_SYS


__all__ = [
    "Market",
    "LLMInvestor",
    "LLMShortSeller",
    "LLMRetailCoordinator",
    "LLMMomentumBuyer",
    "LLMValueInvestor",
    "LLMInstitutionalHolder",
]
