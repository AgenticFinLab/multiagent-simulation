"""Standard market-state contract shared by every canonical agent.

This module is the *single source of truth* for the shape of the market
state that canonical participant agents consume from the broadcast payload.
It lives in :mod:`masim.format` (not :mod:`masim.agents`) so that any
non-agent framework module (evaluators, replayers, dashboards) can build a
:class:`StandardMarketState` from a raw broadcast dict without importing
the agent layer.

Every scenario whose ``market_features`` list is empty is required to
broadcast ``market_data`` payloads with at least the fields enumerated in
:data:`REQUIRED_BROADCAST_FIELDS`. Canonical agents read *only* these
fields, which is what makes them portable between scenarios.

Niche scenarios (e.g. FlashCrash with ``microstructure_book``) attach
extra fields to the same payload; canonical agents ignore them by
consulting them through :attr:`StandardMarketState.raw`.

Fail-loud contract (2026-07-24 revision):

*   ``price`` is the minimum viable market signal. Silent default to 0.0
    would allow "free buys" (fill_price=0) and poison every
    portfolio-based metric — so the factory raises :class:`ValueError`.
*   ``fundamental`` and ``deviation`` may be legitimately absent for
    scenarios that do not model an intrinsic value; the factory then
    stores ``NaN`` (not 0.0) and every downstream metric must treat
    ``NaN`` as "unavailable", not as "at fair price".
*   ``round`` and ``prev_price`` MUST be present in the broadcast; a
    coordinator that omits them has violated the broadcast contract and
    a ``KeyError`` propagates so the bug is caught immediately rather
    than absorbed silently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


#: Fields that every canonical market broadcast MUST populate, regardless
#: of the specific market archetype. Coordinator-specific fields (such as
#: ``polarization`` or ``belief``) are allowed on top but do not appear
#: here — this constant is intentionally the intersection.
REQUIRED_BROADCAST_FIELDS: tuple = ("price", "prev_price", "round")


@dataclass
class StandardMarketState:
    """Per-round snapshot consumed by canonical agents.

    Required fields are populated from the market broadcast and the agent's
    own portfolio state. Optional fields default to ``None`` / empty when the
    scenario does not provide them; agents that depend on them must declare
    that dependency on their canonical Rule class via the
    ``REQUIRES_FEATURES`` class attribute (consumed by
    :mod:`masim.interface.customized.agent_catalog`).
    """

    # --- core market signal (every scenario broadcasts these) ---------------
    round: int
    price: float
    prev_price: float
    fundamental: float
    deviation: float
    price_change: float

    # --- agent portfolio (read from custom_state) ---------------------------
    cash: float
    position: float

    # --- derived convenience field ------------------------------------------
    portfolio_value: float

    # --- optional, scenario-dependent ---------------------------------------
    volatility: Optional[float] = None
    recent_returns: List[float] = field(default_factory=list)

    # --- escape hatch for scenarios that attach extra payload keys ----------
    raw: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    @classmethod
    def from_market_data(
        cls,
        market_data: Dict[str, Any],
        *,
        cash: float,
        position: float,
        recent_returns: Optional[List[float]] = None,
        volatility: Optional[float] = None,
    ) -> "StandardMarketState":
        """Build a :class:`StandardMarketState` from a broadcast payload.

        Contract (all violations raise, none silently default):
          * ``market_data['price']``  MUST be present and non-None.
          * ``market_data['prev_price']`` MUST be present.
          * ``market_data['round']``  MUST be present.

        ``fundamental`` and ``deviation`` may legitimately be missing for
        scenarios that do not model a fair value; they are then stored as
        ``NaN`` and every downstream metric must interpret ``NaN`` as
        "unavailable", NOT as "zero deviation".
        """
        # ── FAIL-LOUD: required broadcast fields ──────────────────────
        # `price` is the minimum viable market signal. If the market
        # coordinator broadcasts a payload without a price, agents cannot
        # make decisions — silently defaulting to 0.0 would allow "free
        # buys" (fill_price=0) and poison every portfolio-based metric.
        if "price" not in market_data or market_data["price"] is None:
            raise ValueError(
                "StandardMarketState.from_market_data: market_data is missing "
                "'price'. Every scenario coordinator MUST broadcast price. "
                "Silent default to 0.0 would falsify portfolio_value and "
                "make fill_price=0 (agents 'buy for free')."
            )
        # `prev_price` and `round` are part of the canonical broadcast
        # contract (see REQUIRED_BROADCAST_FIELDS). We fail loudly rather
        # than papering over a coordinator bug with a synthetic value that
        # would look plausible.
        if "prev_price" not in market_data:
            raise KeyError(
                "StandardMarketState.from_market_data: market_data is missing "
                "'prev_price'. Every canonical coordinator MUST broadcast "
                "prev_price (equal to price on round 0). See "
                "masim.format.state.REQUIRED_BROADCAST_FIELDS."
            )
        if "round" not in market_data:
            raise KeyError(
                "StandardMarketState.from_market_data: market_data is missing "
                "'round'. Every canonical coordinator MUST broadcast round. "
                "See masim.format.state.REQUIRED_BROADCAST_FIELDS."
            )

        price = float(market_data["price"])
        prev_price = float(market_data["prev_price"])

        # For fundamental/deviation: if the scenario does NOT model a
        # fundamental value, coordinators should still broadcast an
        # explicit `fundamental` field (NaN or matching price). Silently
        # defaulting to price would lie to the LLM prompt ("Fundamental =
        # Price, Deviation = 0", i.e. perfect fair pricing) and poison
        # every under_revision / bias_magnitude / price_deviation metric.
        _fund_raw = market_data.get("fundamental")
        if _fund_raw is None:
            fundamental = float("nan")
        else:
            fundamental = float(_fund_raw)

        _dev_raw = market_data.get("deviation")
        if _dev_raw is None:
            # Derive from price/fundamental when possible; else NaN.
            if fundamental == fundamental and fundamental != 0.0:  # not NaN
                deviation = (price - fundamental) / fundamental
            else:
                deviation = float("nan")
        else:
            deviation = float(_dev_raw)

        if prev_price > 0:
            price_change = (price - prev_price) / prev_price
        else:
            price_change = 0.0

        return cls(
            round=int(market_data["round"]),
            price=price,
            prev_price=prev_price,
            fundamental=fundamental,
            deviation=deviation,
            price_change=price_change,
            cash=float(cash),
            position=float(position),
            portfolio_value=float(cash) + float(position) * price,
            volatility=volatility,
            recent_returns=list(recent_returns or []),
            raw=dict(market_data),
        )

    # ------------------------------------------------------------------
    def template_vars(self) -> Dict[str, Any]:
        """Return the kwargs that fill an LLM ``user_message`` template."""
        return {
            "round": self.round,
            "price": self.price,
            "prev_price": self.prev_price,
            "fundamental": self.fundamental,
            "deviation": self.deviation,
            "price_change": self.price_change,
            "cash": self.cash,
            "position": self.position,
            "portfolio_value": self.portfolio_value,
        }

    # ------------------------------------------------------------------
    # Fail-loud raw-field accessors (2026-07-24)
    #
    # Every canonical agent that reads a scenario-specific broadcast field
    # SHOULD use ``raw_require`` (for fields the agent's REQUIRES_FEATURES
    # tuple declares mandatory) or ``raw_optional`` (for fields that the
    # archetype profile explicitly documents as optional-with-default).
    #
    # Bare ``state.raw.get("key", default)`` is deprecated: it hides intent
    # and papers over coordinator/scenario mis-wiring with a silent
    # numerical fallback that then falsifies downstream computation.
    # ------------------------------------------------------------------

    def raw_require(self, key: str, cast=None):
        """Return ``raw[key]`` or raise ``KeyError`` if absent.

        Use this for scenario broadcast fields the agent depends on to
        function correctly (i.e. fields listed in the agent's class-level
        ``REQUIRES_FEATURES`` tuple).  A missing key indicates a
        coordinator/scenario configuration bug — surface it, do NOT
        substitute a silent numeric default.

        Parameters
        ----------
        key
            Name of the field to fetch from the broadcast payload.
        cast
            Optional callable applied to the value (e.g. ``float``, ``int``).
            When ``None`` the raw value is returned untouched.
        """
        if key not in self.raw:
            raise KeyError(
                f"StandardMarketState.raw_require: required broadcast "
                f"field {key!r} is missing from market_data. "
                f"Available keys: {sorted(self.raw)}. "
                f"Fix the coordinator so it emits this field, or mark it "
                f"optional via raw_optional() only if the archetype profile "
                f"documents an explicit default."
            )
        value = self.raw[key]
        if cast is not None:
            return cast(value)
        return value

    def raw_optional(self, key: str, *, default, cast=None):
        """Return ``raw[key]`` or ``default`` if absent.

        Use this only for scenario broadcast fields that the archetype
        profile ("masim/agents/defines/<domain>/<stem>.md") documents as
        optional with a named default.  The intent-baring name distinguishes
        this from bare ``state.raw.get(...)`` at code-review time.

        Parameters
        ----------
        key
            Name of the field to fetch.
        default
            Value returned when ``key`` is absent (or its raw value is
            ``None`` — treated identically because JSON round-trip can
            introduce ``None`` where a missing key would be more accurate).
        cast
            Optional callable applied to a *present* value.  Never applied
            to the default (so numeric defaults do not need to be pre-cast).
        """
        if key not in self.raw or self.raw[key] is None:
            return default
        value = self.raw[key]
        if cast is not None:
            return cast(value)
        return value


__all__ = ["StandardMarketState", "REQUIRED_BROADCAST_FIELDS"]
