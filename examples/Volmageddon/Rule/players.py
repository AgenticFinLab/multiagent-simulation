import random
import logging
from masim.player.base import Action

"""Volmageddon Rule-Based Simulation

February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours trading

Theoretical Foundation:
- Volatility product feedback (Bergsma & Jiang, 2022)
- Short volatility crowding (Culp et al., 2018)
- Inverse VIX ETN dynamics

Key Dynamics:
- ShortVolTrader: Sells VIX futures/ETNs, profits from contango but faces tail risk
- VolETNManager: Must buy VIX futures when VIX rises, creating positive feedback
- LongVolHedger: Holds long VIX positions as portfolio hedge
- VolArbitrageur: Trades VIX term structure dislocations
- EquityTrader: Trades equities, affected by volatility spike

Parameters from config (see configs/Volmageddon/Rule/players.yml):
"""

from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer

logger = logging.getLogger("Volmageddon")


class Market(GeneralPlayer):
    """
    Market agent for Volmageddon simulation.
    
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
        """Short volatility: profits from contango, faces tail risk."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        stop_loss = extras["stop_loss"]
        
        if deviation > stop_loss:
            buy_qty = min(abs(position), int(abs(position) * 0.8))
            if buy_qty > 0 and position < 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation < -0.02:
            sell_qty = min(1000, int(cash / price) if price > 0 else 0)
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Inverse VIX ETN: must buy VIX futures when VIX rises (positive feedback)."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        rebalance_threshold = extras["rebalance_threshold"]
        rebalance_size = extras["rebalance_size"]
        
        if deviation > rebalance_threshold:
            buy_qty = min(int(deviation * rebalance_size), int(cash / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Long vol hedge: holds VIX for portfolio insurance."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        hedge_ratio = extras["hedge_ratio"]
        
        if deviation < -0.05:
            buy_qty = min(500, int(cash * hedge_ratio / price) if price > 0 else 0)
            if buy_qty > 0:
                return {"action": "buy", "quantity": buy_qty}
        elif deviation > 0.1:
            sell_qty = min(500, max(position, 0))
            if sell_qty > 0:
                return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """VIX term structure arbitrage."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        entry_threshold = extras["entry_threshold"]
        
        if abs(deviation) > entry_threshold:
            qty = min(5000, int(abs(deviation) * 20000))
            if deviation > 0:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
            else:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
        return {"action": "hold", "quantity": 0}

    def _make_decision(self, price: float, fundamental: float, deviation: float) -> dict:
        """Basic equity trading."""
        extras = self.config.extras
        cash = self.state.custom_state["cash"]
        position = self.state.custom_state["position"]
        risk_limit = extras["risk_limit"]
        
        if abs(deviation) > risk_limit * 2:
            qty = min(1000, int(abs(deviation) * 3000))
            if deviation < 0:
                buy_qty = min(qty, int(cash / price) if price > 0 else 0)
                if buy_qty > 0:
                    return {"action": "buy", "quantity": buy_qty}
            else:
                sell_qty = min(qty, max(position, 0))
                if sell_qty > 0:
                    return {"action": "sell", "quantity": sell_qty}
        return {"action": "hold", "quantity": 0}


__all__ = ["Market", "ShortVolTrader", "VolETNManager", "LongVolHedger", "VolArbitrageur", "EquityTrader"]
