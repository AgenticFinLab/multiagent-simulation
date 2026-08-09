"""Credit Minsky-Cycle — canonical market coordinator.

Profile: masim/agents/defines/market/credit-minsky-cycle.md
Mechanism: Standard linear price-impact + regime-gated mean-reversion + Gaussian
    noise, extended with a categorical Minsky financing regime state
    {hedge, speculative, ponzi} whose transitions are a deterministic function
    of aggregate leverage L(t).  gamma varies by regime: full-strength in hedge,
    halved in speculative, near-zero in ponzi — the endogenous Minsky-moment
    mechanism.  Optional second co-broadcast MBS asset for GFC2008 mode.
Broadcast: 15 fields (16 with mbs_price if mbs_enabled) — credit_price,
    prev_credit_price, price_change, fundamental_credit_price,
    aggregate_leverage, prev_aggregate_leverage, minsky_regime,
    prev_minsky_regime, regime_transition_this_round, num_borrowers,
    num_lenders, num_extenders, num_contractors, net_credit_demand, round
    [+ mbs_price if mbs_enabled]
"""

from __future__ import annotations

import logging
import math
import random
from typing import Any, Dict, List

from masim.agents._coordinator_base import CanonicalMarketCoordinator

logger = logging.getLogger("masim.agents.market_credit_minsky_cycle")


