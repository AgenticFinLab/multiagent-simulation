"""Deposit Bank-Run Diamond-Dybvig — canonical market coordinator.

Profile: examples/AGENT_POOL/market/deposit-bank-run-diamond-dybvig.md
Mechanism: Withdrawal-fraction cumulative state with first-mover advantage,
    mark-to-market bond losses, panic-threshold trigger, and post-failure
    haircut on remaining claims.  One-way regime latch: solvent -> stressed
    -> failed.  Diamond & Dybvig (1983) extended with Goldstein-Pauzner (2005)
    common-knowledge cascade and Rochet-Vives (2004) solvency-floor selection.
Broadcast: 13 fields — withdrawal_fraction, prev_withdrawal_fraction,
    withdrawal_rate_this_round, solvency_ratio, prev_solvency_ratio,
    bond_mtm_loss, regime_status, num_withdrawers, num_holders,
    num_returners, panic_indicator, haircut_applied, round
"""

from __future__ import annotations

import logging
import math
import random
from typing import Any, Dict, List

from masim.agents._coordinator_base import CanonicalMarketCoordinator
from masim.format.broadcast import get_coordinator_action_types

logger = logging.getLogger("masim.agents.market_deposit_bank_run_diamond_dybvig")

_VALID_ACTION_TYPES = get_coordinator_action_types("deposit-bank-run-diamond-dybvig")


