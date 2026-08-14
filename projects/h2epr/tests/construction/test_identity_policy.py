from __future__ import annotations

from dataclasses import replace

import pytest

from h2epr.construction import (
    ArchitectureGenericIdentity,
    ArchitectureSourceManifest,
    Availability,
    EventSpecUsage,
    FullDraftTargetDemoIdentity,
    IdentityPolicyError,
    LineageRef,
    PrefixCleanStrictIdentity,
    PrefixContaminatedDemoIdentity,
    PrefixProjectionAttestation,
    ReviewState,
    SourceDescriptor,
    SourceKind,
    StrictSourceFieldPolicy,
    StrictSourceManifest,
    identity_from_snapshot,
    validate_strict_entry,
)


def _strict_identity(*, ancestors=()):
    return PrefixCleanStrictIdentity("strict-root", ancestors=ancestors)


def _projection(**changes: object) -> PrefixProjectionAttestation:
    values = {
        "source_draft_sha256": "a" * 64,
        "cutoff": "2026-01-01",
        "projection_policy": "synthetic-prefix-v1",
        "claim_pointers": ("/stages/0",),
        "suffix_absence_attested": True,
        "producer_identity": "clean-builder",
        "review_receipt_id": "synthetic-review",
        "reference_absence_attested": True,
        "availability": Availability.AVAILABLE_BEFORE_T0,
        "architecture_diagnostics_present": False,
    }
    values.update(changes)
    return PrefixProjectionAttestation(**values)


def _strict_manifest(*descriptors: SourceDescriptor) -> StrictSourceManifest:
    if not descriptors:
        descriptors = (
            SourceDescriptor(
                logical_source_id="synthetic-prefix",
                source_kind=SourceKind.DRAFT_EPG_PREFIX_PROJECTION,
                relative_path="draft_epg_prefix_projection.json",
                expected_sha256="b" * 64,
                availability=Availability.AVAILABLE_BEFORE_T0,
                review_state=ReviewState.APPROVED,
            ),
        )
    return StrictSourceManifest(tuple(descriptors))


def _event_spec_descriptor(source_id: str = "synthetic-event-spec") -> SourceDescriptor:
    return SourceDescriptor(
        logical_source_id=source_id,
        source_kind=SourceKind.EVENT_SPEC,
        relative_path="event_spec.json",
        expected_sha256="c" * 64,
        availability=Availability.AVAILABLE_BEFORE_T0,
        review_state=ReviewState.APPROVED,
    )


def _forged_source_descriptor(**changes: object) -> SourceDescriptor:
    values = {
        "logical_source_id": "synthetic-event-spec",
        "source_kind": SourceKind.EVENT_SPEC,
        "relative_path": "event_spec.json",
        "expected_sha256": "c" * 64,
        "availability": Availability.AVAILABLE_BEFORE_T0,
        "review_state": ReviewState.APPROVED,
    }
    values.update(changes)
    descriptor = object.__new__(SourceDescriptor)
    for field_name, value in values.items():
        object.__setattr__(descriptor, field_name, value)
    return descriptor


def _forged_strict_manifest(descriptors: object) -> StrictSourceManifest:
    manifest = object.__new__(StrictSourceManifest)
    object.__setattr__(manifest, "descriptors", descriptors)
    return manifest


def _strict_lineage(**changes: str) -> LineageRef:
    values = {
        "artifact_id": "strict-parent",
        "artifact_kind": "ConstructionBundle",
        "artifact_sha256": "d" * 64,
        "construction_state": "prefix_clean_strict",
        "artifact_scope": "target_specific",
        "source_scope": "prefix_target_specific",
        "builder_access": "prefix_allowlist_only",
        "contamination_status": "clean_prefix_only",
        "protocol_eligibility": "strict_eligible",
    }
    values.update(changes)
    return LineageRef(**values)


def _architecture_lineage() -> LineageRef:
    return LineageRef(
        artifact_id="architecture-parent",
        artifact_kind="ConstructionBundle",
        artifact_sha256="e" * 64,
        construction_state="architecture_generic",
        artifact_scope="generic_only",
        source_scope="full_draft_generic_only",
        builder_access="full_target_draft",
        contamination_status="full_draft_exposed",
        protocol_eligibility="architecture_demo_only",
    )


