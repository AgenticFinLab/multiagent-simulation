"""Investor order format — the single source of truth for agent output.

Every canonical agent (Rule or LLM) in :mod:`masim.agents` MUST return orders
constructed through this module.  Hand-rolled dicts are still accepted for
backwards compatibility; common LLM sign/zero representation drift is
canonicalised and other schema drift is rejected by :func:`validate_order`.

Public surface
--------------

* :class:`InvestorOrder` — frozen dataclass carrying the full order payload.
  Use one of the classmethod factories (:meth:`InvestorOrder.hold`,
  :meth:`InvestorOrder.buy`, :meth:`InvestorOrder.sell`,
  :meth:`InvestorOrder.from_llm_decision`, :meth:`InvestorOrder.noop`) to
  build an instance; direct construction is discouraged.
* :func:`validate_order` — legacy dict validator, retained so downstream
  code that still consumes raw dicts (bundle writers, format-drift tests)
  keeps working.
* :data:`INVESTOR_ORDER_REQUIRED_FIELDS`, :data:`INVESTOR_ORDER_ACTION_VALUES`
  — the format schema constants; these are what
  :meth:`InvestorOrder.to_dict` guarantees.

Contract summary (mirrors ``masim/agents/defines`` §I/O Contract)
----------------------------------------------------------------

Required fields on the wire (dict form):
    ``action``      — one of ``"buy"``, ``"sell"``, ``"hold"``
    ``quantity``    — non-negative float (0 iff action == hold)
    ``bid_price``   — positive float (execution reference price)
    ``investor``    — the emitting player identity
    ``strategy``    — the canonical archetype STRATEGY (kebab stem)

Optional fields:
    ``reasoning``       — short audit trail (≤200 chars enforced by base class)
    ``analysis``        — LLM chain-of-thought (≤1000 chars, LLM path only)
    ``_skipped``        — True for bootstrap-round no-op placeholders
    ``_skipped_reason`` — why the placeholder was emitted
    ``_clipped``        — True when the base class clipped down the size
    ``_clipped_from``   — original action before clipping
    ``_clipped_intended_quantity`` — original quantity before clipping
    ``_clipped_reason`` — free-form reason string
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Set

INVESTOR_ORDER_REQUIRED_FIELDS: List[str] = [
    "action",
    "quantity",
    "investor",
    "strategy",
]

INVESTOR_ORDER_ACTION_VALUES: Set[str] = {"buy", "sell", "hold"}

# Constants used by the LLM path when parsing/serialising raw model output.
BUY: str = "buy"
SELL: str = "sell"
HOLD: str = "hold"


def normalize_action_quantity(action: Any, quantity: Any) -> tuple[str, float]:
    """Return canonical action and non-negative order size.

    LLMs commonly express sells with a negative quantity or emit a zero-size
    buy/sell.  The wire contract uses a separate action field and therefore
    always stores quantity as a non-negative magnitude.  A zero-size trade is
    semantically a hold.
    """
    normalized_action = str(action).lower().strip()
    try:
        magnitude = abs(float(quantity))
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Quantity must be numeric, got {type(quantity).__name__}"
        ) from exc

    if normalized_action == HOLD or magnitude == 0:
        return HOLD, 0.0
    return normalized_action, magnitude


def signed_order_quantity(order: Mapping[str, Any]) -> float:
    """Read an order quantity using a signed value for legacy market math."""
    quantity = float(order.get("quantity", 0.0) or 0.0)
    action = str(order.get("action", "")).lower().strip()
    if action == BUY:
        return abs(quantity)
    if action == SELL:
        return -abs(quantity)
    if action == HOLD:
        return 0.0
    return quantity


# ---------------------------------------------------------------------------
# Structured order
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InvestorOrder:
    """Structured investor decision, format-locked.

    Frozen so orders cannot be mutated after emission — this makes the audit
    trail reliable and prevents the pipeline from silently rewriting quantities
    downstream. Emit new instances via ``dataclasses.replace`` when the base
    class needs to clip.

    All numeric fields are stored as ``float`` for pipeline homogeneity even
    if the caller passed ``int`` (see :meth:`_normalise_quantity`).
    """

    action: str
    quantity: float
    bid_price: float
    investor: str
    strategy: str
    reasoning: str = ""
    analysis: str = ""
    # Bookkeeping flags — populated by :mod:`masim.agents._base` when it
    # clips a buy/sell to a hold or shrinks the size for cash/inventory.
    skipped: bool = False
    skipped_reason: str = ""
    clipped: bool = False
    clipped_from: str = ""
    clipped_intended_quantity: float = 0.0
    clipped_reason: str = ""
    # Free-form extras (rarely used; e.g. cost-basis annotation for
    # DispositionTrader). Kept as a plain dict so the frozen dataclass
    # stays hashable-adjacent while allowing agents to attach metadata
    # without extending the schema. Do NOT rely on this for
    # protocol-required fields.
    extras: Mapping[str, Any] = field(default_factory=dict)

    # -- factories --------------------------------------------------------

    @classmethod
    def hold(
        cls,
        *,
        price: float,
        investor: str = "",
        strategy: str = "",
        reasoning: str = "",
    ) -> "InvestorOrder":
        """Build a HOLD order (quantity = 0, bid_price = reference price)."""
        return cls(
            action=HOLD,
            quantity=0.0,
            bid_price=cls._normalise_price(price),
            investor=investor,
            strategy=strategy,
            reasoning=reasoning,
        )

    @classmethod
    def buy(
        cls,
        *,
        quantity: float,
        price: float,
        investor: str = "",
        strategy: str = "",
        reasoning: str = "",
    ) -> "InvestorOrder":
        """Build a BUY order (quantity > 0, price > 0).

        Fail-loud on ``price <= 0``: a BUY order without a positive
        execution reference price is meaningless and produces silent
        ``fill_price = 0`` cash bookkeeping downstream. Callers with a
        genuinely unknown reference should emit a HOLD (or a ``noop``
        for the bootstrap round) instead.
        """
        normalised_price = cls._require_positive_price(price, action=BUY)
        return cls(
            action=BUY,
            quantity=cls._normalise_quantity(quantity),
            bid_price=normalised_price,
            investor=investor,
            strategy=strategy,
            reasoning=reasoning,
        )

    @classmethod
    def sell(
        cls,
        *,
        quantity: float,
        price: float,
        investor: str = "",
        strategy: str = "",
        reasoning: str = "",
    ) -> "InvestorOrder":
        """Build a SELL order (quantity > 0, price > 0).

        See :meth:`InvestorOrder.buy` for the fail-loud rationale on
        ``price <= 0``.
        """
        normalised_price = cls._require_positive_price(price, action=SELL)
        return cls(
            action=SELL,
            quantity=cls._normalise_quantity(quantity),
            bid_price=normalised_price,
            investor=investor,
            strategy=strategy,
            reasoning=reasoning,
        )

    @classmethod
    def noop(
        cls,
        *,
        investor: str,
        strategy: str,
        reason: str = "no_market_data",
    ) -> "InvestorOrder":
        """Build a bootstrap-round no-op order.

        Bootstrap rounds are those where the agent has not yet received a
        market broadcast. Emitting a real HOLD here would pollute downstream
        statistics; this factory sets ``skipped=True`` so audit passes can
        exclude the placeholder from metrics.
        """
        return cls(
            action=HOLD,
            quantity=0.0,
            bid_price=0.0,
            investor=investor,
            strategy=strategy,
            skipped=True,
            skipped_reason=reason,
        )

    @classmethod
    def from_llm_decision(
        cls,
        decision: Mapping[str, Any],
        *,
        investor: str,
        strategy: str,
    ) -> "InvestorOrder":
        """Build an order from a validated LLM ``<decision>`` JSON payload.

        Preconditions
        -------------
        ``decision`` MUST already have been validated by the category
        validator registered in :data:`masim.format.SCENARIO_ORDER_FORMAT`
        (this is what :func:`masim.utils.llm_utils.robust_llm_call` does via
        its ``validate_fn`` parameter — a failing decision triggers a retry,
        so by the time this factory runs, every required field is present
        and well-typed).  Consequently this factory performs NO silent
        defaulting: missing ``bid_price`` is not filled with ``market_price``,
        and quantity sign / zero-out drift is not silently rewritten.

        Extras preservation
        -------------------
        Any field in ``decision`` that is not part of the canonical order
        schema (e.g. ``provides_liquidity`` for the maker/taker category) is
        preserved in :attr:`extras` so downstream consumers that know the
        category can read it back out via :meth:`to_dict`.
        """
        action = str(decision["action"]).lower().strip()
        quantity = float(decision.get("quantity", 0.0) or 0.0)

        # ``bid_price`` is only part of some categories (limit_order,
        # maker_taker_order); it is absent from participation_order. The
        # validator has already enforced this — here we simply mirror what
        # the validator accepted, defaulting to 0.0 when the field is not in
        # the schema at all (participation_order market coordinators ignore
        # bid_price anyway).
        bid_price_raw = decision.get("bid_price")
        bid_price = float(bid_price_raw) if bid_price_raw is not None else 0.0

        reasoning = str(decision.get("reasoning", ""))[:200]
        analysis = str(decision.get("analysis", ""))[:1000]

        # Everything the validator accepted that is NOT part of the base
        # schema (action / bid_price / quantity / reasoning / analysis) is
        # forwarded through ``extras`` so category-specific extensions
        # survive the round-trip to the wire.
        _KNOWN = {"action", "bid_price", "quantity", "reasoning", "analysis"}
        extras = {k: v for k, v in decision.items() if k not in _KNOWN}

        return cls(
            action=action,
            quantity=cls._normalise_quantity(quantity),
            bid_price=cls._normalise_price(bid_price),
            investor=investor,
            strategy=strategy,
            reasoning=reasoning,
            analysis=analysis,
            extras=extras,
        )

    @classmethod
    def from_dict(cls, order: Mapping[str, Any]) -> "InvestorOrder":
        """Recover an :class:`InvestorOrder` from a plain dict payload.

        Backwards-compatibility bridge for older Rule agents that still
        return raw dicts; the :mod:`masim.agents._base` finaliser calls this
        to normalise everything to the structured form before validation.
        """
        action = str(order.get("action", HOLD)).lower().strip()
        try:
            quantity = float(order.get("quantity", 0.0) or 0.0)
        except (TypeError, ValueError):
            quantity = 0.0
        raw_bid = order.get("bid_price")
        try:
            bid_price = float(raw_bid) if raw_bid is not None else 0.0
        except (TypeError, ValueError):
            bid_price = 0.0
        # Fail-loud contract: BUY/SELL orders reaching from_dict MUST already
        # carry a strictly positive bid_price. The historical silent clamp to
        # zero has been removed so scenario code that produces an invalid
        # BUY/SELL dict is surfaced immediately instead of laundered through
        # a hold-shaped record. HOLD orders may still carry a non-positive
        # bid_price for legacy disk-restore paths (normalised to >= 0).
        if action in (BUY, SELL):
            bid_price = cls._require_positive_price(bid_price, action=action)
            normalised_bid = bid_price
        else:
            normalised_bid = cls._normalise_price(bid_price) if bid_price > 0 else 0.0
        return cls(
            action=action,
            quantity=cls._normalise_quantity(quantity) if quantity > 0 else 0.0,
            bid_price=normalised_bid,
            investor=str(order.get("investor", "")),
            strategy=str(order.get("strategy", "")),
            reasoning=str(order.get("reasoning", ""))[:200],
            analysis=str(order.get("analysis", ""))[:1000],
            skipped=bool(order.get("_skipped", False)),
            skipped_reason=str(order.get("_skipped_reason", "")),
            clipped=bool(order.get("_clipped", False)),
            clipped_from=str(order.get("_clipped_from", "")),
            clipped_intended_quantity=float(
                order.get("_clipped_intended_quantity", 0.0) or 0.0
            ),
            clipped_reason=str(order.get("_clipped_reason", "")),
        )

    # -- serialization ----------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to the wire-format dict consumed by the pipeline.

        The keys are the exact set advertised in the module docstring; the
        underscore-prefixed bookkeeping flags are only included when set,
        so vanilla orders stay small.
        """
        out: Dict[str, Any] = {
            "action": self.action,
            "quantity": float(self.quantity),
            "bid_price": float(self.bid_price),
            "investor": self.investor,
            "strategy": self.strategy,
        }
        if self.reasoning:
            out["reasoning"] = self.reasoning
        if self.analysis:
            out["analysis"] = self.analysis
        if self.skipped:
            out["_skipped"] = True
            if self.skipped_reason:
                out["_skipped_reason"] = self.skipped_reason
        if self.clipped:
            out["_clipped"] = True
            if self.clipped_from:
                out["_clipped_from"] = self.clipped_from
            if self.clipped_intended_quantity:
                out["_clipped_intended_quantity"] = float(
                    self.clipped_intended_quantity
                )
            if self.clipped_reason:
                out["_clipped_reason"] = self.clipped_reason
        if self.extras:
            for k, v in self.extras.items():
                out.setdefault(k, v)
        return out

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _normalise_quantity(q: Any) -> float:
        try:
            value = float(q)
        except (TypeError, ValueError):
            return 0.0
        return max(value, 0.0)

    @staticmethod
    def _normalise_price(p: Any) -> float:
        try:
            value = float(p)
        except (TypeError, ValueError):
            return 0.0
        return max(value, 0.0)

    @staticmethod
    def _require_positive_price(p: Any, *, action: str) -> float:
        """Return ``float(p)`` iff strictly positive; fail-loud otherwise.

        Used by :meth:`InvestorOrder.buy` and :meth:`InvestorOrder.sell`
        to reject nonsense reference prices at construction time. The
        historical :meth:`_normalise_price` — which silently clamped
        negatives to zero — is preserved for legacy dict-restoration
        paths (:meth:`from_dict`) where zeroing a bogus value keeps the
        downstream ``validate_order`` diagnostics readable.
        """
        try:
            value = float(p)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"InvestorOrder.{action}: price must be numeric, got "
                f"{p!r} ({type(p).__name__})."
            ) from exc
        if value <= 0:
            raise ValueError(
                f"InvestorOrder.{action}: price must be strictly positive, "
                f"got {value!r}. A {action.upper()} order without a "
                f"positive reference price would produce silent "
                f"fill_price=0 cash bookkeeping downstream — emit a HOLD "
                f"(or InvestorOrder.noop for the bootstrap round) instead."
            )
        return value

    # -- assertions -------------------------------------------------------

    def assert_valid(self) -> None:
        """Run the wire-format validator on ``self.to_dict()``.

        Convenience so callers that hold an ``InvestorOrder`` — rather
        than a raw dict — can trigger the same strict schema check that
        the pipeline runs at emission time. Raises :class:`ValueError`
        on any violation.
        """
        validate_order(self.to_dict())


