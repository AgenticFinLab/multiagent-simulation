import random
import logging
from masim.player.base import Action

"""LossAversion Rule-Based Simulation

Loss aversion from prospect theory causes investors to hold losers too long and sell winners too early

Theoretical Foundation:
- Kahneman & Tversky (1979): Prospect Theory
- Tversky & Kahneman (1992): Cumulative Prospect Theory
- Odean (1998): Are investors reluctant to realize their losses?

Key Dynamics:
- LossAverseInvestor: Values losses 2-2.5x more than gains, holds losers, sells winners
- BreakEvenTrader: Takes excessive risk to get back to break-even
- RationalTrader: Makes decisions based on expected utility without bias
- MomentumTrader: Follows price trends
- MarketMaker: Provides liquidity and earns spread

Parameters from config (see configs/LossAversion/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("LossAversion")


class Market(GeneralPlayer):
    """
    Market agent for LossAversion simulation.
    
    Price Formation Model:
        P(t+1) = P(t) + λ × NetDemand + γ × (F - P(t)) + ε
    
    Where:
        - λ: Price impact coefficient
        - γ: Mean reversion strength  
        - F: Fundamental value
        - ε: Random noise
    """
    async def perceive(
        self,
        observation,
        prev_result=None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num
        
        if "price" not in self.state.custom_state:
            self._initialize_market_state()
        
        orders = self._extract_orders(observation)
        market_result = self._clear_market(orders)
        self._update_state(market_result)
        self._log_market_state()
    
    def _initialize_market_state(self) -> None:
        extras = self.config.extras
        self.state.custom_state["price"] = extras["initial_price"]
        self.state.custom_state["fundamental"] = extras["fundamental_value"]
        self.state.custom_state["price_history"] = []
        self.state.custom_state["volume_history"] = []
        
        self.state.custom_state["price_impact"] = extras["price_impact"]
        self.state.custom_state["mean_reversion"] = extras["mean_reversion"]
        self.state.custom_state["noise_std"] = extras["noise_std"]
    
    def _extract_orders(self, observation) -> list:
        orders = []
        for msg in observation.messages:
            if msg.get("type") == "order":
                orders.append({
                    "agent_id": msg.get("from"),
                    "action": msg.get("action"),
                    "quantity": msg.get("quantity"),
                    "agent_type": msg.get("agent_type"),
                })
        return orders
    
    def _clear_market(self, orders: list) -> dict:
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        
        buy_orders = [o for o in orders if o["action"] == "buy"]
        sell_orders = [o for o in orders if o["action"] == "sell"]
        total_buy = sum(o["quantity"] for o in buy_orders)
        total_sell = sum(o["quantity"] for o in sell_orders)
        net_demand = total_buy - total_sell
        
        price_impact = self.state.custom_state["price_impact"]
        mean_reversion = self.state.custom_state["mean_reversion"]
        noise_std = self.state.custom_state["noise_std"]
        
        price_change = price_impact * net_demand
        reversion = mean_reversion * (fundamental - price)
        noise = random.gauss(0, noise_std)
        
        new_price = price + price_change + reversion + noise
        new_price = max(new_price, 0.01)
        
        volume = min(total_buy, total_sell) + abs(net_demand) * 0.5
        
        return {
            "price": new_price,
            "volume": volume,
            "net_demand": net_demand,
        }
    
    def _update_state(self, market_result: dict) -> None:
        self.state.custom_state["price"] = market_result["price"]
        self.state.custom_state["price_history"].append(market_result["price"])
        self.state.custom_state["volume_history"].append(market_result["volume"])
    
    def _log_market_state(self) -> None:
        logger = logging.getLogger("{name}")
        logger.debug(
            "Round %%d: price=%%.2f",
            self.state.custom_state["round"],
            self.state.custom_state["price"],
        )
    
    async def step(self):
        price = self.state.custom_state["price"]
        fundamental = self.state.custom_state["fundamental"]
        deviation = (price - fundamental) / fundamental if fundamental > 0 else 0
        
        market_update = {
            "type": "market_update",
            "price": price,
            "fundamental": fundamental,
            "deviation": deviation,
            "round": self.state.custom_state["round"],
        }
        
        return Action(
            action_type="market_broadcast",
            payload={"market_data": market_update, "outbound_messages": [{"payload": market_update, "content_type": "market_update"}]},
            source_id=self.identity,
        )


    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Loss averse: values losses 2.25x more than gains (prospect theory).
        
        Sells winners too early (deviation > sell_gain_threshold) and
        holds losers too long (reluctant to realize losses).
        """
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        loss_lambda = extras["loss_aversion_lambda"]
        sell_gain = extras["sell_gain_threshold"]
        
        entry_price = self.state.custom_state["entry_price"]
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl_pct > sell_gain:
            sell_qty = min(max(position, 0), int(position * 0.7))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        elif pnl_pct < -sell_gain * loss_lambda:
            sell_qty = min(max(position, 0), int(position * 0.2))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Break-even effect: takes excessive risk to get back to break-even."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_increase = extras["risk_increase_factor"]
        
        entry_price = self.state.custom_state["entry_price"]
        pnl_pct = (price - entry_price) / entry_price if entry_price > 0 else 0
        
        if pnl_pct < -0.05:
            risky_qty = min(int(abs(pnl_pct) * risk_increase * 5000), int(cash / price) if price > 0 else 0)
            if risky_qty > 0:
                return {"action": "buy", "quantity": risky_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Rational: makes decisions based on expected utility."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_aversion = extras["risk_aversion"]
        
        if abs(deviation) > 0.03:
            qty = min(500, int(abs(deviation) * risk_aversion * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Momentum following."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras["entry_threshold"]
        
        if abs(deviation) > entry_threshold:
            qty = min(500, int(abs(deviation) * 3000))
            if deviation > 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Market making: provides liquidity."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        inventory_limit = extras["inventory_limit"]
        
        if abs(position) < inventory_limit:
            qty = 300
            if deviation > 0:
                return {"action": "sell", "quantity": min(qty, max(position, 0))}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "LossAverseInvestor", "BreakEvenTrader", "RationalTrader", "MomentumTrader", "MarketMaker"]
