"""FX Currency Peg and Attack — canonical market coordinator.

Profile: examples/AGENT_POOL/market/fx-currency-peg-and-attack.md
Mechanism: Linear price-impact + intervention-boosted mean-reversion around
           an official peg with finite reserve-financed defense and regime
           switch on reserve depletion.  Based on Krugman (1979) first-generation
           balance-of-payments crisis, Obstfeld (1996) escape-clause mean-reversion,
           and Kyle (1985) linear price-impact adapted to spot FX via
           Evans & Lyons (2002).
Broadcast: 12 fields — exchange_rate, prev_exchange_rate, fundamental, peg_rate,
           deviation, volume, net_pressure, reserves, peg_status, num_attackers,
           num_defenders, round
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict, List

from masim.agents._coordinator_base import CanonicalMarketCoordinator

logger = logging.getLogger("masim.agents.coordinator.fx_peg")


class MarketFxCurrencyPegAndAttack(CanonicalMarketCoordinator):
    """FX rate coordinator with reserves ledger and regime-switching peg defense.

    Theoretical basis: Krugman (1979) reserves-depletion regime switch,
    Obstfeld (1996) contingent escape-clause gamma-boost, Kyle (1985) linear
    price impact adapted to FX via Evans & Lyons (2002), Gaussian noise
    per Roll (1984) / Bessembinder (1994).
    """

    STRATEGY = "fx-currency-peg-and-attack"
    DISPLAY_NAME = "FX Currency Peg & Attack"
    SUMMARY = (
        "Single-pair FX coordinator with official peg, finite reserves "
        "defense, and regime-switching mean-reversion."
    )
    BROADCAST_FIELDS = (
        "exchange_rate",
        "prev_exchange_rate",
        "fundamental",
        "peg_rate",
        "deviation",
        "volume",
        "net_pressure",
        "reserves",
        "peg_status",
        "num_attackers",
        "num_defenders",
        "round",
    )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Read required extras and initialize FX market state.

        Raises KeyError on any missing required parameter.
        """
        s = self.state.custom_state

        # Required extras (raise KeyError on missing)
        initial_rate = extras["initial_exchange_rate"]
        fundamental_rate = extras["fundamental_rate"]
        peg_rate = extras["peg_rate"]
        price_impact = extras["price_impact"]
        mean_reversion_pull = extras["mean_reversion_pull"]
        reserves_initial = extras["reserves_initial"]
        cb_intervention_threshold = extras["cb_intervention_threshold"]
        noise_std = extras["noise_std"]
        # record_path and custom_state_hot_limit already read by base class

        # Optional extras with documented defaults
        rate_floor = extras.get("rate_floor", 0.01)
        reserves_floor = extras.get("reserves_floor", 0.0)
        peg_band = extras.get("peg_band", 0.05)
        intervention_normaliser = extras.get("intervention_normaliser", 1000.0)
        gamma_post_break = extras.get("gamma_post_break", mean_reversion_pull)
        attack_threshold = extras.get("attack_threshold", 0.02)

        # Initial state writes
        s["exchange_rate"] = float(initial_rate)
        s["prev_exchange_rate"] = float(initial_rate)
        s["fundamental"] = float(fundamental_rate)
        s["peg_rate"] = float(peg_rate)
        s["price_impact"] = float(price_impact)
        s["mean_reversion_pull"] = float(mean_reversion_pull)
        s["cb_intervention_threshold"] = float(cb_intervention_threshold)
        s["noise_std"] = float(noise_std)
        s["reserves"] = float(reserves_initial)
        s["peg_status"] = "defending" if reserves_initial > 0 else "broken"
        s["deviation"] = 0.0
        s["net_pressure"] = 0.0
        s["num_attackers"] = 0
        s["num_defenders"] = 0

        # Structural/optional parameters
        s["rate_floor"] = float(rate_floor)
        s["reserves_floor"] = float(reserves_floor)
        s["peg_band"] = float(peg_band)
        s["intervention_normaliser"] = float(intervention_normaliser)
        s["gamma_post_break"] = float(gamma_post_break)
        s["attack_threshold"] = float(attack_threshold)

        # History buffers
        s["rate_history"] = self._make_history_buffer("exchange_rate")
        s["reserves_history"] = self._make_history_buffer("reserves")

    # ------------------------------------------------------------------
    # Market advance
    # ------------------------------------------------------------------

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's FX rate transition and return the broadcast dict.

        Steps:
        1. Aggregate orders (buy/sell/defend/sell-reserves/replenish)
        2. Update reserves ledger
        3. Determine peg status regime
        4. Compute gamma_eff (intervention-boosted or post-break)
        5. Draw noise, compute raw transition, clamp
        6. Compute derived observables
        7. Write state
        8. Return broadcast dict
        """
        s = self.state.custom_state

        # READ current state
        R_t = s["exchange_rate"]
        F = s["fundamental"]
        peg_rate = s["peg_rate"]
        reserves = s["reserves"]
        lam = s["price_impact"]
        gamma = s["mean_reversion_pull"]
        beta = s["cb_intervention_threshold"]
        sigma = s["noise_std"]
        rate_floor = s["rate_floor"]
        reserves_floor = s["reserves_floor"]
        peg_band = s["peg_band"]
        intervention_normaliser = s["intervention_normaliser"]
        gamma_post_break = s["gamma_post_break"]

        # Re-read fundamental and peg_rate from extras in case scenario driver
        # mutated them between rounds (Exogenous Driver Boundary channel b)
        extras = self.config.extras
        if "fundamental_rate" in extras:
            F = float(extras["fundamental_rate"])
            s["fundamental"] = F
        if "peg_rate" in extras:
            peg_rate = float(extras["peg_rate"])
            s["peg_rate"] = peg_rate

        # ----------------------------------------------------------
        # STEP 1: Aggregate orders
        # ----------------------------------------------------------
        buy_qty = 0.0
        sell_qty = 0.0
        defender_qty = 0.0
        replenish_qty = 0.0
        num_attackers = 0
        num_defenders = 0

        _VALID_ACTIONS = {
            "buy",
            "sell",
            "defend",
            "sell-reserves",
            "replenish",
            "hold",
        }

        for o in orders:
            if "action" not in o:
                raise ValueError(
                    f"Investor order missing required 'action' field: {o!r}"
                )
            action = o["action"]
            if action not in _VALID_ACTIONS:
                raise ValueError(
                    f"Unknown action {action!r} for fx-currency-peg-and-attack "
                    f"coordinator; valid actions are {sorted(_VALID_ACTIONS)}."
                )
            if "quantity" not in o:
                raise ValueError(
                    f"Investor order missing required 'quantity' field: {o!r}"
                )
            try:
                qty = float(o["quantity"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Investor order has non-numeric quantity {o['quantity']!r}: {o!r}"
                ) from exc
            if qty < 0:
                raise ValueError(
                    f"Investor order has negative quantity {qty}: {o!r}"
                )
            # Zero-quantity non-hold orders are a semantic error — an investor
            # that wants to do nothing MUST emit action="hold".
            if qty == 0 and action != "hold":
                raise ValueError(
                    f"Investor order with quantity=0 must use action='hold', "
                    f"got action={action!r}: {o!r}"
                )

            role = o.get("role")

            if action == "buy":
                buy_qty += qty
                if role == "attacker":
                    num_attackers += 1
            elif action == "defend":
                buy_qty += qty
                defender_qty += qty
                num_defenders += 1
            elif action == "sell":
                sell_qty += qty
                if role == "attacker" or role is None:
                    num_attackers += 1
            elif action == "sell-reserves":
                sell_qty += qty
                defender_qty += qty
                num_defenders += 1
            elif action == "replenish":
                replenish_qty += qty
            elif action == "hold":
                pass

        # net_pressure: buy + defend - sell - sell-reserves (replenish excluded)
        net_pressure = buy_qty - sell_qty

        # intervention_size: clamped by available reserves
        intervention_size = min(defender_qty, reserves)

        # ----------------------------------------------------------
        # STEP 2: Reserves update
        # ----------------------------------------------------------
        if defender_qty > reserves:
            logger.info(
                "Defender qty %.2f exceeds reserves %.2f; clamping intervention.",
                defender_qty,
                reserves,
            )
        new_reserves = max(reserves - abs(intervention_size) + replenish_qty, 0.0)

        # ----------------------------------------------------------
        # STEP 3: Peg status regime
        # ----------------------------------------------------------
        peg_defending = (
            new_reserves > reserves_floor
            and abs(R_t - peg_rate) < peg_band * peg_rate
        )
        peg_status_new = "defending" if peg_defending else "broken"

        # ----------------------------------------------------------
        # STEP 4: Effective gamma
        # ----------------------------------------------------------
        if peg_status_new == "defending":
            gamma_eff = gamma + beta * min(
                intervention_size / intervention_normaliser, 1.0
            )
        else:
            gamma_eff = gamma_post_break

        # ----------------------------------------------------------
        # STEP 5: Noise draw and raw transition
        # ----------------------------------------------------------
        epsilon = random.gauss(0, sigma)

        R_raw = R_t + lam * net_pressure + gamma_eff * (F - R_t) + epsilon
        new_R = max(R_raw, rate_floor)

        # ----------------------------------------------------------
        # STEP 6: Derived observables
        # ----------------------------------------------------------
        if F != 0:
            deviation = (new_R - F) / F
        else:
            deviation = 0.0

        volume = min(buy_qty, sell_qty) + 0.5 * abs(net_pressure)

        # ----------------------------------------------------------
        # STEP 7: Write state atomically
        # ----------------------------------------------------------
        s["prev_exchange_rate"] = R_t
        s["exchange_rate"] = new_R
        s["reserves"] = new_reserves
        s["peg_status"] = peg_status_new
        s["deviation"] = deviation
        s["net_pressure"] = net_pressure
        s["num_attackers"] = num_attackers
        s["num_defenders"] = num_defenders

        # Append to history buffers
        s["rate_history"].append(new_R)
        s["reserves_history"].append(new_reserves)

        # ----------------------------------------------------------
        # STEP 8: Return broadcast dict
        # ----------------------------------------------------------
        return {
            "exchange_rate": new_R,
            "prev_exchange_rate": R_t,
            "fundamental": F,
            "peg_rate": peg_rate,
            "deviation": deviation,
            "volume": volume,
            "net_pressure": net_pressure,
            "reserves": new_reserves,
            "peg_status": peg_status_new,
            "num_attackers": num_attackers,
            "num_defenders": num_defenders,
            "round": round_num,
        }


__all__ = ["MarketFxCurrencyPegAndAttack"]