# ---------------------------------------------------------------------------
# Legacy dict validator
# ---------------------------------------------------------------------------


def validate_order(order: Any) -> None:
    """Validate an investor order against the required schema.

    Accepts either a raw ``dict`` or an :class:`InvestorOrder` (converted via
    :meth:`InvestorOrder.to_dict` first). The check is intentionally strict:
    the schema is a public contract and downstream analytics assume it.  For
    legacy LLM dicts, signed quantities and zero-size trades are canonicalised
    in place before the strict checks run.

    Raises:
        ValueError: If any required field is missing or has an invalid value.
    """
    if isinstance(order, InvestorOrder):
        order = order.to_dict()
    if not isinstance(order, Mapping):
        raise ValueError(
            f"validate_order expects dict or InvestorOrder, got {type(order).__name__}"
        )

    missing = [f for f in INVESTOR_ORDER_REQUIRED_FIELDS if f not in order]
    if missing:
        raise ValueError(f"Order missing required fields: {', '.join(missing)}")

    action = order["action"]
    if action not in INVESTOR_ORDER_ACTION_VALUES:
        raise ValueError(
            f"Invalid action '{action}'. Must be one of: "
            f"{', '.join(sorted(INVESTOR_ORDER_ACTION_VALUES))}"
        )

    quantity = order["quantity"]
    if not isinstance(quantity, (int, float)):
        raise ValueError(f"Quantity must be numeric, got {type(quantity).__name__}")

    # Canonicalise the two harmless representation drifts most often produced
    # by LLMs.  Dicts are intentionally updated in place so the validated wire
    # payload is the same object later sent to the market.
    normalized_action, normalized_quantity = normalize_action_quantity(
        action, quantity
    )
    if isinstance(order, dict):
        order["action"] = normalized_action
        order["quantity"] = normalized_quantity
    action = normalized_action
    quantity = normalized_quantity

    if action == HOLD and quantity != 0:
        raise ValueError(
            f"HOLD orders must have quantity=0, got {quantity}"
        )
    if action in (BUY, SELL) and quantity == 0 and not order.get("_clipped"):
        # A buy/sell with quantity==0 is only allowed via the clipping path
        # (base class marks it explicitly). Any other zero-size buy/sell is
        # almost certainly a bug in the agent.
        raise ValueError(
            f"{action.upper()} orders must have quantity > 0 (or be marked _clipped)"
        )

    bid_price = order.get("bid_price")
    if bid_price is not None:
        if not isinstance(bid_price, (int, float)):
            raise ValueError(
                f"bid_price must be numeric, got {type(bid_price).__name__}"
            )
        if bid_price < 0:
            raise ValueError(f"bid_price must be non-negative, got {bid_price}")
        if action in (BUY, SELL) and bid_price <= 0 and not order.get("_skipped"):
            raise ValueError(
                f"{action.upper()} orders require positive bid_price, got {bid_price}"
            )


__all__ = [
    "INVESTOR_ORDER_REQUIRED_FIELDS",
    "INVESTOR_ORDER_ACTION_VALUES",
    "BUY",
    "SELL",
    "HOLD",
    "normalize_action_quantity",
    "signed_order_quantity",
    "InvestorOrder",
    "validate_order",
]
