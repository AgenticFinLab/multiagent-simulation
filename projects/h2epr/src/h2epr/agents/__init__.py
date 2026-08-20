"""Definition-driven Agent pilot surfaces.

These modules are explicit opt-in research code. Importing :mod:`h2epr` does
not load the pilot or activate a simulation runtime.
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
