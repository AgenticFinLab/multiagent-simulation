"""Typed backend factory registry for the current package contract."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from h2epr.benchmark.package import EventPackage

from .interface import DecisionBackend
from .rule import DeclarativeRuleBackend


class BackendRegistryError(ValueError):
    """A selected binding has no exact registered decision implementation."""


class BackendFactory(Protocol):
    def __call__(
        self,
        package: EventPackage,
        *,
        run_id: str,
        run_seed: int,
    ) -> DecisionBackend: ...


def _rule_factory(
    package: EventPackage,
    *,
    run_id: str,
    run_seed: int,
) -> DeclarativeRuleBackend:
    return DeclarativeRuleBackend(
        package,
        run_id=run_id,
        run_seed=run_seed,
    )


BACKEND_FACTORIES: dict[str, Callable[..., DecisionBackend]] = {
    "h2epr.backend.rule.declarative.v4": _rule_factory,
}


def build_backend(
    package: EventPackage,
    *,
    backend_name: str,
    run_id: str,
    run_seed: int,
) -> DecisionBackend:
    binding = package.binding
    if binding["backend"] != backend_name:
        raise BackendRegistryError("backend_binding_selection_mismatch")
    implementation_id = binding["implementation_id"]
    try:
        factory = BACKEND_FACTORIES[implementation_id]
    except KeyError as exc:
        raise BackendRegistryError(
            f"backend_factory_unavailable:{backend_name}:{implementation_id}"
        ) from exc
    backend = factory(
        package,
        run_id=run_id,
        run_seed=run_seed,
    )
    if (
        backend.backend_name != backend_name
        or backend.implementation_id != implementation_id
    ):
        raise BackendRegistryError("backend_factory_identity_mismatch")
    return backend


__all__ = [
    "BACKEND_FACTORIES",
    "BackendRegistryError",
    "build_backend",
]
