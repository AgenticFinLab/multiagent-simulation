"""Versioned shared world state.

What this is
------------
An implementation of :class:`masim.platform.world.base.SharedState` — the M10
"blackboard" the platform contract has been promising but Part 1 never had.
Prices, order-flow summaries, information pools and any other variable that
describes **the world rather than one agent** live here, with a version stamped
on every commit so a reader can ask "what did the world look like at round N".

Scope now, shard-ready
----------------------
Today this is a **single global world** held by the driver (the Simulator
process), and its current population path is a *projection*: after each level the
driver stages whatever a coordinator broadcast into that coordinator's own
scope. Two consequences, both deliberate:

* agents do not write the world directly — they still publish through their
  normal outbound messages, so **no simulation behaviour changes**; and
* the world can already hold several independent scopes, which is the shape a
  multi-market or multi-asset run needs. ``read_all(key)`` reads one variable
  across every scope, which is the primitive macro-level aggregation requires
  (for example "price" across market_a / market_b, or a cross-asset total).

Making the world writable *by agents* (an order book that several actors mutate,
or a shared information pool) needs either a World actor or replicated per-actor
views. That is a larger change and is deliberately not attempted here; this
class is the interface it will be built behind.

Versioning
----------
``set()`` stages a value; ``commit()`` publishes the staged values atomically as
one version and appends the delta to the history. Reads always see the last
committed version, so a level's writes never leak half-applied. ``snapshot()``
and ``restore()`` make the world the first part of the framework that can
actually be taken back in time — which is what a resume needs once agent books
are also recoverable.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from masim.platform.world.base import SharedState, WorldVersion

#: Sentinel distinguishing "not present" from a stored ``None``.
_MISSING = object()


class VersionedSharedState(SharedState):
    """Single global shared state with scopes and versioned commits.

    Args:
        default_scope: scope used when a caller does not name one. ``"world"``
            keeps unscoped variables in one namespace.
    """

    def __init__(self, default_scope: str = "world") -> None:
        self.default_scope = default_scope
        self._live: Dict[str, Any] = {}
        self._pending: Dict[str, Any] = {}
        self._version = WorldVersion(round_num=0, level=0, seq=0)
        self._history: List[Dict[str, Any]] = []

    # -- key handling ------------------------------------------------------

    @staticmethod
    def _compose(scope: str, key: str) -> str:
        return f"{scope}.{key}" if scope else key

    @staticmethod
    def _decompose(composite: str) -> Tuple[str, str]:
        scope, _, key = composite.partition(".")
        return scope, key

    # -- SharedState contract ---------------------------------------------

    def get(self, key: str, default: Any = _MISSING, scope: Optional[str] = None) -> Any:
        """Read a shared variable.

        Raises:
            KeyError: when the variable is absent and no ``default`` is given —
                the contract demands loud behaviour rather than silent ``None``.
        """
        composite = self._compose(scope or self.default_scope, key)
        if composite in self._live:
            return self._live[composite]
        if default is not _MISSING:
            return default
        raise KeyError(
            f"SharedState has no committed variable {key!r} in scope "
            f"{scope or self.default_scope!r} (known keys: "
            f"{sorted(self._live)[:12]}{' …' if len(self._live) > 12 else ''})"
        )

    def set(
        self,
        key: str,
        value: Any,
        version: WorldVersion,
        scope: Optional[str] = None,
    ) -> None:
        """Stage a value for the next commit, stamped with ``version``."""
        composite = self._compose(scope or self.default_scope, key)
        self._pending[composite] = value
        if (version.round_num, version.level, version.seq) > (
            self._version.round_num,
            self._version.level,
            self._version.seq,
        ):
            self._version = version

    def version(self) -> WorldVersion:
        """Return the current committed version."""
        return self._version

    def snapshot(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """Return a shallow copy of the committed variables.

        With ``scope`` given, returns just that scope's variables under their
        short names; otherwise returns every variable keyed ``scope.key``.
        """
        if scope is None:
            return dict(self._live)
        prefix = self._compose(scope, "")
        return {
            composite[len(prefix) :]: value
            for composite, value in self._live.items()
            if composite.startswith(prefix)
        }

    # -- commit / history --------------------------------------------------

    def commit(self, version: Optional[WorldVersion] = None) -> WorldVersion:
        """Publish all staged writes as one version and record the delta."""
        if version is not None and (version.round_num, version.level) > (
            self._version.round_num,
            self._version.level,
        ):
            self._version = version
        delta = {key: value for key, value in self._pending.items()}
        self._live.update(delta)
        self._pending.clear()
        if delta:
            self._history.append(
                {
                    "round_num": self._version.round_num,
                    "level": self._version.level,
                    "seq": self._version.seq,
                    "changed": sorted(delta),
                }
            )
        return self._version

    def has_pending(self) -> bool:
        """True when staged writes have not been committed yet."""
        return bool(self._pending)

    def history(self) -> List[Dict[str, Any]]:
        """Return the per-commit deltas (which keys changed, and when)."""
        return list(self._history)

    # -- multi-scope helpers (the macro-aggregation primitive) -------------

    def scopes(self) -> List[str]:
        """Return every scope currently holding a variable."""
        return sorted({self._decompose(key)[0] for key in self._live})

    def read_all(self, key: str) -> Dict[str, Any]:
        """Read one short key across every scope.

        This is what a cross-market or cross-asset question needs: e.g.
        ``world.read_all("price")`` returns ``{"market_a": …, "market_b": …}``.
        """
        out: Dict[str, Any] = {}
        for scope in self.scopes():
            composite = self._compose(scope, key)
            if composite in self._live:
                out[scope] = self._live[composite]
        return out

    def keys(self, scope: Optional[str] = None) -> List[str]:
        """Return the short keys of one scope (or every composite key)."""
        if scope is None:
            return sorted(self._live)
        prefix = self._compose(scope, "")
        return sorted(
            composite[len(prefix) :]
            for composite in self._live
            if composite.startswith(prefix)
        )

    # -- persistence / rollback -------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialisable form: version, committed variables and the history."""
        return {
            "version": {
                "round_num": self._version.round_num,
                "level": self._version.level,
                "seq": self._version.seq,
            },
            "scopes": self.scopes(),
            "values": dict(self._live),
            "history": self.history(),
        }

    def restore(self, payload: Dict[str, Any]) -> None:
        """Replace the committed state with ``payload`` (from :meth:`to_dict`)."""
        version = payload.get("version") or {}
        self._version = WorldVersion(
            round_num=int(version.get("round_num", 0)),
            level=int(version.get("level", 0)),
            seq=int(version.get("seq", 0)),
        )
        self._live = dict(payload.get("values") or {})
        self._history = list(payload.get("history") or [])
        self._pending.clear()

    def __len__(self) -> int:
        return len(self._live)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return (
            f"VersionedSharedState(version=r{self._version.round_num}"
            f".l{self._version.level}, variables={len(self._live)}, "
            f"scopes={self.scopes()})"
        )


__all__ = ["VersionedSharedState"]
