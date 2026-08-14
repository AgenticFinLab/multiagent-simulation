"""Immutable typed values for the G1 Construction IR."""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]

SOURCE_DESCRIPTOR_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
DIAGNOSTIC_CODE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
CANONICAL_JSON_POINTER = re.compile(r"^(?:/(?:[^~/]|~[01])+)+$")


class Presence(str, Enum):
    ABSENT = "absent"
    EXPLICIT_NULL = "explicit_null"
    PRESENT = "present"
    INVALID = "invalid_unparsed"


class Availability(str, Enum):
    AVAILABLE_BEFORE_T0 = "available_before_t0"
    CONSTRUCTION_ONLY = "construction_only"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class ReviewState(str, Enum):
    UNREVIEWED = "unreviewed"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"


class SourceKind(str, Enum):
    SOURCE_IDENTITY = "source_identity"
    SAMPLE_MANIFEST = "sample_manifest"
    EVENT_SPEC = "event_spec"
    FROZEN_EVIDENCE = "frozen_evidence"
    DRAFT_EPG = "draft_epg"
    DRAFT_EPG_PREFIX_PROJECTION = "draft_epg_prefix_projection"
    NON_TARGET_CONTEMPORANEOUS_SOURCE = "non_target_contemporaneous_source"
    GENERIC_CONTRACT = "generic_contract"
    SYNTHETIC = "synthetic"
    GOLD_FALLBACK = "gold_fallback"
    TARGET_SUFFIX = "target_suffix"


class TimeRole(str, Enum):
    OCCURRENCE = "occurrence_time"
    INFORMATION_AVAILABLE = "information_available_time"


class TimePrecision(str, Enum):
    EXACT_DATETIME = "exact_datetime"
    DATE = "date"
    MONTH = "month"
    YEAR = "year"
    RANGE = "range"
    FREE_TEXT = "free_text"
    UNKNOWN = "unknown"


class EndpointStatus(str, Enum):
    KNOWN = "known"
    UNRESOLVED = "unresolved"
    EXTERNAL = "external"
    UNKNOWN = "unknown"
    SUSPICIOUS = "suspicious"


@dataclass(frozen=True)
class SourcePointer:
    source_id: str
    json_pointer: str


@dataclass(frozen=True)
class AnnotatedValue:
    source_id: str
    pointer: str
    presence: Presence
    raw_value: JsonValue | None
    raw_content_sha256: str
    normalized_candidate: JsonValue | None = None
    diagnostic_status: str = "parsed"


@dataclass(frozen=True)
class TimeExpression:
    source_id: str
    pointer: str
    raw_value: JsonValue | None
    normalized_candidate: str | None
    precision: TimePrecision
    interval_lower: str | None
    interval_upper: str | None
    uncertainty: str
    diagnostic_status: str
    time_role: TimeRole


@dataclass(frozen=True)
class EndpointRef:
    source_id: str
    pointer: str
    raw_identifier: str
    status: EndpointStatus
    normalized_candidate: str | None = None


@dataclass(frozen=True)
class EvidenceRef:
    source_id: str
    pointer: str
    content_sha256: str
    availability: Availability
    review_state: ReviewState
    excerpt: "ApprovedExcerpt | None" = None


@dataclass(frozen=True)
class ApprovedExcerpt:
    approval_id: str
    purpose: str
    text: str
    utf8_bytes: int

    def __post_init__(self) -> None:
        from .evidence import EvidencePolicyError

        if not isinstance(self.approval_id, str) or not self.approval_id.strip():
            raise EvidencePolicyError("approval_id_required")
        if not isinstance(self.purpose, str) or not self.purpose.strip():
            raise EvidencePolicyError("purpose_required")
        if not isinstance(self.text, str):
            raise EvidencePolicyError("excerpt_text_must_be_string")
        size = len(self.text.encode("utf-8"))
        if size > 280:
            raise EvidencePolicyError("excerpt_too_large")
        if isinstance(self.utf8_bytes, bool) or not isinstance(self.utf8_bytes, int):
            raise EvidencePolicyError("excerpt_byte_count_invalid")
        if self.utf8_bytes != size:
            raise EvidencePolicyError("excerpt_byte_count_mismatch")

    @classmethod
    def create(cls, approval_id: str, purpose: str, text: str) -> "ApprovedExcerpt":
        size = len(text.encode("utf-8"))
        return cls(approval_id=approval_id, purpose=purpose, text=text, utf8_bytes=size)


