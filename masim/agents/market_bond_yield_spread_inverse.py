"""Bond Yield Spread Inverse — canonical market coordinator.

Profile: examples/AGENT_POOL/market/bond-yield-spread-inverse.md
Mechanism: Linear price-impact with fundamental-anchored mean-reversion pull
           plus a central-bank (ECB/Fed) intervention channel that discretely
           shifts the mean-reversion anchor upward when severe stress is
           detected.  Bond price is primary; yield/spread are derived by
           inversion (implied_spread = 1/P - 1).
Theoretical basis: Vasicek (1977) / CIR (1985) short-rate anchor for the
           fundamental; Duffie & Singleton (1999) default-premium channel for
           the CB intervention shift; Kyle (1985) linear price-impact; Roll
           (1984) Gaussian noise.
Broadcast: 12 fields — bond_price, prev_bond_price, price_change, fundamental,
           deviation, implied_spread, volume, num_buyers, num_sellers,
           net_demand, cb_intervention_active, round
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict, List

from masim.agents._coordinator_base import CanonicalMarketCoordinator

logger = logging.getLogger("masim.agents.coordinator.bond_spread")


class MarketBondYieldSpreadInverse(CanonicalMarketCoordinator):
    """Bond price coordinator with inverse-yield spread and CB intervention.

    Theoretical basis: Vasicek/CIR affine-term-structure mean-reversion,
    Duffie-Singleton (1999) reduced-form default-premium channel for CB
    intervention, Kyle (1985) linear price-impact, Roll (1984) Gaussian noise.
    """

    STRATEGY = "bond-yield-spread-inverse"
    DISPLAY_NAME = "Bond Yield Spread (Inverse)"
    SUMMARY = (
        "Single-issuer bond price coordinator with inverse-yield spread "
        "semantics and a central-bank intervention channel."
    )
    BROADCAST_FIELDS = (
        "bond_price",
        "prev_bond_price",
        "price_change",
        "fundamental",
        "deviation",
        "implied_spread",
        "volume",
        "num_buyers",
        "num_sellers",
        "net_demand",
        "cb_intervention_active",
        "round",
    )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Read required extras and initialize bond market state.

        Raises KeyError on any missing required parameter.
        """
        s = self.state.custom_state

        # Required extras (raise KeyError on missing)
        initial_bond_price = extras["initial_bond_price"]
        # Accept either key name for backward compatibility
        if "fundamental_price" in extras:
            fundamental_price = extras["fundamental_price"]
        elif "fundamental_value" in extras:
            fundamental_price = extras["fundamental_value"]
        else:
            raise KeyError("fundamental_price")
        initial_spread = extras["initial_spread"]
        price_impact = extras["price_impact"]
        mean_reversion_pull = extras["mean_reversion_pull"]
        # Accept either key name
        if "cb_intervention_shift" in extras:
            cb_intervention_shift = extras["cb_intervention_shift"]
        elif "intervention_bonus" in extras:
            cb_intervention_shift = extras["intervention_bonus"]
        else:
            raise KeyError("cb_intervention_shift")
        noise_std = extras["noise_std"]
        # record_path and custom_state_hot_limit already read by base class

        # Optional extras with documented defaults
        spread_floor = extras.get("spread_floor", 0.0)
        spread_cap = extras.get("spread_cap", 5.0)
        intervention_trigger = extras.get("intervention_trigger", False)

        # Initial state writes
        s["bond_price"] = float(initial_bond_price)
        s["prev_bond_price"] = float(initial_bond_price)
        s["fundamental"] = float(fundamental_price)
        s["implied_spread"] = float(initial_spread)
        s["price_change"] = 0.0
        s["deviation"] = (
            (float(initial_bond_price) - float(fundamental_price))
            / float(fundamental_price)
        )
        s["cb_intervention_active"] = 0

        # Mechanism coefficients
        s["price_impact"] = float(price_impact)
        s["mean_reversion_pull"] = float(mean_reversion_pull)
        s["cb_intervention_shift"] = float(cb_intervention_shift)
        s["noise_std"] = float(noise_std)

        # Structural parameters
        s["spread_floor"] = float(spread_floor)
        s["spread_cap"] = float(spread_cap)
        s["intervention_trigger"] = bool(intervention_trigger)

        # History buffers
        s["price_history"] = self._make_history_buffer("bond_price")
        s["fundamental_history"] = self._make_history_buffer("fundamental")
        s["spread_history"] = self._make_history_buffer("implied_spread")
        s["volume_history"] = self._make_history_buffer("volume")

    # ------------------------------------------------------------------
    # Market advance
    # ------------------------------------------------------------------

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's bond price transition and return the broadcast dict.

        Steps:
        1. Aggregate orders (buy/sell)
        2. Determine CB intervention signal
        3. Update fundamental with intervention bonus
        4. Draw noise
        5. Compute raw transition with price-impact + mean-reversion + noise
        6. Clamp to inverse-spread band
        7. Compute derived observables (price_change, deviation, implied_spread, volume)
        8. Write state
        9. Return broadcast dict
        """
        s = self.state.custom_state

        # READ current state
        P_t = s["bond_price"]
        F_t = s["fundamental"]
        lam = s["price_impact"]
        gamma = s["mean_reversion_pull"]
        b = s["cb_intervention_shift"]
        sigma = s["noise_std"]
        spread_floor = s["spread_floor"]
        spread_cap = s["spread_cap"]
        intervention_trigger = s["intervention_trigger"]

        # ----------------------------------------------------------
        # STEP 1: Aggregate orders
        # ----------------------------------------------------------
        buy_qty = 0.0
        sell_qty = 0.0
        num_buyers = 0
        num_sellers = 0
        cb_intervention_signal = False

        for o in orders:
            msg_type = o.get("type")

            # Handle CB intervention signal messages (channel a)
            if msg_type == "cb_intervention":
                if intervention_trigger:
                    if "active" not in o:
                        raise ValueError(
                            "cb_intervention message missing 'active' field: "
                            f"{o!r}. Silent-ignore would let a broken CB "
                            "signal drift into 'no intervention' by default."
                        )
                    active = o["active"]
                    if not isinstance(active, bool):
                        raise ValueError(
                            "cb_intervention 'active' must be bool, "
                            f"got {type(active).__name__}: {o!r}"
                        )
                    cb_intervention_signal = cb_intervention_signal or active
                continue

            # Handle standard orders (fail-loud on missing/malformed fields)
            if "action" not in o:
                raise ValueError(
                    "bond coordinator: order missing required 'action' "
                    f"field: {o!r}. Investor emit path must go through "
                    "masim.format.validate_order."
                )
            action = o["action"]
            if "quantity" not in o:
                raise ValueError(
                    "bond coordinator: order missing required 'quantity' "
                    f"field: {o!r}."
                )
            try:
                qty = float(o["quantity"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "bond coordinator: order 'quantity'="
                    f"{o['quantity']!r} not numeric: {o!r}."
                ) from exc

            if action == "buy" and qty > 0:
                buy_qty += qty
                num_buyers += 1
            elif action == "sell" and qty > 0:
                sell_qty += qty
                num_sellers += 1

        net_demand = buy_qty - sell_qty

        # ----------------------------------------------------------
        # STEP 2: Determine CB intervention from channel (b) or combined
        # ----------------------------------------------------------
        # Channel (b): extras mutation
        extras_cb = bool(self.config.extras.get("cb_intervention_active", False))
        # OR-combine both channels
        cb_active = cb_intervention_signal or extras_cb
        I_cb_active = 1 if cb_active else 0

        # ----------------------------------------------------------
        # STEP 3: Update fundamental with intervention bonus
        # ----------------------------------------------------------
        F_new = F_t + b * I_cb_active

        # ----------------------------------------------------------
        # STEP 4: Draw noise
        # ----------------------------------------------------------
        epsilon = random.gauss(0, sigma)

        # ----------------------------------------------------------
        # STEP 5: Compute raw price transition
        # P_raw = P(t) + lambda * NetDemand + gamma * (F(t+1) - P(t)) + epsilon
        # ----------------------------------------------------------
        P_raw = P_t + lam * net_demand + gamma * (F_new - P_t) + epsilon

        # ----------------------------------------------------------
        # STEP 6: Clamp to inverse-spread band
        # p_min = 1/(1 + spread_cap)
        # p_max = 1/(1 + spread_floor)
        # ----------------------------------------------------------
        p_min = 1.0 / (1.0 + spread_cap)
        p_max = 1.0 / (1.0 + spread_floor)
        new_price = max(min(P_raw, p_max), p_min)

        if P_raw < p_min or P_raw > p_max:
            logger.debug(
                "Bond price P_raw=%.6f clamped to [%.6f, %.6f] in round %d.",
                P_raw,
                p_min,
                p_max,
                round_num,
            )

        # ----------------------------------------------------------
        # STEP 7: Derived observables
        # ----------------------------------------------------------
        price_change = new_price - P_t
        deviation = (new_price - F_new) / F_new
        implied_spread = max(min(1.0 / new_price - 1.0, spread_cap), spread_floor)
        volume = min(buy_qty, sell_qty) + 0.5 * abs(net_demand)

        # ----------------------------------------------------------
        # STEP 8: Write state atomically
        # ----------------------------------------------------------
        s["prev_bond_price"] = P_t
        s["bond_price"] = new_price
        s["fundamental"] = F_new
        s["price_change"] = price_change
        s["deviation"] = deviation
        s["implied_spread"] = implied_spread
        s["cb_intervention_active"] = I_cb_active

        # Append to history buffers
        s["price_history"].append(new_price)
        s["fundamental_history"].append(F_new)
        s["spread_history"].append(implied_spread)
        s["volume_history"].append(volume)

        # ----------------------------------------------------------
        # STEP 9: Return broadcast dict
        # ----------------------------------------------------------
        return {
            "bond_price": new_price,
            "prev_bond_price": P_t,
            "price_change": price_change,
            "fundamental": F_new,
            "deviation": deviation,
            "implied_spread": implied_spread,
            "volume": volume,
            "num_buyers": num_buyers,
            "num_sellers": num_sellers,
            "net_demand": net_demand,
            "cb_intervention_active": I_cb_active,
            "round": round_num,
        }


__all__ = ["MarketBondYieldSpreadInverse"]
