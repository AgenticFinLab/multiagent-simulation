"""Crypto Algorithmic Stablecoin Depeg — canonical market coordinator.

Profile: examples/AGENT_POOL/market/crypto-algostable-depeg.md
Mechanism: Two-asset coupled linear price-impact + mean-reversion of stablecoin
           to peg + arbitrage-triggered mint/burn dilution + Gaussian idiosyncratic
           noise.  Models an algorithmic stablecoin (UST) redeemable for a fixed
           dollar amount of a paired governance token (LUNA) via a mint/burn
           arbitrage mechanism.
Theoretical basis: Klages-Mundt et al. (2020) algorithmic-stablecoin arbitrage-
           driven peg stability; Routledge & Zetlin-Jones (2022) reflexive
           death-spiral positive feedback; Kyle (1985) linear price-impact for
           LUNA; Roll (1984) Gaussian noise per asset.
Broadcast: 12 fields — luna_price, prev_luna_price, ust_price, prev_ust_price,
           luna_supply, prev_luna_supply, ust_depeg_amount, arb_flow_this_round,
           anchor_tvl, num_burners, num_minters, round
"""

from __future__ import annotations

import logging
import math
import random
from typing import Any, Dict, List

from masim.agents._coordinator_base import CanonicalMarketCoordinator

logger = logging.getLogger("masim.agents.coordinator.crypto_algostable")


