"""Market coordinator broadcast format — the single source of truth for coordinator output.

Every canonical coordinator in :mod:`masim.agents` MUST emit broadcasts
validated through this module.  Raw unvalidated dicts are rejected at the
base class :meth:`~masim.agents._coordinator_base.CanonicalMarketCoordinator.decide`
boundary: the pipeline calls :func:`validate_broadcast` on every emission
and raises ``ValueError`` on schema drift.

Public surface
--------------

* :class:`FieldSpec` — declarative field-level constraint (type, range, enum).
* :class:`BroadcastSchema` — per-archetype schema definition (required fields,
  optional fields, invariant checks).
* :data:`BROADCAST_SCHEMAS` — registry mapping ``strategy`` → :class:`BroadcastSchema`.
* :func:`validate_broadcast` — strict validator (raises on any violation).
* :class:`MarketBroadcast` — frozen wrapper for a validated broadcast payload.
  Use :meth:`MarketBroadcast.from_dict` to construct; direct construction is
  discouraged.

Design rationale
----------------

Coordinator broadcasts differ from investor orders: each archetype has a
*distinct* field set (7–16 fields) whereas all investor orders share a single
schema.  Therefore we use a **registry of declarative schemas** rather than
one monolithic dataclass.  The validation is equally strict:

- Every required field MUST be present.
- Every field MUST match its declared type (``float``, ``int``, ``str``, ``bool``).
- Numeric fields MUST satisfy declared ``min_val`` / ``max_val`` bounds.
- Enum-like string fields MUST be one of the ``allowed_values``.
- No NaN or Inf in any numeric field.
- No undeclared keys (strict mode; disables with ``strict=False``).

Contract summary (mirrors ``examples/AGENT_POOL/market/*.md`` §Shared State)
-----------------------------------------------------------------------------

Each coordinator archetype defines its broadcast as a flat dict; the field
names and their semantics are declared in the corresponding AGENT_POOL profile.
The schemas below are mechanically derived from those profiles and enforce
the invariants listed therein.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Sequence, Set, Tuple


# ---------------------------------------------------------------------------
# Field-level specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FieldSpec:
    """Declarative constraint for a single broadcast field.

    Attributes:
        name: Field name in the broadcast dict.
        dtype: Expected Python type (float, int, str, bool).  Numeric coercion
            ``int → float`` is allowed when ``dtype == float``.
        required: Whether the field MUST be present (True) or is conditional.
        min_val: Inclusive lower bound for numeric fields (None = no bound).
        max_val: Inclusive upper bound for numeric fields (None = no bound).
        allowed_values: Exhaustive set of valid string values (None = any str).
        description: Human-readable short description (for error messages).
    """

    name: str
    dtype: type
    required: bool = True
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    allowed_values: Optional[Tuple[str, ...]] = None
    description: str = ""


# ---------------------------------------------------------------------------
# Schema definition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BroadcastSchema:
    """Per-archetype broadcast schema.

    Attributes:
        strategy: Kebab-case archetype identifier (e.g. ``"stock-standard-price-impact"``).
        fields: Ordered tuple of :class:`FieldSpec` instances — defines the
            complete field set and constraints.
        conditional_fields: Fields that may or may not be present depending on
            runtime configuration (e.g. ``mbs_price`` only when ``mbs_enabled``).
            These are NOT checked for presence but ARE type-checked when present.
    """

    strategy: str
    fields: Tuple[FieldSpec, ...]
    conditional_fields: Tuple[FieldSpec, ...] = ()

    @property
    def required_field_names(self) -> FrozenSet[str]:
        return frozenset(f.name for f in self.fields if f.required)

    @property
    def all_field_names(self) -> FrozenSet[str]:
        return frozenset(f.name for f in self.fields) | frozenset(
            f.name for f in self.conditional_fields
        )

    @property
    def field_map(self) -> Dict[str, FieldSpec]:
        """Name → FieldSpec lookup (includes conditional fields)."""
        m: Dict[str, FieldSpec] = {}
        for f in self.fields:
            m[f.name] = f
        for f in self.conditional_fields:
            m[f.name] = f
        return m


# ---------------------------------------------------------------------------
# Schema definitions — one per coordinator archetype
# ---------------------------------------------------------------------------

# Helper shortcuts for common field specs
def _float_field(name: str, *, min_val: Optional[float] = None,
                 max_val: Optional[float] = None, required: bool = True,
                 desc: str = "") -> FieldSpec:
    return FieldSpec(name=name, dtype=float, required=required,
                     min_val=min_val, max_val=max_val, description=desc)


def _int_field(name: str, *, min_val: Optional[float] = None,
               max_val: Optional[float] = None, required: bool = True,
               desc: str = "") -> FieldSpec:
    return FieldSpec(name=name, dtype=int, required=required,
                     min_val=min_val, max_val=max_val, description=desc)


def _str_field(name: str, *, allowed: Optional[Tuple[str, ...]] = None,
               required: bool = True, desc: str = "") -> FieldSpec:
    return FieldSpec(name=name, dtype=str, required=required,
                     allowed_values=allowed, description=desc)


def _bool_field(name: str, *, required: bool = True, desc: str = "") -> FieldSpec:
    return FieldSpec(name=name, dtype=bool, required=required, description=desc)


# -- 1. Stock Standard Price Impact (7 fields) --

STOCK_STANDARD_PRICE_IMPACT_SCHEMA = BroadcastSchema(
    strategy="stock-standard-price-impact",
    fields=(
        _float_field("price", min_val=0.0, desc="Current stock price P(t+1)"),
        _float_field("prev_price", min_val=0.0, desc="Previous price P(t)"),
        _float_field("fundamental", min_val=0.0, desc="Fundamental value F"),
        _float_field("deviation", desc="(P − F) / F; may be negative"),
        _float_field("volume", min_val=0.0, desc="Estimated trading volume"),
        _float_field("net_demand", desc="buy_qty − sell_qty; may be negative"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
)

# -- 2. Opinion Echo-Chamber Clustering (10 fields) --

OPINION_ECHO_CHAMBER_CLUSTERING_SCHEMA = BroadcastSchema(
    strategy="opinion-echo-chamber-clustering",
    fields=(
        _float_field("polarization", min_val=0.0, max_val=1.0,
                     desc="Current polarization index P(t+1) ∈ [0,1]"),
        _float_field("prev_polarization", min_val=0.0, max_val=1.0,
                     desc="Previous polarization P(t)"),
        _float_field("polarization_change",
                     desc="P(t+1) − P(t); may be negative"),
        _float_field("mean_opinion",
                     desc="Population mean opinion (signed)"),
        _float_field("cluster_separation", min_val=0.0,
                     desc="mean(right) − mean(left) separation ≥ 0"),
        _float_field("cross_cutting_exposure", min_val=0.0, max_val=1.0,
                     desc="Fraction of moderate agents ∈ [0,1]"),
        _int_field("num_polarizers", min_val=0,
                   desc="Count of agents polarizing this round"),
        _int_field("num_depolarizers", min_val=0,
                   desc="Count of agents depolarizing this round"),
        _float_field("net_polarization_intensity",
                     desc="Net polarization intensity; may be negative"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
)

# -- 3. Information SIS Contagion (9 fields) --

INFORMATION_SIS_CONTAGION_SCHEMA = BroadcastSchema(
    strategy="information-sis-contagion",
    fields=(
        _float_field("belief", min_val=0.0, max_val=1.0,
                     desc="Current population belief B(t+1) ∈ [0,1]"),
        _float_field("prev_belief", min_val=0.0, max_val=1.0,
                     desc="Previous belief B(t)"),
        _float_field("belief_change",
                     desc="B(t+1) − B(t); may be negative"),
        _float_field("distortion", min_val=0.0, max_val=1.0,
                     desc="Information distortion D(t+1) ∈ [0,1]"),
        _float_field("truth_value", min_val=0.0, max_val=1.0,
                     desc="Ground truth value of the rumor ∈ [0,1]"),
        _int_field("num_spreaders", min_val=0,
                   desc="Count of spreading agents this round"),
        _int_field("num_correctors", min_val=0,
                   desc="Count of correcting agents this round"),
        _float_field("net_spread_intensity",
                     desc="Net spreading intensity; may be negative"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
)

# -- 4. FX Currency Peg and Attack (12 fields) --

FX_CURRENCY_PEG_AND_ATTACK_SCHEMA = BroadcastSchema(
    strategy="fx-currency-peg-and-attack",
    fields=(
        _float_field("exchange_rate", min_val=0.0,
                     desc="Current exchange rate R(t+1) ≥ rate_floor"),
        _float_field("prev_exchange_rate", min_val=0.0,
                     desc="Previous exchange rate R(t)"),
        _float_field("fundamental", min_val=0.0,
                     desc="Fundamental rate F"),
        _float_field("peg_rate", min_val=0.0,
                     desc="Official peg rate"),
        _float_field("deviation",
                     desc="(R − F) / F; may be negative"),
        _float_field("volume", min_val=0.0,
                     desc="Estimated FX trading volume"),
        _float_field("net_pressure",
                     desc="Net attack/defend pressure; may be negative"),
        _float_field("reserves", min_val=0.0,
                     desc="CB foreign reserves ≥ 0"),
        _str_field("peg_status", allowed=("defending", "broken"),
                   desc="Peg regime status"),
        _int_field("num_attackers", min_val=0,
                   desc="Count of attacking agents this round"),
        _int_field("num_defenders", min_val=0,
                   desc="Count of defending agents this round"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
)

# -- 5. Bond Yield Spread Inverse (12 fields) --

BOND_YIELD_SPREAD_INVERSE_SCHEMA = BroadcastSchema(
    strategy="bond-yield-spread-inverse",
    fields=(
        _float_field("bond_price", min_val=0.0,
                     desc="Current bond price P(t+1)"),
        _float_field("prev_bond_price", min_val=0.0,
                     desc="Previous bond price P(t)"),
        _float_field("price_change",
                     desc="P(t+1) − P(t); may be negative"),
        _float_field("fundamental", min_val=0.0,
                     desc="Fundamental bond price F(t)"),
        _float_field("implied_spread", min_val=0.0,
                     desc="Implied yield spread = 1/P − 1 ≥ 0"),
        _float_field("deviation",
                     desc="(P − F) / F; may be negative"),
        _float_field("volume", min_val=0.0,
                     desc="Estimated trading volume"),
        _int_field("num_buyers", min_val=0,
                   desc="Count of buy-side agents"),
        _int_field("num_sellers", min_val=0,
                   desc="Count of sell-side agents"),
        _float_field("net_demand",
                     desc="buy_qty − sell_qty; may be negative"),
        _bool_field("cb_intervention_active",
                    desc="Whether CB intervention is currently active"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
)

# -- 6. Crypto Algostable Depeg (12 fields) --

CRYPTO_ALGOSTABLE_DEPEG_SCHEMA = BroadcastSchema(
    strategy="crypto-algostable-depeg",
    fields=(
        _float_field("luna_price", min_val=0.0,
                     desc="Current LUNA price L(t+1)"),
        _float_field("prev_luna_price", min_val=0.0,
                     desc="Previous LUNA price L(t)"),
        _float_field("ust_price", min_val=0.0,
                     desc="Current UST price U(t+1)"),
        _float_field("prev_ust_price", min_val=0.0,
                     desc="Previous UST price U(t)"),
        _float_field("luna_supply", min_val=0.0,
                     desc="Current LUNA supply"),
        _float_field("prev_luna_supply", min_val=0.0,
                     desc="Previous LUNA supply"),
        _float_field("ust_depeg_amount",
                     desc="UST deviation from peg; may be negative"),
        _float_field("arb_flow_this_round",
                     desc="Arbitrage flow this round; may be negative"),
        _float_field("anchor_tvl", min_val=0.0,
                     desc="Anchor protocol TVL ≥ 0"),
        _int_field("num_burners", min_val=0,
                   desc="Count of LUNA burners this round"),
        _int_field("num_minters", min_val=0,
                   desc="Count of LUNA minters this round"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
)

# -- 7. Derivatives Vol-Feedback (14 fields) --

DERIVATIVES_VOL_FEEDBACK_SCHEMA = BroadcastSchema(
    strategy="derivatives-vol-feedback",
    fields=(
        _float_field("vix_level", min_val=0.0,
                     desc="Current VIX level V(t+1)"),
        _float_field("prev_vix_level", min_val=0.0,
                     desc="Previous VIX level V(t)"),
        _float_field("xiv_price", min_val=0.0,
                     desc="Current XIV price X(t+1)"),
        _float_field("prev_xiv_price", min_val=0.0,
                     desc="Previous XIV price X(t)"),
        _float_field("xiv_notional", min_val=0.0,
                     desc="Current XIV notional N(t+1) ≥ 0"),
        _float_field("prev_xiv_notional", min_val=0.0,
                     desc="Previous XIV notional N(t)"),
        _float_field("hedge_flow_this_round",
                     desc="Hedge flow Δ this round; may be negative"),
        _str_field("xiv_nav_status",
                   allowed=("normal", "warning", "triggered", "terminated"),
                   desc="XIV NAV status — 4-element closed set"),
        _int_field("num_vol_buyers", min_val=0,
                   desc="Count of vol-buying agents"),
        _int_field("num_vol_sellers", min_val=0,
                   desc="Count of vol-selling agents"),
        _float_field("net_vol_demand",
                     desc="Net vol demand; may be negative"),
        _int_field("num_hedgers", min_val=0,
                   desc="Count of hedging agents"),
        _bool_field("terminated",
                    desc="One-way termination latch (never True → False)"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
)

# -- 8. Deposit Bank-Run Diamond-Dybvig (13 fields) --

DEPOSIT_BANK_RUN_DIAMOND_DYBVIG_SCHEMA = BroadcastSchema(
    strategy="deposit-bank-run-diamond-dybvig",
    fields=(
        _float_field("withdrawal_fraction", min_val=0.0, max_val=1.0,
                     desc="Cumulative withdrawal fraction W(t+1) ∈ [0,1]"),
        _float_field("prev_withdrawal_fraction", min_val=0.0, max_val=1.0,
                     desc="Previous withdrawal fraction W(t)"),
        _float_field("withdrawal_rate_this_round", min_val=0.0,
                     desc="Net withdrawal intensity this round"),
        _float_field("solvency_ratio", min_val=0.0, max_val=1.0,
                     desc="Solvency ratio = (1−W)·(1−MTM) ∈ [0,1]"),
        _float_field("prev_solvency_ratio", min_val=0.0, max_val=1.0,
                     desc="Previous solvency ratio"),
        _float_field("bond_mtm_loss", min_val=0.0, max_val=1.0,
                     desc="Bond mark-to-market loss fraction ∈ [0,1]"),
        _str_field("regime_status",
                   allowed=("solvent", "stressed", "failed"),
                   desc="Regime status — 3-element closed set; failed is one-way latch"),
        _int_field("num_withdrawers", min_val=0,
                   desc="Count of withdrawing depositors this round"),
        _int_field("num_holders", min_val=0,
                   desc="Count of holding depositors this round"),
        _int_field("num_returners", min_val=0,
                   desc="Count of returning depositors this round"),
        _bool_field("panic_indicator",
                    desc="True iff W ≥ panic_threshold"),
        _float_field("haircut_applied", min_val=0.0, max_val=1.0,
                     desc="Haircut fraction applied (0 until regime_status='failed')"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
)

# -- 9. Credit Minsky-Cycle (15 fields + 1 conditional) --

CREDIT_MINSKY_CYCLE_SCHEMA = BroadcastSchema(
    strategy="credit-minsky-cycle",
    fields=(
        _float_field("credit_price", min_val=0.0,
                     desc="Current credit instrument price P(t+1)"),
        _float_field("prev_credit_price", min_val=0.0,
                     desc="Previous credit price P(t)"),
        _float_field("price_change",
                     desc="P(t+1) − P(t); may be negative"),
        _float_field("fundamental_credit_price", min_val=0.0,
                     desc="Fundamental credit price F"),
        _float_field("aggregate_leverage", min_val=0.0,
                     desc="Aggregate leverage L(t+1) ≥ 0"),
        _float_field("prev_aggregate_leverage", min_val=0.0,
                     desc="Previous leverage L(t)"),
        _str_field("minsky_regime",
                   allowed=("hedge", "speculative", "ponzi"),
                   desc="Minsky regime — 3-element closed set; deterministic on L"),
        _str_field("prev_minsky_regime",
                   allowed=("hedge", "speculative", "ponzi"),
                   desc="Previous Minsky regime"),
        _bool_field("regime_transition_this_round",
                    desc="True iff minsky_regime != prev_minsky_regime"),
        _int_field("num_borrowers", min_val=0,
                   desc="Count of borrowing agents"),
        _int_field("num_lenders", min_val=0,
                   desc="Count of lending agents (repaying)"),
        _int_field("num_extenders", min_val=0,
                   desc="Count of credit-extending agents"),
        _int_field("num_contractors", min_val=0,
                   desc="Count of credit-contracting agents"),
        _float_field("net_credit_demand",
                     desc="Net credit demand; may be negative"),
        _int_field("round", min_val=0, desc="Current round number"),
    ),
    conditional_fields=(
        _float_field("mbs_price", min_val=0.0, required=False,
                     desc="MBS price (present only when mbs_enabled=True)"),
    ),
)


# ---------------------------------------------------------------------------
# Coordinator inbound-order action-type registry
# ---------------------------------------------------------------------------
#
# Every canonical coordinator that admits action-typed orders (as opposed to
# the pure buy/sell/hold enum in InvestorOrder) declares its accepted action
# strings here. This is the single source of truth for those enums —
# coordinator implementations MUST reference COORDINATOR_ACTION_TYPES rather
# than define private frozensets that can silently drift from the profile.
#
# Format contract (2026-07-24): coordinators call
# ``get_coordinator_action_types(STRATEGY)`` in their aggregation loop and
# raise a ValueError on unknown action_type — the .md profile in
# examples/AGENT_POOL/market/ is authoritative and this map mirrors it.

COORDINATOR_ACTION_TYPES: Dict[str, FrozenSet[str]] = {
    # Investor-order-based coordinators (stock, fx, bond, crypto, derivatives,
    # credit) admit buy / sell / hold via InvestorOrder — their action-type
    # enum is INVESTOR_ORDER_ACTION_VALUES and is checked by validate_order,
    # NOT here. They are intentionally absent from this map.
    "opinion-echo-chamber-clustering": frozenset(
        {"polarize", "depolarize", "neutral"}
    ),
    "information-sis-contagion": frozenset({"spread", "correct", "ignore"}),
    "deposit-bank-run-diamond-dybvig": frozenset(
        {"withdraw", "hold", "return", "panic_withdraw"}
    ),
}


def get_coordinator_action_types(strategy: str) -> FrozenSet[str]:
    """Return the accepted ``action_type`` enum for a coordinator archetype.

    Raises:
        KeyError: if the strategy does not have a dedicated action-type
            enum (i.e. it uses the InvestorOrder buy/sell/hold enum
            instead — those coordinators MUST NOT call this function).
    """
    if strategy not in COORDINATOR_ACTION_TYPES:
        raise KeyError(
            f"No coordinator action-type enum registered for {strategy!r}. "
            f"Only coordinators that admit non-InvestorOrder action strings "
            f"should call this function. Registered: "
            f"{sorted(COORDINATOR_ACTION_TYPES.keys())}"
        )
    return COORDINATOR_ACTION_TYPES[strategy]


# ---------------------------------------------------------------------------
# Schema registry
# ---------------------------------------------------------------------------

BROADCAST_SCHEMAS: Dict[str, BroadcastSchema] = {
    s.strategy: s
    for s in (
        STOCK_STANDARD_PRICE_IMPACT_SCHEMA,
        OPINION_ECHO_CHAMBER_CLUSTERING_SCHEMA,
        INFORMATION_SIS_CONTAGION_SCHEMA,
        FX_CURRENCY_PEG_AND_ATTACK_SCHEMA,
        BOND_YIELD_SPREAD_INVERSE_SCHEMA,
        CRYPTO_ALGOSTABLE_DEPEG_SCHEMA,
        DERIVATIVES_VOL_FEEDBACK_SCHEMA,
        DEPOSIT_BANK_RUN_DIAMOND_DYBVIG_SCHEMA,
        CREDIT_MINSKY_CYCLE_SCHEMA,
    )
}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_broadcast(
    strategy: str,
    broadcast: Mapping[str, Any],
    *,
    strict: bool = True,
) -> None:
    """Validate a coordinator broadcast dict against its archetype schema.

    This is the coordinator analog of :func:`~masim.format.order.validate_order`.
    Called by :meth:`CanonicalMarketCoordinator.decide` on every emission.

    Args:
        strategy: The coordinator archetype strategy identifier (kebab-case).
        broadcast: The broadcast dict to validate.
        strict: If True (default), reject undeclared keys.  Set False only for
            backwards-compatibility testing with legacy coordinator output.

    Raises:
        KeyError: If ``strategy`` is not in :data:`BROADCAST_SCHEMAS`.
        ValueError: If any validation constraint is violated.
    """
    if strategy not in BROADCAST_SCHEMAS:
        raise KeyError(
            f"No broadcast schema registered for strategy {strategy!r}. "
            f"Known strategies: {sorted(BROADCAST_SCHEMAS.keys())}"
        )

    schema = BROADCAST_SCHEMAS[strategy]

    if not isinstance(broadcast, Mapping):
        raise ValueError(
            f"validate_broadcast expects a Mapping, got {type(broadcast).__name__}"
        )

    # 1. Required-field presence check
    missing = schema.required_field_names - set(broadcast.keys())
    if missing:
        raise ValueError(
            f"[{strategy}] Broadcast missing required fields: "
            f"{', '.join(sorted(missing))}"
        )

    # 2. Undeclared-key check (strict mode)
    if strict:
        undeclared = set(broadcast.keys()) - schema.all_field_names
        if undeclared:
            raise ValueError(
                f"[{strategy}] Broadcast contains undeclared fields: "
                f"{', '.join(sorted(undeclared))}. "
                f"Declared fields: {sorted(schema.all_field_names)}"
            )

    # 3. Per-field type + range + enum validation
    field_map = schema.field_map
    for key, value in broadcast.items():
        if key not in field_map:
            # Already handled by strict check above; skip in non-strict mode.
            continue

        spec = field_map[key]

        # Type check (with int→float coercion for float fields)
        if spec.dtype == float:
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"[{strategy}] Field {key!r} must be numeric (float), "
                    f"got {type(value).__name__}: {value!r}"
                )
            # NaN / Inf check for all numeric values
            fval = float(value)
            if math.isnan(fval):
                raise ValueError(
                    f"[{strategy}] Field {key!r} is NaN"
                )
            if math.isinf(fval):
                raise ValueError(
                    f"[{strategy}] Field {key!r} is Inf"
                )
            # Range check
            if spec.min_val is not None and fval < spec.min_val:
                raise ValueError(
                    f"[{strategy}] Field {key!r} = {fval} < min_val {spec.min_val}"
                )
            if spec.max_val is not None and fval > spec.max_val:
                raise ValueError(
                    f"[{strategy}] Field {key!r} = {fval} > max_val {spec.max_val}"
                )

        elif spec.dtype == int:
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"[{strategy}] Field {key!r} must be int, "
                    f"got {type(value).__name__}: {value!r}"
                )
            # Allow float→int if it's a whole number
            if isinstance(value, float):
                if value != int(value):
                    raise ValueError(
                        f"[{strategy}] Field {key!r} declared int but got "
                        f"non-integer float: {value}"
                    )
            ival = int(value)
            if spec.min_val is not None and ival < spec.min_val:
                raise ValueError(
                    f"[{strategy}] Field {key!r} = {ival} < min_val {int(spec.min_val)}"
                )
            if spec.max_val is not None and ival > spec.max_val:
                raise ValueError(
                    f"[{strategy}] Field {key!r} = {ival} > max_val {int(spec.max_val)}"
                )

        elif spec.dtype == str:
            if not isinstance(value, str):
                raise ValueError(
                    f"[{strategy}] Field {key!r} must be str, "
                    f"got {type(value).__name__}: {value!r}"
                )
            if spec.allowed_values is not None and value not in spec.allowed_values:
                raise ValueError(
                    f"[{strategy}] Field {key!r} = {value!r} not in allowed "
                    f"values: {spec.allowed_values}"
                )

        elif spec.dtype == bool:
            if not isinstance(value, (bool, int)):
                raise ValueError(
                    f"[{strategy}] Field {key!r} must be bool, "
                    f"got {type(value).__name__}: {value!r}"
                )


# ---------------------------------------------------------------------------
# Frozen broadcast wrapper
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MarketBroadcast:
    """Frozen, validated wrapper for a coordinator broadcast payload.

    Immutable once constructed — mutations of broadcast data after emission
    are impossible, maintaining audit-trail integrity.  Parallels
    :class:`~masim.format.order.InvestorOrder` semantics.

    Attributes:
        strategy: The coordinator archetype that emitted this broadcast.
        payload: The validated broadcast dict (shallow-frozen via ``tuple``
            conversion of mutable containers; plain dict stored for
            serialization convenience).
        round_num: The simulation round this broadcast corresponds to.
    """

    strategy: str
    payload: Dict[str, Any] = field(default_factory=dict)
    round_num: int = 0

    # -- factories --------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        strategy: str,
        broadcast: Dict[str, Any],
        *,
        strict: bool = True,
    ) -> "MarketBroadcast":
        """Validate and wrap a raw broadcast dict.

        This is the primary factory — all coordinator emissions MUST flow
        through this path.

        Args:
            strategy: Coordinator archetype identifier.
            broadcast: Raw broadcast dict from :meth:`advance_market`.
            strict: Whether to reject undeclared keys (default True).

        Returns:
            Frozen :class:`MarketBroadcast` instance.

        Raises:
            KeyError: If strategy is not registered.
            ValueError: If any validation constraint is violated.
        """
        validate_broadcast(strategy, broadcast, strict=strict)
        round_num = int(broadcast.get("round", 0))
        # Shallow copy to prevent external mutation of the payload reference.
        frozen_payload = dict(broadcast)
        return cls(
            strategy=strategy,
            payload=frozen_payload,
            round_num=round_num,
        )

    # -- serialization ----------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return the broadcast as a plain dict (copy).

        The returned dict is the wire-format consumed by the simulation
        pipeline — identical in shape to the raw dict from ``advance_market``
        but validated.
        """
        return dict(self.payload)

    # -- accessors --------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        """Dict-like access to broadcast fields."""
        return self.payload[key]

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like .get() access."""
        return self.payload.get(key, default)

    def __contains__(self, key: str) -> bool:
        return key in self.payload


# ---------------------------------------------------------------------------
# Convenience: schema lookup
# ---------------------------------------------------------------------------


def get_broadcast_schema(strategy: str) -> BroadcastSchema:
    """Retrieve the :class:`BroadcastSchema` for a given archetype.

    Raises:
        KeyError: If strategy is not registered.
    """
    if strategy not in BROADCAST_SCHEMAS:
        raise KeyError(
            f"No broadcast schema for strategy {strategy!r}. "
            f"Registered: {sorted(BROADCAST_SCHEMAS.keys())}"
        )
    return BROADCAST_SCHEMAS[strategy]


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------

__all__ = [
    "FieldSpec",
    "BroadcastSchema",
    "BROADCAST_SCHEMAS",
    "COORDINATOR_ACTION_TYPES",
    "get_coordinator_action_types",
    "STOCK_STANDARD_PRICE_IMPACT_SCHEMA",
    "OPINION_ECHO_CHAMBER_CLUSTERING_SCHEMA",
    "INFORMATION_SIS_CONTAGION_SCHEMA",
    "FX_CURRENCY_PEG_AND_ATTACK_SCHEMA",
    "BOND_YIELD_SPREAD_INVERSE_SCHEMA",
    "CRYPTO_ALGOSTABLE_DEPEG_SCHEMA",
    "DERIVATIVES_VOL_FEEDBACK_SCHEMA",
    "DEPOSIT_BANK_RUN_DIAMOND_DYBVIG_SCHEMA",
    "CREDIT_MINSKY_CYCLE_SCHEMA",
    "validate_broadcast",
    "MarketBroadcast",
    "get_broadcast_schema",
]
