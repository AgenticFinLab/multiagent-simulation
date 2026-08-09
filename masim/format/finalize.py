"""Centralised order-finalisation helpers — the single point of truth for
the *clip → validate → emit* pipeline that every canonical agent (Rule /
LLM / RAG) — and any scenario code that reimplements ``perceive/decide``
— must funnel through.

Design rationale
----------------

Historically the finalisation logic lived on the canonical bases
(``CanonicalRulePlayer._finalize_order`` and
``CanonicalLLMPlayer._finalize_llm_order``).  This module extracts that
logic into pure, importable functions so:

*   The fail-loud rules (positive ``bid_price`` on non-hold orders,
    strict schema on the wire payload) are enforced in **one file** —
    ``masim.format`` is the natural home because it already owns the
    format contracts (``InvestorOrder``, ``validate_order``,
    ``limit_order.validate_decision``).
*   Any scenario ``players.py`` that legitimately reimplements the
    ``perceive/decide/act`` skeleton (e.g. bespoke RAG plumbing, custom
    memory pipelines) can ``from masim.format import ...`` these helpers
    and never re-derive the wire semantics.
*   The canonical bases themselves become thin wrappers, which
    guarantees that Rule / LLM / RAG code paths cannot drift apart on
    order semantics.

Public helpers
--------------

* :func:`require_positive_bid_price` — strict guard used at every emit site.
* :func:`clip_order_to_liquidity` — the pure clip-to-cash/inventory transform.
* :func:`finalize_rule_order` — Rule-path finaliser (fills bid_price from
  ``state.price`` when the subclass omitted / zero-defaulted it — the
  original Rule-path semantics, unchanged).
* :func:`finalize_llm_order` — LLM-path finaliser (category-aware:
  limit_order / maker_taker_order MUST arrive with ``bid_price > 0``
  because the LLM schema validator already enforced this; the substitute
  from ``state.price`` is allowed only for participation_order where
  ``bid_price`` is not part of the schema).
* :func:`emit_order_envelope` — build the wire dict (payload +
  ``outbound_messages``) that the pipeline consumes.

There is intentionally **no silent-fill anywhere in this module**.
Every substitution that does occur (participation_order fills bid_price
from state.price) is *explicit*, category-scoped, and documented at the
substitution site.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Mapping, Optional, Union

from masim.format.order import (
    BUY,
    HOLD,
    SELL,
    InvestorOrder,
    validate_order,
)


# ---------------------------------------------------------------------------
# Strict guards
# ---------------------------------------------------------------------------


def require_positive_bid_price(
    bid_price: Any,
    action: Any,
    *,
    context: str = "",
) -> float:
    """Return ``float(bid_price)`` iff the (action, bid_price) pair is valid.

    Contract
    --------
    * ``action == HOLD``      → any non-negative ``bid_price`` is accepted;
      returned as ``float``.
    * ``action in (BUY, SELL)`` → ``bid_price`` MUST be a strictly positive
      finite number; otherwise raises :class:`ValueError`.

    This is the ONE fail-loud check every emit site (Rule / LLM / RAG /
    hand-written scenario code) MUST invoke before serialising an order.
    Silent fallback to ``state.price`` — historically implemented ad-hoc
    inside individual scenarios — is explicitly forbidden here; callers
    that need a category-aware substitution should go through
    :func:`finalize_llm_order` which documents the participation_order
    exception in one place.

    Parameters
    ----------
    bid_price
        Raw ``bid_price`` produced by the agent (LLM decision dict or
        Rule ``decide_order`` return value).
    action
        Canonical action string; must be one of ``"buy"``, ``"sell"``,
        ``"hold"`` (case-normalisation is the caller's responsibility —
        the canonical bases already normalise via
        :meth:`InvestorOrder.from_llm_decision`).
    context
        Free-form label included in the error message so failures point
        at the emit site (e.g. ``"AnchoringEffect.LLM/LLMAnchoredTrader"``).
    """
    try:
        price = float(bid_price)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"require_positive_bid_price[{context or 'unknown'}]: "
            f"bid_price must be numeric, got {bid_price!r} "
            f"({type(bid_price).__name__})."
        ) from exc
    normalized_action = str(action).lower().strip()
    if normalized_action == HOLD:
        if price < 0:
            raise ValueError(
                f"require_positive_bid_price[{context or 'unknown'}]: "
                f"HOLD orders may carry a zero or positive bid_price for "
                f"audit purposes, but negative values are not allowed "
                f"(got {price!r})."
            )
        return price
    if normalized_action in (BUY, SELL):
        if price <= 0:
            raise ValueError(
                f"require_positive_bid_price[{context or 'unknown'}]: "
                f"{normalized_action.upper()} orders REQUIRE bid_price > 0. "
                f"Got {price!r}. The LLM schema validator "
                f"(masim.format.limit_order.validate_decision) already "
                f"enforces this at LLM output; a zero/negative value "
                f"reaching this guard indicates the validator was "
                f"bypassed or the scenario code short-circuited it. "
                f"Silent fallback to state.price is forbidden — fix the "
                f"upstream emit path."
            )
        return price
    raise ValueError(
        f"require_positive_bid_price[{context or 'unknown'}]: "
        f"unknown action {action!r}; expected one of buy/sell/hold."
    )


# ---------------------------------------------------------------------------
# Pure order transforms
# ---------------------------------------------------------------------------


def clip_order_to_liquidity(
    order: InvestorOrder,
    *,
    cash: float,
    position: float,
    bid_price: float,
) -> InvestorOrder:
    """Clip a buy/sell order to available cash / inventory.

    Returns a new :class:`InvestorOrder`; the original is unchanged (the
    dataclass is frozen, so mutation is impossible anyway — we call
    :func:`dataclasses.replace` to build the successor).

    Semantics (unchanged from the historical canonical bases):

    * BUY: quantity clipped to ``cash / bid_price`` when insufficient cash.
    * SELL: quantity clipped to ``position`` when insufficient inventory.
    * If the clipped quantity is zero and the original action was
      BUY/SELL, the order becomes a HOLD but the ``clipped_from`` /
      ``clipped_intended_quantity`` fields are populated so downstream
      behavioural metrics (action_frequency, decision_entropy) can still
      distinguish a clipped-to-zero decision from a genuine HOLD.
    """
    original_action = order.action
    original_quantity = float(order.quantity or 0.0)

    action = original_action
    quantity = original_quantity
    clipped = False
    clipped_reason = ""

    if action == BUY and quantity > 0:
        affordable = cash / bid_price if bid_price > 0 else 0.0
        new_qty = min(quantity, max(affordable, 0.0))
        if new_qty < quantity:
            clipped = True
            clipped_reason = "insufficient_cash"
        quantity = new_qty
    elif action == SELL and quantity > 0:
        new_qty = min(quantity, max(position, 0.0))
        if new_qty < quantity:
            clipped = True
            clipped_reason = "insufficient_position"
        quantity = new_qty

    clipped_to_hold = False
    if quantity <= 0 and original_action in (BUY, SELL):
        clipped_to_hold = True
        if not clipped_reason:
            clipped_reason = "zero_quantity_after_clip"
        action = HOLD
        quantity = 0.0
    elif quantity <= 0 and action != HOLD:
        action = HOLD
        quantity = 0.0

    result = dataclasses.replace(
        order,
        action=action,
        quantity=float(quantity),
        bid_price=float(bid_price),
    )
    if clipped or clipped_to_hold:
        result = dataclasses.replace(
            result,
            clipped=True,
            clipped_from=original_action,
            clipped_intended_quantity=float(original_quantity),
            clipped_reason=clipped_reason or "unspecified",
        )
    return result


# ---------------------------------------------------------------------------
# Rule / LLM finalisers
# ---------------------------------------------------------------------------


def finalize_rule_order(
    order: InvestorOrder,
    *,
    state,  # StandardMarketState (import-time-cycle-free)
    investor: str,
    strategy: str,
) -> InvestorOrder:
    """Finalise a Rule-agent order.

    Category-aware ``bid_price`` semantics — no silent fallback for BUY/SELL:

    * HOLD orders may legitimately arrive with ``bid_price <= 0``; we
      substitute ``state.price`` so the wire payload carries a
      meaningful reference price for audits.  The substitution is
      explicit and gated on ``action == HOLD``.
    * BUY / SELL orders MUST arrive with a strictly positive
      ``bid_price``.  Rule agents are expected to compute their own
      reference price inside :meth:`decide_order`; a non-positive value
      here indicates a subclass bug (e.g. dividing by an uninitialised
      state field) and is refused via :func:`require_positive_bid_price`
      rather than papered over with ``state.price``.  This mirrors the
      contract of :func:`finalize_llm_order` and the M4 fail-loud
      invariant enforced by :meth:`InvestorOrder.from_dict`.
    """
    original_action = order.action

    if original_action in (BUY, SELL):
        require_positive_bid_price(
            order.bid_price,
            original_action,
            context=f"finalize_rule_order/{strategy or 'unknown'}",
        )
        ref_price = float(order.bid_price)
    else:  # HOLD — explicit, single-site substitution
        ref_price = (
            float(order.bid_price) if order.bid_price > 0 else float(state.price)
        )

    clipped = clip_order_to_liquidity(
        order,
        cash=float(state.cash),
        position=float(state.position),
        bid_price=ref_price,
    )
    finalized = dataclasses.replace(
        clipped,
        investor=investor,
        strategy=strategy or clipped.strategy,
        bid_price=float(ref_price),
    )
    # Defence-in-depth: a BUY/SELL that survived clipping must still be
    # priced.  clip_order_to_liquidity may downgrade a BUY/SELL to HOLD
    # when cash/inventory is exhausted, so we re-check the post-clip
    # action rather than the original one.
    if finalized.action in (BUY, SELL):
        require_positive_bid_price(
            finalized.bid_price,
            finalized.action,
            context=f"finalize_rule_order/defence/{strategy or 'unknown'}",
        )
    validate_order(finalized.to_dict())
    return finalized


def finalize_llm_order(
    order: InvestorOrder,
    *,
    state,  # StandardMarketState
    category: str,
    strategy: str = "",
) -> InvestorOrder:
    """Finalise an LLM-agent order.

    Category-aware ``bid_price`` semantics — no silent fallback:

    * ``limit_order`` / ``maker_taker_order``: the LLM schema validator
      (``limit_order.validate_decision`` /
      ``maker_taker_order.validate_decision``) has already enforced
      ``bid_price > 0`` for every non-hold action.  Any BUY / SELL
      arriving here with ``bid_price <= 0`` indicates the validator was
      bypassed — raise :class:`ValueError` rather than paper over it
      with ``state.price``.
    * ``participation_order``: this category intentionally omits
      ``bid_price`` from the LLM schema; substitute ``state.price``
      *explicitly* so downstream cash bookkeeping still has a numeric
      reference.  The substitution is documented here (single site) and
      is category-gated.
    """
    original_action = order.action

    if category == "participation_order":
        bid_price = float(state.price)
    else:
        if original_action in (BUY, SELL):
            require_positive_bid_price(
                order.bid_price,
                original_action,
                context=f"finalize_llm_order[{category}]/{strategy or 'unknown'}",
            )
        bid_price = float(order.bid_price)

    finalized = clip_order_to_liquidity(
        order,
        cash=float(state.cash),
        position=float(state.position),
        bid_price=bid_price,
    )
    # Defence-in-depth: reject any non-hold order that made it here with
    # bid_price <= 0 despite the category-aware handling above.
    if finalized.action in (BUY, SELL):
        require_positive_bid_price(
            finalized.bid_price,
            finalized.action,
            context=(
                f"finalize_llm_order[{category}]/defence/{strategy or 'unknown'}"
            ),
        )
    validate_order(finalized.to_dict())
    return finalized


# ---------------------------------------------------------------------------
# Wire envelope
# ---------------------------------------------------------------------------


def emit_order_envelope(
    order: InvestorOrder,
    *,
    strip_analysis: bool = True,
    agent_state: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Serialise an :class:`InvestorOrder` for the pipeline.

    Produces the flat ``payload + outbound_messages`` dict that the
    simulator expects. When ``strip_analysis`` is True (default), the
    LLM chain-of-thought (``analysis``) is dropped from the outbound
    copy so downstream market coordinators / peer investors never see
    the agent's internal reasoning — this is the historical Rule/LLM
    base behaviour, preserved.

    ``agent_state`` — when supplied, its keys are merged both into the
    top-level result dict AND into every outbound message payload.
    This is how canonical Rule / LLM bases inject truthful ``cash``,
    ``position``, ``agent_type`` into the wire so market coordinators
    can log real portfolio state rather than fabricate zeroes.
    """
    payload = order.to_dict()
    # `validate_order` is idempotent; running it here means every code
    # path that reaches the network is guaranteed to match the schema
    # regardless of which factory produced the order.
    validate_order(payload)
    outbound_payload = {
        k: v for k, v in payload.items()
        if not (strip_analysis and k == "analysis")
    }
    envelope: Dict[str, Any] = {
        **payload,
        "outbound_messages": [
            {"payload": outbound_payload, "content_type": "investor_bid"}
        ],
    }
    if agent_state:
        envelope.update(agent_state)
        for msg in envelope["outbound_messages"]:
            msg["payload"].update(agent_state)
    return envelope


__all__ = [
    "require_positive_bid_price",
    "clip_order_to_liquidity",
    "finalize_rule_order",
    "finalize_llm_order",
    "emit_order_envelope",
]
