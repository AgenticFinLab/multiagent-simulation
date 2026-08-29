"""Static component registry for the Panic executable successor."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from masim.integrations.event_process import AppendOnlyTransport, TraceWriter

from .registry import implementation_versions
from .runtime_components import (
    PanicEnvironment,
    PanicObservationProjector,
    PanicParticipantExecutor,
    PanicReducer,
    PanicTraceCompiler,
)
from .scenario_rules import TIME_POLICY


@dataclass(frozen=True)
class RuntimeComponent:
    """One versioned implementation bound to a runtime responsibility."""

    role: str
    implementation_id: str
    implementation_version: str
    public_interface: str
    implementation: Any


_COMPONENTS = (
    RuntimeComponent(
        "policy_registry",
        "h2epr.component.0288.policy-registry",
        "0.1.0",
        "h2epr.static_policy_registry",
        implementation_versions,
    ),
    RuntimeComponent(
        "scheduler",
        "h2epr.component.0288.partial-order-scheduler",
        "0.1.0",
        "h2epr.scenario.partial_order",
        TIME_POLICY,
    ),
    RuntimeComponent(
        "observation_projector",
        PanicObservationProjector.implementation_id,
        PanicObservationProjector.implementation_version,
        "h2epr.runtime.observation_projector",
        PanicObservationProjector,
    ),
    RuntimeComponent(
        "participant_executor",
        PanicParticipantExecutor.implementation_id,
        PanicParticipantExecutor.implementation_version,
        "h2epr.runtime.participant_executor",
        PanicParticipantExecutor,
    ),
    RuntimeComponent(
        "message_transport",
        "masim.event-process.append-only-transport",
        "0.0.1",
        "masim.integrations.event_process.AppendOnlyTransport",
        AppendOnlyTransport,
    ),
    RuntimeComponent(
        "environment",
        PanicEnvironment.implementation_id,
        PanicEnvironment.implementation_version,
        "h2epr.runtime.environment",
        PanicEnvironment,
    ),
    RuntimeComponent(
        "reducer",
        PanicReducer.implementation_id,
        PanicReducer.implementation_version,
        "masim.integrations.event_process.AuthoritativeReducer.apply_batch",
        PanicReducer,
    ),
    RuntimeComponent(
        "trace",
        "masim.event-process.trace-writer",
        "0.0.1",
        "masim.integrations.event_process.TraceWriter",
        TraceWriter,
    ),
    RuntimeComponent(
        "compiler",
        PanicTraceCompiler.implementation_id,
        PanicTraceCompiler.implementation_version,
        "h2epr.runtime.trace_compiler",
        PanicTraceCompiler,
    ),
)

COMPONENTS_BY_ROLE: Mapping[str, RuntimeComponent] = MappingProxyType(
    {component.role: component for component in _COMPONENTS}
)
COMPONENTS_BY_ID: Mapping[str, RuntimeComponent] = MappingProxyType(
    {component.implementation_id: component for component in _COMPONENTS}
)

if len(COMPONENTS_BY_ROLE) != 9 or len(COMPONENTS_BY_ID) != 9:
    raise ValueError("panic_runtime_component_registry_invalid")


def runtime_component(role: str) -> RuntimeComponent:
    try:
        return COMPONENTS_BY_ROLE[role]
    except KeyError as exc:
        raise KeyError(f"unknown_panic_runtime_component:{role}") from exc


def component_bindings_document() -> dict[str, dict[str, str]]:
    """Return the closed serialized bindings without implementation objects."""

    return {
        role: {
            "implementation_id": component.implementation_id,
            "implementation_version": component.implementation_version,
        }
        for role, component in COMPONENTS_BY_ROLE.items()
    }


__all__ = [
    "COMPONENTS_BY_ID",
    "COMPONENTS_BY_ROLE",
    "RuntimeComponent",
    "component_bindings_document",
    "runtime_component",
]
