"""ConfirmationBias Rule-Based Simulation

Confirmation bias causes traders to seek and overweight evidence confirming their
existing beliefs, leading to polarized positions and mispricing.

Theoretical Foundation:
- Nickerson (1998): Confirmation bias — A ubiquitous phenomenon in many guises
- Lord, Ross & Lepper (1979): Biased assimilation and attitude polarization
- Rabin & Schrag (1999): First impressions matter — a model of confirmatory bias

Agents:
- Market: Price formation via net-demand + mean-reversion
- BeliefAnchor: Forms strong prior beliefs and selectively filters confirming evidence (destabilizing)
- SelectiveScanner: Seeks information supporting current position, ignores contradictions (destabilizing)
- BalancedAnalyst: Evaluates all evidence equally regardless of priors (stabilizing)
- ContrarianTrader: Looks for disconfirming evidence, trades against biased consensus (stabilizing)
- NoiseTrader: Random uninformed trader providing baseline liquidity (neutral)
"""

import logging
import random
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer

logger = logging.getLogger(__name__)


class Market(GeneralPlayer):
    """Market agent — clears orders and broadcasts price each round."""

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "price" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["price"] = float(extras["initial_price"])
            self.state.custom_state["fundamental"] = float(extras["fundamental_value"])
            self.state.custom_state["price_impact"] = float(extras["price_impact"])
            self.state.custom_state["mean_reversion"] = float(extras["mean_reversion"])
            self.state.custom_state["noise_std"] = float(extras["noise_std"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="ConfirmationBias/Market", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        orders: List[Dict] = []
        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload
                if isinstance(payload, dict):
                    orders.append(payload)

        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        buy_vol = sum(o.get("quantity", 0) for o in orders if o.get("action") == "buy")
        sell_vol = sum(
            o.get("quantity", 0) for o in orders if o.get("action") == "sell"
        )
        net_demand = buy_vol - sell_vol

        price_change = self.state.custom_state["price_impact"] * net_demand
        reversion = self.state.custom_state["mean_reversion"] * (fundamental - price)
        noise = random.gauss(0, self.state.custom_state["noise_std"])
        new_price = max(price + price_change + reversion + noise, 0.01)
        self.state.custom_state["price"] = new_price
        self.state.custom_state["price_history"].append(new_price)

        deviation = (new_price - fundamental) / fundamental if fundamental > 0 else 0.0
        self.state.custom_state["deviation"] = deviation
        logger.debug(
            "Round %d: price=%.2f deviation=%.4f",
            observation.round,
            new_price,
            deviation,
        )

    async def decide(self) -> Dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = self.state.custom_state["deviation"]
        market_data = {
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }
        return {
            "market_data": market_data,
            "outbound_messages": [
                {"payload": market_data, "content_type": "market_update"}
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        return Action(
            action_type="market_broadcast",
            payload=decision_payload,
            source_id=self.identity,
        )


class BeliefAnchor(GeneralPlayer):
    """Forms strong prior beliefs and selectively filters confirming evidence.

    Theory: Nickerson (1998) confirmation bias. Overweights information that
    confirms existing belief direction, amplifying trend.
    Role: destabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["belief"] = float(extras.get("initial_belief", 1.0))
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="ConfirmationBias/BeliefAnchor", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        belief = self.state.custom_state.get("belief", 1.0)
        extras = self.config.extras
        confirmation_strength = float(extras.get("confirmation_strength", 0.7))
        order_size = int(extras.get("order_size", 500))

        # Update belief: overweight confirming signals
        if deviation > 0 and belief > 0:
            belief = min(belief * (1 + confirmation_strength * deviation), 3.0)
        elif deviation < 0 and belief < 0:
            belief = max(belief * (1 + confirmation_strength * abs(deviation)), -3.0)
        else:
            belief = belief * 0.95 + deviation * 0.5
        self.state.custom_state["belief"] = belief

        action, quantity = "hold", 0
        if belief > 0.5:
            buy_qty = min(order_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty
        elif belief < -0.5:
            sell_qty = min(order_size, max(position, 0))
            if sell_qty > 0:
                action, quantity = "sell", sell_qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class SelectiveScanner(GeneralPlayer):
    """Seeks information supporting current position, ignores contradictions.

    Theory: Lord, Ross & Lepper (1979) biased assimilation. Filters market
    signals to amplify current position direction.
    Role: destabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="ConfirmationBias/SelectiveScanner", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        scan_threshold = float(extras.get("scan_threshold", 0.02))
        order_size = int(extras.get("order_size", 600))

        # Only act when signal confirms current position direction
        action, quantity = "hold", 0
        if deviation > scan_threshold and position >= 0:
            # Confirming bullish signal — buy more
            buy_qty = min(order_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty
        elif deviation < -scan_threshold and position >= 0:
            # Disconfirming signal while bullish — partially sell
            sell_qty = min(order_size // 2, max(position, 0))
            if sell_qty > 0:
                action, quantity = "sell", sell_qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class BalancedAnalyst(GeneralPlayer):
    """Evaluates all evidence equally regardless of prior beliefs.

    Theory: Bayesian rational updating. Processes signals without cognitive bias.
    Role: stabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="ConfirmationBias/BalancedAnalyst", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        analysis_threshold = float(extras.get("analysis_threshold", 0.05))
        order_size = int(extras.get("order_size", 400))

        action, quantity = "hold", 0
        if deviation < -analysis_threshold:
            buy_qty = min(order_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty
        elif deviation > analysis_threshold:
            sell_qty = min(order_size, max(position, 0))
            if sell_qty > 0:
                action, quantity = "sell", sell_qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class ContrarianTrader(GeneralPlayer):
    """Looks for disconfirming evidence, trades against biased consensus.

    Theory: Rabin & Schrag (1999) — rational traders exploit systematic bias errors.
    Role: stabilizing.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="ConfirmationBias/ContrarianTrader", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        deviation = market_data.get("deviation", 0.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        contrarian_threshold = float(extras.get("contrarian_threshold", 0.05))
        order_size = int(extras.get("order_size", 500))

        action, quantity = "hold", 0
        # Trade against the trend — buy when overpriced crowd will reverse, sell when unduly depressed
        if deviation > contrarian_threshold:
            sell_qty = min(order_size, max(position, 0))
            if sell_qty > 0:
                action, quantity = "sell", sell_qty
        elif deviation < -contrarian_threshold:
            buy_qty = min(order_size, int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                action, quantity = "buy", buy_qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


class NoiseTrader(GeneralPlayer):
    """Random uninformed trader providing baseline liquidity.

    Theory: Black (1986) noise trader model.
    Role: neutral.
    """

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        if "cash" not in self.state.custom_state:
            extras = self.config.extras
            self.state.custom_state["cash"] = float(extras["initial_cash"])
            self.state.custom_state["position"] = int(extras["initial_position"])
            self.state.custom_state["price_history"] = []
            self.state.custom_state["history_buffer"] = HistoryBuffer(
                folder="ConfirmationBias/NoiseTrader", entry_limit=200
            )

        self.state.custom_state["round"] = observation.round
        if observation.inbounds:
            for inb in observation.inbounds:
                data = inb.payload
                if isinstance(data, dict) and "price" in data:
                    self.state.custom_state["market_data"] = data
                    self.state.custom_state["price_history"].append(data["price"])

    async def decide(self) -> Dict:
        market_data = self.state.custom_state.get("market_data", {})
        price = market_data.get("price", 100.0)
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        extras = self.config.extras
        prob = float(extras["trade_probability"])

        action, quantity = "hold", 0
        if random.random() < prob:
            qty = random.randint(100, 500)
            side = "buy" if random.random() > 0.5 else "sell"
            if side == "buy":
                qty = min(qty, int(cash / price) if price > 0 else 0)
            else:
                qty = min(qty, max(position, 0))
            if qty > 0:
                action, quantity = side, qty

        return {
            "action": action,
            "quantity": quantity,
            "outbound_messages": [
                {
                    "payload": {"action": action, "quantity": quantity},
                    "content_type": "order",
                }
            ],
        }

    async def act(self, decision_payload: Dict) -> Action:
        action = decision_payload["action"]
        quantity = decision_payload["quantity"]
        price = self.state.custom_state.get("market_data", {}).get("price", 100.0)
        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * price
            self.state.custom_state["position"] -= quantity
        return Action(
            action_type="order", payload=decision_payload, source_id=self.identity
        )


__all__ = [
    "Market",
    "BeliefAnchor",
    "SelectiveScanner",
    "BalancedAnalyst",
    "ContrarianTrader",
    "NoiseTrader",
]