class MarketDepositBankRunDiamondDybvig(CanonicalMarketCoordinator):
    """Deposit-run coordinator with Diamond-Dybvig first-mover advantage and solvency regime switch.

    Theoretical basis: Diamond & Dybvig (1983) sequential-service bank-run
    equilibrium; Goldstein & Pauzner (2005) common-knowledge cascade above
    panic threshold; Rochet & Vives (2004) global-games unique-equilibrium
    solvency-floor selection; Jiang et al. (2023) mark-to-market bond losses;
    Farhi & Tirole (2012) optional depositor-return channel.
    """

    STRATEGY = "deposit-bank-run-diamond-dybvig"
    DISPLAY_NAME = "Deposit Bank-Run (Diamond-Dybvig)"
    SUMMARY = (
        "Withdrawal-fraction cumulative-state coordinator with first-mover "
        "advantage, panic-threshold cascade, MTM bond losses, and one-way "
        "solvent/stressed/failed regime latch."
    )
    BROADCAST_FIELDS = (
        "withdrawal_fraction",
        "prev_withdrawal_fraction",
        "withdrawal_rate_this_round",
        "solvency_ratio",
        "prev_solvency_ratio",
        "bond_mtm_loss",
        "regime_status",
        "num_withdrawers",
        "num_holders",
        "num_returners",
        "panic_indicator",
        "haircut_applied",
        "round",
    )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Read all required extras and initialize the deposit-market state."""
        s = self.state.custom_state

        # Required extras (raise KeyError on missing)
        _initial_deposits = extras["initial_deposits"]
        _initial_bond_portfolio_value = extras["initial_bond_portfolio_value"]
        initial_W = extras["initial_withdrawal_fraction"]
        alpha = extras["withdrawal_impact"]
        beta = extras["return_impact"]
        panic_threshold = extras["panic_threshold"]
        solvency_floor = extras["solvency_floor"]
        stressed_floor = extras["stressed_floor"]
        haircut_fraction = extras["haircut_fraction"]
        bond_mtm_loss_scalar = extras["bond_mtm_loss"]
        noise_std = extras["noise_std"]
        allow_returns = extras["allow_returns"]

        # Validate ordering constraint
        if not (solvency_floor < stressed_floor < 1.0):
            raise ValueError(
                f"Must satisfy solvency_floor < stressed_floor < 1; "
                f"got solvency_floor={solvency_floor}, stressed_floor={stressed_floor}"
            )

        # Optional extras
        bond_mtm_loss_trajectory = extras.get("bond_mtm_loss_trajectory", None)

        # Cache parameters
        s["_alpha"] = alpha
        s["_beta"] = beta
        s["_panic_threshold"] = panic_threshold
        s["_solvency_floor"] = solvency_floor
        s["_stressed_floor"] = stressed_floor
        s["_haircut_fraction"] = haircut_fraction
        s["_bond_mtm_loss_scalar"] = bond_mtm_loss_scalar
        s["_noise_std"] = noise_std
        s["_allow_returns"] = allow_returns
        s["_bond_mtm_loss_trajectory"] = bond_mtm_loss_trajectory

        # Determine initial bond_mtm_loss
        if bond_mtm_loss_trajectory is not None and len(bond_mtm_loss_trajectory) > 0:
            current_mtm_loss = bond_mtm_loss_trajectory[0]
        else:
            current_mtm_loss = bond_mtm_loss_scalar

        # Initial solvency
        initial_solvency = (1.0 - initial_W) * (1.0 - current_mtm_loss)

        # Initial state writes
        s["withdrawal_fraction"] = initial_W
        s["prev_withdrawal_fraction"] = initial_W
        s["withdrawal_rate_this_round"] = 0.0
        s["solvency_ratio"] = initial_solvency
        s["prev_solvency_ratio"] = initial_solvency
        s["bond_mtm_loss"] = current_mtm_loss
        s["regime_status"] = "solvent"
        s["panic_indicator"] = 1 if initial_W >= panic_threshold else 0
        s["haircut_applied"] = 0.0
        s["num_withdrawers"] = 0
        s["num_holders"] = 0
        s["num_returners"] = 0

        # History buffers
        s["_withdrawal_history"] = self._make_history_buffer("withdrawal_fraction")
        s["_solvency_history"] = self._make_history_buffer("solvency_ratio")
        s["_regime_history"] = self._make_history_buffer("regime_status")
        s["_bond_mtm_loss_history"] = self._make_history_buffer("bond_mtm_loss")
        s["_withdrawer_count_history"] = self._make_history_buffer("withdrawer_count")

    # ------------------------------------------------------------------
    # Market advance
    # ------------------------------------------------------------------

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's deposit-market transition and return 13-field broadcast."""
        s = self.state.custom_state

        # Read current state
        W_t = s["withdrawal_fraction"]
        solvency_t = s["solvency_ratio"]
        regime_t = s["regime_status"]

        # Read parameters
        alpha = s["_alpha"]
        beta = s["_beta"]
        sigma = s["_noise_std"]
        panic_threshold = s["_panic_threshold"]
        solvency_floor = s["_solvency_floor"]
        stressed_floor = s["_stressed_floor"]
        haircut_fraction = s["_haircut_fraction"]
        allow_returns = s["_allow_returns"]
        bond_mtm_loss_trajectory = s["_bond_mtm_loss_trajectory"]
        bond_mtm_loss_scalar = s["_bond_mtm_loss_scalar"]

        # ------------------------------------------------------------------
        # Read exogenous MTM loss for this round
        # ------------------------------------------------------------------
        if bond_mtm_loss_trajectory is not None:
            if round_num >= len(bond_mtm_loss_trajectory):
                raise IndexError(
                    f"bond_mtm_loss_trajectory length {len(bond_mtm_loss_trajectory)} "
                    f"is shorter than round {round_num}"
                )
            bond_mtm_loss_current = bond_mtm_loss_trajectory[round_num]
        else:
            bond_mtm_loss_current = bond_mtm_loss_scalar

        # ------------------------------------------------------------------
        # Aggregate inbound actions
        # ------------------------------------------------------------------
        num_withdrawers = 0
        num_holders = 0
        num_returners = 0
        total_withdraw_share = 0.0
        total_return_share = 0.0

        for action in orders:
            if "action_type" not in action:
                raise ValueError(
                    f"Investor order missing required 'action_type' field: {action!r}"
                )
            action_type = action["action_type"]

            if action_type not in _VALID_ACTION_TYPES:
                raise ValueError(
                    f"Invalid action_type {action_type!r}; "
                    f"must be one of {_VALID_ACTION_TYPES}"
                )

            if "intensity" not in action:
                raise ValueError(
                    f"Investor order missing required 'intensity' field: {action!r}"
                )
            if "share" not in action:
                raise ValueError(
                    f"Investor order missing required 'share' field: {action!r}"
                )

            # Validate ranges
            try:
                intensity = float(action["intensity"])
                share = float(action["share"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Non-numeric intensity/share in action: {action!r}"
                ) from exc

            if not (0.0 <= intensity <= 1.0):
                raise ValueError(
                    f"intensity {intensity} outside [0,1] in action: {action!r}"
                )
            if not (0.0 <= share <= 1.0):
                raise ValueError(
                    f"share {share} outside [0,1] in action: {action!r}"
                )

            if action_type in ("withdraw", "panic_withdraw"):
                num_withdrawers += 1
                total_withdraw_share += intensity * share
            elif action_type == "return":
                num_returners += 1
                total_return_share += intensity * share
            elif action_type == "hold":
                num_holders += 1
            # intensity == 0 => treated as hold for aggregation purposes
            # but still counted in the correct category above

        n_actions = max(1, len(orders))
        net_withdraw_fraction = total_withdraw_share / n_actions
        net_return_fraction = (total_return_share / n_actions) * (
            1.0 if allow_returns else 0.0
        )

        # ------------------------------------------------------------------
        # Branch: if regime is "failed", short-circuit (frozen state)
        # ------------------------------------------------------------------
        if regime_t == "failed":
            # Post-failure: state frozen, no transitions
            new_W = W_t
            new_solvency = solvency_t
            new_regime = "failed"
            panic_ind = s["panic_indicator"]
            haircut = s["haircut_applied"]
            # Force counters to 0 in broadcast (no actions accepted)
            num_withdrawers = 0
            num_returners = 0
        else:
            # ------------------------------------------------------------------
            # Compute noise
            # ------------------------------------------------------------------
            eps = random.gauss(0, sigma) if sigma > 0 else 0.0

            # ------------------------------------------------------------------
            # Compute transition
            # ------------------------------------------------------------------
            W_raw = (
                W_t
                + alpha * net_withdraw_fraction
                - beta * net_return_fraction
                + eps
            )

            # Monotone guard (when allow_returns is False)
            if not allow_returns:
                W_guarded = max(W_raw, W_t)
            else:
                W_guarded = W_raw

            # Clip to [0, 1]
            new_W = min(1.0, max(0.0, W_guarded))

            # Solvency identity
            new_solvency = (1.0 - new_W) * (1.0 - bond_mtm_loss_current)

            # Panic indicator
            panic_ind = 1 if new_W >= panic_threshold else 0

            # ------------------------------------------------------------------
            # Evaluate regime latch
            # ------------------------------------------------------------------
            if new_solvency < solvency_floor:
                new_regime = "failed"
                haircut = haircut_fraction
            elif new_W >= panic_threshold or new_solvency < stressed_floor:
                new_regime = "stressed"
                haircut = 0.0
            else:
                new_regime = "solvent"
                haircut = 0.0

        # ------------------------------------------------------------------
        # Validate
        # ------------------------------------------------------------------
        for name, val in [
            ("withdrawal_fraction", new_W),
            ("solvency_ratio", new_solvency),
            ("haircut_applied", haircut),
        ]:
            if math.isnan(val) or math.isinf(val):
                raise ValueError(
                    f"[{self.identity}] {name} is {val} in round {round_num}"
                )

        # ------------------------------------------------------------------
        # Compute derived fields
        # ------------------------------------------------------------------
        withdrawal_rate = new_W - W_t

        # ------------------------------------------------------------------
        # Write state atomically (prev before current)
        # ------------------------------------------------------------------
        s["prev_withdrawal_fraction"] = W_t
        s["prev_solvency_ratio"] = solvency_t
        s["withdrawal_fraction"] = new_W
        s["withdrawal_rate_this_round"] = withdrawal_rate
        s["solvency_ratio"] = new_solvency
        s["bond_mtm_loss"] = bond_mtm_loss_current
        s["regime_status"] = new_regime
        s["panic_indicator"] = panic_ind
        s["haircut_applied"] = haircut
        s["num_withdrawers"] = num_withdrawers
        s["num_holders"] = num_holders
        s["num_returners"] = num_returners

        # Append to history buffers
        s["_withdrawal_history"].append(new_W)
        s["_solvency_history"].append(new_solvency)
        s["_regime_history"].append(new_regime)
        s["_bond_mtm_loss_history"].append(bond_mtm_loss_current)
        s["_withdrawer_count_history"].append(num_withdrawers)

        # ------------------------------------------------------------------
        # Return broadcast dict
        # ------------------------------------------------------------------
        return {
            "withdrawal_fraction": new_W,
            "prev_withdrawal_fraction": W_t,
            "withdrawal_rate_this_round": withdrawal_rate,
            "solvency_ratio": new_solvency,
            "prev_solvency_ratio": solvency_t,
            "bond_mtm_loss": bond_mtm_loss_current,
            "regime_status": new_regime,
            "num_withdrawers": num_withdrawers,
            "num_holders": num_holders,
            "num_returners": num_returners,
            "panic_indicator": panic_ind,
            "haircut_applied": haircut,
            "round": round_num,
        }


__all__ = ["MarketDepositBankRunDiamondDybvig"]