def test_four_construction_identities_are_distinct_closed_types() -> None:
    identities = [
        ArchitectureGenericIdentity("architecture"),
        FullDraftTargetDemoIdentity("target-demo"),
        PrefixContaminatedDemoIdentity("contaminated"),
        PrefixCleanStrictIdentity("strict"),
    ]
    assert len({type(item) for item in identities}) == 4
    assert len({item.identity_tuple for item in identities}) == 4


@pytest.mark.parametrize(
    "identity",
    [
        ArchitectureGenericIdentity("architecture"),
        FullDraftTargetDemoIdentity("target-demo"),
        PrefixContaminatedDemoIdentity("contaminated"),
    ],
    ids=["architecture", "full-draft-demo", "prefix-contaminated"],
)
def test_non_strict_identity_cannot_enter_strict_processing(identity: object) -> None:
    with pytest.raises(IdentityPolicyError, match="strict_identity_required"):
        validate_strict_entry(identity, _strict_manifest(), _projection(), "strict-root")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_scope", "generic_only"),
        ("source_scope", "full_draft_target_specific"),
        ("builder_access", "full_target_draft"),
        ("contamination_status", "full_draft_exposed"),
        ("protocol_eligibility", "architecture_demo_only"),
    ],
)
def test_flag_only_strict_relabel_is_rejected(field: str, value: str) -> None:
    snapshot = _strict_identity().to_snapshot()
    snapshot[field] = value
    with pytest.raises(IdentityPolicyError, match="identity_tuple_mismatch"):
        identity_from_snapshot(snapshot)


def test_cross_state_ancestry_is_rejected() -> None:
    ancestor = _architecture_lineage()
    identity = _strict_identity(ancestors=(ancestor,))
    with pytest.raises(IdentityPolicyError, match="cross_state_ancestry"):
        validate_strict_entry(
            identity,
            _strict_manifest(),
            _projection(),
            "strict-root",
            expected_lineage=(ancestor,),
        )


def test_consistent_root_rename_still_fails_external_anchor() -> None:
    renamed = PrefixCleanStrictIdentity("renamed-root")
    with pytest.raises(IdentityPolicyError, match="external_root_mismatch"):
        validate_strict_entry(renamed, _strict_manifest(), _projection(), "strict-root")


def test_candidate_lineage_requires_independent_expected_binding() -> None:
    with pytest.raises(IdentityPolicyError, match="expected_lineage_required"):
        validate_strict_entry(
            _strict_identity(ancestors=(_strict_lineage(),)),
            _strict_manifest(),
            _projection(),
            "strict-root",
        )


def test_architecture_diagnostics_are_rejected_from_strict_processing() -> None:
    with pytest.raises(IdentityPolicyError, match="architecture_diagnostics_forbidden"):
        validate_strict_entry(
            _strict_identity(), _strict_manifest(),
            _projection(architecture_diagnostics_present=True), "strict-root"
        )


@pytest.mark.parametrize(
    ("kind", "availability", "code"),
    [
        (SourceKind.DRAFT_EPG, Availability.AVAILABLE_BEFORE_T0, "full_draft_forbidden"),
        (SourceKind.GOLD_FALLBACK, Availability.AVAILABLE_BEFORE_T0, "gold_fallback_forbidden"),
        (SourceKind.TARGET_SUFFIX, Availability.AVAILABLE_BEFORE_T0, "strict_source_kind_forbidden"),
        (SourceKind.DRAFT_EPG_PREFIX_PROJECTION, Availability.UNKNOWN, "unknown_availability"),
        (SourceKind.DRAFT_EPG_PREFIX_PROJECTION, Availability.CONSTRUCTION_ONLY, "not_available_before_t0"),
    ],
)
def test_strict_sources_fail_closed(
    kind: SourceKind, availability: Availability, code: str
) -> None:
    descriptor = SourceDescriptor(
        logical_source_id="synthetic-prefix",
        source_kind=kind,
        relative_path="draft_epg_prefix_projection.json" if kind is SourceKind.DRAFT_EPG_PREFIX_PROJECTION else "draft_epg.json",
        expected_sha256="b" * 64,
        availability=availability,
        review_state=ReviewState.APPROVED,
    )
    with pytest.raises(IdentityPolicyError, match=code):
        validate_strict_entry(_strict_identity(), _strict_manifest(descriptor), _projection(), "strict-root")


