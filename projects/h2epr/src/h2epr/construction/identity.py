"""Closed construction identities and strict-entry validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .model import (
    ArchitectureSourceManifest,
    Availability,
    ReviewState,
    SourceKind,
    StrictSourceManifest,
    validated_source_manifest_descriptors,
)


class IdentityPolicyError(ValueError):
    """A closed construction identity or strict source policy was violated."""


STABLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
CANONICAL_JSON_POINTER = re.compile(r"^(?:/(?:[^~/]|~[01])+)+$")

IDENTITY_TUPLES = {
    (
        "architecture_generic",
        "generic_only",
        "full_draft_generic_only",
        "full_target_draft",
        "full_draft_exposed",
        "architecture_demo_only",
    ),
    (
        "full_draft_target_demo",
        "target_specific",
        "full_draft_target_specific",
        "full_target_draft",
        "full_draft_exposed",
        "architecture_demo_only",
    ),
    (
        "prefix_contaminated_demo",
        "target_specific",
        "prefix_target_specific",
        "prefix_inputs_after_full_draft_exposure",
        "full_draft_exposed",
        "architecture_demo_only",
    ),
    (
        "prefix_clean_strict",
        "target_specific",
        "prefix_target_specific",
        "prefix_allowlist_only",
        "clean_prefix_only",
        "strict_eligible",
    ),
}


def _validate_stable(value: object, code: str) -> None:
    if not isinstance(value, str) or STABLE_ID.fullmatch(value) is None:
        raise IdentityPolicyError(code)


def _validate_exact_stable(value: object, code: str) -> None:
    if type(value) is not str or STABLE_ID.fullmatch(value) is None:
        raise IdentityPolicyError(code)


def _exact_field(value: object, name: str, missing: object) -> object:
    try:
        state = object.__getattribute__(value, "__dict__")
    except (AttributeError, TypeError):
        return missing
    if type(state) is not dict or name not in state:
        return missing
    return state[name]


def _validate_pointer_tuple(pointers: object, *, empty_code: str) -> tuple[str, ...]:
    if not isinstance(pointers, tuple) or not pointers:
        raise IdentityPolicyError(empty_code)
    if len(set(pointers)) != len(pointers):
        raise IdentityPolicyError("duplicate_event_spec_pointer")
    for pointer in pointers:
        if not isinstance(pointer, str) or CANONICAL_JSON_POINTER.fullmatch(pointer) is None:
            raise IdentityPolicyError("malformed_event_spec_pointer")
    return pointers


@dataclass(frozen=True)
class LineageRef:
    """Closed immutable reference to one sealed construction artifact."""

    artifact_id: str
    artifact_kind: str
    artifact_sha256: str
    construction_state: str
    artifact_scope: str
    source_scope: str
    builder_access: str
    contamination_status: str
    protocol_eligibility: str

    def __post_init__(self) -> None:
        _validate_exact_stable(self.artifact_id, "lineage_artifact_id_invalid")
        _validate_exact_stable(self.artifact_kind, "lineage_artifact_kind_invalid")
        if type(self.artifact_sha256) is not str or LOWER_SHA256.fullmatch(
            self.artifact_sha256
        ) is None:
            raise IdentityPolicyError("lineage_artifact_hash_invalid")
        if any(
            type(value) is not str
            for value in (
                self.construction_state,
                self.artifact_scope,
                self.source_scope,
                self.builder_access,
                self.contamination_status,
                self.protocol_eligibility,
            )
        ):
            raise IdentityPolicyError("lineage_identity_tuple_invalid")
        if self.identity_tuple not in IDENTITY_TUPLES:
            raise IdentityPolicyError("lineage_identity_tuple_invalid")

    @property
    def identity_tuple(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.construction_state,
            self.artifact_scope,
            self.source_scope,
            self.builder_access,
            self.contamination_status,
            self.protocol_eligibility,
        )

    def to_snapshot(self) -> dict[str, str]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_kind": self.artifact_kind,
            "artifact_sha256": self.artifact_sha256,
            "construction_state": self.construction_state,
            "artifact_scope": self.artifact_scope,
            "source_scope": self.source_scope,
            "builder_access": self.builder_access,
            "contamination_status": self.contamination_status,
            "protocol_eligibility": self.protocol_eligibility,
        }

    @classmethod
    def from_snapshot(cls, snapshot: object) -> "LineageRef":
        expected_fields = {
            "artifact_id",
            "artifact_kind",
            "artifact_sha256",
            "construction_state",
            "artifact_scope",
            "source_scope",
            "builder_access",
            "contamination_status",
            "protocol_eligibility",
        }
        if not isinstance(snapshot, dict) or set(snapshot) != expected_fields:
            raise IdentityPolicyError("lineage_fields_not_closed")
        if any(not isinstance(snapshot[name], str) for name in expected_fields):
            raise IdentityPolicyError("lineage_field_type_invalid")
        return cls(**snapshot)


@dataclass(frozen=True)
class ConstructionIdentity:
    artifact_id: str
    ancestors: tuple[LineageRef, ...] = field(default_factory=tuple)
    construction_state: str = field(init=False)
    artifact_scope: str = field(init=False)
    source_scope: str = field(init=False)
    builder_access: str = field(init=False)
    contamination_status: str = field(init=False)
    protocol_eligibility: str = field(init=False)

    def __post_init__(self) -> None:
        _validate_exact_stable(self.artifact_id, "artifact_id_invalid")
        if type(self.ancestors) is not tuple or any(
            type(item) is not LineageRef for item in self.ancestors
        ):
            raise IdentityPolicyError("typed_lineage_required")
        for name in (
            "construction_state",
            "artifact_scope",
            "source_scope",
            "builder_access",
            "contamination_status",
            "protocol_eligibility",
        ):
            object.__setattr__(self, name, object.__getattribute__(self, name))

    @property
    def identity_tuple(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.construction_state,
            self.artifact_scope,
            self.source_scope,
            self.builder_access,
            self.contamination_status,
            self.protocol_eligibility,
        )

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "construction_state": self.construction_state,
            "artifact_scope": self.artifact_scope,
            "source_scope": self.source_scope,
            "builder_access": self.builder_access,
            "contamination_status": self.contamination_status,
            "protocol_eligibility": self.protocol_eligibility,
            "ancestors": [item.to_snapshot() for item in self.ancestors],
        }


@dataclass(frozen=True)
class ArchitectureGenericIdentity(ConstructionIdentity):
    construction_state: str = field(default="architecture_generic", init=False)
    artifact_scope: str = field(default="generic_only", init=False)
    source_scope: str = field(default="full_draft_generic_only", init=False)
    builder_access: str = field(default="full_target_draft", init=False)
    contamination_status: str = field(default="full_draft_exposed", init=False)
    protocol_eligibility: str = field(default="architecture_demo_only", init=False)


@dataclass(frozen=True)
class FullDraftTargetDemoIdentity(ConstructionIdentity):
    construction_state: str = field(default="full_draft_target_demo", init=False)
    artifact_scope: str = field(default="target_specific", init=False)
    source_scope: str = field(default="full_draft_target_specific", init=False)
    builder_access: str = field(default="full_target_draft", init=False)
    contamination_status: str = field(default="full_draft_exposed", init=False)
    protocol_eligibility: str = field(default="architecture_demo_only", init=False)


@dataclass(frozen=True)
class PrefixContaminatedDemoIdentity(ConstructionIdentity):
    construction_state: str = field(default="prefix_contaminated_demo", init=False)
    artifact_scope: str = field(default="target_specific", init=False)
    source_scope: str = field(default="prefix_target_specific", init=False)
    builder_access: str = field(default="prefix_inputs_after_full_draft_exposure", init=False)
    contamination_status: str = field(default="full_draft_exposed", init=False)
    protocol_eligibility: str = field(default="architecture_demo_only", init=False)


@dataclass(frozen=True)
class PrefixCleanStrictIdentity(ConstructionIdentity):
    construction_state: str = field(default="prefix_clean_strict", init=False)
    artifact_scope: str = field(default="target_specific", init=False)
    source_scope: str = field(default="prefix_target_specific", init=False)
    builder_access: str = field(default="prefix_allowlist_only", init=False)
    contamination_status: str = field(default="clean_prefix_only", init=False)
    protocol_eligibility: str = field(default="strict_eligible", init=False)


IDENTITIES = {
    "architecture_generic": ArchitectureGenericIdentity,
    "full_draft_target_demo": FullDraftTargetDemoIdentity,
    "prefix_contaminated_demo": PrefixContaminatedDemoIdentity,
    "prefix_clean_strict": PrefixCleanStrictIdentity,
}

IDENTITY_TUPLE_BY_TYPE = {
    ArchitectureGenericIdentity: (
        "architecture_generic",
        "generic_only",
        "full_draft_generic_only",
        "full_target_draft",
        "full_draft_exposed",
        "architecture_demo_only",
    ),
    FullDraftTargetDemoIdentity: (
        "full_draft_target_demo",
        "target_specific",
        "full_draft_target_specific",
        "full_target_draft",
        "full_draft_exposed",
        "architecture_demo_only",
    ),
    PrefixContaminatedDemoIdentity: (
        "prefix_contaminated_demo",
        "target_specific",
        "prefix_target_specific",
        "prefix_inputs_after_full_draft_exposure",
        "full_draft_exposed",
        "architecture_demo_only",
    ),
    PrefixCleanStrictIdentity: (
        "prefix_clean_strict",
        "target_specific",
        "prefix_target_specific",
        "prefix_allowlist_only",
        "clean_prefix_only",
        "strict_eligible",
    ),
}


def _validated_lineage(
    value: object, *, type_code: str = "typed_lineage_required"
) -> LineageRef:
    if type(value) is not LineageRef:
        raise IdentityPolicyError(type_code)
    missing = object()
    artifact_id = _exact_field(value, "artifact_id", missing)
    _validate_exact_stable(artifact_id, "lineage_artifact_id_invalid")
    artifact_kind = _exact_field(value, "artifact_kind", missing)
    _validate_exact_stable(artifact_kind, "lineage_artifact_kind_invalid")
    artifact_sha256 = _exact_field(value, "artifact_sha256", missing)
    if (
        type(artifact_sha256) is not str
        or LOWER_SHA256.fullmatch(artifact_sha256) is None
    ):
        raise IdentityPolicyError("lineage_artifact_hash_invalid")
    identity_tuple = tuple(
        _exact_field(value, name, missing)
        for name in (
            "construction_state",
            "artifact_scope",
            "source_scope",
            "builder_access",
            "contamination_status",
            "protocol_eligibility",
        )
    )
    if any(type(item) is not str for item in identity_tuple):
        raise IdentityPolicyError("lineage_identity_tuple_invalid")
    if identity_tuple not in IDENTITY_TUPLES:
        raise IdentityPolicyError("lineage_identity_tuple_invalid")
    return LineageRef(
        artifact_id,
        artifact_kind,
        artifact_sha256,
        *identity_tuple,
    )


def _validated_identity(
    value: object,
    expected_type: type[ConstructionIdentity],
    *,
    type_code: str,
) -> ConstructionIdentity:
    if type(value) is not expected_type:
        raise IdentityPolicyError(type_code)
    missing = object()
    artifact_id = _exact_field(value, "artifact_id", missing)
    _validate_exact_stable(artifact_id, "artifact_id_invalid")
    ancestors = _exact_field(value, "ancestors", missing)
    if type(ancestors) is not tuple:
        raise IdentityPolicyError("typed_lineage_required")
    validated_ancestors = tuple(_validated_lineage(item) for item in ancestors)
    identity_tuple = tuple(
        _exact_field(value, name, missing)
        for name in (
            "construction_state",
            "artifact_scope",
            "source_scope",
            "builder_access",
            "contamination_status",
            "protocol_eligibility",
        )
    )
    if any(type(item) is not str for item in identity_tuple):
        raise IdentityPolicyError("identity_tuple_mismatch")
    if identity_tuple != IDENTITY_TUPLE_BY_TYPE[expected_type]:
        raise IdentityPolicyError("identity_tuple_mismatch")
    return expected_type(artifact_id, validated_ancestors)


def validated_architecture_generic_identity(
    value: object,
) -> ArchitectureGenericIdentity:
    """Revalidate architecture identity before a parser touches its sources."""
    try:
        identity = _validated_identity(
            value,
            ArchitectureGenericIdentity,
            type_code="architecture_generic_identity_required",
        )
    except IdentityPolicyError as exc:
        raise TypeError("architecture_generic_identity_required") from exc
    assert type(identity) is ArchitectureGenericIdentity
    return identity


def identity_from_snapshot(snapshot: dict[str, Any]) -> ConstructionIdentity:
    expected_fields = {
        "artifact_id",
        "construction_state",
        "artifact_scope",
        "source_scope",
        "builder_access",
        "contamination_status",
        "protocol_eligibility",
        "ancestors",
    }
    if not isinstance(snapshot, dict) or set(snapshot) != expected_fields:
        raise IdentityPolicyError("identity_fields_not_closed")
    state = snapshot.get("construction_state")
    identity_type = IDENTITIES.get(state)
    if identity_type is None:
        raise IdentityPolicyError("unknown_construction_state")
    raw_ancestors = snapshot.get("ancestors")
    if not isinstance(raw_ancestors, list):
        raise IdentityPolicyError("identity_ancestors_not_array")
    ancestors = tuple(LineageRef.from_snapshot(item) for item in raw_ancestors)
    identity = identity_type(snapshot.get("artifact_id", ""), ancestors)
    expected = identity.to_snapshot()
    for field_name in (
        "construction_state", "artifact_scope", "source_scope", "builder_access",
        "contamination_status", "protocol_eligibility",
    ):
        if snapshot.get(field_name) != expected[field_name]:
            raise IdentityPolicyError("identity_tuple_mismatch")
    return identity


@dataclass(frozen=True)
class PrefixProjectionAttestation:
    source_draft_sha256: str
    cutoff: str
    projection_policy: str
    claim_pointers: tuple[str, ...]
    suffix_absence_attested: bool
    producer_identity: str
    review_receipt_id: str
    reference_absence_attested: bool
    availability: Availability
    architecture_diagnostics_present: bool

    def __post_init__(self) -> None:
        _projection_values(self)


def _projection_values(
    projection: object,
) -> tuple[str, str, str, tuple[str, ...], bool, str, str, bool, Availability, bool]:
    if type(projection) is not PrefixProjectionAttestation:
        raise IdentityPolicyError("projection_attestation_type_invalid")
    missing = object()
    source_draft_sha256 = getattr(projection, "source_draft_sha256", missing)
    if (
        type(source_draft_sha256) is not str
        or LOWER_SHA256.fullmatch(source_draft_sha256) is None
    ):
        raise IdentityPolicyError("projection_source_hash_invalid")
    cutoff = getattr(projection, "cutoff", missing)
    if type(cutoff) is not str or not cutoff:
        raise IdentityPolicyError("projection_cutoff_invalid")
    projection_policy = getattr(projection, "projection_policy", missing)
    if type(projection_policy) is not str or not projection_policy:
        raise IdentityPolicyError("projection_policy_invalid")
    claim_pointers = getattr(projection, "claim_pointers", missing)
    if type(claim_pointers) is not tuple or not claim_pointers:
        raise IdentityPolicyError("projection_claim_pointers_invalid")
    if any(type(pointer) is not str for pointer in claim_pointers):
        raise IdentityPolicyError("projection_claim_pointers_invalid")
    if len(set(claim_pointers)) != len(claim_pointers) or any(
        CANONICAL_JSON_POINTER.fullmatch(pointer) is None
        for pointer in claim_pointers
    ):
        raise IdentityPolicyError("projection_claim_pointers_invalid")
    suffix_absence_attested = getattr(
        projection, "suffix_absence_attested", missing
    )
    if type(suffix_absence_attested) is not bool:
        raise IdentityPolicyError("projection_suffix_attestation_type_invalid")
    producer_identity = getattr(projection, "producer_identity", missing)
    if type(producer_identity) is not str or not producer_identity:
        raise IdentityPolicyError("producer_identity_missing")
    review_receipt_id = getattr(projection, "review_receipt_id", missing)
    if type(review_receipt_id) is not str or not review_receipt_id:
        raise IdentityPolicyError("review_receipt_missing")
    reference_absence_attested = getattr(
        projection, "reference_absence_attested", missing
    )
    if type(reference_absence_attested) is not bool:
        raise IdentityPolicyError("projection_reference_attestation_type_invalid")
    availability = getattr(projection, "availability", missing)
    if type(availability) is not Availability:
        raise IdentityPolicyError("projection_availability_invalid")
    architecture_diagnostics_present = getattr(
        projection, "architecture_diagnostics_present", missing
    )
    if type(architecture_diagnostics_present) is not bool:
        raise IdentityPolicyError("projection_diagnostics_flag_type_invalid")
    return (
        source_draft_sha256,
        cutoff,
        projection_policy,
        claim_pointers,
        suffix_absence_attested,
        producer_identity,
        review_receipt_id,
        reference_absence_attested,
        availability,
        architecture_diagnostics_present,
    )


def _validated_projection(projection: object) -> PrefixProjectionAttestation:
    """Revalidate and reconstruct one closed projection attestation."""
    return PrefixProjectionAttestation(*_projection_values(projection))


@dataclass(frozen=True)
class StrictSourceFieldPolicy:
    observed_event_spec_pointers: tuple[str, ...]
    allowed_event_spec_pointers: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_pointer_tuple(
            self.observed_event_spec_pointers, empty_code="event_spec_observed_policy_empty"
        )
        _validate_pointer_tuple(
            self.allowed_event_spec_pointers, empty_code="event_spec_allowed_policy_empty"
        )
        if not set(self.allowed_event_spec_pointers) <= set(
            self.observed_event_spec_pointers
        ):
            raise IdentityPolicyError("event_spec_allowed_pointer_not_observed")

    def allows(self, pointer: str) -> bool:
        return (
            pointer in self.observed_event_spec_pointers
            and pointer in self.allowed_event_spec_pointers
        )


@dataclass(frozen=True)
class EventSpecUsage:
    logical_source_id: str
    used_json_pointers: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_stable(self.logical_source_id, "event_spec_source_id_invalid")
        _validate_pointer_tuple(
            self.used_json_pointers, empty_code="event_spec_usage_empty"
        )


def _validate_exact_event_spec_bindings(
    usage: EventSpecUsage,
    policy: StrictSourceFieldPolicy,
) -> tuple[EventSpecUsage, StrictSourceFieldPolicy]:
    missing = object()
    logical_source_id = getattr(usage, "logical_source_id", missing)
    if type(logical_source_id) is not str:
        raise IdentityPolicyError("event_spec_source_id_invalid")
    used_pointers = getattr(usage, "used_json_pointers", missing)
    if type(used_pointers) is not tuple or not used_pointers:
        raise IdentityPolicyError("event_spec_usage_empty")
    if any(type(pointer) is not str for pointer in used_pointers):
        raise IdentityPolicyError("malformed_event_spec_pointer")

    observed_pointers = getattr(policy, "observed_event_spec_pointers", missing)
    if type(observed_pointers) is not tuple or not observed_pointers:
        raise IdentityPolicyError("event_spec_observed_policy_empty")
    if any(type(pointer) is not str for pointer in observed_pointers):
        raise IdentityPolicyError("malformed_event_spec_pointer")
    allowed_pointers = getattr(policy, "allowed_event_spec_pointers", missing)
    if type(allowed_pointers) is not tuple or not allowed_pointers:
        raise IdentityPolicyError("event_spec_allowed_policy_empty")
    if any(type(pointer) is not str for pointer in allowed_pointers):
        raise IdentityPolicyError("malformed_event_spec_pointer")

    return (
        EventSpecUsage(
            logical_source_id=logical_source_id,
            used_json_pointers=used_pointers,
        ),
        StrictSourceFieldPolicy(
            observed_event_spec_pointers=observed_pointers,
            allowed_event_spec_pointers=allowed_pointers,
        ),
    )


def validate_strict_entry(
    identity: object,
    manifest: object,
    projection: PrefixProjectionAttestation,
    expected_root_artifact_id: str,
    *,
    expected_lineage: tuple[LineageRef, ...] | None = None,
    event_spec_usage: EventSpecUsage | None = None,
    event_spec_policy: StrictSourceFieldPolicy | None = None,
) -> None:
    validated_identity = _validated_identity(
        identity,
        PrefixCleanStrictIdentity,
        type_code="strict_identity_required",
    )
    try:
        descriptors = validated_source_manifest_descriptors(
            manifest, StrictSourceManifest
        )
    except ValueError as exc:
        raise IdentityPolicyError(str(exc)) from exc
    if type(expected_root_artifact_id) is not str or (
        STABLE_ID.fullmatch(expected_root_artifact_id) is None
    ):
        raise IdentityPolicyError("external_root_mismatch")
    if validated_identity.artifact_id != expected_root_artifact_id:
        raise IdentityPolicyError("external_root_mismatch")
    validated_expected_lineage = None
    if expected_lineage is not None:
        if type(expected_lineage) is not tuple:
            raise IdentityPolicyError("typed_expected_lineage_required")
        validated_expected_lineage = tuple(
            _validated_lineage(item, type_code="typed_expected_lineage_required")
            for item in expected_lineage
        )
    if validated_identity.ancestors and validated_expected_lineage is None:
        raise IdentityPolicyError("expected_lineage_required")
    if (
        validated_expected_lineage is not None
        and validated_identity.ancestors != validated_expected_lineage
    ):
        raise IdentityPolicyError("external_lineage_mismatch")
    for ancestor in validated_identity.ancestors:
        if ancestor.construction_state != "prefix_clean_strict":
            raise IdentityPolicyError("cross_state_ancestry")
    projection = _validated_projection(projection)
    if projection.architecture_diagnostics_present:
        raise IdentityPolicyError("architecture_diagnostics_forbidden")
    if not projection.suffix_absence_attested:
        raise IdentityPolicyError("suffix_absence_not_attested")
    if not projection.reference_absence_attested:
        raise IdentityPolicyError("reference_absence_not_attested")
    if not projection.producer_identity:
        raise IdentityPolicyError("producer_identity_missing")
    if not projection.review_receipt_id:
        raise IdentityPolicyError("review_receipt_missing")
    if projection.availability is Availability.UNKNOWN:
        raise IdentityPolicyError("projection_unknown_availability")
    if projection.availability is not Availability.AVAILABLE_BEFORE_T0:
        raise IdentityPolicyError("projection_not_available_before_t0")
    if len(projection.source_draft_sha256) != 64 or any(
        character not in "0123456789abcdef" for character in projection.source_draft_sha256
    ):
        raise IdentityPolicyError("projection_source_hash_invalid")
    if not projection.cutoff or not projection.projection_policy or not projection.claim_pointers:
        raise IdentityPolicyError("projection_manifest_incomplete")
    descriptors_by_id: dict[str, list[SourceKind]] = {}
    event_spec_ids: list[str] = []
    for descriptor in descriptors:
        try:
            kind = SourceKind(descriptor.source_kind)
        except ValueError as exc:
            raise IdentityPolicyError("unknown_source_kind") from exc
        if kind is SourceKind.DRAFT_EPG:
            raise IdentityPolicyError("full_draft_forbidden")
        if kind is SourceKind.GOLD_FALLBACK:
            raise IdentityPolicyError("gold_fallback_forbidden")
        if descriptor.availability is Availability.UNKNOWN:
            raise IdentityPolicyError("unknown_availability")
        if descriptor.availability is not Availability.AVAILABLE_BEFORE_T0:
            raise IdentityPolicyError("not_available_before_t0")
        if descriptor.review_state is not ReviewState.APPROVED:
            raise IdentityPolicyError("source_not_approved")
        if kind not in {
            SourceKind.EVENT_SPEC,
            SourceKind.DRAFT_EPG_PREFIX_PROJECTION,
            SourceKind.NON_TARGET_CONTEMPORANEOUS_SOURCE,
            SourceKind.GENERIC_CONTRACT,
            SourceKind.SYNTHETIC,
        }:
            raise IdentityPolicyError("strict_source_kind_forbidden")
        descriptors_by_id.setdefault(descriptor.logical_source_id, []).append(kind)
        if kind is SourceKind.EVENT_SPEC:
            event_spec_ids.append(descriptor.logical_source_id)

    if len(set(event_spec_ids)) > 1:
        raise IdentityPolicyError("event_spec_descriptor_set_unbound")
    if event_spec_ids:
        if event_spec_usage is None or event_spec_policy is None:
            raise IdentityPolicyError("event_spec_usage_and_policy_required")
    elif event_spec_usage is not None or event_spec_policy is not None:
        raise IdentityPolicyError("event_spec_source_missing")
    if event_spec_usage is not None and event_spec_policy is not None:
        if type(event_spec_usage) is not EventSpecUsage:
            raise IdentityPolicyError("event_spec_usage_type_invalid")
        if type(event_spec_policy) is not StrictSourceFieldPolicy:
            raise IdentityPolicyError("event_spec_policy_type_invalid")
        validated_usage, validated_policy = _validate_exact_event_spec_bindings(
            event_spec_usage,
            event_spec_policy,
        )
        matching = descriptors_by_id.get(validated_usage.logical_source_id, [])
        if not matching:
            raise IdentityPolicyError("event_spec_source_missing")
        if len(matching) != 1:
            raise IdentityPolicyError("event_spec_source_ambiguous")
        if matching[0] is not SourceKind.EVENT_SPEC:
            raise IdentityPolicyError("event_spec_usage_source_kind_mismatch")
        for pointer in validated_usage.used_json_pointers:
            if (
                pointer not in validated_policy.observed_event_spec_pointers
                or pointer not in validated_policy.allowed_event_spec_pointers
            ):
                raise IdentityPolicyError("event_spec_pointer_forbidden")