class MarketCryptoAlgostableDepeg(CanonicalMarketCoordinator):
    """Two-asset coupled LUNA/UST coordinator with mint/burn arbitrage feedback.

    Theoretical basis: Klages-Mundt et al. (2020) bi-stability and arbitrage-
    driven peg; Routledge & Zetlin-Jones (2022) death-spiral spectral-radius
    amplification; Kyle (1985) linear price-impact for LUNA order flow;
    Roll (1984) / Corbet et al. (2019) independent Gaussian noise per asset.
    """

    STRATEGY = "crypto-algostable-depeg"
    DISPLAY_NAME = "Crypto Algostable Depeg"
    SUMMARY = (
        "Two-asset coupled LUNA/UST coordinator with arbitrage-driven "
        "mint/burn dilution and death-spiral feedback."
    )
    BROADCAST_FIELDS = (
        "luna_price",
        "prev_luna_price",
        "ust_price",
        "prev_ust_price",
        "luna_supply",
        "prev_luna_supply",
        "ust_depeg_amount",
        "arb_flow_this_round",
        "anchor_tvl",
        "num_burners",
        "num_minters",
        "round",
    )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Read required extras and initialize two-asset crypto market state.

        Raises KeyError on any missing required parameter.
        """
        s = self.state.custom_state

        # Required extras (raise KeyError on missing)
        initial_luna_price = extras["initial_luna_price"]
        initial_ust_price = extras["initial_ust_price"]
        initial_luna_supply = extras["initial_luna_supply"]
        initial_anchor_tvl = extras["initial_anchor_tvl"]
        peg_target = extras["peg_target"]
        price_impact_luna = extras["price_impact_luna"]
        price_impact_ust = extras["price_impact_ust"]
        mean_reversion_luna = extras["mean_reversion_luna"]
        mean_reversion_ust = extras["mean_reversion_ust"]
        luna_fundamental = extras["luna_fundamental"]
        arb_threshold = extras["arb_threshold"]
        arb_intensity = extras["arb_intensity"]
        anchor_deposit_rate = extras["anchor_deposit_rate"]
        noise_std = extras["noise_std"]
        # record_path and custom_state_hot_limit already read by base class

        # Optional extras with documented defaults
        luna_price_floor = extras.get("luna_price_floor", 0.001)
        ust_price_floor = extras.get("ust_price_floor", 0.001)
        luna_price_ceiling = extras.get("luna_price_ceiling", float("inf"))
        rounds_per_year = extras.get("ROUNDS_PER_YEAR", 365)

        # Initial state writes — prices and supply
        s["luna_price"] = float(initial_luna_price)
        s["prev_luna_price"] = float(initial_luna_price)
        s["ust_price"] = float(initial_ust_price)
        s["prev_ust_price"] = float(initial_ust_price)
        s["luna_supply"] = float(initial_luna_supply)
        s["prev_luna_supply"] = float(initial_luna_supply)
        s["anchor_tvl"] = float(initial_anchor_tvl)

        # Derived state
        s["ust_depeg_amount"] = 0.0
        s["arb_flow_this_round"] = 0.0
        s["num_burners"] = 0
        s["num_minters"] = 0

        # Mechanism coefficients
        s["peg_target"] = float(peg_target)
        s["price_impact_luna"] = float(price_impact_luna)
        s["price_impact_ust"] = float(price_impact_ust)
        s["mean_reversion_luna"] = float(mean_reversion_luna)
        s["mean_reversion_ust"] = float(mean_reversion_ust)
        s["luna_fundamental"] = float(luna_fundamental)
        s["arb_threshold"] = float(arb_threshold)
        s["arb_intensity"] = float(arb_intensity)
        s["anchor_deposit_rate"] = float(anchor_deposit_rate)
        s["noise_std"] = float(noise_std)
        s["initial_luna_supply"] = float(initial_luna_supply)

        # Structural parameters
        s["luna_price_floor"] = float(luna_price_floor)
        s["ust_price_floor"] = float(ust_price_floor)
        s["luna_price_ceiling"] = float(luna_price_ceiling)
        s["rounds_per_year"] = int(rounds_per_year)

        # History buffers
        s["luna_price_history"] = self._make_history_buffer("luna_price")
        s["ust_price_history"] = self._make_history_buffer("ust_price")
        s["luna_supply_history"] = self._make_history_buffer("luna_supply")
        s["anchor_tvl_history"] = self._make_history_buffer("anchor_tvl")

    # ------------------------------------------------------------------
    # Market advance
    # ------------------------------------------------------------------

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's two-asset coupled transition and return broadcast.

        This coordinator performs state writes inside advance_market (which
        corresponds to the 'decide' phase), as documented in the profile's
        deviation from the standard skill guidance.  The chained computation
        (arb_flow depends on intermediate U_raw) requires this ordering.

        Steps:
        1.  Aggregate orders across six action types
        2.  Draw noise (independent per asset)
        3.  Raw UST transition (soft peg pull)
        4.  Arbitrage trigger check
        5.  Arbitrage flow computation (conditional)
        6.  Supply update + dilution (conditional)
        7.  Final LUNA transition
        8.  Clamps + final UST
        9.  Anchor TVL update
        10. Write state
        11. Return broadcast dict
        """
        s = self.state.custom_state

        # READ current state
        L_t = s["luna_price"]
        U_t = s["ust_price"]
        S_t = s["luna_supply"]
        A_t = s["anchor_tvl"]

        # Coefficients (re-read from extras for exogenous driver boundary)
        extras = self.config.extras
        lam_L = s["price_impact_luna"]
        lam_U = s["price_impact_ust"]
        gamma_L = s["mean_reversion_luna"]
        gamma_U = s["mean_reversion_ust"]
        F_L = s["luna_fundamental"]
        peg_target = s["peg_target"]
        arb_threshold = s["arb_threshold"]
        arb_intensity = s["arb_intensity"]
        anchor_deposit_rate = s["anchor_deposit_rate"]
        sigma = s["noise_std"]
        floor_L = s["luna_price_floor"]
        floor_U = s["ust_price_floor"]
        ceil_L = s["luna_price_ceiling"]
        initial_luna_supply = s["initial_luna_supply"]
        rounds_per_year = s["rounds_per_year"]

        # Re-read mutable extras (Exogenous Driver Boundary channel b)
        if "anchor_deposit_rate" in extras:
            anchor_deposit_rate = float(extras["anchor_deposit_rate"])
            s["anchor_deposit_rate"] = anchor_deposit_rate
        if "luna_fundamental" in extras:
            F_L = float(extras["luna_fundamental"])
            s["luna_fundamental"] = F_L
        if "arb_threshold" in extras:
            arb_threshold = float(extras["arb_threshold"])
            s["arb_threshold"] = arb_threshold

        # lambda_U_arb defaults to lambda_U per profile
        lam_U_arb = lam_U

        # ----------------------------------------------------------
        # STEP 1: Aggregate orders across six action types
        # ----------------------------------------------------------
        buy_luna_qty = 0.0
        sell_luna_qty = 0.0
        mint_ust_qty = 0.0
        burn_ust_qty = 0.0
        deposit_anchor_qty = 0.0
        withdraw_anchor_qty = 0.0
        num_burners = 0
        num_minters = 0

        _VALID_ACTIONS = {
            "buy_luna", "sell_luna", "mint_ust", "burn_ust",
            "deposit_anchor", "withdraw_anchor", "hold",
        }
        for o in orders:
            if "action_type" not in o:
                raise ValueError(
                    "crypto coordinator: order missing required "
                    f"'action_type': {o!r}. Silent-default to hold would "
                    "zero out demand."
                )
            action_type = o["action_type"]
            if action_type not in _VALID_ACTIONS:
                raise ValueError(
                    "crypto coordinator: unknown "
                    f"action_type={action_type!r}. Valid: "
                    f"{sorted(_VALID_ACTIONS)}. Order: {o!r}"
                )

            if "size" not in o:
                raise ValueError(
                    "crypto coordinator: order missing required "
                    f"'size' field: {o!r}"
                )
            try:
                size = float(o["size"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "crypto coordinator: order 'size'="
                    f"{o['size']!r} not numeric: {o!r}"
                ) from exc

            if size < 0:
                raise ValueError(
                    "crypto coordinator: negative order size "
                    f"{size} is disallowed: {o!r}"
                )

            if action_type == "buy_luna":
                buy_luna_qty += size
            elif action_type == "sell_luna":
                sell_luna_qty += size
            elif action_type == "mint_ust":
                mint_ust_qty += size
                num_minters += 1
            elif action_type == "burn_ust":
                burn_ust_qty += size
                num_burners += 1
            elif action_type == "deposit_anchor":
                deposit_anchor_qty += size
            elif action_type == "withdraw_anchor":
                withdraw_anchor_qty += size
            elif action_type == "hold":
                pass

        net_demand_luna = buy_luna_qty - sell_luna_qty
        net_demand_ust = mint_ust_qty - burn_ust_qty

        # ----------------------------------------------------------
        # STEP 2: Draw noise (independent per asset)
        # ----------------------------------------------------------
        epsilon_L = random.gauss(0, sigma)
        epsilon_U = random.gauss(0, sigma)

        # ----------------------------------------------------------
        # STEP 3: Raw UST transition (soft peg pull only)
        # U_raw = U(t) + lambda_U * NetD_U + gamma_U * (peg - U(t)) + epsilon_U
        # ----------------------------------------------------------
        U_raw = U_t + lam_U * net_demand_ust + gamma_U * (peg_target - U_t) + epsilon_U

        # ----------------------------------------------------------
        # STEP 4: Arbitrage trigger check
        # ----------------------------------------------------------
        arb_flow = 0.0
        new_luna_minted = 0.0
        luna_burnt = 0.0
        dilution = 0.0
        L_after_dilution = L_t

        if abs(U_raw - peg_target) > arb_threshold:
            # ----------------------------------------------------------
            # STEP 5: Arbitrage flow computation
            # arb_flow = arb_intensity * (peg_target - U_raw) + burn_ust_qty - mint_ust_qty
            # Positive = net UST minted (peg above); negative = net UST burned
            # ----------------------------------------------------------
            arb_flow = (
                arb_intensity * (peg_target - U_raw)
                + burn_ust_qty
                - mint_ust_qty
            )

            # ----------------------------------------------------------
            # STEP 6: Supply update + dilution (conditional)
            # ----------------------------------------------------------
            if arb_flow < 0:
                # Net UST burn -> mint LUNA (death-spiral leg)
                new_luna_minted = abs(arb_flow) / max(L_t, floor_L)
                S_new = S_t + new_luna_minted
                dilution = new_luna_minted / S_t if S_t > 0 else 0.0
                L_after_dilution = L_t * (1.0 - dilution)
            elif arb_flow > 0:
                # Net UST mint -> burn LUNA
                luna_burnt = arb_flow / max(L_t, floor_L)
                S_new = max(S_t - luna_burnt, initial_luna_supply)
                dilution = 0.0
                L_after_dilution = L_t
            else:
                S_new = S_t
                dilution = 0.0
                L_after_dilution = L_t
        else:
            # Arbitrage dormant
            S_new = S_t
            L_after_dilution = L_t

        # Log supply hyperinflation warning
        if S_new / initial_luna_supply > 100:
            logger.warning(
                "LUNA supply hyperinflation: S/S(0) = %.1f in round %d.",
                S_new / initial_luna_supply,
                round_num,
            )

        # ----------------------------------------------------------
        # STEP 7: Final LUNA transition
        # L_raw = L_after_dilution + lambda_L * NetD_L + gamma_L * (F_L - L_after_dilution) + epsilon_L
        # ----------------------------------------------------------
        L_raw = (
            L_after_dilution
            + lam_L * net_demand_luna
            + gamma_L * (F_L - L_after_dilution)
            + epsilon_L
        )

        # ----------------------------------------------------------
        # STEP 8: Clamps + final UST
        # ----------------------------------------------------------
        L_new = max(min(L_raw, ceil_L), floor_L)
        U_new = max(U_raw + arb_flow * lam_U_arb, floor_U)

        # Derived observables
        ust_depeg_amount = U_new - peg_target

        # ----------------------------------------------------------
        # STEP 9: Anchor TVL update
        # A(t+1) = max(A(t) + deposit - min(withdraw, A(t)) + A(t)*rate/RPY, 0)
        # ----------------------------------------------------------
        actual_withdraw = min(withdraw_anchor_qty, A_t)
        if withdraw_anchor_qty > A_t:
            logger.warning(
                "Withdraw %.2f exceeds Anchor TVL %.2f; clamping.",
                withdraw_anchor_qty,
                A_t,
            )
        yield_accrual = A_t * anchor_deposit_rate / rounds_per_year
        A_new = max(A_t + deposit_anchor_qty - actual_withdraw + yield_accrual, 0.0)

        # ----------------------------------------------------------
        # STEP 10: Validate — raise ValueError on NaN/Inf
        # ----------------------------------------------------------
        for name, val in [
            ("luna_price", L_new),
            ("ust_price", U_new),
            ("luna_supply", S_new),
            ("anchor_tvl", A_new),
        ]:
            if math.isnan(val) or math.isinf(val):
                raise ValueError(
                    f"[{self.identity}] {name} is {val} in round {round_num}; aborting."
                )
        if S_new < 0:
            raise ValueError(
                f"[{self.identity}] luna_supply is negative ({S_new}) "
                f"in round {round_num}; aborting."
            )

        # ----------------------------------------------------------
        # STEP 11: Write state atomically (prev before current)
        # ----------------------------------------------------------
        s["prev_luna_price"] = L_t
        s["luna_price"] = L_new
        s["prev_ust_price"] = U_t
        s["ust_price"] = U_new
        s["prev_luna_supply"] = S_t
        s["luna_supply"] = S_new
        s["anchor_tvl"] = A_new
        s["ust_depeg_amount"] = ust_depeg_amount
        s["arb_flow_this_round"] = arb_flow
        s["num_burners"] = num_burners
        s["num_minters"] = num_minters

        # Append to history buffers
        s["luna_price_history"].append(L_new)
        s["ust_price_history"].append(U_new)
        s["luna_supply_history"].append(S_new)
        s["anchor_tvl_history"].append(A_new)

        # ----------------------------------------------------------
        # STEP 12: Return broadcast dict
        # ----------------------------------------------------------
        return {
            "luna_price": L_new,
            "prev_luna_price": L_t,
            "ust_price": U_new,
            "prev_ust_price": U_t,
            "luna_supply": S_new,
            "prev_luna_supply": S_t,
            "ust_depeg_amount": ust_depeg_amount,
            "arb_flow_this_round": arb_flow,
            "anchor_tvl": A_new,
            "num_burners": num_burners,
            "num_minters": num_minters,
            "round": round_num,
        }


__all__ = ["MarketCryptoAlgostableDepeg"]
