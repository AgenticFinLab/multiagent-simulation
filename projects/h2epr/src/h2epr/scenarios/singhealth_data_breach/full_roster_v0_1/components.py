"""Static component registry for the SingHealth executable successor."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from masim.integrations.event_process import AppendOnlyTransport, TraceWriter

from .registry import implementation_versions
from .runtime_components import (
    SingHealthEnvironment,
    SingHealthObservationProjector,
    SingHealthParticipantExecutor,
    SingHealthReducer,
    SingHealthTraceCompiler,
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
        "h2epr.component.0616.policy-registry",
        "0.1.0",
        "h2epr.static_policy_registry",
        implementation_versions,
    ),
    RuntimeComponent(
        "scheduler",
        "h2epr.component.0616.event-anchor-partial-order-scheduler",
        "0.1.0",
        "h2epr.scenario.event_anchor_partial_order",
        TIME_POLICY,
    ),
    RuntimeComponent(
        "observation_projector",
        SingHealthObservationProjector.implementation_id,
        SingHealthObservationProjector.implementation_version,
        "h2epr.runtime.observation_projector",
        SingHealthObservationProjector,
    ),
    RuntimeComponent(
        "participant_executor",
        SingHealthParticipantExecutor.implementation_id,
        SingHealthParticipantExecutor.implementation_version,
        "h2epr.runtime.participant_executor",
        SingHealthParticipantExecutor,
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
        SingHealthEnvironment.implementation_id,
        SingHealthEnvironment.implementation_version,
        "h2epr.runtime.environment",
        SingHealthEnvironment,
    ),
    RuntimeComponent(
        "reducer",
        SingHealthReducer.implementation_id,
        SingHealthReducer.implementation_version,
        "masim.integrations.event_process.AuthoritativeReducer.apply_batch",
        SingHealthReducer,
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
        SingHealthTraceCompiler.implementation_id,
        SingHealthTraceCompiler.implementation_version,
        "h2epr.runtime.trace_compiler",
        SingHealthTraceCompiler,
    ),
)

COMPONENTS_BY_ROLE: Mapping[str, RuntimeComponent] = MappingProxyType(
    {component.role: component for component in _COMPONENTS}
)
COMPONENTS_BY_ID: Mapping[str, RuntimeComponent] = MappingProxyType(
    {component.implementation_id: component for component in _COMPONENTS}
)

if len(COMPONENTS_BY_ROLE) != 9 or len(COMPONENTS_BY_ID) != 9:
    raise ValueError("singhealth_runtime_component_registry_invalid")


def runtime_component(role: str) -> RuntimeComponent:
    try:
        return COMPONENTS_BY_ROLE[role]
    except KeyError as exc:
        raise KeyError(f"unknown_singhealth_runtime_component:{role}") from exc


def component_bindings_document() -> dict[str, dict[str, str]]:
    """Return serialized bindings without exposing implementation objects."""

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