class MarketCreditMinskyCycle(CanonicalMarketCoordinator):
    """Minsky-cycle credit market coordinator with endogenous leverage-regime state.

    Theoretical basis: Minsky (1986/1992) Financial Instability Hypothesis
    (hedge/speculative/ponzi regime taxonomy); Kyle (1985) linear price-impact;
    Brock & Hommes (1998) regime-gated mean-reversion; Adrian & Shin (2010) and
    Kiyotaki & Moore (1997) procyclical leverage accumulation; Gorton & Metrick
    (2012) securitised-banking co-movement for the optional MBS asset.
    """

    STRATEGY = "credit-minsky-cycle"
    DISPLAY_NAME = "Credit Minsky-Cycle"
    SUMMARY = (
        "Credit market with endogenous Minsky financing regime "
        "(hedge/speculative/ponzi) gating mean-reversion strength; "
        "stability breeds instability as leverage accumulates."
    )
    BROADCAST_FIELDS = (
        "credit_price",
        "prev_credit_price",
        "price_change",
        "fundamental_credit_price",
        "aggregate_leverage",
        "prev_aggregate_leverage",
        "minsky_regime",
        "prev_minsky_regime",
        "regime_transition_this_round",
        "num_borrowers",
        "num_lenders",
        "num_extenders",
        "num_contractors",
        "net_credit_demand",
        "round",
    )

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def init_market_state(self, extras: Dict[str, Any]) -> None:
        """Read all required extras and initialize the credit-market state."""
        s = self.state.custom_state

        # Required extras (raise KeyError on missing)
        initial_credit_price = extras["initial_credit_price"]
        fundamental_credit_price = extras["fundamental_credit_price"]
        initial_leverage = extras["initial_leverage"]
        price_impact = extras["price_impact"]
        mean_reversion_pull_base = extras["mean_reversion_pull_base"]
        borrowing_impact = extras["borrowing_impact_on_leverage"]
        repayment_impact = extras["repayment_impact_on_leverage"]
        L_spec_threshold = extras["leverage_speculative_threshold"]
        L_ponzi_threshold = extras["leverage_ponzi_threshold"]
        noise_std = extras["noise_std"]
        mbs_enabled = extras["mbs_enabled"]

        # Optional extras with documented defaults
        price_floor = extras.get("price_floor", 0.01)
        ponzi_gamma_multiplier = extras.get("ponzi_gamma_multiplier", 0.05)
        speculative_gamma_multiplier = extras.get("speculative_gamma_multiplier", 0.5)

        # Validate gamma multiplier ordering (invariant #10)
        if not (1.0 >= speculative_gamma_multiplier >= ponzi_gamma_multiplier >= 0.0):
            raise ValueError(
                f"Must satisfy 1 >= speculative_gamma_multiplier >= "
                f"ponzi_gamma_multiplier >= 0; got spec={speculative_gamma_multiplier}, "
                f"ponzi={ponzi_gamma_multiplier}"
            )

        # Conditionally required extras for MBS mode
        if mbs_enabled:
            initial_mbs_price = extras["initial_mbs_price"]
            fundamental_mbs_price = extras["fundamental_mbs_price"]
        else:
            initial_mbs_price = None
            fundamental_mbs_price = None

        # Cache parameters
        s["_price_impact"] = price_impact
        s["_mean_reversion_pull_base"] = mean_reversion_pull_base
        s["_borrowing_impact"] = borrowing_impact
        s["_repayment_impact"] = repayment_impact
        s["_L_spec_threshold"] = L_spec_threshold
        s["_L_ponzi_threshold"] = L_ponzi_threshold
        s["_noise_std"] = noise_std
        s["_price_floor"] = price_floor
        s["_ponzi_gamma_multiplier"] = ponzi_gamma_multiplier
        s["_speculative_gamma_multiplier"] = speculative_gamma_multiplier
        s["_mbs_enabled"] = mbs_enabled

        # Compute initial regime
        initial_regime = self._compute_regime(
            initial_leverage, L_spec_threshold, L_ponzi_threshold
        )

        # State variables
        s["credit_price"] = initial_credit_price
        s["prev_credit_price"] = initial_credit_price
        s["price_change"] = 0.0
        s["fundamental_credit_price"] = fundamental_credit_price
        s["aggregate_leverage"] = initial_leverage
        s["prev_aggregate_leverage"] = initial_leverage
        s["minsky_regime"] = initial_regime
        s["prev_minsky_regime"] = initial_regime
        s["regime_transition_this_round"] = False

        # History buffers
        s["_credit_price_history"] = self._make_history_buffer("credit_price")
        s["_leverage_history"] = self._make_history_buffer("leverage")
        s["_regime_history"] = self._make_history_buffer("regime")

        # MBS state (conditional)
        if mbs_enabled:
            s["mbs_price"] = initial_mbs_price
            s["prev_mbs_price"] = initial_mbs_price
            s["fundamental_mbs_price"] = fundamental_mbs_price
            s["_mbs_price_history"] = self._make_history_buffer("mbs_price")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_regime(
        leverage: float, L_spec: float, L_ponzi: float
    ) -> str:
        """Deterministic regime function of aggregate leverage."""
        if leverage < L_spec:
            return "hedge"
        elif leverage < L_ponzi:
            return "speculative"
        else:
            return "ponzi"

    def _compute_gamma(self, regime: str) -> float:
        """Compute the regime-gated mean-reversion coefficient."""
        s = self.state.custom_state
        gamma_base = s["_mean_reversion_pull_base"]
        if regime == "hedge":
            return gamma_base
        elif regime == "speculative":
            return s["_speculative_gamma_multiplier"] * gamma_base
        else:  # "ponzi"
            return s["_ponzi_gamma_multiplier"] * gamma_base

    # ------------------------------------------------------------------
    # Market advance
    # ------------------------------------------------------------------

    def advance_market(
        self, orders: List[Dict[str, Any]], round_num: int
    ) -> Dict[str, Any]:
        """Compute one round's credit-market transition and return broadcast dict."""
        s = self.state.custom_state

        # Read current state
        P_t = s["credit_price"]
        F = s["fundamental_credit_price"]
        L_t = s["aggregate_leverage"]
        regime_t = s["minsky_regime"]
        mbs_enabled = s["_mbs_enabled"]

        # Read parameters
        lam = s["_price_impact"]
        sigma = s["_noise_std"]
        eta = s["_borrowing_impact"]
        zeta = s["_repayment_impact"]
        L_spec = s["_L_spec_threshold"]
        L_ponzi = s["_L_ponzi_threshold"]
        price_floor = s["_price_floor"]

        # MBS state (conditional)
        if mbs_enabled:
            M_t = s["mbs_price"]
            F_mbs = s["fundamental_mbs_price"]

        # ------------------------------------------------------------------
        # Step 2: Aggregate orders
        # ------------------------------------------------------------------
        buy_credit_qty = 0.0
        sell_credit_qty = 0.0
        borrow_qty = 0.0
        repay_qty = 0.0
        extend_qty = 0.0
        contract_qty = 0.0
        buy_mbs_qty = 0.0
        sell_mbs_qty = 0.0
        num_borrowers = 0
        num_lenders = 0
        num_extenders = 0
        num_contractors = 0

        _VALID_ACTIONS = {
            "buy_credit", "sell_credit", "borrow", "repay",
            "extend_credit", "contract_credit", "buy_mbs", "sell_mbs",
            # "hold" is an explicit no-op — the profile documents "no message"
            # as an implicit no-op, but under the project's fail-loud policy
            # every investor MUST emit an explicit action, so we require the
            # "hold" sentinel instead of tolerating missing action_type.
            "hold",
        }
        for o in orders:
            if "action_type" not in o or o["action_type"] is None:
                raise ValueError(
                    "credit coordinator: order missing required "
                    f"'action_type': {o!r}. Silent-skip would zero out demand."
                )
            action_type = o["action_type"]
            if action_type not in _VALID_ACTIONS:
                raise ValueError(
                    "credit coordinator: unknown "
                    f"action_type={action_type!r}; valid: "
                    f"{sorted(_VALID_ACTIONS)}. Order: {o!r}"
                )

            if "size" not in o:
                raise ValueError(
                    f"credit coordinator: order missing 'size': {o!r}"
                )
            try:
                size = float(o["size"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"credit coordinator: order 'size'={o['size']!r} "
                    f"not numeric: {o!r}"
                ) from exc
            if size < 0:
                raise ValueError(
                    "credit coordinator: negative order size "
                    f"{size} is disallowed: {o!r}"
                )

            if action_type == "buy_credit":
                buy_credit_qty += size
                num_lenders += 1
            elif action_type == "sell_credit":
                sell_credit_qty += size
            elif action_type == "borrow":
                borrow_qty += size
                num_borrowers += 1
            elif action_type == "repay":
                repay_qty += size
            elif action_type == "extend_credit":
                extend_qty += size
                num_extenders += 1
            elif action_type == "contract_credit":
                contract_qty += size
                num_contractors += 1
            elif action_type == "buy_mbs":
                if not mbs_enabled:
                    raise ValueError(
                        "credit coordinator: buy_mbs received but "
                        "mbs_enabled=False. Silent-skip would let a "
                        "misconfigured scenario silently drop MBS flow; "
                        "fix the extras or the investor emit path."
                    )
                buy_mbs_qty += size
            elif action_type == "sell_mbs":
                if not mbs_enabled:
                    raise ValueError(
                        "credit coordinator: sell_mbs received but "
                        "mbs_enabled=False. See buy_mbs comment above."
                    )
                sell_mbs_qty += size

        net_credit_demand = buy_credit_qty - sell_credit_qty
        net_borrowing = borrow_qty + extend_qty
        net_repayment = repay_qty + contract_qty
        net_mbs_demand = buy_mbs_qty - sell_mbs_qty

        # ------------------------------------------------------------------
        # Step 3: Leverage update
        # ------------------------------------------------------------------
        L_raw = L_t + eta * net_borrowing - zeta * net_repayment
        L_next = max(L_raw, 0.0)

        # ------------------------------------------------------------------
        # Step 4: Regime transition (deterministic function of L(t+1))
        # ------------------------------------------------------------------
        regime_next = self._compute_regime(L_next, L_spec, L_ponzi)
        regime_transition = regime_next != regime_t
        gamma_effective = self._compute_gamma(regime_next)

        # ------------------------------------------------------------------
        # Step 5: Credit price transition
        # ------------------------------------------------------------------
        eps_credit = random.gauss(0, sigma) if sigma > 0 else 0.0
        P_raw = P_t + lam * net_credit_demand + gamma_effective * (F - P_t) + eps_credit
        credit_price_next = max(P_raw, price_floor)
        price_change = credit_price_next - P_t

        # ------------------------------------------------------------------
        # Step 6: MBS price transition (conditional)
        # ------------------------------------------------------------------
        if mbs_enabled:
            eps_mbs = random.gauss(0, sigma) if sigma > 0 else 0.0
            MBS_raw = (
                M_t + lam * net_mbs_demand + gamma_effective * (F_mbs - M_t) + eps_mbs
            )
            mbs_price_next = max(MBS_raw, price_floor)

        # ------------------------------------------------------------------
        # Validate
        # ------------------------------------------------------------------
        for name, val in [
            ("aggregate_leverage", L_next),
            ("credit_price", credit_price_next),
        ]:
            if math.isnan(val) or math.isinf(val):
                raise ValueError(
                    f"[{self.identity}] {name} is {val} in round {round_num}"
                )
        if mbs_enabled:
            if math.isnan(mbs_price_next) or math.isinf(mbs_price_next):
                raise ValueError(
                    f"[{self.identity}] mbs_price is {mbs_price_next} in round {round_num}"
                )

        # ------------------------------------------------------------------
        # Step 7: Write state atomically
        # ------------------------------------------------------------------
        s["prev_credit_price"] = P_t
        s["credit_price"] = credit_price_next
        s["price_change"] = price_change
        s["prev_aggregate_leverage"] = L_t
        s["aggregate_leverage"] = L_next
        s["prev_minsky_regime"] = regime_t
        s["minsky_regime"] = regime_next
        s["regime_transition_this_round"] = regime_transition

        if mbs_enabled:
            s["prev_mbs_price"] = M_t
            s["mbs_price"] = mbs_price_next

        # Append to history buffers
        s["_credit_price_history"].append(credit_price_next)
        s["_leverage_history"].append(L_next)
        s["_regime_history"].append(regime_next)
        if mbs_enabled:
            s["_mbs_price_history"].append(mbs_price_next)

        # ------------------------------------------------------------------
        # Step 8: Return broadcast dict
        # ------------------------------------------------------------------
        broadcast: Dict[str, Any] = {
            "credit_price": credit_price_next,
            "prev_credit_price": P_t,
            "price_change": price_change,
            "fundamental_credit_price": F,
            "aggregate_leverage": L_next,
            "prev_aggregate_leverage": L_t,
            "minsky_regime": regime_next,
            "prev_minsky_regime": regime_t,
            "regime_transition_this_round": regime_transition,
            "num_borrowers": num_borrowers,
            "num_lenders": num_lenders,
            "num_extenders": num_extenders,
            "num_contractors": num_contractors,
            "net_credit_demand": net_credit_demand,
            "round": round_num,
        }

        if mbs_enabled:
            broadcast["mbs_price"] = mbs_price_next

        return broadcast


__all__ = ["MarketCreditMinskyCycle"]
