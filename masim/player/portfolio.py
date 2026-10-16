"""Agent bookkeeping: the single sanctioned mutation path for cash and position.

Why an object instead of a dict
-------------------------------
Cash and position used to live as bare entries in ``state.custom_state`` and
were mutated from many places — the framework's fill helper, but also 704
direct writes across 175 legacy scenario modules (the audit's ``SEM-CASH-MUT``).
Two writers of one ledger cannot be prevented by convention, only by removing
the other entry points.

:class:`Portfolio` is that single entry point. It is deliberately a thin facade
over ``custom_state`` so that:

*   reading ``custom_state["cash"]`` keeps working for every existing
    archetype and report (no migration required), and
*   *writing* has exactly one sanctioned method, :meth:`Portfolio.apply_fill`,
    which the platform calls from the fill path and nothing else calls.

The legacy dict writes remain physically possible (Python has no private
fields); the point is that a new archetype never needs one, and the audit keeps
flagging them as defects rather than as "the way it is done".
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from masim.platform.execution.base import Fill


class Portfolio:
    """Cash/position book for one agent, backed by ``custom_state``.

    Attributes:
        _state: the owning agent's ``custom_state`` dict. Not copied: the book
            must be the same object the rest of the framework reads.
    """

    # Keys are part of the on-disk report format; changing them is a breaking
    # change for analysis code.
    CASH_KEY = "cash"
    POSITION_KEY = "position"

    def __init__(self, state: Dict[str, Any]):
        self._state = state

    # -- read side ---------------------------------------------------------

    @property
    def cash(self) -> float:
        """Current cash balance."""
        return float(self._state.get(self.CASH_KEY, 0.0))

    @property
    def position(self) -> float:
        """Current signed position size."""
        return float(self._state.get(self.POSITION_KEY, 0.0))

    def equity(self, mark_price: Optional[float] = None) -> float:
        """Cash plus position marked at ``mark_price`` (cash-only when None)."""
        if mark_price is None:
            return self.cash
        return self.cash + self.position * float(mark_price)

    def snapshot(self) -> Dict[str, float]:
        """Return a plain dict copy of the book, for reporting/tests."""
        return {"cash": self.cash, "position": self.position}

    def initialize(self, cash: float, position: float) -> None:
        """Seed the book once, at agent construction time."""
        self._state[self.CASH_KEY] = float(cash)
        self._state[self.POSITION_KEY] = float(position)

    # -- write side (the only one) -----------------------------------------

    def apply_fill(self, fill: Fill) -> None:
        """Settle one execution report against the book.

        This is the *only* sanctioned way an agent's cash and position change.
        It is idempotent per fill object in the sense that the caller is
        responsible for passing each fill exactly once; the platform issues
        exactly one fill per accepted order.

        Contract:
            * a rejected fill or a zero ``fill_quantity`` changes nothing;
            * a HOLD changes nothing;
            * a non-zero quantity requires a strictly positive ``fill_price``
              (the platform re-validates before calling, and this is the second
              line of defence).
        """
        if fill.rejected or fill.fill_quantity == 0:
            return
        if fill.action not in ("buy", "sell"):
            return
        if not (fill.fill_price > 0):
            raise ValueError(
                "Portfolio.apply_fill: non-zero fill_quantity requires "
                f"fill_price > 0 (got {fill.fill_price!r}, "
                f"investor={fill.investor!r}, action={fill.action!r})."
            )

        if fill.action == "buy":
            self._state[self.CASH_KEY] = self.cash - fill.fill_quantity * fill.fill_price
            self._state[self.POSITION_KEY] = self.position + fill.fill_quantity
        else:  # sell
            self._state[self.CASH_KEY] = self.cash + fill.fill_quantity * fill.fill_price
            self._state[self.POSITION_KEY] = self.position - fill.fill_quantity

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Portfolio(cash={self.cash:.2f}, position={self.position:.4f})"
