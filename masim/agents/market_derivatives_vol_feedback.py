"""Derivatives Vol-Feedback — canonical market coordinator.

Profile: masim/agents/defines/market/derivatives-vol-feedback.md
Mechanism: Two-asset coupled VIX (implied-vol index) and XIV (inverse-vol ETN)
    coordinator with short-gamma hedging-flow feedback.  When |delta_V/V| exceeds
    a rebalance threshold, ETN issuers must buy volatility, amplifying the move
    (Cheng 2019; Bhansali & Harris 2018).  A one-way NAV-floor termination latch
    permanently extinguishes the XIV leg when its NAV drops below a prospectus-
    defined fraction of initial price (SEC 2018 XIV acceleration clause).
Broadcast: 14 fields — vix_level, prev_vix_level, xiv_price, prev_xiv_price,
    xiv_notional, prev_xiv_notional, hedge_flow_this_round, xiv_nav_status,
    num_vol_buyers, num_vol_sellers, net_vol_demand, num_hedgers, terminated, round
"""

from __future__ import annotations

import logging
import math
import random
from typing import Any, Dict, List

from masim.agents._coordinator_base import CanonicalMarketCoordinator

logger = logging.getLogger("masim.agents.market_derivatives_vol_feedback")


class MarketDerivativesVolFeedback(CanonicalMarketCoordinator):
    """Two-asset coupled VIX/XIV coordinator with short-gamma hedging-flow feedback.

    Theoretical basis: Black-Scholes-Merton 1973 (ETN NAV linkage to vol),
    Duffie & Pan 1997 (gamma/vega risk decomposition and hedge-flow sign),
    Kyle 1985 (linear price-impact), Cheng 2019 (reflexive short-vol feedback
    and NAV-floor termination), Bhansali & Harris 2018 (crowded short-vol
    amplification), Roll 1984 (Gaussian idiosyncratic noise).
    """

    STRATEGY = "derivatives-vol-feedback"
    DISPLAY_NAME = "Derivatives Vol-Feedback"
    SUMMARY = (
        "Two-asset coupled VIX/XIV coordinator with short-gamma "
        "hedging-flow reflexive feedback and NAV-floor termination latch."
    )
    BROADCAST_FIELDS = (
        "vix_level",
        "prev_vix_level",
        "xiv_price",
        "prev_xiv_price",
        "xiv_notional",
        "prev_xiv_notional",
        "hedge_flow_this_round",
        "xiv_nav_status",
        "num_vol_buyers",
        "num_vol_sellers",
        "net_vol_demand",
        "num_hedgers",
        "terminated",
        "round",
    )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Read required extras and initialize all state variables."""
        s = self.state.custom_state

        # Required extras (raise KeyError on missing)
        initial_vix = extras["initial_vix"]
        initial_xiv_price = extras["initial_xiv_price"]
        initial_xiv_notional = extras["initial_xiv_notional"]
        vol_mean_reversion_target = extras["vol_mean_reversion_target"]
        price_impact_vix = extras["price_impact_vix"]
        price_impact_xiv = extras["price_impact_xiv"]
        vol_mean_reversion_pull = extras["vol_mean_reversion_pull"]
        hedge_flow_coefficient = extras["hedge_flow_coefficient"]
        rebalance_threshold = extras["rebalance_threshold"]
        nav_floor_frac = extras["nav_floor_frac"]
        leverage_inverse_k = extras["leverage_inverse_k"]
        noise_std_vix = extras["noise_std_vix"]
        noise_std_xiv = extras["noise_std_xiv"]

        # Validate leverage_inverse_k
        if leverage_inverse_k < 0:
            raise ValueError(
                f"leverage_inverse_k must be >= 0, got {leverage_inverse_k}"
            )

        # Optional extras with documented defaults
        vix_floor = extras.get("vix_floor", 1.0)
        vix_ceiling = extras.get("vix_ceiling", float("inf"))
        xiv_price_floor = extras.get("xiv_price_floor", 0.01)
        hedge_flow_application_coefficient = extras.get(
            "hedge_flow_application_coefficient", 1.0
        )

        # Cache parameters
        s["_vol_mean_reversion_target"] = vol_mean_reversion_target
        s["_price_impact_vix"] = price_impact_vix
        s["_price_impact_xiv"] = price_impact_xiv
        s["_vol_mean_reversion_pull"] = vol_mean_reversion_pull
        s["_hedge_flow_coefficient"] = hedge_flow_coefficient
        s["_rebalance_threshold"] = rebalance_threshold
        s["_nav_floor_frac"] = nav_floor_frac
        s["_leverage_inverse_k"] = leverage_inverse_k
        s["_noise_std_vix"] = noise_std_vix
        s["_noise_std_xiv"] = noise_std_xiv
        s["_vix_floor"] = vix_floor
        s["_vix_ceiling"] = vix_ceiling
        s["_xiv_price_floor"] = xiv_price_floor
        s["_hedge_flow_application_coefficient"] = hedge_flow_application_coefficient
        s["_initial_xiv_price"] = initial_xiv_price

        # State variables (cold-start: prev == current)
        s["vix_level"] = initial_vix
        s["prev_vix_level"] = initial_vix
        s["xiv_price"] = initial_xiv_price
        s["prev_xiv_price"] = initial_xiv_price
        s["xiv_notional"] = initial_xiv_notional
        s["prev_xiv_notional"] = initial_xiv_notional
        s["hedge_flow_this_round"] = 0.0
        s["xiv_nav_status"] = "normal"
        s["num_vol_buyers"] = 0
        s["num_vol_sellers"] = 0
        s["net_vol_demand"] = 0.0
        s["num_hedgers"] = 0
        s["terminated"] = False

        # History buffers
        s["_vix_level_history"] = self._make_history_buffer("vix_level")
        s["_xiv_price_history"] = self._make_history_buffer("xiv_price")
        s["_xiv_notional_history"] = self._make_history_buffer("xiv_notional")
        s["_hedge_flow_history"] = self._make_history_buffer("hedge_flow")

    # ------------------------------------------------------------------
    # Market advance
    # ------------------------------------------------------------------

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute the two-state coupled transition and return 14-field broadcast."""
        s = self.state.custom_state

        # Read current state
        V_t = s["vix_level"]
        X_t = s["xiv_price"]
        N_t = s["xiv_notional"]
        terminated_t = s["terminated"]

        # Read cached parameters
        V_bar = s["_vol_mean_reversion_target"]
        lambda_v = s["_price_impact_vix"]
        lambda_x = s["_price_impact_xiv"]
        gamma_v = s["_vol_mean_reversion_pull"]
        phi = s["_hedge_flow_coefficient"]
        rebalance_threshold = s["_rebalance_threshold"]
        nav_floor_frac = s["_nav_floor_frac"]
        k = s["_leverage_inverse_k"]
        sigma_v = s["_noise_std_vix"]
        sigma_x = s["_noise_std_xiv"]
        vix_floor = s["_vix_floor"]
        vix_ceiling = s["_vix_ceiling"]
        xiv_price_floor = s["_xiv_price_floor"]
        phi_apply = s["_hedge_flow_application_coefficient"]
        X_0 = s["_initial_xiv_price"]

        # ------------------------------------------------------------------
        # Step 2: Aggregate orders
        # ------------------------------------------------------------------
        buy_xiv_qty = 0.0
        sell_xiv_qty = 0.0
        long_vol_qty = 0.0
        short_vol_qty = 0.0
        hedge_qty = 0.0
        num_vol_buyers = 0
        num_vol_sellers = 0
        num_hedgers = 0

        _VALID_ACTIONS = {
            "buy_xiv",
            "sell_xiv",
            "long_vol",
            "short_vol",
            "hedge",
            "hold",
        }

        for o in orders:
            if "action_type" not in o:
                raise ValueError(
                    f"Investor order missing required 'action_type' field: {o!r}"
                )
            action_type = o["action_type"]
            if action_type not in _VALID_ACTIONS:
                raise ValueError(
                    f"Unknown action_type {action_type!r} for derivatives-vol-feedback "
                    f"coordinator; valid actions are {sorted(_VALID_ACTIONS)}."
                )
            if "size" not in o:
                raise ValueError(
                    f"Investor order missing required 'size' field: {o!r}"
                )
            try:
                size = float(o["size"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Investor order has non-numeric size {o['size']!r}: {o!r}"
                ) from exc
            if size < 0:
                raise ValueError(
                    f"Investor order has negative size {size}: {o!r}"
                )

            # Post-termination: XIV orders become no-ops (documented mechanism,
            # not a defensive fallback).  Only affects XIV buy/sell after the
            # depeg termination event has fired; agent may still emit them
            # because the broadcast lags by one round.
            if terminated_t and action_type in ("buy_xiv", "sell_xiv"):
                logger.debug(
                    "XIV order after termination; converting to no-op: %r", o
                )
                continue

            if action_type == "buy_xiv":
                buy_xiv_qty += size
            elif action_type == "sell_xiv":
                sell_xiv_qty += size
            elif action_type == "long_vol":
                long_vol_qty += size
                num_vol_buyers += 1
            elif action_type == "short_vol":
                short_vol_qty += size
                num_vol_sellers += 1
            elif action_type == "hedge":
                hedge_qty += size
                num_vol_buyers += 1
                num_hedgers += 1
            elif action_type == "hold":
                pass

        net_demand_xiv = buy_xiv_qty - sell_xiv_qty
        net_vol_demand = long_vol_qty + hedge_qty - short_vol_qty

        # ------------------------------------------------------------------
        # Step 3: Draw noise
        # ------------------------------------------------------------------
        eps_v = random.gauss(0, sigma_v) if sigma_v > 0 else 0.0
        eps_x = random.gauss(0, sigma_x) if sigma_x > 0 else 0.0

        # ------------------------------------------------------------------
        # Step 4: Raw VIX transition (no hedge feedback yet)
        # ------------------------------------------------------------------
        V_raw = V_t + lambda_v * net_vol_demand + gamma_v * (V_bar - V_t) + eps_v

        # ------------------------------------------------------------------
        # Step 5: Rebalance-threshold check
        # ------------------------------------------------------------------
        delta_raw = (V_raw - V_t) / V_t if V_t > 0 else 0.0
        hedge_flow_t = 0.0

        if abs(delta_raw) > rebalance_threshold and not terminated_t:
            # ------------------------------------------------------------------
            # Step 6: Hedge flow computation
            # ------------------------------------------------------------------
            excess = abs(delta_raw) - rebalance_threshold
            sign_delta = 1.0 if delta_raw > 0 else -1.0
            hedge_flow_t = phi * N_t * excess * sign_delta / V_t

            # Defensive cap: |hedge_flow| <= 10 * N(t) / V(t)
            cap = 10.0 * N_t / V_t if V_t > 0 else float("inf")
            if abs(hedge_flow_t) > cap:
                logger.warning(
                    "Hedge flow %.2f exceeds defensive cap %.2f; clamping.",
                    hedge_flow_t,
                    cap,
                )
                hedge_flow_t = cap * sign_delta

            # ------------------------------------------------------------------
            # Step 7: Feedback-augmented vol
            # ------------------------------------------------------------------
            V_next_raw = V_raw + phi_apply * hedge_flow_t
        else:
            V_next_raw = V_raw

        # ------------------------------------------------------------------
        # Step 8: Clamp VIX
        # ------------------------------------------------------------------
        V_next = max(vix_floor, min(V_next_raw, vix_ceiling))

        # ------------------------------------------------------------------
        # Step 9: XIV leverage-inverse coupling
        # ------------------------------------------------------------------
        delta_realised = (V_next - V_t) / V_t if V_t > 0 else 0.0
        X_lev = X_t * (1.0 - k * delta_realised)

        # ------------------------------------------------------------------
        # Step 10: XIV price-impact + noise
        # ------------------------------------------------------------------
        X_raw = X_lev + lambda_x * net_demand_xiv + eps_x

        # ------------------------------------------------------------------
        # Step 11: NAV-floor termination check
        # ------------------------------------------------------------------
        if terminated_t:
            # Already terminated: freeze XIV price
            X_next = X_t
            terminated_next = True
            xiv_nav_status = "terminated"
        elif X_raw < X_0 * nav_floor_frac:
            # Termination triggered this round
            X_next = max(X_raw, xiv_price_floor)
            terminated_next = True
            xiv_nav_status = "triggered"
        else:
            X_next = max(X_raw, xiv_price_floor)
            terminated_next = False
            if X_next < 0.5 * X_0:
                xiv_nav_status = "warning"
            else:
                xiv_nav_status = "normal"

        # ------------------------------------------------------------------
        # Step 12: Notional update
        # ------------------------------------------------------------------
        if terminated_next and not terminated_t:
            # Legal extinguishment at termination settlement
            N_next = 0.0
        elif terminated_t:
            # Remains zero after termination
            N_next = 0.0
        else:
            wear = 0.001 * abs(hedge_flow_t) * V_t
            N_next = max(N_t + lambda_x * net_demand_xiv * V_t - wear, 0.0)

        # ------------------------------------------------------------------
        # Validate
        # ------------------------------------------------------------------
        for name, val in [
            ("vix_level", V_next),
            ("xiv_price", X_next),
            ("xiv_notional", N_next),
        ]:
            if math.isnan(val) or math.isinf(val):
                raise ValueError(
                    f"[{self.identity}] {name} is {val} in round {round_num}"
                )
        if N_next < 0:
            raise ValueError(
                f"[{self.identity}] xiv_notional < 0 in round {round_num}"
            )

        # ------------------------------------------------------------------
        # Step 13: Write state
        # ------------------------------------------------------------------
        s["prev_vix_level"] = V_t
        s["vix_level"] = V_next
        s["prev_xiv_price"] = X_t
        s["xiv_price"] = X_next
        s["prev_xiv_notional"] = N_t
        s["xiv_notional"] = N_next
        s["hedge_flow_this_round"] = hedge_flow_t
        s["xiv_nav_status"] = xiv_nav_status
        s["num_vol_buyers"] = num_vol_buyers
        s["num_vol_sellers"] = num_vol_sellers
        s["net_vol_demand"] = net_vol_demand
        s["num_hedgers"] = num_hedgers
        s["terminated"] = terminated_next

        # Append to history buffers
        s["_vix_level_history"].append(V_next)
        s["_xiv_price_history"].append(X_next)
        s["_xiv_notional_history"].append(N_next)
        s["_hedge_flow_history"].append(hedge_flow_t)

        # ------------------------------------------------------------------
        # Step 14: Return broadcast dict
        # ------------------------------------------------------------------
        return {
            "vix_level": V_next,
            "prev_vix_level": V_t,
            "xiv_price": X_next,
            "prev_xiv_price": X_t,
            "xiv_notional": N_next,
            "prev_xiv_notional": N_t,
            "hedge_flow_this_round": hedge_flow_t,
            "xiv_nav_status": xiv_nav_status,
            "num_vol_buyers": num_vol_buyers,
            "num_vol_sellers": num_vol_sellers,
            "net_vol_demand": net_vol_demand,
            "num_hedgers": num_hedgers,
            "terminated": terminated_next,
            "round": round_num,
        }


__all__ = ["MarketDerivativesVolFeedback"]
