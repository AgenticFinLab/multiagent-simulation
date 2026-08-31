"""Static component registry for the Note7 executable successor."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from masim.integrations.event_process import AppendOnlyTransport, TraceWriter

from .registry import implementation_versions
from .runtime_components import (
    Note7Environment,
    Note7ObservationProjector,
    Note7ParticipantExecutor,
    Note7Reducer,
    Note7TraceCompiler,
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
        "h2epr.component.0481.policy-registry",
        "0.1.0",
        "h2epr.static_policy_registry",
        implementation_versions,
    ),
    RuntimeComponent(
        "scheduler",
        "h2epr.component.0481.event-anchor-partial-order-scheduler",
        "0.1.0",
        "h2epr.scenario.event_anchor_partial_order",
        TIME_POLICY,
    ),
    RuntimeComponent(
        "observation_projector",
        Note7ObservationProjector.implementation_id,
        Note7ObservationProjector.implementation_version,
        "h2epr.runtime.observation_projector",
        Note7ObservationProjector,
    ),
    RuntimeComponent(
        "participant_executor",
        Note7ParticipantExecutor.implementation_id,
        Note7ParticipantExecutor.implementation_version,
        "h2epr.runtime.participant_executor",
        Note7ParticipantExecutor,
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
        Note7Environment.implementation_id,
        Note7Environment.implementation_version,
        "h2epr.runtime.environment",
        Note7Environment,
    ),
    RuntimeComponent(
        "reducer",
        Note7Reducer.implementation_id,
        Note7Reducer.implementation_version,
        "masim.integrations.event_process.AuthoritativeReducer.apply_batch",
        Note7Reducer,
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
        Note7TraceCompiler.implementation_id,
        Note7TraceCompiler.implementation_version,
        "h2epr.runtime.trace_compiler",
        Note7TraceCompiler,
    ),
)

COMPONENTS_BY_ROLE: Mapping[str, RuntimeComponent] = MappingProxyType(
    {component.role: component for component in _COMPONENTS}
)
COMPONENTS_BY_ID: Mapping[str, RuntimeComponent] = MappingProxyType(
    {component.implementation_id: component for component in _COMPONENTS}
)

if len(COMPONENTS_BY_ROLE) != 9 or len(COMPONENTS_BY_ID) != 9:
    raise ValueError("note7_runtime_component_registry_invalid")


def runtime_component(role: str) -> RuntimeComponent:
    try:
        return COMPONENTS_BY_ROLE[role]
    except KeyError as exc:
        raise KeyError(f"unknown_note7_runtime_component:{role}") from exc


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
