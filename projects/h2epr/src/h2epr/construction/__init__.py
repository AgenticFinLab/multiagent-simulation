"""Public construction-layer API.

This project API builds Construction IR only; it
does not construct participants, a world, a runtime bundle, or a simulation.
"""

from .evidence import EvidencePolicyError, bounded_diagnostic, minimize_evidence
from .identity import (
    ArchitectureGenericIdentity,
    ConstructionIdentity,
    EventSpecUsage,
    FullDraftTargetDemoIdentity,
    IdentityPolicyError,
    LineageRef,
    PrefixCleanStrictIdentity,
    PrefixContaminatedDemoIdentity,
    PrefixProjectionAttestation,
    StrictSourceFieldPolicy,
    identity_from_snapshot,
    validate_strict_entry,
)
from .model import (
    ActionRecord,
    AnnotatedValue,
    ApprovedExcerpt,
    ArchitectureSourceManifest,
    Availability,
    ConstructionDiagnostic,
    ConstructionIR,
    ContainerNode,
    EndpointRef,
    EndpointStatus,
    EntityMention,
    EvidenceRef,
    Presence,
    RelationRecord,
    ReviewState,
    SourceDescriptor,
    SourceDocumentIdentity,
    SourceKind,
    SourcePointer,
    StrictSourceManifest,
    StructureRecord,
    TimeExpression,
    TimePrecision,
    TimeRole,
    TransactionRecord,
)
from .parser import annotate_absent, annotate_invalid, annotate_value, parse_architecture_generic
from .snapshot import canonical_snapshot_bytes, mutation_descriptor, snapshot_sha256
from .source import SourceAdapter, SourcePolicyError
from .time import parse_endpoint, parse_time_expression

__all__ = [name for name in globals() if not name.startswith("_")]