@dataclass(frozen=True)
class ConstructionDiagnostic:
    code: str
    summary: str
    pointer: str

    def __post_init__(self) -> None:
        _construction_diagnostic_values(self)


def _construction_diagnostic_values(
    diagnostic: object,
) -> tuple[str, str, str]:
    from .evidence import EvidencePolicyError

    if type(diagnostic) is not ConstructionDiagnostic:
        raise EvidencePolicyError("diagnostic_type_invalid")
    missing = object()
    code = getattr(diagnostic, "code", missing)
    if type(code) is not str or DIAGNOSTIC_CODE.fullmatch(code) is None:
        raise EvidencePolicyError("diagnostic_code_invalid")
    summary = getattr(diagnostic, "summary", missing)
    if type(summary) is not str:
        raise EvidencePolicyError("diagnostic_summary_must_be_string")
    if "\n" in summary or "\r" in summary:
        raise EvidencePolicyError("diagnostic_summary_multiline")
    if len(summary.encode("utf-8")) > 160:
        raise EvidencePolicyError("diagnostic_summary_too_large")
    pointer = getattr(diagnostic, "pointer", missing)
    if type(pointer) is not str or (
        pointer != "" and CANONICAL_JSON_POINTER.fullmatch(pointer) is None
    ):
        raise EvidencePolicyError("diagnostic_pointer_invalid")
    return code, summary, pointer


def _validated_construction_diagnostic(
    diagnostic: object,
) -> ConstructionDiagnostic:
    return ConstructionDiagnostic(*_construction_diagnostic_values(diagnostic))


@dataclass(frozen=True)
class SourceDescriptor:
    logical_source_id: str
    source_kind: SourceKind | str
    relative_path: str
    expected_sha256: str
    availability: Availability
    review_state: ReviewState

    def __post_init__(self) -> None:
        _source_descriptor_values(self)


@dataclass(frozen=True)
class ArchitectureSourceManifest:
    descriptors: tuple[SourceDescriptor, ...]
    entry_policy: str = field(default="architecture_generic", init=False)

    def __post_init__(self) -> None:
        _source_manifest_descriptors(self, ArchitectureSourceManifest)


@dataclass(frozen=True)
class StrictSourceManifest:
    descriptors: tuple[SourceDescriptor, ...]
    entry_policy: str = field(default="prefix_clean_strict", init=False)

    def __post_init__(self) -> None:
        _source_manifest_descriptors(self, StrictSourceManifest)


def _source_descriptor_values(
    descriptor: object,
) -> tuple[str, SourceKind | str, str, str, Availability, ReviewState]:
    if type(descriptor) is not SourceDescriptor:
        raise ValueError("source_descriptor_type_invalid")
    missing = object()
    logical_source_id = getattr(descriptor, "logical_source_id", missing)
    if (
        type(logical_source_id) is not str
        or SOURCE_DESCRIPTOR_ID.fullmatch(logical_source_id) is None
    ):
        raise ValueError("source_descriptor_id_invalid")
    source_kind = getattr(descriptor, "source_kind", missing)
    if type(source_kind) is not SourceKind and type(source_kind) is not str:
        raise ValueError("source_descriptor_kind_invalid")
    relative_path = getattr(descriptor, "relative_path", missing)
    if type(relative_path) is not str or not relative_path:
        raise ValueError("source_descriptor_path_invalid")
    expected_sha256 = getattr(descriptor, "expected_sha256", missing)
    if (
        type(expected_sha256) is not str
        or LOWER_SHA256.fullmatch(expected_sha256) is None
    ):
        raise ValueError("source_descriptor_hash_invalid")
    availability = getattr(descriptor, "availability", missing)
    if type(availability) is not Availability:
        raise ValueError("source_descriptor_availability_invalid")
    review_state = getattr(descriptor, "review_state", missing)
    if type(review_state) is not ReviewState:
        raise ValueError("source_descriptor_review_state_invalid")
    return (
        logical_source_id,
        source_kind,
        relative_path,
        expected_sha256,
        availability,
        review_state,
    )


def _source_manifest_descriptors(
    manifest: object,
    expected_type: type[ArchitectureSourceManifest] | type[StrictSourceManifest],
) -> tuple[SourceDescriptor, ...]:
    if type(manifest) is not expected_type:
        raise ValueError("source_manifest_type_invalid")
    missing = object()
    descriptors = getattr(manifest, "descriptors", missing)
    if type(descriptors) is not tuple:
        raise ValueError("source_manifest_descriptors_invalid")
    for descriptor in descriptors:
        _source_descriptor_values(descriptor)
    return descriptors