def test_strict_source_must_be_approved() -> None:
    descriptor = replace(_strict_manifest().descriptors[0], review_state=ReviewState.UNREVIEWED)
    with pytest.raises(IdentityPolicyError, match="source_not_approved"):
        validate_strict_entry(_strict_identity(), _strict_manifest(descriptor), _projection(), "strict-root")


def test_event_spec_strict_field_allowlist_is_exact_and_deny_by_default() -> None:
    policy = StrictSourceFieldPolicy(
        observed_event_spec_pointers=(
            "/domain", "/language_mode", "/public_event_id", "/schema_version", "/title"
        ),
        allowed_event_spec_pointers=(
            "/domain", "/language_mode", "/public_event_id", "/schema_version", "/title"
        )
    )
    assert policy.allows("/title")
    for pointer in ("/category", "/event_descriptor", "/keywords", "/region_hint", "/time_hint"):
        assert not policy.allows(pointer)


def test_matching_event_spec_usage_enters_real_strict_boundary() -> None:
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    validate_strict_entry(
        _strict_identity(),
        _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
        _projection(),
        "strict-root",
        event_spec_usage=EventSpecUsage("synthetic-event-spec", ("/event_id",)),
        event_spec_policy=policy,
    )


def test_forbidden_event_spec_usage_fails_real_strict_boundary() -> None:
    policy = StrictSourceFieldPolicy(
        ("/event_descriptor", "/event_id"), ("/event_id",)
    )
    with pytest.raises(IdentityPolicyError, match="event_spec_pointer_forbidden"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage(
                "synthetic-event-spec", ("/event_descriptor",)
            ),
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_mutable_usage_impostor() -> None:
    class MutableUsageImpostor:
        logical_source_id = "synthetic-event-spec"
        used_json_pointers = ("/event_id",)

    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_usage_type_invalid"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=MutableUsageImpostor(),  # type: ignore[arg-type]
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_policy_impostor_with_permissive_allows() -> None:
    class PermissivePolicyImpostor:
        observed_event_spec_pointers = ("/event_id",)
        allowed_event_spec_pointers = ("/event_id",)

        def allows(self, pointer: str) -> bool:
            return True

    with pytest.raises(IdentityPolicyError, match="event_spec_policy_type_invalid"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage("synthetic-event-spec", ("/event_id",)),
            event_spec_policy=PermissivePolicyImpostor(),  # type: ignore[arg-type]
        )


def test_event_spec_strict_entry_rejects_overriding_policy_subclass() -> None:
    class PermissivePolicySubclass(StrictSourceFieldPolicy):
        def allows(self, pointer: str) -> bool:
            return True

    policy = PermissivePolicySubclass(("/event_id",), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_policy_type_invalid"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage("synthetic-event-spec", ("/event_id",)),
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_revalidates_forged_exact_policy_state() -> None:
    policy = object.__new__(StrictSourceFieldPolicy)
    object.__setattr__(policy, "observed_event_spec_pointers", ("/event_id",))
    object.__setattr__(
        policy,
        "allowed_event_spec_pointers",
        ("/event_id", "/event_descriptor"),
    )
    with pytest.raises(
        IdentityPolicyError, match="event_spec_allowed_pointer_not_observed"
    ):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage("synthetic-event-spec", ("/event_id",)),
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_logical_source_id_string_subclass() -> None:
    class SourceIdImpostor(str):
        def __hash__(self) -> int:
            return hash("synthetic-event-spec")

        def __eq__(self, other: object) -> bool:
            return other == "synthetic-event-spec"

    usage = EventSpecUsage(SourceIdImpostor("absent-event-spec"), ("/event_id",))
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_source_id_invalid"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=usage,
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_used_pointer_tuple_subclass() -> None:
    class UsedPointerTupleImpostor(tuple):
        def __iter__(self):
            return iter(("/event_id",))

    usage = EventSpecUsage(
        "synthetic-event-spec",
        UsedPointerTupleImpostor(("/event_descriptor",)),
    )
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_usage_empty"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=usage,
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_used_pointer_string_subclass() -> None:
    class UsedPointerImpostor(str):
        def __hash__(self) -> int:
            return hash("/event_id")

        def __eq__(self, other: object) -> bool:
            return other == "/event_id"

    usage = EventSpecUsage(
        "synthetic-event-spec",
        (UsedPointerImpostor("/event_descriptor"),),
    )
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="malformed_event_spec_pointer"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=usage,
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_observed_pointer_tuple_subclass() -> None:
    class ObservedTupleImpostor(tuple):
        def __iter__(self):
            return iter(("/event_descriptor",))

        def __contains__(self, item: object) -> bool:
            return True

    policy = StrictSourceFieldPolicy(
        ObservedTupleImpostor(("/event_id",)),
        ("/event_descriptor",),
    )
    with pytest.raises(IdentityPolicyError, match="event_spec_observed_policy_empty"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage(
                "synthetic-event-spec", ("/event_descriptor",)
            ),
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_observed_pointer_string_subclass() -> None:
    class ObservedPointerImpostor(str):
        def __hash__(self) -> int:
            return hash("/event_descriptor")

        def __eq__(self, other: object) -> bool:
            return other == "/event_descriptor"

    policy = StrictSourceFieldPolicy(
        (ObservedPointerImpostor("/event_id"),),
        ("/event_descriptor",),
    )
    with pytest.raises(IdentityPolicyError, match="malformed_event_spec_pointer"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage(
                "synthetic-event-spec", ("/event_descriptor",)
            ),
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_allowed_pointer_tuple_subclass() -> None:
    class AllowedTupleImpostor(tuple):
        def __contains__(self, item: object) -> bool:
            return True

    policy = StrictSourceFieldPolicy(
        ("/event_id", "/event_descriptor"),
        AllowedTupleImpostor(("/event_id",)),
    )
    with pytest.raises(IdentityPolicyError, match="event_spec_allowed_policy_empty"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage(
                "synthetic-event-spec", ("/event_descriptor",)
            ),
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_allowed_pointer_string_subclass() -> None:
    class AllowedPointerImpostor(str):
        def __hash__(self) -> int:
            return hash("/event_descriptor")

        def __eq__(self, other: object) -> bool:
            return other == "/event_descriptor"

    policy = StrictSourceFieldPolicy(
        ("/event_descriptor",),
        (AllowedPointerImpostor("/event_id"),),
    )
    with pytest.raises(IdentityPolicyError, match="malformed_event_spec_pointer"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage(
                "synthetic-event-spec", ("/event_descriptor",)
            ),
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_forged_usage_missing_source_id() -> None:
    usage = object.__new__(EventSpecUsage)
    object.__setattr__(usage, "used_json_pointers", ("/event_id",))
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_source_id_invalid"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=usage,
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_forged_usage_missing_pointer_tuple() -> None:
    usage = object.__new__(EventSpecUsage)
    object.__setattr__(usage, "logical_source_id", "synthetic-event-spec")
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_usage_empty"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=usage,
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_forged_policy_missing_observed_tuple() -> None:
    policy = object.__new__(StrictSourceFieldPolicy)
    object.__setattr__(policy, "allowed_event_spec_pointers", ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_observed_policy_empty"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage("synthetic-event-spec", ("/event_id",)),
            event_spec_policy=policy,
        )


def test_event_spec_strict_entry_rejects_forged_policy_missing_allowed_tuple() -> None:
    policy = object.__new__(StrictSourceFieldPolicy)
    object.__setattr__(policy, "observed_event_spec_pointers", ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_allowed_policy_empty"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage("synthetic-event-spec", ("/event_id",)),
            event_spec_policy=policy,
        )


def test_allowed_event_spec_pointer_must_also_be_observed() -> None:
    policy = StrictSourceFieldPolicy(
        ("/event_descriptor", "/event_id"), ("/event_id",)
    )
    with pytest.raises(IdentityPolicyError, match="event_spec_pointer_forbidden"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage(
                "synthetic-event-spec", ("/event_descriptor",)
            ),
            event_spec_policy=policy,
        )


def test_policy_rejects_allowed_pointer_absent_from_observed_set() -> None:
    with pytest.raises(
        IdentityPolicyError, match="event_spec_allowed_pointer_not_observed"
    ):
        StrictSourceFieldPolicy(
            ("/event_id",), ("/event_id", "/unobserved")
        )


def test_event_spec_descriptor_requires_usage_and_policy() -> None:
    with pytest.raises(IdentityPolicyError, match="event_spec_usage_and_policy_required"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
        )


def test_projection_claim_pointer_is_not_event_spec_authorization() -> None:
    with pytest.raises(IdentityPolicyError, match="event_spec_usage_and_policy_required"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(claim_pointers=("/event_id",)),
            "strict-root",
        )


def test_event_spec_usage_cannot_bind_non_event_source() -> None:
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_usage_source_kind_mismatch"):
        validate_strict_entry(
            _strict_identity(),
            _strict_manifest(_strict_manifest().descriptors[0], _event_spec_descriptor()),
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage("synthetic-prefix", ("/event_id",)),
            event_spec_policy=policy,
        )


def test_event_spec_usage_cannot_bind_absent_or_ambiguous_source() -> None:
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    usage = EventSpecUsage("absent-event-spec", ("/event_id",))
    manifest = _strict_manifest(
        _strict_manifest().descriptors[0],
        _event_spec_descriptor("event-spec-a"),
    )
    with pytest.raises(IdentityPolicyError, match="event_spec_source_missing"):
        validate_strict_entry(
            _strict_identity(), manifest, _projection(), "strict-root",
            event_spec_usage=usage, event_spec_policy=policy,
        )

    duplicate_manifest = _strict_manifest(
        _strict_manifest().descriptors[0],
        _event_spec_descriptor("duplicate-event-spec"),
        _event_spec_descriptor("duplicate-event-spec"),
    )
    with pytest.raises(IdentityPolicyError, match="event_spec_source_ambiguous"):
        validate_strict_entry(
            _strict_identity(), duplicate_manifest, _projection(), "strict-root",
            event_spec_usage=EventSpecUsage("duplicate-event-spec", ("/event_id",)),
            event_spec_policy=policy,
        )


def test_singular_event_spec_binding_rejects_distinct_unbound_descriptor() -> None:
    policy = StrictSourceFieldPolicy(("/event_id",), ("/event_id",))
    manifest = _strict_manifest(
        _strict_manifest().descriptors[0],
        _event_spec_descriptor("event-spec-a"),
        _event_spec_descriptor("event-spec-b"),
    )
    with pytest.raises(IdentityPolicyError, match="event_spec_descriptor_set_unbound"):
        validate_strict_entry(
            _strict_identity(),
            manifest,
            _projection(),
            "strict-root",
            event_spec_usage=EventSpecUsage("event-spec-a", ("/event_id",)),
            event_spec_policy=policy,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "other-parent"),
        ("artifact_kind", "OtherBundle"),
        ("artifact_sha256", "f" * 64),
        ("construction_state", "prefix_contaminated_demo"),
        ("artifact_scope", "generic_only"),
        ("source_scope", "full_draft_target_specific"),
        ("builder_access", "full_target_draft"),
        ("contamination_status", "full_draft_exposed"),
        ("protocol_eligibility", "architecture_demo_only"),
    ],
)
def test_strict_lineage_mutation_fails_external_binding(field: str, value: str) -> None:
    expected = _strict_lineage()
    values = expected.to_snapshot()
    values[field] = value
    if field in {
        "construction_state",
        "artifact_scope",
        "source_scope",
        "builder_access",
        "contamination_status",
        "protocol_eligibility",
    }:
        with pytest.raises(IdentityPolicyError, match="lineage_identity_tuple_invalid"):
            LineageRef.from_snapshot(values)
        return
    candidate = LineageRef.from_snapshot(values)
    with pytest.raises(IdentityPolicyError, match="external_lineage_mismatch"):
        validate_strict_entry(
            _strict_identity(ancestors=(candidate,)),
            _strict_manifest(),
            _projection(),
            "strict-root",
            expected_lineage=(expected,),
        )


def test_raw_lineage_dictionary_is_not_accepted() -> None:
    with pytest.raises(IdentityPolicyError, match="typed_lineage_required"):
        PrefixCleanStrictIdentity(
            "strict-root", ancestors=(_strict_lineage().to_snapshot(),)  # type: ignore[arg-type]
        )


def test_unknown_identity_bearing_field_is_rejected() -> None:
    snapshot = _strict_identity().to_snapshot()
    snapshot["artifact_kind"] = "ConstructionBundle"
    with pytest.raises(IdentityPolicyError, match="identity_fields_not_closed"):
        identity_from_snapshot(snapshot)


def test_typed_lineage_snapshot_is_deterministic_and_closed() -> None:
    lineage = _strict_lineage()
    snapshot = lineage.to_snapshot()
    assert LineageRef.from_snapshot(dict(snapshot)) == lineage
    assert lineage.to_snapshot() == snapshot
    snapshot["unknown_identity_field"] = "not-accepted"
    with pytest.raises(IdentityPolicyError, match="lineage_fields_not_closed"):
        LineageRef.from_snapshot(snapshot)


def test_malformed_and_duplicate_event_spec_pointers_fail_closed() -> None:
    with pytest.raises(IdentityPolicyError, match="malformed_event_spec_pointer"):
        EventSpecUsage("synthetic-event-spec", ("not-a-pointer",))
    with pytest.raises(IdentityPolicyError, match="duplicate_event_spec_pointer"):
        StrictSourceFieldPolicy(("/event_id", "/event_id"), ("/event_id",))
    with pytest.raises(IdentityPolicyError, match="event_spec_allowed_policy_empty"):
        StrictSourceFieldPolicy(("/event_id",), ())
    with pytest.raises(IdentityPolicyError, match="malformed_event_spec_pointer"):
        StrictSourceFieldPolicy(("//ambiguous",), ("/event_id",))


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("suffix_absence_attested", False, "suffix_absence_not_attested"),
        ("reference_absence_attested", False, "reference_absence_not_attested"),
        ("producer_identity", "", "producer_identity_missing"),
        ("review_receipt_id", "", "review_receipt_missing"),
        ("availability", Availability.UNKNOWN, "projection_unknown_availability"),
        ("availability", Availability.CONSTRUCTION_ONLY, "projection_not_available_before_t0"),
        ("source_draft_sha256", "invalid", "projection_source_hash_invalid"),
        ("claim_pointers", (), "projection_claim_pointers_invalid"),
    ],
    ids=[
        "suffix_absence_attested-False-suffix_absence_not_attested",
        "reference_absence_attested-False-reference_absence_not_attested",
        "producer_identity--producer_identity_missing",
        "review_receipt_id--review_receipt_missing",
        "availability-unknown-projection_unknown_availability",
        "availability-construction_only-projection_not_available_before_t0",
        "source_draft_sha256-invalid-projection_source_hash_invalid",
        "claim_pointers-value7-projection_manifest_incomplete",
    ],
)
def test_projection_attestation_fails_closed(field: str, value: object, code: str) -> None:
    with pytest.raises(IdentityPolicyError, match=code):
        validate_strict_entry(
            _strict_identity(), _strict_manifest(), _projection(**{field: value}), "strict-root"
        )


def test_architecture_and_strict_source_manifests_are_not_interchangeable() -> None:
    architecture_manifest = ArchitectureSourceManifest(_strict_manifest().descriptors)
    with pytest.raises(IdentityPolicyError, match="source_manifest_type_invalid"):
        validate_strict_entry(_strict_identity(), architecture_manifest, _projection(), "strict-root")


def test_strict_entry_rejects_strict_manifest_subclass() -> None:
    class ManifestImpostor(StrictSourceManifest):
        def __getattribute__(self, name: str):
            if name == "descriptors":
                raise AssertionError("descriptor access must not run")
            return super().__getattribute__(name)

    manifest = object.__new__(ManifestImpostor)
    with pytest.raises(IdentityPolicyError, match="source_manifest_type_invalid"):
        validate_strict_entry(_strict_identity(), manifest, _projection(), "strict-root")


def test_strict_entry_rejects_descriptor_tuple_subclass_without_iteration() -> None:
    class DescriptorTupleImpostor(tuple):
        def __iter__(self):
            raise AssertionError("iteration must not run")

    manifest = _forged_strict_manifest(DescriptorTupleImpostor(()))
    with pytest.raises(IdentityPolicyError, match="source_manifest_descriptors_invalid"):
        validate_strict_entry(_strict_identity(), manifest, _projection(), "strict-root")


def test_strict_entry_rejects_source_descriptor_subclass() -> None:
    class DescriptorImpostor(SourceDescriptor):
        def __getattribute__(self, name: str):
            raise AssertionError("field access must not run")

    descriptor = object.__new__(DescriptorImpostor)
    with pytest.raises(IdentityPolicyError, match="source_descriptor_type_invalid"):
        validate_strict_entry(
            _strict_identity(), _forged_strict_manifest((descriptor,)), _projection(), "strict-root"
        )


def test_strict_entry_rejects_descriptor_logical_id_string_subclass() -> None:
    class LogicalIdImpostor(str):
        def __hash__(self) -> int:
            raise AssertionError("hash must not run")

        def __eq__(self, other: object) -> bool:
            raise AssertionError("equality must not run")

    descriptor = _forged_source_descriptor(
        logical_source_id=LogicalIdImpostor("synthetic-event-spec")
    )
    with pytest.raises(IdentityPolicyError, match="source_descriptor_id_invalid"):
        validate_strict_entry(
            _strict_identity(), _forged_strict_manifest((descriptor,)), _projection(), "strict-root"
        )


def test_strict_entry_rejects_descriptor_kind_string_subclass() -> None:
    class KindImpostor(str):
        def __eq__(self, other: object) -> bool:
            raise AssertionError("equality must not run")

        __hash__ = str.__hash__

    descriptor = _forged_source_descriptor(source_kind=KindImpostor("event_spec"))
    with pytest.raises(IdentityPolicyError, match="source_descriptor_kind_invalid"):
        validate_strict_entry(
            _strict_identity(), _forged_strict_manifest((descriptor,)), _projection(), "strict-root"
        )


def test_strict_entry_rejects_forged_descriptor_missing_fields_stably() -> None:
    expected = {
        "logical_source_id": "source_descriptor_id_invalid",
        "source_kind": "source_descriptor_kind_invalid",
        "relative_path": "source_descriptor_path_invalid",
        "expected_sha256": "source_descriptor_hash_invalid",
        "availability": "source_descriptor_availability_invalid",
        "review_state": "source_descriptor_review_state_invalid",
    }
    for missing_field, code in expected.items():
        descriptor = _forged_source_descriptor()
        object.__delattr__(descriptor, missing_field)
        with pytest.raises(IdentityPolicyError, match=code):
            validate_strict_entry(
                _strict_identity(),
                _forged_strict_manifest((descriptor,)),
                _projection(),
                "strict-root",
            )


def test_strict_entry_rejects_strict_identity_subclass() -> None:
    class StrictIdentitySubclass(PrefixCleanStrictIdentity):
        pass

    with pytest.raises(IdentityPolicyError, match="strict_identity_required"):
        validate_strict_entry(
            StrictIdentitySubclass("strict-root"),
            _strict_manifest(),
            _projection(),
            "strict-root",
        )


def test_strict_entry_rejects_altered_exact_identity_tuple() -> None:
    identity = _strict_identity()
    object.__setattr__(identity, "construction_state", "architecture_generic")
    with pytest.raises(IdentityPolicyError, match="identity_tuple_mismatch"):
        validate_strict_entry(
            identity, _strict_manifest(), _projection(), "strict-root"
        )


def test_strict_entry_rejects_forged_identity_missing_fields_stably() -> None:
    values = {
        "artifact_id": "strict-root",
        "ancestors": (),
        "construction_state": "prefix_clean_strict",
        "artifact_scope": "target_specific",
        "source_scope": "prefix_target_specific",
        "builder_access": "prefix_allowlist_only",
        "contamination_status": "clean_prefix_only",
        "protocol_eligibility": "strict_eligible",
    }
    for missing_field in values:
        identity = object.__new__(PrefixCleanStrictIdentity)
        for field_name, value in values.items():
            if field_name != missing_field:
                object.__setattr__(identity, field_name, value)
        with pytest.raises(IdentityPolicyError):
            validate_strict_entry(
                identity, _strict_manifest(), _projection(), "strict-root"
            )


def test_strict_entry_revalidates_exact_lineage_type_and_tuple() -> None:
    class LineageSubclass(LineageRef):
        pass

    subclass = LineageSubclass(**_strict_lineage().to_snapshot())
    with pytest.raises(IdentityPolicyError, match="typed_lineage_required"):
        validate_strict_entry(
            _strict_identity(ancestors=(subclass,)),
            _strict_manifest(),
            _projection(),
            "strict-root",
            expected_lineage=(_strict_lineage(),),
        )

    altered = _strict_lineage()
    object.__setattr__(altered, "contamination_status", "full_draft_exposed")
    identity = _strict_identity(ancestors=(altered,))
    with pytest.raises(IdentityPolicyError, match="lineage_identity_tuple_invalid"):
        validate_strict_entry(
            identity,
            _strict_manifest(),
            _projection(),
            "strict-root",
            expected_lineage=(altered,),
        )


def test_strict_entry_rejects_forged_lineage_missing_fields_stably() -> None:
    values = _strict_lineage().to_snapshot()
    for missing_field in values:
        lineage = object.__new__(LineageRef)
        for field_name, value in values.items():
            if field_name != missing_field:
                object.__setattr__(lineage, field_name, value)
        identity = _strict_identity(ancestors=(lineage,))
        with pytest.raises(IdentityPolicyError):
            validate_strict_entry(
                identity,
                _strict_manifest(),
                _projection(),
                "strict-root",
                expected_lineage=(lineage,),
            )


def test_projection_constructor_rejects_claim_pointer_list() -> None:
    with pytest.raises(
        IdentityPolicyError, match="projection_claim_pointers_invalid"
    ):
        _projection(claim_pointers=["/stages/0"])


def test_projection_constructor_rejects_claim_pointer_string_subclass() -> None:
    class PointerSubclass(str):
        pass

    with pytest.raises(
        IdentityPolicyError, match="projection_claim_pointers_invalid"
    ):
        _projection(claim_pointers=(PointerSubclass("/stages/0"),))


def test_projection_constructor_rejects_non_boolean_attestations() -> None:
    for field_name, reason in (
        ("suffix_absence_attested", "projection_suffix_attestation_type_invalid"),
        ("reference_absence_attested", "projection_reference_attestation_type_invalid"),
    ):
        with pytest.raises(IdentityPolicyError, match=reason):
            _projection(**{field_name: 1})


def test_projection_constructor_rejects_noncanonical_availability() -> None:
    with pytest.raises(IdentityPolicyError, match="projection_availability_invalid"):
        _projection(availability="available_before_t0")


def test_strict_entry_rejects_projection_subclass() -> None:
    class ProjectionSubclass(PrefixProjectionAttestation):
        pass

    projection = object.__new__(ProjectionSubclass)
    for field_name, value in _projection().__dict__.items():
        object.__setattr__(projection, field_name, value)
    with pytest.raises(
        IdentityPolicyError, match="projection_attestation_type_invalid"
    ):
        validate_strict_entry(
            _strict_identity(), _strict_manifest(), projection, "strict-root"
        )


def test_strict_entry_rejects_forged_projection_missing_fields_stably() -> None:
    values = _projection().__dict__
    expected = {
        "source_draft_sha256": "projection_source_hash_invalid",
        "cutoff": "projection_cutoff_invalid",
        "projection_policy": "projection_policy_invalid",
        "claim_pointers": "projection_claim_pointers_invalid",
        "suffix_absence_attested": "projection_suffix_attestation_type_invalid",
        "producer_identity": "producer_identity_missing",
        "review_receipt_id": "review_receipt_missing",
        "reference_absence_attested": "projection_reference_attestation_type_invalid",
        "availability": "projection_availability_invalid",
        "architecture_diagnostics_present": "projection_diagnostics_flag_type_invalid",
    }
    for missing_field, reason in expected.items():
        projection = object.__new__(PrefixProjectionAttestation)
        for field_name, value in values.items():
            if field_name != missing_field:
                object.__setattr__(projection, field_name, value)
        with pytest.raises(IdentityPolicyError, match=reason):
            validate_strict_entry(
                _strict_identity(),
                _strict_manifest(),
                projection,
                "strict-root",
            )


def test_valid_projection_attestation_remains_accepted() -> None:
    validate_strict_entry(
        _strict_identity(), _strict_manifest(), _projection(), "strict-root"
    )
