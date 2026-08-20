"""Definition binding and conformance surfaces.

The historical engineering baseline remains an explicit opt-in module.
Importing :mod:`h2epr` does not load it or activate a simulation runtime.
"""

from .definition import (
    AgentConformanceError,
    AgentObservation,
    BindingValidationError,
    DecisionDraft,
    DecisionOutcome,
    DecisionRecord,
    DefinitionBinding,
    DefinitionDrivenAgent,
    SemanticIntent,
    load_binding_catalog,
)

__all__ = [
    "AgentConformanceError",
    "AgentObservation",
    "BindingValidationError",
    "DecisionDraft",
    "DecisionOutcome",
    "DecisionRecord",
    "DefinitionBinding",
    "DefinitionDrivenAgent",
    "SemanticIntent",
    "load_binding_catalog",
]
