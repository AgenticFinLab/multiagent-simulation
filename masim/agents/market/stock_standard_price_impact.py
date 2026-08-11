"""Standard price-impact stock market — canonical market coordinator.

Profile: masim/agents/defines/market/stock-standard-price-impact.md
Mechanism: Linear price-impact with mean-reversion and Gaussian noise
           (Kyle 1985 + Brock & Hommes 1998 + Roll 1984).
Broadcast: 7 fields — price, prev_price, fundamental, deviation, volume,
           net_demand, round.

Transition equation:
    P(t+1) = max(P(t) + lambda * NetDemand + gamma * (F - P(t)) + eps, price_floor)
    eps ~ N(0, sigma^2)
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

from masim.agents._coordinator_base import CanonicalMarketCoordinator


class MarketStockStandardPriceImpact(CanonicalMarketCoordinator):
    """Single-asset equity market with linear price-impact, mean-reversion,
    and Gaussian noise.

    Theoretical basis:
      - Kyle (1985): linear price-impact from net demand (lambda term).
      - Brock & Hommes (1998): mean-reversion toward fundamental (gamma term).
      - Roll (1984): idiosyncratic Gaussian microstructure noise (epsilon term).
    """

    STRATEGY = "stock-standard-price-impact"
    DISPLAY_NAME = "Standard Price-Impact Stock Market"
    SUMMARY = (
        "Linear price-impact coordinator with mean-reversion toward "
        "fundamental and Gaussian noise."
    )
    BROADCAST_FIELDS = (
        "price",
        "prev_price",
        "fundamental",
        "deviation",
        "volume",
        "net_demand",
        "round",
    )

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Initialize market state from extras.

        Required extras (raises KeyError on missing):
            initial_price, fundamental_value, price_impact (lambda),
            mean_reversion (gamma), noise_std (sigma), record_path,
            custom_state_hot_limit.
        Optional:
            price_floor (default 0.01).
        """
        # --- Required extras (KeyError propagates on missing) ---
        initial_price = extras["initial_price"]
        fundamental_value = extras["fundamental_value"]
        price_impact = extras["price_impact"]
        mean_reversion = extras["mean_reversion"]
        noise_std = extras["noise_std"]
        # record_path and custom_state_hot_limit are consumed by
        # _run_initialization in the base class, but we access them here
        # to enforce the KeyError contract.
        _ = extras["record_path"]
        _ = extras["custom_state_hot_limit"]

        # --- Optional extras ---
        price_floor = extras.get("price_floor", 0.01)

        # --- Write initial state ---
        cs = self.state.custom_state
        cs["price"] = float(initial_price)
        cs["prev_price"] = float(initial_price)
        cs["fundamental"] = float(fundamental_value)
        cs["price_impact"] = float(price_impact)
        cs["mean_reversion"] = float(mean_reversion)
        cs["noise_std"] = float(noise_std)
        cs["price_floor"] = float(price_floor)
        cs["deviation"] = 0.0

        # --- History buffer ---
        cs["price_history"] = self._make_history_buffer("price")

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's price transition and return 7-field broadcast.

        Steps:
          1. Aggregate orders (buy_qty, sell_qty, net_demand).
          2. Draw noise epsilon ~ N(0, sigma^2).
          3. Compute raw transition P_raw.
          4. Clamp to price_floor.
          5. Derive deviation and volume.
          6. Write state atomically.
          7. Return broadcast dict.
        """
        cs = self.state.custom_state

        # Read current state
        price_t = cs["price"]
        fundamental = cs["fundamental"]
        lam = cs["price_impact"]
        gamma = cs["mean_reversion"]
        sigma = cs["noise_std"]
        price_floor = cs["price_floor"]

        # 1. Aggregate orders
        agg = self._aggregate_standard_orders(orders)
        buy_qty = agg["buy_qty"]
        sell_qty = agg["sell_qty"]
        net_demand = agg["net_demand"]

        # 2. Draw noise
        eps = random.gauss(0, sigma) if sigma > 0 else 0.0

        # 3. Compute raw transition
        p_raw = price_t + lam * net_demand + gamma * (fundamental - price_t) + eps

        # 4. Floor clamp
        new_price = max(p_raw, price_floor)

        # 5. Derived observables
        if fundamental != 0.0:
            deviation = (new_price - fundamental) / fundamental
        else:
            deviation = 0.0

        volume = min(buy_qty, sell_qty) + 0.5 * abs(net_demand)

        # 6. Write state atomically (prev_price first for invariant #1)
        cs["prev_price"] = price_t
        cs["price"] = new_price
        cs["deviation"] = deviation
        cs["price_history"].append(new_price)

        # 7. Return broadcast dict
        return {
            "price": new_price,
            "prev_price": price_t,
            "fundamental": fundamental,
            "deviation": deviation,
            "volume": volume,
            "net_demand": net_demand,
            "round": round_num,
        }


__all__ = ["MarketStockStandardPriceImpact"]
