"""Registered declarative Rule backend for current event packages."""

from __future__ import annotations

from h2epr.benchmark.package import EventPackage

from ._rule_core import _DeclarativeRuleBackendBase


class DeclarativeRuleBackend(_DeclarativeRuleBackendBase):
    """Produce deterministic participant decisions from admitted Rule rows."""

    implementation_id = "h2epr.backend.rule.declarative.v4"

    def __init__(
        self,
        package: EventPackage,
        *,
        run_id: str,
        run_seed: int,
    ) -> None:
        super().__init__(package, run_id=run_id, run_seed=run_seed)  # type: ignore[arg-type]


__all__ = ["DeclarativeRuleBackend"]