def validated_source_descriptor(descriptor: object) -> SourceDescriptor:
    """Revalidate and reconstruct one closed source descriptor."""
    return SourceDescriptor(*_source_descriptor_values(descriptor))


def validated_source_manifest_descriptors(
    manifest: object,
    expected_type: type[ArchitectureSourceManifest] | type[StrictSourceManifest],
) -> tuple[SourceDescriptor, ...]:
    """Revalidate a manifest before a consumer uses supplied behavior."""
    descriptors = _source_manifest_descriptors(manifest, expected_type)
    return tuple(validated_source_descriptor(item) for item in descriptors)


@dataclass(frozen=True)
class LoadedSource:
    descriptor: SourceDescriptor
    content_sha256: str
    document: JsonValue
    content_size_bytes: int


@dataclass(frozen=True)
class StructureRecord:
    source_id: str
    pointer: str
    structure_kind: str
    raw_identifier: AnnotatedValue
    index_value: AnnotatedValue


@dataclass(frozen=True)
class ContainerNode:
    source_id: str
    pointer: str
    container_kind: str
    item_count: int


@dataclass(frozen=True)
class EntityMention:
    source_id: str
    pointer: str
    identifier: AnnotatedValue
    name: AnnotatedValue
    entity_type: AnnotatedValue
    role: AnnotatedValue
    attributes: Mapping[str, AnnotatedValue]

    def __post_init__(self) -> None:
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))


@dataclass(frozen=True)
class ActionRecord:
    source_id: str
    pointer: str
    actor: EndpointRef
    name: AnnotatedValue
    details: tuple[AnnotatedValue, ...]
    occurrence_time: TimeExpression


@dataclass(frozen=True)
class RelationRecord:
    source_id: str
    pointer: str
    endpoints: tuple[EndpointRef, EndpointRef]
    relation_type: AnnotatedValue
    relation_name: AnnotatedValue
    bidirectional: AnnotatedValue
    occurrence_times: tuple[TimeExpression, ...]


@dataclass(frozen=True)
class TransactionRecord:
    source_id: str
    pointer: str
    endpoints: tuple[EndpointRef, EndpointRef]
    name: AnnotatedValue
    transaction_type: AnnotatedValue
    details: tuple[AnnotatedValue, ...]
    instruments: tuple[AnnotatedValue, ...]
    occurrence_time: TimeExpression


@dataclass(frozen=True)
class SourceDocumentIdentity:
    source_id: str
    source_kind: SourceKind
    content_sha256: str
    content_size_bytes: int
    availability: Availability
    review_state: ReviewState


@dataclass(frozen=True)
class ConstructionIR:
    identity: Any
    sources: tuple[SourceDocumentIdentity, ...]
    values: tuple[AnnotatedValue, ...]
    containers: tuple[ContainerNode, ...]
    times: tuple[TimeExpression, ...]
    structures: tuple[StructureRecord, ...]
    entities: tuple[EntityMention, ...]
    actions: tuple[ActionRecord, ...]
    relations: tuple[RelationRecord, ...]
    transactions: tuple[TransactionRecord, ...]
    evidence: tuple[EvidenceRef, ...]
    diagnostics: tuple[ConstructionDiagnostic, ...]
    unknown_field_pointers: tuple[SourcePointer, ...]
    snapshot_version: str = "h2epr.construction_ir.v1"

    @classmethod
    def empty(cls, identity: Any) -> "ConstructionIR":
        return cls(identity, (), (), (), (), (), (), (), (), (), (), (), ())


def to_plain(value: Any) -> Any:
    """Convert the immutable IR to deterministic JSON-compatible values."""
    if isinstance(value, ApprovedExcerpt):
        ApprovedExcerpt(value.approval_id, value.purpose, value.text, value.utf8_bytes)
    if isinstance(value, ConstructionDiagnostic):
        diagnostic = _validated_construction_diagnostic(value)
        return {
            "code": diagnostic.code,
            "summary": diagnostic.summary,
            "pointer": diagnostic.pointer,
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): to_plain(item) for key, item in value.items()}
    if is_dataclass(value):
        return {item.name: to_plain(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, (tuple, list)):
        return [to_plain(item) for item in value]
    return value
